from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Campaign(db.Model):
    """Campaign model for storing campaign briefs and tracking status"""
    
    __tablename__ = 'campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.String(50), nullable=False)  # Google Ads customer ID
    account_id = db.Column(db.String(50), db.ForeignKey('accounts.id'), nullable=True)  # Link to account
    google_campaign_id = db.Column(db.String(50), nullable=True)  # Google Ads campaign ID
    brief = db.Column(db.Text, nullable=True)  # JSON string of campaign brief
    status = db.Column(db.String(50), nullable=False, default='draft')  # draft, approved, active, paused, cancelled
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)
    
    # Budget and pacing fields
    budget_amount = db.Column(db.Float, nullable=True)  # Monthly budget
    current_spend = db.Column(db.Float, default=0.0)
    pacing_strategy = db.Column(db.String(20), default='linear')  # linear, accelerated, conservative, adaptive
    pacing_status = db.Column(db.String(20))  # on_track, underspending, overspending, at_risk, exhausted
    last_pacing_check = db.Column(db.DateTime)
    projected_spend = db.Column(db.Float)
    billing_period_start = db.Column(db.DateTime)
    billing_period_end = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Campaign {self.name}>'
    
    def to_dict(self):
        """Convert campaign to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'customer_id': self.customer_id,
            'google_campaign_id': self.google_campaign_id,
            'brief': self.brief,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'budget_amount': self.budget_amount,
            'current_spend': self.current_spend,
            'pacing_strategy': self.pacing_strategy,
            'pacing_status': self.pacing_status,
            'last_pacing_check': self.last_pacing_check.isoformat() if self.last_pacing_check else None,
            'projected_spend': self.projected_spend,
            'billing_period_start': self.billing_period_start.isoformat() if self.billing_period_start else None,
            'billing_period_end': self.billing_period_end.isoformat() if self.billing_period_end else None
        }

