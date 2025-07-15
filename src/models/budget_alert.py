"""
Budget Alert Model
Stores budget alerts and notifications for campaigns
"""

from datetime import datetime
from src.config.database import db


class BudgetAlertModel(db.Model):
    """Budget alert database model"""
    __tablename__ = 'budget_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # overspending, underspending, exhausted, at_risk
    severity = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    message = db.Column(db.Text, nullable=False)
    current_spend = db.Column(db.Float, nullable=False)
    budget_limit = db.Column(db.Float, nullable=False)
    projected_spend = db.Column(db.Float, nullable=False)
    recommended_action = db.Column(db.Text)
    resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    campaign = db.relationship('Campaign', backref='budget_alerts')
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'message': self.message,
            'current_spend': self.current_spend,
            'budget_limit': self.budget_limit,
            'projected_spend': self.projected_spend,
            'recommended_action': self.recommended_action,
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'created_at': self.created_at.isoformat()
        }
    
    def resolve(self):
        """Mark alert as resolved"""
        self.resolved = True
        self.resolved_at = datetime.utcnow()