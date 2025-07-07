"""
Authentication API Endpoints
Provides registration, login, and token management
"""

from flask import Blueprint, request, jsonify, g
import logging
from src.auth.authentication import (
    create_auth_service, token_required, get_current_user,
    extract_token_from_request
)
from src.models.user import User, UserStatus
from database import db
import re

logger = logging.getLogger(__name__)

# Create blueprint
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            return jsonify({
                'success': False,
                'error': 'Invalid email format'
            }), 400
        
        # Validate password strength
        password = data['password']
        if len(password) < 8:
            return jsonify({
                'success': False,
                'error': 'Password must be at least 8 characters long'
            }), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email'].lower()).first()
        if existing_user:
            return jsonify({
                'success': False,
                'error': 'User already exists with this email'
            }), 409
        
        # Generate username from email if not provided
        username = data.get('username', data['email'].split('@')[0])
        
        # Check if username is taken
        existing_username = User.query.filter_by(username=username.lower()).first()
        if existing_username:
            return jsonify({
                'success': False,
                'error': 'Username already taken'
            }), 409
        
        # Create user
        user = User(
            email=data['email'],
            username=username,
            password=password,
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone'),
            company=data.get('company'),
            department=data.get('department'),
            status=UserStatus.ACTIVE  # Auto-activate for now
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        auth_service = create_auth_service()
        token = auth_service.generate_token(user.id, user.email)
        
        logger.info(f"User registered successfully: {user.email}")
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'token': token
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Registration failed'
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user with email and password"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({
                'success': False,
                'error': 'Invalid email or password'
            }), 401
        
        # Check if account is locked
        if user.is_account_locked():
            return jsonify({
                'success': False,
                'error': 'Account is temporarily locked due to too many failed attempts'
            }), 423
        
        # Check if account is active
        if user.status != UserStatus.ACTIVE:
            return jsonify({
                'success': False,
                'error': 'Account is not active'
            }), 403
        
        # Verify password
        if not user.check_password(password):
            user.increment_failed_login()
            db.session.commit()
            
            return jsonify({
                'success': False,
                'error': 'Invalid email or password'
            }), 401
        
        # Reset failed login attempts
        user.reset_failed_login()
        db.session.commit()
        
        # Generate token
        auth_service = create_auth_service()
        token = auth_service.generate_token(user.id, user.email)
        
        logger.info(f"User logged in successfully: {user.email}")
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user.to_dict(),
            'token': token
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Login failed'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """Logout user and revoke token"""
    try:
        # Get token from request
        token = extract_token_from_request()
        
        if token:
            # Revoke token (in production, add to blacklist)
            auth_service = create_auth_service()
            auth_service.revoke_token(token)
        
        logger.info(f"User logged out: {g.current_user.email}")
        
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        }), 200
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Logout failed'
        }), 500


@auth_bp.route('/refresh', methods=['POST'])
@token_required
def refresh_token():
    """Refresh JWT token"""
    try:
        # Get current token
        token = extract_token_from_request()
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'No token provided'
            }), 400
        
        # Generate new token
        auth_service = create_auth_service()
        new_token = auth_service.refresh_token(token)
        
        if not new_token:
            return jsonify({
                'success': False,
                'error': 'Token refresh failed'
            }), 401
        
        return jsonify({
            'success': True,
            'token': new_token
        }), 200
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Token refresh failed'
        }), 500


@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """Get current user profile"""
    try:
        user = get_current_user()
        
        return jsonify({
            'success': True,
            'user': user.to_dict(include_sensitive=False)
        }), 200
        
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get profile'
        }), 500


@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile():
    """Update current user profile"""
    try:
        user = get_current_user()
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = [
            'first_name', 'last_name', 'phone', 
            'company', 'department'
        ]
        
        updated_fields = []
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
                updated_fields.append(field)
        
        if updated_fields:
            db.session.commit()
            logger.info(f"Profile updated for {user.email}: {updated_fields}")
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Update profile error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to update profile'
        }), 500


@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """Change user password"""
    try:
        user = get_current_user()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({
                'success': False,
                'error': 'Current password and new password are required'
            }), 400
        
        # Verify current password
        if not user.check_password(data['current_password']):
            return jsonify({
                'success': False,
                'error': 'Current password is incorrect'
            }), 401
        
        # Validate new password
        new_password = data['new_password']
        if len(new_password) < 8:
            return jsonify({
                'success': False,
                'error': 'New password must be at least 8 characters long'
            }), 400
        
        # Update password
        user.set_password(new_password)
        db.session.commit()
        
        logger.info(f"Password changed for user: {user.email}")
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to change password'
        }), 500


@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """Verify if a token is valid"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({
                'valid': False,
                'error': 'No token provided'
            }), 400
        
        auth_service = create_auth_service()
        user = auth_service.get_current_user(token)
        
        if user:
            return jsonify({
                'valid': True,
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({
                'valid': False,
                'error': 'Invalid or expired token'
            }), 401
            
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return jsonify({
            'valid': False,
            'error': 'Token verification failed'
        }), 500


# Error handlers
@auth_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 'Bad request'
    }), 400


@auth_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 'Unauthorized'
    }), 401


@auth_bp.errorhandler(403)
def forbidden(error):
    return jsonify({
        'success': False,
        'error': 'Forbidden'
    }), 403


@auth_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500