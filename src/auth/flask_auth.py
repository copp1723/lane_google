"""
Flask-compatible authentication decorators and utilities
"""

import jwt
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, g, current_app
from werkzeug.security import generate_password_hash, check_password_hash

from src.models.user import User
from src.config.settings import settings
from src.utils.flask_responses import unauthorized_response, forbidden_response

logger = logging.getLogger(__name__)


class AuthManager:
    """Flask-compatible authentication manager"""
    
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.security.jwt_expiration_hours * 60
    SECRET_KEY = settings.security.jwt_secret_key
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=AuthManager.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, AuthManager.SECRET_KEY, algorithm="HS256")
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict):
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, AuthManager.SECRET_KEY, algorithm="HS256")
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str):
        """Decode JWT token"""
        try:
            payload = jwt.decode(token, AuthManager.SECRET_KEY, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception("Token has expired")
        except jwt.JWTError:
            raise Exception("Could not validate credentials")
    
    @staticmethod
    def create_user(db_session, user_data):
        """Create a new user"""
        try:
            # Check if user exists
            existing_user = User.query.filter_by(email=user_data['email']).first()
            if existing_user:
                raise Exception("User with this email already exists")
            
            # Create user
            user = User(
                email=user_data['email'],
                full_name=user_data.get('full_name', ''),
                company_name=user_data.get('company_name', ''),
                phone=user_data.get('phone', ''),
                role=user_data.get('role', 'user')
            )
            user.set_password(user_data['password'])
            user.save()
            
            return user
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    @staticmethod
    def authenticate_user(db_session, email: str, password: str):
        """Authenticate user with email and password"""
        return User.authenticate(email, password)
    
    @staticmethod
    def create_session(user_id: str, token: str):
        """Create user session (placeholder for session management)"""
        # In a real implementation, you might store this in Redis or database
        logger.info(f"Session created for user {user_id}")
    
    @staticmethod
    def invalidate_session(user_id: str, token: str):
        """Invalidate user session"""
        logger.info(f"Session invalidated for user {user_id}")


def extract_token_from_request():
    """Extract JWT token from request headers"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    return None


def token_required(f):
    """Decorator to require authentication token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = extract_token_from_request()
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Authentication token is required'
            }), 401
        
        try:
            # Decode token
            payload = AuthManager.decode_token(token)
            
            # Get user
            user_id = payload['sub']
            user = User.query.get(user_id)
            
            if not user or not user.is_active:
                return jsonify({
                    'success': False,
                    'error': 'Invalid token or user not found'
                }), 401
            
            # Store user in request context
            g.current_user = user
            
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Invalid token'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # First check if user is authenticated
        token = extract_token_from_request()
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Authentication token is required'
            }), 401
        
        try:
            # Decode token
            payload = AuthManager.decode_token(token)
            
            # Get user
            user_id = payload['sub']
            user = User.query.get(user_id)
            
            if not user or not user.is_active:
                return jsonify({
                    'success': False,
                    'error': 'Invalid token or user not found'
                }), 401
            
            # Check admin role
            if not user.is_admin:
                return jsonify({
                    'success': False,
                    'error': 'Admin access required'
                }), 403
            
            # Store user in request context
            g.current_user = user
            
        except Exception as e:
            logger.error(f"Admin token validation error: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Invalid token'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated


def get_current_user():
    """Get current authenticated user from request context"""
    return getattr(g, 'current_user', None)