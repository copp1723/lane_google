"""
User Management Routes
"""

from flask import Blueprint, request, jsonify
from src.auth.authentication import token_required, admin_required
from src.models.user import User, UserRole, UserStatus
from src.config.database import db
import logging

logger = logging.getLogger(__name__)

# Create blueprint
user_bp = Blueprint('users', __name__)


@user_bp.route('/', methods=['GET'])
@token_required
def list_users():
    """List all users (admin only)"""
    try:
        users = User.query.all()
        return jsonify({
            'success': True,
            'users': [user.to_dict() for user in users]
        }), 200
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to list users'
        }), 500


@user_bp.route('/<user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    """Get specific user details"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get user'
        }), 500


@user_bp.route('/<user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Update user details (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'phone', 'company', 'department', 'role', 'status']
        for field in allowed_fields:
            if field in data:
                if field == 'role':
                    setattr(user, field, UserRole(data[field]))
                elif field == 'status':
                    setattr(user, field, UserStatus(data[field]))
                else:
                    setattr(user, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to update user'
        }), 500


@user_bp.route('/<user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete user (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Soft delete by setting status to inactive
        user.status = UserStatus.INACTIVE
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User deactivated successfully'
        }), 200
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to delete user'
        }), 500