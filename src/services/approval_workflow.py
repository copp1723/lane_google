"""
Approval Workflow Service
Manages approval processes for campaign changes and budget adjustments
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field
import asyncio
from database import db

logger = logging.getLogger(__name__)


class ApprovalStatus(Enum):
    """Approval request status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class ApprovalType(Enum):
    """Types of approval requests"""
    CAMPAIGN_LAUNCH = "campaign_launch"
    BUDGET_INCREASE = "budget_increase"
    BUDGET_DECREASE = "budget_decrease"
    CAMPAIGN_PAUSE = "campaign_pause"
    CAMPAIGN_DELETE = "campaign_delete"
    TARGETING_CHANGE = "targeting_change"
    BID_STRATEGY_CHANGE = "bid_strategy_change"


class Priority(Enum):
    """Approval priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class ApprovalRequest:
    """Approval request data structure"""
    id: str
    request_type: ApprovalType
    requester_id: str
    campaign_id: str
    title: str
    description: str
    priority: Priority
    approval_config: Dict[str, Any]  # rules, approvers, etc.
    request_data: Dict[str, Any]  # specific data for the request
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None


@dataclass
class ApprovalRule:
    """Approval rule configuration"""
    request_type: ApprovalType
    conditions: Dict[str, Any]  # conditions that trigger this rule
    approvers: List[str]  # user IDs or roles
    approval_mode: str  # single, majority, unanimous
    timeout_hours: int
    auto_approve_conditions: Optional[Dict[str, Any]] = None
    escalation_rules: Optional[Dict[str, Any]] = None


class ApprovalWorkflow:
    """Manages approval workflows for campaign operations"""
    
    def __init__(self):
        self.pending_requests = {}
        self.approval_rules = self._initialize_default_rules()
        self.notification_callbacks = []
        self.monitoring_task = None
        
    def _initialize_default_rules(self) -> Dict[ApprovalType, ApprovalRule]:
        """Initialize default approval rules"""
        return {
            ApprovalType.CAMPAIGN_LAUNCH: ApprovalRule(
                request_type=ApprovalType.CAMPAIGN_LAUNCH,
                conditions={'budget_threshold': 1000},
                approvers=['campaign_manager'],
                approval_mode='single',
                timeout_hours=24,
                auto_approve_conditions={'budget_under': 500}
            ),
            ApprovalType.BUDGET_INCREASE: ApprovalRule(
                request_type=ApprovalType.BUDGET_INCREASE,
                conditions={'increase_percent': 20},
                approvers=['budget_manager', 'campaign_manager'],
                approval_mode='single',
                timeout_hours=12,
                auto_approve_conditions={'increase_under': 100}
            ),
            ApprovalType.BUDGET_DECREASE: ApprovalRule(
                request_type=ApprovalType.BUDGET_DECREASE,
                conditions={'decrease_percent': 50},
                approvers=['campaign_manager'],
                approval_mode='single',
                timeout_hours=6
            ),
            ApprovalType.CAMPAIGN_PAUSE: ApprovalRule(
                request_type=ApprovalType.CAMPAIGN_PAUSE,
                conditions={},
                approvers=['campaign_manager'],
                approval_mode='single',
                timeout_hours=4
            ),
            ApprovalType.CAMPAIGN_DELETE: ApprovalRule(
                request_type=ApprovalType.CAMPAIGN_DELETE,
                conditions={},
                approvers=['account_admin', 'campaign_manager'],
                approval_mode='majority',
                timeout_hours=48
            )
        }
    
    async def start_monitoring(self):
        """Start approval monitoring for timeouts"""
        if self.monitoring_task:
            return
        
        logger.info("Starting approval workflow monitoring")
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
    
    async def stop_monitoring(self):
        """Stop approval monitoring"""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None
    
    async def _monitoring_loop(self):
        """Monitor for expired approvals"""
        while True:
            try:
                await self._check_expired_requests()
                await asyncio.sleep(300)  # Check every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in approval monitoring: {str(e)}")
                await asyncio.sleep(60)
    
    async def _check_expired_requests(self):
        """Check for and handle expired approval requests"""
        current_time = datetime.utcnow()
        
        for request_id, request in list(self.pending_requests.items()):
            if (request.status == ApprovalStatus.PENDING and 
                request.expires_at and 
                current_time > request.expires_at):
                
                logger.warning(f"Approval request {request_id} expired")
                request.status = ApprovalStatus.EXPIRED
                
                # Handle expiration based on type
                await self._handle_expired_request(request)
                
                # Remove from pending
                del self.pending_requests[request_id]
    
    async def _handle_expired_request(self, request: ApprovalRequest):
        """Handle expired approval request"""
        # Store in database
        from src.models.approval_request import ApprovalRequestModel
        
        db_request = ApprovalRequestModel(
            id=request.id,
            request_type=request.request_type.value,
            requester_id=request.requester_id,
            campaign_id=request.campaign_id,
            title=request.title,
            description=request.description,
            priority=request.priority.value,
            status=request.status.value,
            expires_at=request.expires_at,
            request_data=request.request_data
        )
        db.session.add(db_request)
        db.session.commit()
        
        # Notify stakeholders
        await self._notify_expiration(request)
    
    async def submit_approval_request(self, request_type: ApprovalType,
                                    requester_id: str, campaign_id: str,
                                    title: str, description: str,
                                    request_data: Dict[str, Any],
                                    priority: Priority = Priority.MEDIUM) -> str:
        """Submit a new approval request"""
        
        # Get approval rule
        rule = self.approval_rules.get(request_type)
        if not rule:
            raise ValueError(f"No approval rule defined for {request_type.value}")
        
        # Check if auto-approval applies
        if await self._check_auto_approval(rule, request_data):
            logger.info(f"Auto-approving {request_type.value} request")
            await self._execute_auto_approval(
                request_type, requester_id, campaign_id, request_data
            )
            return "auto_approved"
        
        # Create approval request
        request_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=rule.timeout_hours)
        
        approval_request = ApprovalRequest(
            id=request_id,
            request_type=request_type,
            requester_id=requester_id,
            campaign_id=campaign_id,
            title=title,
            description=description,
            priority=priority,
            approval_config={
                'approvers': rule.approvers,
                'approval_mode': rule.approval_mode,
                'timeout_hours': rule.timeout_hours
            },
            request_data=request_data,
            expires_at=expires_at
        )
        
        # Store pending request
        self.pending_requests[request_id] = approval_request
        
        # Store in database
        from src.models.approval_request import ApprovalRequestModel
        
        db_request = ApprovalRequestModel(
            id=request_id,
            request_type=request_type.value,
            requester_id=requester_id,
            campaign_id=campaign_id,
            title=title,
            description=description,
            priority=priority.value,
            status=ApprovalStatus.PENDING.value,
            expires_at=expires_at,
            request_data=request_data,
            approval_config=approval_request.approval_config
        )
        db.session.add(db_request)
        db.session.commit()
        
        # Notify approvers
        await self._notify_approvers(approval_request)
        
        logger.info(f"Created approval request {request_id} for {request_type.value}")
        return request_id
    
    async def _check_auto_approval(self, rule: ApprovalRule, 
                                 request_data: Dict[str, Any]) -> bool:
        """Check if request qualifies for auto-approval"""
        if not rule.auto_approve_conditions:
            return False
        
        for condition, threshold in rule.auto_approve_conditions.items():
            if condition == 'budget_under':
                if request_data.get('budget_amount', 0) >= threshold:
                    return False
            elif condition == 'increase_under':
                if request_data.get('increase_amount', 0) >= threshold:
                    return False
        
        return True
    
    async def _execute_auto_approval(self, request_type: ApprovalType,
                                   requester_id: str, campaign_id: str,
                                   request_data: Dict[str, Any]):
        """Execute auto-approved request"""
        try:
            await self._execute_approved_action(request_type, campaign_id, request_data)
            
            # Log auto-approval
            logger.info(f"Auto-executed {request_type.value} for campaign {campaign_id}")
            
        except Exception as e:
            logger.error(f"Error executing auto-approval: {str(e)}")
            raise
    
    async def approve_request(self, request_id: str, approver_id: str,
                            comments: Optional[str] = None) -> bool:
        """Approve a pending request"""
        request = self.pending_requests.get(request_id)
        if not request:
            raise ValueError(f"Approval request {request_id} not found")
        
        if request.status != ApprovalStatus.PENDING:
            raise ValueError(f"Request {request_id} is not pending approval")
        
        # Validate approver authorization
        if not await self._validate_approver(request, approver_id):
            raise ValueError(f"User {approver_id} not authorized to approve this request")
        
        # Approve request
        request.status = ApprovalStatus.APPROVED
        request.approved_by = approver_id
        request.approved_at = datetime.utcnow()
        
        # Update database
        from src.models.approval_request import ApprovalRequestModel
        db_request = ApprovalRequestModel.query.get(request_id)
        if db_request:
            db_request.status = ApprovalStatus.APPROVED.value
            db_request.approved_by = approver_id
            db_request.approved_at = request.approved_at
            db_request.comments = comments
            db.session.commit()
        
        # Execute the approved action
        try:
            await self._execute_approved_action(
                request.request_type, request.campaign_id, request.request_data
            )
            
            # Remove from pending
            del self.pending_requests[request_id]
            
            # Notify requester
            await self._notify_approval(request, approver_id, comments)
            
            logger.info(f"Approved and executed request {request_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error executing approved action: {str(e)}")
            # Revert approval status
            request.status = ApprovalStatus.PENDING
            raise
    
    async def reject_request(self, request_id: str, rejector_id: str,
                           reason: str) -> bool:
        """Reject a pending request"""
        request = self.pending_requests.get(request_id)
        if not request:
            raise ValueError(f"Approval request {request_id} not found")
        
        if request.status != ApprovalStatus.PENDING:
            raise ValueError(f"Request {request_id} is not pending approval")
        
        # Validate rejector authorization
        if not await self._validate_approver(request, rejector_id):
            raise ValueError(f"User {rejector_id} not authorized to reject this request")
        
        # Reject request
        request.status = ApprovalStatus.REJECTED
        request.rejection_reason = reason
        
        # Update database
        from src.models.approval_request import ApprovalRequestModel
        db_request = ApprovalRequestModel.query.get(request_id)
        if db_request:
            db_request.status = ApprovalStatus.REJECTED.value
            db_request.rejection_reason = reason
            db.session.commit()
        
        # Remove from pending
        del self.pending_requests[request_id]
        
        # Notify requester
        await self._notify_rejection(request, rejector_id, reason)
        
        logger.info(f"Rejected request {request_id}")
        return True
    
    async def _validate_approver(self, request: ApprovalRequest, user_id: str) -> bool:
        """Validate if user can approve this request"""
        # Check if user is in the approvers list
        approvers = request.approval_config.get('approvers', [])
        
        # For simplicity, assuming user_id matches role
        # In production, you'd check user roles
        return user_id in approvers or user_id == 'admin'
    
    async def _execute_approved_action(self, request_type: ApprovalType,
                                     campaign_id: str, request_data: Dict[str, Any]):
        """Execute the approved action"""
        from campaign import Campaign
        
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        if request_type == ApprovalType.CAMPAIGN_LAUNCH:
            campaign.status = 'active'
            
        elif request_type == ApprovalType.BUDGET_INCREASE:
            new_budget = request_data.get('new_budget')
            if new_budget:
                campaign.budget_amount = new_budget
                
        elif request_type == ApprovalType.BUDGET_DECREASE:
            new_budget = request_data.get('new_budget')
            if new_budget:
                campaign.budget_amount = new_budget
                
        elif request_type == ApprovalType.CAMPAIGN_PAUSE:
            campaign.status = 'paused'
            
        elif request_type == ApprovalType.CAMPAIGN_DELETE:
            # Soft delete by changing status
            campaign.status = 'deleted'
        
        db.session.commit()
        logger.info(f"Executed {request_type.value} for campaign {campaign_id}")
    
    async def _notify_approvers(self, request: ApprovalRequest):
        """Notify approvers about new request"""
        for callback in self.notification_callbacks:
            try:
                await callback('new_request', request)
            except Exception as e:
                logger.error(f"Error in notification callback: {str(e)}")
    
    async def _notify_approval(self, request: ApprovalRequest, approver_id: str,
                             comments: Optional[str]):
        """Notify requester about approval"""
        for callback in self.notification_callbacks:
            try:
                await callback('approved', request, approver_id, comments)
            except Exception as e:
                logger.error(f"Error in notification callback: {str(e)}")
    
    async def _notify_rejection(self, request: ApprovalRequest, rejector_id: str,
                              reason: str):
        """Notify requester about rejection"""
        for callback in self.notification_callbacks:
            try:
                await callback('rejected', request, rejector_id, reason)
            except Exception as e:
                logger.error(f"Error in notification callback: {str(e)}")
    
    async def _notify_expiration(self, request: ApprovalRequest):
        """Notify about expired request"""
        for callback in self.notification_callbacks:
            try:
                await callback('expired', request)
            except Exception as e:
                logger.error(f"Error in notification callback: {str(e)}")
    
    def register_notification_callback(self, callback):
        """Register callback for approval notifications"""
        self.notification_callbacks.append(callback)
    
    def get_pending_requests(self, user_id: Optional[str] = None,
                           campaign_id: Optional[str] = None) -> List[ApprovalRequest]:
        """Get pending approval requests"""
        requests = list(self.pending_requests.values())
        
        if user_id:
            # Filter by approver (simplified check)
            requests = [r for r in requests if user_id in r.approval_config.get('approvers', [])]
        
        if campaign_id:
            requests = [r for r in requests if r.campaign_id == campaign_id]
        
        return requests
    
    def get_request_status(self, request_id: str) -> Optional[ApprovalRequest]:
        """Get status of a specific request"""
        return self.pending_requests.get(request_id)


# Global approval workflow instance
approval_workflow = ApprovalWorkflow()