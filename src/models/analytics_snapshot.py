"""
Analytics Snapshot Model
Stores time-series analytics data for campaigns
"""

from datetime import datetime
from database import db


class AnalyticsSnapshot(db.Model):
    """Analytics snapshot for time-series data"""
    __tablename__ = 'analytics_snapshots'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.String(255), db.ForeignKey('campaigns.id'), nullable=False)
    
    # Metric information
    metric_type = db.Column(db.String(50), nullable=False)  # impressions, clicks, cost, etc.
    metric_value = db.Column(db.Float, nullable=False)
    
    # Dimensions for slicing data
    dimension = db.Column(db.String(50), default='overall')  # overall, by_device, by_location, etc.
    dimension_value = db.Column(db.String(100))  # mobile, desktop, US, etc.
    
    # Time period
    period_type = db.Column(db.String(20), default='hourly')  # hourly, daily, weekly
    period_start = db.Column(db.DateTime)
    period_end = db.Column(db.DateTime)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    campaign = db.relationship('Campaign', backref='analytics_snapshots')
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_campaign_metric_date', 'campaign_id', 'metric_type', 'created_at'),
        db.Index('idx_metric_dimension', 'metric_type', 'dimension', 'dimension_value'),
    )
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'metric_type': self.metric_type,
            'metric_value': self.metric_value,
            'dimension': self.dimension,
            'dimension_value': self.dimension_value,
            'period_type': self.period_type,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'created_at': self.created_at.isoformat()
        }