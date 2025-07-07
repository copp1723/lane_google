"""
Authentication and Authorization Routes
Enterprise-grade user authentication with JWT and RBAC
"""

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, 
    get_jwt_identity, get_jwt
)
from datetime import datetime, timedelta
import uuid

from src.database import db
from src.models.user import User, UserRole, UserStatus
from src.models.audit_log import AuditLog, AuditAction, AuditSeverity
from src.config import config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user account"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        # Validate required fields
        required_fields = ['email', 'username', 'password', 'first_name', 'last_name']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400
        
        # Check if user already exists
        existing_user = User.query.filter(
            (User.email == data['email'].lower()) | 
            (User.username == data['username'].lower())
        ).first()
        
        if existing_user:
            return jsonify({'error': 'User with this email or username already exists'}), 409
        
        # Create new user
        user = User(
            email=data['email'],
            username=data['username'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone'),
            company=data.get('company'),
            department=data.get('department'),
            role=UserRole.VIEWER  # Default role
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Log registration
        AuditLog.log_user_action(
            action=AuditAction.USER_CREATED,
            user_id=user.id,
            description=f"User {user.username} registered",
            ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'status': 'success'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login with JWT token generation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        username_or_email = data.get('username') or data.get('email')
        password = data.get('password')
        
        if not username_or_email or not password:
            return jsonify({'error': 'Username/email and password are required'}), 400
        
        # Find user
        user = User.query.filter(
            (User.email == username_or_email.lower()) | 
            (User.username == username_or_email.lower())
        ).first()
        
        if not user:
            # Log failed login attempt
            AuditLog.log_security_event(
                action=AuditAction.LOGIN_FAILED,
                description=f"Login attempt with non-existent username: {username_or_email}",
                ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
                user_agent=request.headers.get('User-Agent')
            )
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if account is locked
        if user.is_account_locked():
            AuditLog.log_security_event(
                action=AuditAction.LOGIN_FAILED,
                user_id=user.id,
                description=f"Login attempt on locked account: {user.username}",
                ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
                user_agent=request.headers.get('User-Agent')
            )
            return jsonify({'error': 'Account is temporarily locked'}), 423
        
        # Check password
        if not user.check_password(password):
            user.increment_failed_login()
            db.session.commit()
            
            AuditLog.log_security_event(
                action=AuditAction.LOGIN_FAILED,
                user_id=user.id,
                description=f"Failed login attempt for user: {user.username}",
                ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
                user_agent=request.headers.get('User-Agent')
            )
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if account is active
        if not user.is_active:
            AuditLog.log_security_event(
                action=AuditAction.LOGIN_FAILED,
                user_id=user.id,
                description=f"Login attempt on inactive account: {user.username}",
                ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
                user_agent=request.headers.get('User-Agent')
            )
            return jsonify({'error': 'Account is not active'}), 403
        
        # Successful login
        user.reset_failed_login()
        db.session.commit()
        
        # Create JWT tokens
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(seconds=config.jwt.access_token_expires)
        )
        refresh_token = create_refresh_token(
            identity=user.id,
            expires_delta=timedelta(seconds=config.jwt.refresh_token_expires)
        )
        
        # Log successful login
        AuditLog.log_user_action(
            action=AuditAction.LOGIN,
            user_id=user.id,
            description=f"User {user.username} logged in successfully",
            ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(),
            'expires_in': config.jwt.access_token_expires,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token using refresh token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 404
        
        # Create new access token
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(seconds=config.jwt.access_token_expires)
        )
        
        return jsonify({
            'access_token': access_token,
            'expires_in': config.jwt.access_token_expires,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': f'Token refresh failed: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user:
            # Log logout
            AuditLog.log_user_action(
                action=AuditAction.LOGOUT,
                user_id=user.id,
                description=f"User {user.username} logged out",
                ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
                user_agent=request.headers.get('User-Agent')
            )
        
        # In a production system, you would add the JWT to a blacklist
        # For now, we'll just return success
        return jsonify({
            'message': 'Logout successful',
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': f'Logout failed: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict(include_sensitive=True),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get profile: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        # Track changes for audit log
        old_values = {}
        new_values = {}
        
        # Update allowed fields
        updatable_fields = ['first_name', 'last_name', 'phone', 'company', 'department']
        for field in updatable_fields:
            if field in data:
                old_values[field] = getattr(user, field)
                setattr(user, field, data[field])
                new_values[field] = data[field]
        
        db.session.commit()
        
        # Log profile update
        if old_values:
            AuditLog.log_user_action(
                action=AuditAction.USER_UPDATED,
                user_id=user.id,
                description=f"User {user.username} updated profile",
                old_values=old_values,
                new_values=new_values,
                ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
                user_agent=request.headers.get('User-Agent')
            )
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict(),
            'status': 'success'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        # Verify current password
        if not user.check_password(current_password):
            AuditLog.log_security_event(
                action=AuditAction.PASSWORD_CHANGED,
                user_id=user.id,
                description=f"Failed password change attempt for user {user.username} - incorrect current password",
                success=False,
                ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
                user_agent=request.headers.get('User-Agent')
            )
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Set new password
        user.set_password(new_password)
        db.session.commit()
        
        # Log password change
        AuditLog.log_security_event(
            action=AuditAction.PASSWORD_CHANGED,
            user_id=user.id,
            description=f"User {user.username} changed password",
            ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({
            'message': 'Password changed successfully',
            'status': 'success'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to change password: {str(e)}'}), 500

# Middleware to load current user
@auth_bp.before_app_request
def load_current_user():
    """Load current user for authenticated requests"""
    g.current_user = None
    
    # Check if we have a valid JWT token
    try:
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        
        if user_id:
            user = User.query.get(user_id)
            if user and user.is_active:
                g.current_user = user
                user.last_activity = datetime.utcnow()
                db.session.commit()
    except:
        pass  # No valid token, continue without user

