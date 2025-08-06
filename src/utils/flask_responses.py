"""
Flask-compatible API Response Utilities
"""

import time
from typing import Any, Dict, Optional
from flask import jsonify


class APIResponse:
    """Flask-compatible API response utility class"""
    
    @staticmethod
    def success(data: Any = None, message: str = "Success", status_code: int = 200):
        """Create a success response"""
        response_data = {
            'success': True,
            'timestamp': int(time.time()),
            'message': message
        }
        
        if data is not None:
            response_data['data'] = data
        
        return jsonify(response_data), status_code
    
    @staticmethod
    def error(message: str = "An error occurred", status_code: int = 400, errors: Dict = None):
        """Create an error response"""
        response_data = {
            'success': False,
            'timestamp': int(time.time()),
            'message': message
        }
        
        if errors:
            response_data['errors'] = errors
        
        return jsonify(response_data), status_code
    
    @staticmethod
    def not_found(message: str = "Resource not found"):
        """Create a not found response"""
        return APIResponse.error(message, 404)
    
    @staticmethod
    def unauthorized(message: str = "Authentication required"):
        """Create an unauthorized response"""
        return APIResponse.error(message, 401)
    
    @staticmethod
    def forbidden(message: str = "Access forbidden"):
        """Create a forbidden response"""
        return APIResponse.error(message, 403)
    
    @staticmethod
    def server_error(message: str = "Internal server error"):
        """Create a server error response"""
        return APIResponse.error(message, 500)


# For backward compatibility with existing usage patterns
def success_response(data: Any = None, message: str = "Success", status_code: int = 200):
    """Create a success response"""
    return APIResponse.success(data, message, status_code)


def error_response(message: str = "An error occurred", status_code: int = 400, errors: Dict = None):
    """Create an error response"""
    return APIResponse.error(message, status_code, errors)


def unauthorized_response(message: str = "Authentication required"):
    """Create an unauthorized response"""
    return APIResponse.unauthorized(message)


def forbidden_response(message: str = "Access forbidden"):
    """Create a forbidden response"""
    return APIResponse.forbidden(message)