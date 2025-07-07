"""
Authentication System
Real user authentication with JWT tokens and password hashing
"""

import logging
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from functools import wraps
from flask import request, jsonify, current_app, g
from database import db
from src.models.user import User

logger = logging.getLogger(__name__)


class AuthenticationService:
    """Handles user authentication and authorization"""
    
    def __init__(self, secret_key: str, jwt_secret: str):
        self.secret_key = secret_key
        self.jwt_secret = jwt_secret
        self.token_expiry_hours = 24
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_token(self, user_id: str, email: str) -> str:
        """Generate JWT token for user"""
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        return token
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
    
    def register_user(self, email: str, password: str, name: str = None) -> Dict[str, Any]:
        """Register a new user"""
        try:
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return {
                    'success': False,
                    'error': 'User already exists with this email'
                }
            
            # Hash password
            password_hash = self.hash_password(password)
            
            # Create user
            user = User(
                email=email,
                password_hash=password_hash,
                name=name or email.split('@')[0],
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.session.add(user)
            db.session.commit()
            
            # Generate token
            token = self.generate_token(str(user.id), user.email)
            
            logger.info(f"User registered successfully: {email}")
            
            return {
                'success': True,
                'user': user.to_dict(),
                'token': token
            }
            
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': 'Registration failed'
            }
    
    def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Login user with email and password"""
        try:
            # Find user
            user = User.query.filter_by(email=email).first()
            if not user:
                return {
                    'success': False,
                    'error': 'Invalid email or password'
                }
            
            # Check if user is active
            if not user.is_active:
                return {
                    'success': False,
                    'error': 'Account is deactivated'
                }
            
            # Verify password
            if not self.verify_password(password, user.password_hash):
                return {
                    'success': False,
                    'error': 'Invalid email or password'
                }
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Generate token
            token = self.generate_token(str(user.id), user.email)
            
            logger.info(f"User logged in successfully: {email}")
            
            return {
                'success': True,
                'user': user.to_dict(),
                'token': token
            }
            
        except Exception as e:
            logger.error(f"Error logging in user: {str(e)}")
            return {
                'success': False,
                'error': 'Login failed'
            }
    
    def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from token"""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get('user_id')
        if not user_id:
            return None
        
        user = User.query.get(user_id)
        if not user or not user.is_active:
            return None
        
        return user
    
    def refresh_token(self, token: str) -> Optional[str]:
        """Refresh an existing token"""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        # Generate new token
        return self.generate_token(payload['user_id'], payload['email'])
    
    def revoke_token(self, token: str) -> bool:
        """Revoke a token (add to blacklist)"""
        # In production, you would maintain a Redis blacklist
        # For now, we'll just log the revocation
        payload = self.verify_token(token)
        if payload:
            logger.info(f"Token revoked for user: {payload.get('email')}")
            return True
        return False


# Authentication decorators
def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        # Initialize auth service
        from src.config.settings import settings
        auth_service = AuthenticationService(
            settings.security.secret_key,
            settings.security.jwt_secret_key
        )
        
        # Get current user
        current_user = auth_service.get_current_user(token)
        if not current_user:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        # Add user to request context
        g.current_user = current_user
        g.token = token
        
        return f(*args, **kwargs)
    
    return decorated


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if not g.current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated


def account_access_required(account_id: str = None):
    """Decorator to require access to specific account"""
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            # Get account ID from URL params if not provided
            target_account_id = account_id or kwargs.get('account_id')
            
            if not target_account_id:
                return jsonify({'error': 'Account ID required'}), 400
            
            # Check if user has access to this account
            from src.models.account import Account
            account = Account.query.get(target_account_id)
            
            if not account:
                return jsonify({'error': 'Account not found'}), 404
            
            # Check permissions
            if not account.has_permission(g.current_user.id, 'viewer'):
                return jsonify({'error': 'Access denied to this account'}), 403
            
            # Add account to request context
            g.current_account = account
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator


# Rate limiting decorator
def rate_limit(requests_per_minute: int = 60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # In production, implement with Redis
            # For now, just log the request
            client_ip = request.remote_addr
            logger.debug(f"Rate limit check for {client_ip}: {requests_per_minute}/min")
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator


# Utility functions
def get_current_user() -> Optional[User]:
    """Get current user from request context"""
    return getattr(g, 'current_user', None)


def get_current_account():
    """Get current account from request context"""
    return getattr(g, 'current_account', None)


def extract_token_from_request() -> Optional[str]:
    """Extract JWT token from request"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    return None


# Initialize authentication service
def create_auth_service() -> AuthenticationService:
    """Create authentication service with current settings"""
    from src.config.settings import settings
    return AuthenticationService(
        settings.security.secret_key,
        settings.security.jwt_secret_key
    )