"""
Flask-SQLAlchemy User Model for Lane Google
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from src.config.flask_database import db
from .flask_base_model import FlaskBaseModel


class User(FlaskBaseModel):
    """
    User model for authentication and profile management
    """
    __tablename__ = 'users'
    
    # Basic user information
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(100), unique=True, nullable=True, index=True)
    full_name = db.Column(db.String(255), nullable=True)
    
    # Authentication
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # Profile information
    company_name = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(100), default='user', nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    
    # Timestamps
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Google Ads integration
    google_ads_customer_id = db.Column(db.String(50), nullable=True)
    google_ads_refresh_token = db.Column(db.Text, nullable=True)
    
    def set_password(self, password: str):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self, include_sensitive: bool = False):
        """Convert user to dictionary for API responses"""
        data = {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'full_name': self.full_name,
            'company_name': self.company_name,
            'role': self.role,
            'phone': self.phone,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'is_verified': self.is_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sensitive:
            data.update({
                'google_ads_customer_id': self.google_ads_customer_id,
                'google_ads_refresh_token': self.google_ads_refresh_token
            })
        
        return data
    
    @staticmethod
    def create_user(email: str, password: str, full_name: str = None, **kwargs):
        """
        Create a new user
        
        Args:
            email: User email
            password: User password  
            full_name: User full name
            **kwargs: Additional user fields
        
        Returns:
            Created User instance
        """
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            raise ValueError(f"User with email {email} already exists")
        
        # Create user
        user = User(
            email=email,
            full_name=full_name,
            **kwargs
        )
        user.set_password(password)
        user.save()
        
        return user
    
    @staticmethod
    def authenticate(email: str, password: str):
        """
        Authenticate user with email and password
        
        Args:
            email: User email
            password: User password
        
        Returns:
            User instance if authenticated, None otherwise
        """
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password) and user.is_active:
            user.update_last_login()
            return user
        return None
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"


# Define user roles and statuses for compatibility
class UserRole:
    USER = 'user'
    ADMIN = 'admin'
    MANAGER = 'manager'
    VIEWER = 'viewer'


class UserStatus:
    ACTIVE = True
    INACTIVE = False