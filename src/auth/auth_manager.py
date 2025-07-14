"""
Consolidated Authentication Manager
Provides unified authentication patterns and utilities
"""

import jwt
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Union
from functools import wraps
from flask import request, g, current_app
from werkzeug.security import check_password_hash, generate_password_hash

from src.models.user import User
from src.utils.responses import unauthorized_response, forbidden_response
from src.services.base_service import BaseService, ServiceResult

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Custom authentication error"""
    pass


class AuthorizationError(Exception):
    """Custom authorization error"""
    pass


class TokenManager:
    """
    JWT Token management utilities
    """
    
    @staticmethod
    def generate_token(user_id: int, user_role: str = None, 
                      expires_in: int = 3600, additional_claims: Dict = None) -> str:
        """
        Generate JWT token
        
        Args:
            user_id: User ID
            user_role: User role
            expires_in: Token expiration in seconds
            additional_claims: Additional JWT claims
        
        Returns:
            JWT token string
        """
        payload = {
            'user_id': user_id,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=expires_in)
        }
        
        if user_role:
            payload['role'] = user_role
        
        if additional_claims:
            payload.update(additional_claims)
        
        return jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    
    @staticmethod
    def decode_token(token: str) -> Dict:
        """
        Decode and validate JWT token
        
        Args:
            token: JWT token string
        
        Returns:
            Decoded token payload
        
        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
    
    @staticmethod
    def refresh_token(token: str, expires_in: int = 3600) -> str:
        """
        Refresh an existing token
        
        Args:
            token: Current JWT token
            expires_in: New expiration time in seconds
        
        Returns:
            New JWT token
        
        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            payload = TokenManager.decode_token(token)
            # Remove old timestamps
            payload.pop('iat', None)
            payload.pop('exp', None)
            
            # Generate new token with same payload
            return TokenManager.generate_token(
                user_id=payload['user_id'],
                user_role=payload.get('role'),
                expires_in=expires_in,
                additional_claims={k: v for k, v in payload.items() 
                                 if k not in ['user_id', 'role']}
            )
        except Exception as e:
            raise AuthenticationError(f"Token refresh failed: {str(e)}")


class PermissionManager:
    """
    Permission and role management
    """
    
    # Define permission hierarchy
    PERMISSIONS = {
        'admin': [
            'admin.access',
            'admin.users.manage',
            'admin.campaigns.manage',
            'admin.settings.manage',
            'user.profile.view',
            'user.profile.edit',
            'campaigns.view',
            'campaigns.create',
            'campaigns.edit',
            'campaigns.delete',
            'ai_agent.access',
            'google_ads.access'
        ],
        'manager': [
            'user.profile.view',
            'user.profile.edit',
            'campaigns.view',
            'campaigns.create',
            'campaigns.edit',
            'ai_agent.access',
            'google_ads.access'
        ],
        'user': [
            'user.profile.view',
            'user.profile.edit',
            'campaigns.view',
            'ai_agent.access'
        ],
        'viewer': [
            'user.profile.view',
            'campaigns.view'
        ]
    }
    
    @classmethod
    def get_role_permissions(cls, role: str) -> List[str]:
        """
        Get permissions for a role
        
        Args:
            role: User role
        
        Returns:
            List of permissions
        """
        return cls.PERMISSIONS.get(role.lower(), [])
    
    @classmethod
    def has_permission(cls, user_role: str, permission: str) -> bool:
        """
        Check if a role has a specific permission
        
        Args:
            user_role: User role
            permission: Permission to check
        
        Returns:
            True if role has permission
        """
        role_permissions = cls.get_role_permissions(user_role)
        return permission in role_permissions
    
    @classmethod
    def validate_permissions(cls, user_role: str, required_permissions: List[str]) -> bool:
        """
        Validate that a role has all required permissions
        
        Args:
            user_role: User role
            required_permissions: List of required permissions
        
        Returns:
            True if role has all permissions
        """
        role_permissions = cls.get_role_permissions(user_role)
        return all(perm in role_permissions for perm in required_permissions)


class AuthenticationService(BaseService):
    """
    Authentication service with unified patterns
    """
    
    def __init__(self, db_session=None):
        super().__init__("AuthenticationService")
        self.db = db_session
        self.token_manager = TokenManager()
        self.permission_manager = PermissionManager()
    
    def authenticate_user(self, email: str, password: str) -> ServiceResult:
        """
        Authenticate user with email and password
        
        Args:
            email: User email
            password: User password
        
        Returns:
            ServiceResult with authentication data
        """
        try:
            # Validate input
            validation = self._validate_input(
                {'email': email, 'password': password},
                required_fields=['email', 'password'],
                field_types={'email': str, 'password': str}
            )
            
            if not validation.success:
                return validation
            
            # Find user
            user = User.query.filter_by(email=email).first()
            if not user:
                return ServiceResult.error_result(
                    message="Invalid credentials",
                    errors={'authentication': ['Invalid email or password']}
                )
            
            # Check password
            if not check_password_hash(user.password_hash, password):
                return ServiceResult.error_result(
                    message="Invalid credentials",
                    errors={'authentication': ['Invalid email or password']}
                )
            
            # Check if user is active
            if not user.is_active:
                return ServiceResult.error_result(
                    message="Account is disabled",
                    errors={'authentication': ['Account has been disabled']}
                )
            
            # Generate token
            token = self.token_manager.generate_token(
                user_id=user.id,
                user_role=user.role,
                expires_in=current_app.config.get('JWT_EXPIRATION_DELTA', 3600)
            )
            
            # Update last login
            user.last_login = datetime.utcnow()
            if self.db:
                self.db.commit()
            
            return ServiceResult.success_result(
                data={
                    'token': token,
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'role': user.role,
                        'permissions': self.permission_manager.get_role_permissions(user.role)
                    }
                },
                message="Authentication successful"
            )
            
        except Exception as e:
            self._log_error("authenticate_user", e)
            return ServiceResult.error_result(
                message="Authentication failed",
                errors={'authentication': [str(e)]}
            )
    
    def validate_token(self, token: str) -> ServiceResult:
        """
        Validate JWT token and return user data
        
        Args:
            token: JWT token
        
        Returns:
            ServiceResult with user data
        """
        try:
            # Decode token
            payload = self.token_manager.decode_token(token)
            
            # Get user
            user = User.query.get(payload['user_id'])
            if not user or not user.is_active:
                return ServiceResult.error_result(
                    message="Invalid token",
                    errors={'token': ['User not found or inactive']}
                )
            
            return ServiceResult.success_result(
                data={
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'role': user.role,
                        'permissions': self.permission_manager.get_role_permissions(user.role)
                    },
                    'token_payload': payload
                },
                message="Token validation successful"
            )
            
        except AuthenticationError as e:
            return ServiceResult.error_result(
                message="Token validation failed",
                errors={'token': [str(e)]}
            )
        except Exception as e:
            self._log_error("validate_token", e)
            return ServiceResult.error_result(
                message="Token validation error",
                errors={'token': [str(e)]}
            )
    
    def refresh_user_token(self, token: str) -> ServiceResult:
        """
        Refresh user token
        
        Args:
            token: Current JWT token
        
        Returns:
            ServiceResult with new token
        """
        try:
            new_token = self.token_manager.refresh_token(token)
            
            return ServiceResult.success_result(
                data={'token': new_token},
                message="Token refreshed successfully"
            )
            
        except AuthenticationError as e:
            return ServiceResult.error_result(
                message="Token refresh failed",
                errors={'token': [str(e)]}
            )
        except Exception as e:
            self._log_error("refresh_user_token", e)
            return ServiceResult.error_result(
                message="Token refresh error",
                errors={'token': [str(e)]}
            )
    
    def check_permissions(self, user_role: str, required_permissions: List[str]) -> ServiceResult:
        """
        Check if user has required permissions
        
        Args:
            user_role: User role
            required_permissions: List of required permissions
        
        Returns:
            ServiceResult indicating permission check result
        """
        try:
            has_permissions = self.permission_manager.validate_permissions(
                user_role, required_permissions
            )
            
            if has_permissions:
                return ServiceResult.success_result(
                    message="Permission check passed"
                )
            else:
                missing_permissions = [
                    perm for perm in required_permissions
                    if not self.permission_manager.has_permission(user_role, perm)
                ]
                
                return ServiceResult.error_result(
                    message="Insufficient permissions",
                    errors={
                        'permissions': [f"Missing permissions: {', '.join(missing_permissions)}"]
                    }
                )
                
        except Exception as e:
            self._log_error("check_permissions", e)
            return ServiceResult.error_result(
                message="Permission check error",
                errors={'permissions': [str(e)]}
            )
    
    def health_check(self) -> ServiceResult:
        """
        Check authentication service health
        
        Returns:
            ServiceResult indicating service health
        """
        try:
            # Test token generation and validation
            test_token = self.token_manager.generate_token(
                user_id=1,
                user_role='user',
                expires_in=60
            )
            
            payload = self.token_manager.decode_token(test_token)
            
            if payload['user_id'] == 1:
                return ServiceResult.success_result(message="Authentication service is healthy")
            else:
                return ServiceResult.error_result(message="Authentication service test failed")
                
        except Exception as e:
            return ServiceResult.error_result(
                message="Authentication service health check failed",
                errors={'health_check': [str(e)]}
            )


# Global authentication service instance
auth_service = AuthenticationService()


def get_current_user() -> Optional[Dict]:
    """
    Get current authenticated user from request context
    
    Returns:
        User data dict or None
    """
    return getattr(g, 'current_user', None)


def extract_token_from_request() -> Optional[str]:
    """
    Extract JWT token from request headers
    
    Returns:
        JWT token string or None
    """
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    return None


def require_auth(f):
    """
    Decorator to require authentication
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = extract_token_from_request()
        if not token:
            return unauthorized_response("Authentication token required")
        
        result = auth_service.validate_token(token)
        if not result.success:
            return unauthorized_response(result.message)
        
        # Store user in request context
        g.current_user = result.data['user']
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_permissions(*permissions):
    """
    Decorator to require specific permissions
    
    Args:
        permissions: Required permissions
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = get_current_user()
            if not current_user:
                return unauthorized_response("Authentication required")
            
            result = auth_service.check_permissions(
                current_user['role'], 
                list(permissions)
            )
            
            if not result.success:
                return forbidden_response(result.message)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_admin(f):
    """
    Decorator to require admin role
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        if not current_user:
            return unauthorized_response("Authentication required")
        
        if current_user['role'] != 'admin':
            return forbidden_response("Admin access required")
        
        return f(*args, **kwargs)
    
    return decorated_function


# Legacy compatibility functions
def token_required(f):
    """
    Legacy token_required decorator for backward compatibility
    """
    return require_auth(f)


def admin_required(f):
    """
    Legacy admin_required decorator for backward compatibility
    """
    return require_admin(f)