"""
Approval Request Model
Stores approval requests for campaign operations
"""

from datetime import datetime
from database import db


class ApprovalRequestModel(db.Model):
    """Approval request database model"""
    __tablename__ = 'approval_requests'
    
    id = db.Column(db.String(36), primary_key=True)
    request_type = db.Column(db.String(50), nullable=False)
    requester_id = db.Column(db.String(50), nullable=False)
    campaign_id = db.Column(db.String(255), db.ForeignKey('campaigns.id'), nullable=False)
    
    # Request details
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20), nullable=False)
    
    # Status and timing
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    # Approval details
    approved_by = db.Column(db.String(50))
    approved_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    comments = db.Column(db.Text)
    
    # Configuration and data
    approval_config = db.Column(db.JSON)  # approvers, rules, etc.
    request_data = db.Column(db.JSON)     # specific request data
    
    # Relationships
    campaign = db.relationship('Campaign', backref='approval_requests')
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'request_type': self.request_type,
            'requester_id': self.requester_id,
            'campaign_id': self.campaign_id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'rejection_reason': self.rejection_reason,
            'comments': self.comments,
            'approval_config': self.approval_config or {},
            'request_data': self.request_data or {}
        }