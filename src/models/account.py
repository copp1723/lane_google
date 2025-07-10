"""
Account Model for Multi-Tenant Support
Enables management of multiple Google Ads accounts with proper isolation
"""

from datetime import datetime
from src.config.database import db
from enum import Enum


class AccountRole(Enum):
    """User roles within an account"""
    VIEWER = "viewer"
    EDITOR = "editor"
    ADMIN = "admin"
    OWNER = "owner"


class Account(db.Model):
    """Account model for multi-tenant management"""
    __tablename__ = 'accounts'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    google_customer_id = db.Column(db.String(50), unique=True, nullable=False)
    
    # Account settings
    timezone = db.Column(db.String(50), default='America/New_York')
    currency = db.Column(db.String(3), default='USD')
    monthly_budget_limit = db.Column(db.Float)
    
    # Status and metadata
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Settings JSON for flexible configuration
    settings = db.Column(db.JSON, default=dict)
    
    # Relationships
    users = db.relationship('AccountUser', back_populates='account', cascade='all, delete-orphan')
    campaigns = db.relationship('Campaign', backref='account', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Account {self.name} ({self.google_customer_id})>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'google_customer_id': self.google_customer_id,
            'timezone': self.timezone,
            'currency': self.currency,
            'monthly_budget_limit': self.monthly_budget_limit,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'settings': self.settings or {}
        }
    
    def get_user_role(self, user_id):
        """Get user's role in this account"""
        account_user = AccountUser.query.filter_by(
            account_id=self.id,
            user_id=user_id
        ).first()
        return account_user.role if account_user else None
    
    def has_permission(self, user_id, required_role):
        """Check if user has required permission level"""
        user_role = self.get_user_role(user_id)
        if not user_role:
            return False
        
        role_hierarchy = {
            AccountRole.VIEWER: 1,
            AccountRole.EDITOR: 2,
            AccountRole.ADMIN: 3,
            AccountRole.OWNER: 4
        }
        
        return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)


class AccountUser(db.Model):
    """Many-to-many relationship between accounts and users with roles"""
    __tablename__ = 'account_users'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.String(50), db.ForeignKey('accounts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.Enum(AccountRole), nullable=False, default=AccountRole.VIEWER)
    
    # Metadata
    invited_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_access = db.Column(db.DateTime)
    
    # Relationships
    account = db.relationship('Account', back_populates='users')
    user = db.relationship('User', foreign_keys=[user_id], backref='account_memberships')
    inviter = db.relationship('User', foreign_keys=[invited_by])
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('account_id', 'user_id', name='_account_user_uc'),
    )
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'account_id': self.account_id,
            'user_id': self.user_id,
            'role': self.role.value,
            'invited_by': self.invited_by,
            'joined_at': self.joined_at.isoformat(),
            'last_access': self.last_access.isoformat() if self.last_access else None
        }