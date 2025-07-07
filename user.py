"""
Enhanced User Model with Enterprise Features
Comprehensive user management with roles and permissions
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum
import uuid

from src.database import db

class UserRole(Enum):
    """User roles for role-based access control"""
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"

class UserStatus(Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

class User(db.Model):
    """Enhanced user model with enterprise features"""
    
    __tablename__ = 'users'
    
    # Primary identification
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # Authentication
    password_hash = db.Column(db.String(255), nullable=False)
    salt = db.Column(db.String(32), nullable=False, default=lambda: str(uuid.uuid4())[:32])
    
    # Profile information
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    company = db.Column(db.String(200), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    
    # Role and permissions
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.VIEWER)
    permissions = db.Column(db.JSON, nullable=True)  # Additional granular permissions
    
    # Account status
    status = db.Column(db.Enum(UserStatus), nullable=False, default=UserStatus.PENDING)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    last_activity = db.Column(db.DateTime, nullable=True)
    
    # Security
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)
    password_changed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Google Ads integration
    google_ads_customer_ids = db.Column(db.JSON, nullable=True)  # List of accessible customer IDs
    google_ads_refresh_token = db.Column(db.String(500), nullable=True)  # Encrypted
    
    # Relationships
    campaigns = db.relationship('Campaign', backref='created_by_user', lazy='dynamic')
    conversations = db.relationship('Conversation', backref='user', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')
    
    def __init__(self, email, username, password, first_name, last_name, **kwargs):
        self.email = email.lower().strip()
        self.username = username.lower().strip()
        self.first_name = first_name.strip()
        self.last_name = last_name.strip()
        self.set_password(password)
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_password(self, password: str) -> None:
        """Set password with proper hashing"""
        self.password_hash = generate_password_hash(password + self.salt)
        self.password_changed_at = datetime.utcnow()
    
    def check_password(self, password: str) -> bool:
        """Check password against hash"""
        return check_password_hash(self.password_hash, password + self.salt)
    
    def is_account_locked(self) -> bool:
        """Check if account is locked due to failed login attempts"""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False
    
    def increment_failed_login(self) -> None:
        """Increment failed login attempts and lock if necessary"""
        from datetime import timedelta
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            # Lock account for 30 minutes
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
    
    def reset_failed_login(self) -> None:
        """Reset failed login attempts on successful login"""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.last_login = datetime.utcnow()
        self.last_activity = datetime.utcnow()
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        # Admin has all permissions
        if self.role == UserRole.ADMIN:
            return True
        
        # Check role-based permissions
        role_permissions = {
            UserRole.MANAGER: [
                'campaigns.create', 'campaigns.edit', 'campaigns.delete', 'campaigns.approve',
                'analytics.view', 'analytics.export', 'users.view', 'google_ads.manage'
            ],
            UserRole.ANALYST: [
                'campaigns.create', 'campaigns.edit', 'campaigns.view',
                'analytics.view', 'analytics.export', 'google_ads.view'
            ],
            UserRole.VIEWER: [
                'campaigns.view', 'analytics.view', 'google_ads.view'
            ]
        }
        
        if permission in role_permissions.get(self.role, []):
            return True
        
        # Check custom permissions
        if self.permissions and permission in self.permissions:
            return self.permissions[permission]
        
        return False
    
    def can_access_customer(self, customer_id: str) -> bool:
        """Check if user can access specific Google Ads customer"""
        if self.role == UserRole.ADMIN:
            return True
        
        if self.google_ads_customer_ids:
            return customer_id in self.google_ads_customer_ids
        
        return False
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_active(self) -> bool:
        """Check if user account is active"""
        return self.status == UserStatus.ACTIVE and not self.is_account_locked()
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'phone': self.phone,
            'company': self.company,
            'department': self.department,
            'role': self.role.value,
            'status': self.status.value,
            'is_verified': self.is_verified,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        }
        
        if include_sensitive:
            data.update({
                'permissions': self.permissions,
                'google_ads_customer_ids': self.google_ads_customer_ids,
                'failed_login_attempts': self.failed_login_attempts,
                'locked_until': self.locked_until.isoformat() if self.locked_until else None
            })
        
        return data
    
    def __repr__(self):
        return f'<User {self.username} ({self.email})>'

