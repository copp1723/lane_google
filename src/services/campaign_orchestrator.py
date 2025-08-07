"""
Campaign Orchestration Service
Manages multi-agent collaboration for Google Ads campaign automation
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field
import json
from src.config.database import db
from src.services.google_ads_agent import GoogleAdsAgent, AgentRole as GoogleAdsAgentRole, create_agent
from src.services.real_google_ads import RealGoogleAdsService

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Agent roles in campaign management"""
    STRATEGIST = "strategist"      # Plans campaign strategy
    CREATOR = "creator"            # Creates campaign structure
    OPTIMIZER = "optimizer"        # Optimizes performance
    MONITOR = "monitor"            # Monitors and alerts
    ANALYST = "analyst"            # Analyzes performance


class TaskPhase(Enum):
    """Campaign task phases"""
    DISCOVERY = "discovery"
    PLANNING = "planning"
    CREATION = "creation"
    REVIEW = "review"
    LAUNCH = "launch"
    MONITORING = "monitoring"
    OPTIMIZATION = "optimization"


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentTask:
    """Represents a task assigned to an agent"""
    id: str
    agent_role: AgentRole
    phase: TaskPhase
    description: str
    context: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


@dataclass
class WorkflowStatus:
    """Campaign workflow status"""
    workflow_id: str
    campaign_id: str
    current_phase: TaskPhase
    progress: float  # 0-100
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    message: str
    start_time: datetime
    estimated_completion: Optional[datetime] = None


class CampaignOrchestrator:
    """Orchestrates campaign management using multiple agents"""
    
    def __init__(self, google_ads_service: RealGoogleAdsService):
        self.google_ads_service = google_ads_service
        self.agents = {}
        self.workflows = {}
        self.task_queue = asyncio.Queue()
        self.status_callbacks = []
        self._initialize_agents()
        
    def _initialize_agents(self):
        """Initialize specialized agents"""
        # Create specialized agents for each role
        self.agents[AgentRole.STRATEGIST] = create_agent(GoogleAdsAgentRole.STRATEGIST)
        self.agents[AgentRole.CREATOR] = create_agent(GoogleAdsAgentRole.CREATOR)
        self.agents[AgentRole.OPTIMIZER] = create_agent(GoogleAdsAgentRole.OPTIMIZER)
        self.agents[AgentRole.MONITOR] = create_agent(GoogleAdsAgentRole.MONITOR)
        self.agents[AgentRole.ANALYST] = create_agent(GoogleAdsAgentRole.ANALYST)
        
        logger.info(f"Initialized {len(self.agents)} specialized agents")
    
    async def create_campaign_workflow(self, campaign_brief: Dict[str, Any], 
                                     campaign_id: str) -> str:
        """Create a complete campaign workflow"""
        workflow_id = str(uuid.uuid4())
        
        # Initialize workflow
        workflow = {
            'id': workflow_id,
            'campaign_id': campaign_id,
            'brief': campaign_brief,
            'tasks': [],
            'status': WorkflowStatus(
                workflow_id=workflow_id,
                campaign_id=campaign_id,
                current_phase=TaskPhase.DISCOVERY,
                progress=0,
                active_tasks=0,
                completed_tasks=0,
                failed_tasks=0,
                message="Initializing campaign workflow",
                start_time=datetime.utcnow()
            )
        }
        
        self.workflows[workflow_id] = workflow
        
        # Create tasks for each phase
        tasks = self._create_workflow_tasks(campaign_brief, campaign_id, workflow_id)
        workflow['tasks'] = tasks
        
        # Start workflow execution
        asyncio.create_task(self._execute_workflow(workflow_id))
        
        logger.info(f"Created campaign workflow {workflow_id} with {len(tasks)} tasks")
        return workflow_id
    
    def _create_workflow_tasks(self, brief: Dict[str, Any], 
                             campaign_id: str, workflow_id: str) -> List[AgentTask]:
        """Create tasks for campaign workflow"""
        tasks = []
        
        # Phase 1: Discovery - Analyze requirements
        discovery_task = AgentTask(
            id=f"{workflow_id}_discovery",
            agent_role=AgentRole.STRATEGIST,
            phase=TaskPhase.DISCOVERY,
            description="Analyze campaign requirements and market conditions",
            context={'brief': brief, 'campaign_id': campaign_id}
        )
        tasks.append(discovery_task)
        
        # Phase 2: Planning - Create strategy
        planning_task = AgentTask(
            id=f"{workflow_id}_planning",
            agent_role=AgentRole.STRATEGIST,
            phase=TaskPhase.PLANNING,
            description="Develop comprehensive campaign strategy",
            context={'brief': brief, 'campaign_id': campaign_id},
            dependencies=[discovery_task.id]
        )
        tasks.append(planning_task)
        
        # Phase 3: Creation - Build campaign
        creation_task = AgentTask(
            id=f"{workflow_id}_creation",
            agent_role=AgentRole.CREATOR,
            phase=TaskPhase.CREATION,
            description="Create campaign structure, ad groups, and ads",
            context={'brief': brief, 'campaign_id': campaign_id},
            dependencies=[planning_task.id]
        )
        tasks.append(creation_task)
        
        # Phase 4: Review - Quality check
        review_task = AgentTask(
            id=f"{workflow_id}_review",
            agent_role=AgentRole.ANALYST,
            phase=TaskPhase.REVIEW,
            description="Review campaign for quality and compliance",
            context={'brief': brief, 'campaign_id': campaign_id},
            dependencies=[creation_task.id]
        )
        tasks.append(review_task)
        
        # Phase 5: Launch - Deploy campaign
        launch_task = AgentTask(
            id=f"{workflow_id}_launch",
            agent_role=AgentRole.CREATOR,
            phase=TaskPhase.LAUNCH,
            description="Launch campaign with appropriate settings",
            context={'brief': brief, 'campaign_id': campaign_id},
            dependencies=[review_task.id]
        )
        tasks.append(launch_task)
        
        # Phase 6: Initial Monitoring
        monitor_task = AgentTask(
            id=f"{workflow_id}_monitor",
            agent_role=AgentRole.MONITOR,
            phase=TaskPhase.MONITORING,
            description="Set up monitoring and initial performance check",
            context={'brief': brief, 'campaign_id': campaign_id},
            dependencies=[launch_task.id]
        )
        tasks.append(monitor_task)
        
        return tasks
    
    async def _execute_workflow(self, workflow_id: str):
        """Execute a campaign workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            logger.error(f"Workflow {workflow_id} not found")
            return
        
        try:
            # Execute tasks in dependency order
            completed_tasks = set()
            
            while len(completed_tasks) < len(workflow['tasks']):
                # Find tasks ready to execute
                ready_tasks = [
                    task for task in workflow['tasks']
                    if task.id not in completed_tasks
                    and all(dep in completed_tasks for dep in task.dependencies)
                    and task.status == TaskStatus.PENDING
                ]
                
                if not ready_tasks:
                    # Check for failed dependencies
                    failed_tasks = [
                        task for task in workflow['tasks']
                        if task.status == TaskStatus.FAILED
                    ]
                    if failed_tasks:
                        logger.error(f"Workflow {workflow_id} has failed tasks")
                        break
                    
                    # No tasks ready, wait
                    await asyncio.sleep(1)
                    continue
                
                # Execute ready tasks in parallel
                await self._execute_tasks_parallel(ready_tasks, workflow)
                
                # Update completed tasks
                for task in ready_tasks:
                    if task.status == TaskStatus.COMPLETED:
                        completed_tasks.add(task.id)
                
                # Update workflow progress
                self._update_workflow_progress(workflow)
            
            # Finalize workflow
            workflow['status'].message = "Campaign workflow completed"
            logger.info(f"Workflow {workflow_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            workflow['status'].message = f"Workflow failed: {str(e)}"
    
    async def _execute_tasks_parallel(self, tasks: List[AgentTask], workflow: Dict):
        """Execute multiple tasks in parallel"""
        # Update active task count
        workflow['status'].active_tasks = len(tasks)
        
        # Create task coroutines
        task_coroutines = [
            self._execute_single_task(task, workflow)
            for task in tasks
        ]
        
        # Execute in parallel
        await asyncio.gather(*task_coroutines, return_exceptions=True)
        
        # Update active task count
        workflow['status'].active_tasks = 0
    
    async def _execute_single_task(self, task: AgentTask, workflow: Dict):
        """Execute a single task"""
        try:
            logger.info(f"Executing task {task.id} for phase {task.phase.value}")
            
            task.status = TaskStatus.IN_PROGRESS
            workflow['status'].current_phase = task.phase
            
            # Get the appropriate agent
            agent = self.agents.get(task.agent_role)
            if not agent:
                raise ValueError(f"No agent available for role {task.agent_role.value}")
            
            # Execute task based on phase
            result = await self._execute_phase_task(task, agent)
            
            # Update task status
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.utcnow()
            workflow['status'].completed_tasks += 1
            
            logger.info(f"Task {task.id} completed successfully")
            
        except Exception as e:
            logger.error(f"Task {task.id} failed: {str(e)}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
            workflow['status'].failed_tasks += 1
    
    async def _execute_phase_task(self, task: AgentTask, agent: GoogleAdsAgent) -> Dict[str, Any]:
        """Execute task based on phase"""
        brief = task.context.get('brief', {})
        
        if task.phase == TaskPhase.DISCOVERY:
            # Analyze market and requirements
            result = await agent.analyze_campaign_brief(brief)
            return {'analysis': result.get('analysis', result)}
        
        elif task.phase == TaskPhase.PLANNING:
            # Create campaign strategy
            # Get previous analysis if available
            previous_tasks = [t for t in self.workflows.get(task.id.split('_')[0], {}).get('tasks', []) 
                            if t.status == TaskStatus.COMPLETED and t.phase == TaskPhase.DISCOVERY]
            
            context = {
                'brief': brief,
                'discovery_analysis': previous_tasks[0].result if previous_tasks else None
            }
            
            prompt = f"""
            Create a comprehensive campaign strategy based on:
            {json.dumps(context, indent=2)}
            
            Include:
            1. Campaign structure (campaigns, ad groups)
            2. Targeting strategy
            3. Bidding strategy
            4. Ad creative approach
            5. Budget allocation
            
            Return as structured JSON.
            """
            response = await agent.chat(prompt, "strategy_planning")
            return {'strategy': response['response']}
        
        elif task.phase == TaskPhase.CREATION:
            # Create campaign structure
            # Get strategy from previous phase
            previous_tasks = [t for t in self.workflows.get(task.id.split('_')[0], {}).get('tasks', []) 
                            if t.status == TaskStatus.COMPLETED and t.phase == TaskPhase.PLANNING]
            
            strategy = previous_tasks[0].result.get('strategy', {}) if previous_tasks else brief
            
            if isinstance(agent, GoogleAdsAgent) and agent.role == GoogleAdsAgentRole.CREATOR:
                result = await agent.generate_campaign_structure(strategy)
                return {'structure': result.get('campaign_structure', result)}
            else:
                # Fallback structure
                campaign_structure = {
                    'campaign': {
                        'name': brief.get('campaign_name', 'New Campaign'),
                        'budget': brief.get('budget', 1000),
                        'bidding_strategy': brief.get('bidding_strategy', 'MAXIMIZE_CONVERSIONS')
                    },
                    'ad_groups': [
                        {
                            'name': 'Ad Group 1',
                            'keywords': brief.get('keywords', []),
                            'ads': []
                        }
                    ]
                }
                return {'structure': campaign_structure}
        
        elif task.phase == TaskPhase.REVIEW:
            # Review campaign quality
            # Get created structure from previous phase
            previous_tasks = [t for t in self.workflows.get(task.id.split('_')[0], {}).get('tasks', []) 
                            if t.status == TaskStatus.COMPLETED and t.phase == TaskPhase.CREATION]
            
            review_context = {
                'brief': brief,
                'campaign_structure': previous_tasks[0].result if previous_tasks else None
            }
            
            result = await agent.analyze_campaign_brief(review_context)
            return {'review': result.get('analysis', result)}
        
        elif task.phase == TaskPhase.LAUNCH:
            # Launch campaign
            # In production, this would activate the campaign via API
            logger.info(f"Launching campaign {task.context.get('campaign_id')}")
            
            # Here we would integrate with self.google_ads_service to actually create the campaign
            # For now, return success
            return {
                'launched': True,
                'campaign_id': task.context.get('campaign_id'),
                'launch_time': datetime.utcnow().isoformat()
            }
        
        elif task.phase == TaskPhase.MONITORING:
            # Set up monitoring
            if isinstance(agent, GoogleAdsAgent) and agent.role == GoogleAdsAgentRole.MONITOR:
                # Get campaign data (in production from Google Ads API)
                campaign_data = {
                    'campaign_id': task.context.get('campaign_id'),
                    'budget': brief.get('budget', 1000),
                    'current_spend': 0,
                    'impressions': 0,
                    'clicks': 0,
                    'conversions': 0,
                    'status': 'ENABLED'
                }
                
                result = await agent.monitor_campaign(campaign_data)
                return result.get('monitoring', {
                    'alerts': [
                        {'type': 'budget_overspend', 'threshold': 0.9},
                        {'type': 'performance_drop', 'threshold': -20},
                        {'type': 'low_impressions', 'threshold': 100}
                    ],
                    'reporting_frequency': 'daily',
                    'metrics': ['impressions', 'clicks', 'conversions', 'cost']
                })
            else:
                # Fallback monitoring config
                return {
                    'monitoring_config': {
                        'alerts': [
                            {'type': 'budget_overspend', 'threshold': 0.9},
                            {'type': 'performance_drop', 'threshold': -20},
                            {'type': 'low_impressions', 'threshold': 100}
                        ],
                        'reporting_frequency': 'daily',
                        'metrics': ['impressions', 'clicks', 'conversions', 'cost']
                    }
                }
        
        else:
            raise ValueError(f"Unknown task phase: {task.phase}")
    
    def _update_workflow_progress(self, workflow: Dict):
        """Update workflow progress"""
        total_tasks = len(workflow['tasks'])
        completed = workflow['status'].completed_tasks
        
        workflow['status'].progress = (completed / total_tasks * 100) if total_tasks > 0 else 0
        
        # Estimate completion time
        if completed > 0:
            elapsed = (datetime.utcnow() - workflow['status'].start_time).total_seconds()
            avg_task_time = elapsed / completed
            remaining_tasks = total_tasks - completed
            estimated_remaining = avg_task_time * remaining_tasks
            workflow['status'].estimated_completion = datetime.utcnow() + timedelta(seconds=estimated_remaining)
        
        # Notify status callbacks
        for callback in self.status_callbacks:
            try:
                callback(workflow['status'])
            except Exception as e:
                logger.error(f"Status callback error: {str(e)}")
    
    def register_status_callback(self, callback):
        """Register a callback for workflow status updates"""
        self.status_callbacks.append(callback)
    
    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowStatus]:
        """Get current workflow status"""
        workflow = self.workflows.get(workflow_id)
        return workflow['status'] if workflow else None
    
    def get_workflow_tasks(self, workflow_id: str) -> List[AgentTask]:
        """Get all tasks for a workflow"""
        workflow = self.workflows.get(workflow_id)
        return workflow['tasks'] if workflow else []
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return False
        
        # Cancel pending tasks
        for task in workflow['tasks']:
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.CANCELLED
        
        workflow['status'].message = "Workflow cancelled"
        logger.info(f"Workflow {workflow_id} cancelled")
        return True


# Global orchestrator instance (initialized in main.py)
campaign_orchestrator = None