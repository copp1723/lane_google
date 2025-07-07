"""
Audit Log Model for Compliance and Security
Comprehensive audit logging for all system activities
"""

from datetime import datetime
from enum import Enum
import uuid
import json

from src.database import db

class AuditAction(Enum):
    """Types of auditable actions"""
    # Authentication actions
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGED = "password_changed"
    
    # User management actions
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_ROLE_CHANGED = "user_role_changed"
    USER_PERMISSIONS_CHANGED = "user_permissions_changed"
    
    # Campaign actions
    CAMPAIGN_CREATED = "campaign_created"
    CAMPAIGN_UPDATED = "campaign_updated"
    CAMPAIGN_DELETED = "campaign_deleted"
    CAMPAIGN_APPROVED = "campaign_approved"
    CAMPAIGN_REJECTED = "campaign_rejected"
    CAMPAIGN_ACTIVATED = "campaign_activated"
    CAMPAIGN_PAUSED = "campaign_paused"
    
    # Google Ads actions
    GOOGLE_ADS_ACCOUNT_CONNECTED = "google_ads_account_connected"
    GOOGLE_ADS_CAMPAIGN_CREATED = "google_ads_campaign_created"
    GOOGLE_ADS_CAMPAIGN_MODIFIED = "google_ads_campaign_modified"
    GOOGLE_ADS_BUDGET_CHANGED = "google_ads_budget_changed"
    
    # AI actions
    AI_CONVERSATION_STARTED = "ai_conversation_started"
    AI_CAMPAIGN_BRIEF_GENERATED = "ai_campaign_brief_generated"
    AI_OPTIMIZATION_PERFORMED = "ai_optimization_performed"
    
    # System actions
    SYSTEM_BACKUP_CREATED = "system_backup_created"
    SYSTEM_MAINTENANCE = "system_maintenance"
    SYSTEM_ERROR = "system_error"
    
    # Data actions
    DATA_EXPORTED = "data_exported"
    DATA_IMPORTED = "data_imported"
    DATA_DELETED = "data_deleted"

class AuditSeverity(Enum):
    """Severity levels for audit events"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditLog(db.Model):
    """Comprehensive audit logging model"""
    
    __tablename__ = 'audit_logs'
    
    # Primary identification
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Action details
    action = db.Column(db.Enum(AuditAction), nullable=False, index=True)
    severity = db.Column(db.Enum(AuditSeverity), nullable=False, default=AuditSeverity.LOW)
    description = db.Column(db.Text, nullable=False)
    
    # User and session information
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True, index=True)
    session_id = db.Column(db.String(100), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 compatible
    user_agent = db.Column(db.Text, nullable=True)
    
    # Resource information
    resource_type = db.Column(db.String(50), nullable=True)  # campaign, user, etc.
    resource_id = db.Column(db.String(36), nullable=True, index=True)
    resource_name = db.Column(db.String(255), nullable=True)
    
    # Change tracking
    old_values = db.Column(db.JSON, nullable=True)  # Previous values
    new_values = db.Column(db.JSON, nullable=True)  # New values
    additional_metadata = db.Column(db.JSON, nullable=True)  # Additional context
    
    # Request information
    request_id = db.Column(db.String(36), nullable=True)
    endpoint = db.Column(db.String(255), nullable=True)
    method = db.Column(db.String(10), nullable=True)
    
    # Outcome
    success = db.Column(db.Boolean, nullable=False, default=True)
    error_message = db.Column(db.Text, nullable=True)
    
    # Timestamp
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    def __init__(self, action, description, **kwargs):
        self.action = action
        self.description = description
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def log_action(cls, action: AuditAction, description: str, **kwargs) -> 'AuditLog':
        """Create and save audit log entry"""
        audit_log = cls(action=action, description=description, **kwargs)
        db.session.add(audit_log)
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            # Log to system logger as fallback
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to save audit log: {str(e)}")
        
        return audit_log
    
    @classmethod
    def log_user_action(cls, action: AuditAction, user_id: str, description: str, **kwargs) -> 'AuditLog':
        """Log user-specific action"""
        return cls.log_action(
            action=action,
            description=description,
            user_id=user_id,
            **kwargs
        )
    
    @classmethod
    def log_campaign_action(cls, action: AuditAction, user_id: str, campaign_id: str, 
                           campaign_name: str, description: str, **kwargs) -> 'AuditLog':
        """Log campaign-specific action"""
        return cls.log_action(
            action=action,
            description=description,
            user_id=user_id,
            resource_type='campaign',
            resource_id=campaign_id,
            resource_name=campaign_name,
            **kwargs
        )
    
    @classmethod
    def log_system_action(cls, action: AuditAction, description: str, **kwargs) -> 'AuditLog':
        """Log system-level action"""
        return cls.log_action(
            action=action,
            description=description,
            severity=AuditSeverity.MEDIUM,
            **kwargs
        )
    
    @classmethod
    def log_security_event(cls, action: AuditAction, description: str, ip_address: str = None, **kwargs) -> 'AuditLog':
        """Log security-related event"""
        return cls.log_action(
            action=action,
            description=description,
            severity=AuditSeverity.HIGH,
            ip_address=ip_address,
            **kwargs
        )
    
    @classmethod
    def log_error(cls, action: AuditAction, description: str, error_message: str, **kwargs) -> 'AuditLog':
        """Log error event"""
        return cls.log_action(
            action=action,
            description=description,
            severity=AuditSeverity.CRITICAL,
            success=False,
            error_message=error_message,
            **kwargs
        )
    
    def to_dict(self) -> dict:
        """Convert audit log to dictionary"""
        return {
            'id': self.id,
            'action': self.action.value,
            'severity': self.severity.value,
            'description': self.description,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'resource_name': self.resource_name,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'additional_metadata': self.additional_metadata,
            'request_id': self.request_id,
            'endpoint': self.endpoint,
            'method': self.method,
            'success': self.success,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<AuditLog {self.action.value} by {self.user_id} at {self.created_at}>'

