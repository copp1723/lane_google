"""
AI Agent API endpoints.
Flask Blueprint version.
"""

from typing import List, Optional, Dict, Any
from flask import Blueprint, request, jsonify, g
import logging

from src.auth.authentication import token_required, get_current_user
from src.models.user import User
from src.config.flask_database import db
from src.utils.flask_responses import APIResponse

logger = logging.getLogger(__name__)

# Create Flask blueprint
ai_agent_bp = Blueprint('ai_agent', __name__)


@ai_agent_bp.route('/', methods=['GET'])
@token_required
def get_ai_agent():
    """
    Get ai agent.
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return APIResponse.error('User not found', 401)
        
        return APIResponse.success({"message": "AI Agent endpoint"}, 'AI Agent endpoint accessed')
        
    except Exception as e:
        logger.error(f"Get AI agent failed: {str(e)}")
        return APIResponse.error('Failed to access AI agent endpoint', 500)
