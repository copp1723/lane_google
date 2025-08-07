"""
Google Ads AI Agent
Specialized AI agents for different campaign management roles
"""

import logging
import json
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime
import asyncio

from src.services.openrouter_client import get_openrouter_client
from src.services.ai_service import ModelConfig, ModelProvider

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Agent roles in campaign management"""
    STRATEGIST = "strategist"      # Plans campaign strategy
    CREATOR = "creator"            # Creates campaign structure
    OPTIMIZER = "optimizer"        # Optimizes performance
    MONITOR = "monitor"            # Monitors and alerts
    ANALYST = "analyst"            # Analyzes performance


class GoogleAdsAgent:
    """AI Agent for Google Ads campaign management"""
    
    def __init__(self, role: AgentRole, model: ModelConfig = None):
        self.role = role
        self.model = model or ModelConfig(
            name="claude-3.5-sonnet",
            provider=ModelProvider.ANTHROPIC,
            context_window=200000,
            max_tokens=8192,
            cost_per_1k_tokens=0.003,
            supports_function_calling=True,
            supports_streaming=True
        )
        self.client = get_openrouter_client()
        self.system_prompts = self._initialize_prompts()
        
    def _initialize_prompts(self) -> Dict[str, str]:
        """Initialize role-specific system prompts"""
        prompts = {
            AgentRole.STRATEGIST: """You are an expert Google Ads strategist for the Lane MCP platform. Your role is to:
1. Analyze business requirements and market conditions
2. Develop comprehensive campaign strategies
3. Define target audiences and geographic targeting
4. Recommend budget allocation and bidding strategies
5. Identify key performance indicators and success metrics

When analyzing requirements, consider:
- Business objectives (leads, sales, awareness, etc.)
- Industry and competitive landscape
- Seasonal trends and timing
- Budget constraints and ROI expectations
- Previous campaign performance (if available)

Provide structured, actionable insights in JSON format when requested.""",

            AgentRole.CREATOR: """You are a Google Ads campaign creation specialist for the Lane MCP platform. Your role is to:
1. Transform strategy into campaign structure
2. Create compelling ad copy and headlines
3. Set up ad groups with relevant keywords
4. Configure targeting and bidding settings
5. Ensure compliance with Google Ads policies

When creating campaigns, focus on:
- Clear campaign organization (campaigns > ad groups > ads/keywords)
- Relevant keyword selection with appropriate match types
- Compelling ad copy that drives action
- Landing page alignment
- Extension setup (sitelinks, callouts, etc.)

Return structured campaign configurations in JSON format.""",

            AgentRole.OPTIMIZER: """You are a Google Ads optimization expert for the Lane MCP platform. Your role is to:
1. Analyze campaign performance data
2. Identify optimization opportunities
3. Recommend bid adjustments and budget changes
4. Suggest keyword additions/removals
5. Propose ad copy improvements

When optimizing, consider:
- Key performance metrics (CTR, CPC, conversion rate, ROAS)
- Quality Score improvements
- Search term analysis
- Audience performance
- Device and geographic performance
- Competitive insights

Provide specific, measurable optimization recommendations.""",

            AgentRole.MONITOR: """You are a Google Ads monitoring specialist for the Lane MCP platform. Your role is to:
1. Track campaign performance in real-time
2. Detect anomalies and issues
3. Alert on budget pacing problems
4. Monitor policy compliance
5. Track competitive changes

When monitoring campaigns, watch for:
- Budget overspending or underspending
- Sudden performance drops
- Policy violations or disapprovals
- Competitive bid changes
- Conversion tracking issues
- Unusual traffic patterns

Provide timely alerts with severity levels and recommended actions.""",

            AgentRole.ANALYST: """You are a Google Ads data analyst for the Lane MCP platform. Your role is to:
1. Perform deep performance analysis
2. Generate actionable insights
3. Create performance reports
4. Identify trends and patterns
5. Provide strategic recommendations

When analyzing data, focus on:
- Performance trends over time
- Attribution analysis
- Audience insights
- Creative performance
- ROI and profitability analysis
- Competitive benchmarking

Present findings with clear visualizations and actionable next steps."""
        }
        
        return prompts
    
    async def chat(self, message: str, context_type: str = "general", 
                   conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Chat with the agent"""
        try:
            # Get role-specific system prompt
            system_prompt = self.system_prompts.get(self.role, self.system_prompts[AgentRole.STRATEGIST])
            
            # Add context-specific instructions
            if context_type == "discovery_analysis":
                system_prompt += "\n\nFor this discovery analysis, focus on understanding the business needs and market opportunity."
            elif context_type == "strategy_planning":
                system_prompt += "\n\nFor strategy planning, create a detailed campaign structure with specific recommendations."
            elif context_type == "campaign_review":
                system_prompt += "\n\nFor campaign review, check for policy compliance and optimization opportunities."
            
            # Build messages
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Make API call
            response = await self.client.chat_completion(
                messages=messages,
                model=self.model.model_id,
                max_tokens=self.model.max_output_tokens,
                temperature=0.7
            )
            
            return {
                'response': response['choices'][0]['message']['content'],
                'role': self.role.value,
                'model_used': self.model.model_id,
                'usage': response.get('usage', {})
            }
            
        except Exception as e:
            logger.error(f"Agent chat error ({self.role.value}): {str(e)}")
            # Return a helpful fallback response
            return {
                'response': self._get_fallback_response(message, context_type),
                'role': self.role.value,
                'model_used': 'fallback',
                'error': str(e)
            }
    
    async def analyze_campaign_brief(self, brief: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze campaign brief based on agent role"""
        analysis_prompts = {
            AgentRole.STRATEGIST: f"""Analyze this campaign brief and provide strategic insights:
{json.dumps(brief, indent=2)}

Provide analysis including:
1. Market opportunity assessment
2. Recommended campaign structure
3. Budget allocation strategy
4. Target audience refinement
5. Success metrics and KPIs

Return analysis in JSON format.""",

            AgentRole.CREATOR: f"""Review this campaign brief for implementation:
{json.dumps(brief, indent=2)}

Provide:
1. Recommended campaign settings
2. Ad group structure
3. Keyword suggestions (10-20 keywords)
4. Ad copy variations (3-5 headlines, 2-3 descriptions)
5. Extension recommendations

Return in JSON format.""",

            AgentRole.ANALYST: f"""Analyze this campaign brief for success probability:
{json.dumps(brief, indent=2)}

Assess:
1. Goal achievability (score 1-10)
2. Budget sufficiency
3. Competitive landscape
4. Risk factors
5. Expected performance ranges

Return analysis in JSON format."""
        }
        
        prompt = analysis_prompts.get(self.role, analysis_prompts[AgentRole.STRATEGIST])
        response = await self.chat(prompt, "brief_analysis")
        
        try:
            # Try to parse JSON response
            analysis = json.loads(response['response'])
            return {
                'success': True,
                'analysis': analysis,
                'agent_role': self.role.value
            }
        except json.JSONDecodeError:
            return {
                'success': True,
                'analysis': response['response'],
                'agent_role': self.role.value,
                'format': 'text'
            }
    
    async def generate_campaign_structure(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Generate campaign structure (Creator role specific)"""
        if self.role != AgentRole.CREATOR:
            return {'error': 'This method is only available for Creator agents'}
        
        prompt = f"""Based on this strategy, create a detailed Google Ads campaign structure:
{json.dumps(strategy, indent=2)}

Generate:
1. Campaign configuration with all settings
2. Ad groups (2-5) with themes
3. Keywords for each ad group (5-10 per group)
4. Ad copy for each ad group (3 responsive search ads)
5. Ad extensions (sitelinks, callouts, structured snippets)

Return complete campaign structure in JSON format following Google Ads API schema."""
        
        response = await self.chat(prompt, "structure_generation")
        
        try:
            structure = json.loads(response['response'])
            return {
                'success': True,
                'campaign_structure': structure
            }
        except json.JSONDecodeError:
            # Return a basic structure if parsing fails
            return {
                'success': True,
                'campaign_structure': self._get_default_campaign_structure(strategy)
            }
    
    async def analyze_performance(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze campaign performance (Optimizer/Analyst role specific)"""
        if self.role not in [AgentRole.OPTIMIZER, AgentRole.ANALYST]:
            return {'error': 'This method is only available for Optimizer and Analyst agents'}
        
        prompt = f"""Analyze this campaign performance data:
{json.dumps(performance_data, indent=2)}

Provide:
1. Performance assessment (good/needs improvement/poor)
2. Key insights and trends
3. Specific optimization recommendations
4. Priority actions (ranked by impact)
5. Expected results from recommendations

Return structured analysis in JSON format."""
        
        response = await self.chat(prompt, "performance_analysis")
        
        try:
            analysis = json.loads(response['response'])
            return {
                'success': True,
                'analysis': analysis,
                'agent_role': self.role.value
            }
        except json.JSONDecodeError:
            return {
                'success': True,
                'analysis': response['response'],
                'agent_role': self.role.value,
                'format': 'text'
            }
    
    async def monitor_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor campaign for issues (Monitor role specific)"""
        if self.role != AgentRole.MONITOR:
            return {'error': 'This method is only available for Monitor agents'}
        
        prompt = f"""Monitor this campaign for issues and anomalies:
{json.dumps(campaign_data, indent=2)}

Check for:
1. Budget pacing issues
2. Performance anomalies
3. Policy compliance risks
4. Conversion tracking problems
5. Competitive threats

Return monitoring results with:
- Issues found (with severity: high/medium/low)
- Recommended actions
- Monitoring alerts to set up

Format as JSON."""
        
        response = await self.chat(prompt, "campaign_monitoring")
        
        try:
            monitoring_result = json.loads(response['response'])
            return {
                'success': True,
                'monitoring': monitoring_result,
                'alerts_generated': len(monitoring_result.get('issues', []))
            }
        except json.JSONDecodeError:
            return {
                'success': True,
                'monitoring': response['response'],
                'format': 'text'
            }
    
    def _get_fallback_response(self, message: str, context_type: str) -> str:
        """Get role-specific fallback response"""
        fallback_responses = {
            AgentRole.STRATEGIST: "I'll help you develop a comprehensive campaign strategy. Let me analyze your requirements and provide strategic recommendations.",
            AgentRole.CREATOR: "I'll help you create an effective campaign structure. Let me design the campaigns, ad groups, and ads for optimal performance.",
            AgentRole.OPTIMIZER: "I'll analyze the performance data and provide optimization recommendations to improve your campaign results.",
            AgentRole.MONITOR: "I'll monitor your campaigns for any issues or opportunities. Let me check the current performance metrics.",
            AgentRole.ANALYST: "I'll provide detailed analysis of your campaign performance and actionable insights for improvement."
        }
        
        return fallback_responses.get(self.role, "I'll help you with your Google Ads campaign.")
    
    def _get_default_campaign_structure(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Get default campaign structure as fallback"""
        return {
            "campaign": {
                "name": strategy.get("campaign_name", "New Campaign"),
                "budget": strategy.get("budget", 1000),
                "bidding_strategy": "MAXIMIZE_CONVERSIONS",
                "networks": ["SEARCH", "SEARCH_PARTNERS"],
                "locations": strategy.get("locations", ["United States"]),
                "languages": ["en"]
            },
            "ad_groups": [
                {
                    "name": "Primary Ad Group",
                    "keywords": [
                        {"text": "example keyword", "match_type": "BROAD"},
                        {"text": "sample keyword", "match_type": "PHRASE"},
                        {"text": "[exact match keyword]", "match_type": "EXACT"}
                    ],
                    "ads": [
                        {
                            "headlines": [
                                "Professional Services",
                                "Get Started Today",
                                "Expert Solutions"
                            ],
                            "descriptions": [
                                "Discover our range of professional services.",
                                "Contact us for a free consultation."
                            ]
                        }
                    ]
                }
            ],
            "extensions": {
                "sitelinks": [
                    {"text": "About Us", "url": "/about"},
                    {"text": "Services", "url": "/services"},
                    {"text": "Contact", "url": "/contact"}
                ],
                "callouts": [
                    "Free Consultation",
                    "Expert Team",
                    "24/7 Support"
                ]
            }
        }


# Factory function to create agents
def create_agent(role: AgentRole, model: ModelConfig = None) -> GoogleAdsAgent:
    """Create a Google Ads agent with specified role"""
    return GoogleAdsAgent(role, model)