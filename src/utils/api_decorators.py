"""
API Decorators for Consistent Response Handling
Provides standardized decorators for common API patterns
"""

import logging
import time
from functools import wraps
from typing import Any, Dict, Optional, Callable
from flask import request, jsonify, g
from src.utils.responses import (
    success_response, error_response, validation_error_response,
    not_found_response, unauthorized_response, forbidden_response,
    server_error_response
)
from src.auth.authentication import token_required, get_current_user

logger = logging.getLogger(__name__)


def api_route(methods=['GET'], auth_required=True, admin_required=False, 
              validate_json=False, rate_limit=None):
    """
    Comprehensive API route decorator with standardized error handling
    
    Args:
        methods: HTTP methods allowed
        auth_required: Whether authentication is required
        admin_required: Whether admin role is required
        validate_json: Whether to validate JSON payload
        rate_limit: Rate limit (requests per minute)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Rate limiting (if specified)
                if rate_limit:
                    # TODO: Implement Redis-based rate limiting
                    pass
                
                # Authentication check
                if auth_required:
                    current_user = get_current_user()
                    if not current_user:
                        return unauthorized_response()
                    
                    # Admin check
                    if admin_required and not current_user.has_permission('admin.access'):
                        return forbidden_response("Admin access required")
                
                # JSON validation
                if validate_json and request.method in ['POST', 'PUT', 'PATCH']:
                    if not request.is_json:
                        return error_response("Content-Type must be application/json", 400)
                    
                    try:
                        request.get_json(force=True)
                    except Exception:
                        return error_response("Invalid JSON payload", 400)
                
                # Execute the route function
                result = f(*args, **kwargs)
                
                # If result is already a response tuple, return it
                if isinstance(result, tuple):
                    return result
                
                # If result is a dict with success/error structure, handle it
                if isinstance(result, dict):
                    if result.get('success', True):
                        return success_response(
                            data=result.get('data'),
                            message=result.get('message', 'Success')
                        )
                    else:
                        return error_response(
                            message=result.get('error', 'An error occurred'),
                            status_code=result.get('status_code', 400)
                        )
                
                # Default success response
                return success_response(data=result)
                
            except ValueError as e:
                logger.warning(f"Validation error in {f.__name__}: {str(e)}")
                return validation_error_response({'general': [str(e)]})
            
            except PermissionError as e:
                logger.warning(f"Permission error in {f.__name__}: {str(e)}")
                return forbidden_response(str(e))
            
            except FileNotFoundError as e:
                logger.warning(f"Not found error in {f.__name__}: {str(e)}")
                return not_found_response(str(e))
            
            except Exception as e:
                logger.error(f"Unexpected error in {f.__name__}: {str(e)}", exc_info=True)
                return server_error_response()
        
        return decorated_function
    return decorator


def validate_request_data(required_fields=None, optional_fields=None, 
                         field_types=None, custom_validators=None):
    """
    Decorator for request data validation
    
    Args:
        required_fields: List of required field names
        optional_fields: List of optional field names
        field_types: Dict mapping field names to expected types
        custom_validators: Dict mapping field names to validation functions
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                data = request.get_json() or {}
                errors = {}
                
                # Check required fields
                if required_fields:
                    for field in required_fields:
                        if field not in data or data[field] is None:
                            errors.setdefault(field, []).append(f"{field} is required")
                
                # Type validation
                if field_types:
                    for field, expected_type in field_types.items():
                        if field in data and data[field] is not None:
                            if not isinstance(data[field], expected_type):
                                errors.setdefault(field, []).append(
                                    f"{field} must be of type {expected_type.__name__}"
                                )
                
                # Custom validation
                if custom_validators:
                    for field, validator in custom_validators.items():
                        if field in data and data[field] is not None:
                            try:
                                if not validator(data[field]):
                                    errors.setdefault(field, []).append(
                                        f"{field} failed validation"
                                    )
                            except Exception as e:
                                errors.setdefault(field, []).append(str(e))
                
                # Return validation errors if any
                if errors:
                    return validation_error_response(errors)
                
                # Add validated data to request context
                g.validated_data = data
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Validation error in {f.__name__}: {str(e)}")
                return error_response("Validation failed", 400)
        
        return decorated_function
    return decorator


def paginated_route(default_limit=20, max_limit=100):
    """
    Decorator for paginated API routes
    
    Args:
        default_limit: Default number of items per page
        max_limit: Maximum allowed items per page
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Extract pagination parameters
                page = int(request.args.get('page', 1))
                limit = int(request.args.get('limit', default_limit))
                
                # Validate pagination parameters
                if page < 1:
                    return error_response("Page must be >= 1", 400)
                
                if limit < 1 or limit > max_limit:
                    return error_response(f"Limit must be between 1 and {max_limit}", 400)
                
                # Add pagination to request context
                g.pagination = {
                    'page': page,
                    'limit': limit,
                    'offset': (page - 1) * limit
                }
                
                return f(*args, **kwargs)
                
            except ValueError:
                return error_response("Invalid pagination parameters", 400)
            except Exception as e:
                logger.error(f"Pagination error in {f.__name__}: {str(e)}")
                return server_error_response()
        
        return decorated_function
    return decorator


def cache_response(ttl=300, key_func=None):
    """
    Decorator for response caching
    
    Args:
        ttl: Time to live in seconds
        key_func: Function to generate cache key
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # TODO: Implement Redis-based caching
            # For now, just execute the function
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def log_api_call(include_request_data=False, include_response_data=False):
    """
    Decorator for API call logging
    
    Args:
        include_request_data: Whether to log request data
        include_response_data: Whether to log response data
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            # Log request
            log_data = {
                'function': f.__name__,
                'method': request.method,
                'path': request.path,
                'user_id': getattr(g, 'current_user', {}).get('id') if hasattr(g, 'current_user') else None,
                'ip': request.remote_addr
            }
            
            if include_request_data and request.is_json:
                log_data['request_data'] = request.get_json()
            
            logger.info(f"API call started: {log_data}")
            
            try:
                result = f(*args, **kwargs)
                
                # Log response
                duration = time.time() - start_time
                log_data.update({
                    'duration': duration,
                    'status': 'success'
                })
                
                if include_response_data and isinstance(result, tuple):
                    response_data = result[0].get_json() if hasattr(result[0], 'get_json') else None
                    if response_data:
                        log_data['response_data'] = response_data
                
                logger.info(f"API call completed: {log_data}")
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                log_data.update({
                    'duration': duration,
                    'status': 'error',
                    'error': str(e)
                })
                logger.error(f"API call failed: {log_data}")
                raise
        
        return decorated_function
    return decorator


def require_permissions(*permissions):
    """
    Decorator to require specific permissions
    
    Args:
        permissions: List of required permissions
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = get_current_user()
            if not current_user:
                return unauthorized_response()
            
            # Check if user has all required permissions
            for permission in permissions:
                if not current_user.has_permission(permission):
                    return forbidden_response(f"Permission '{permission}' required")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def handle_google_ads_errors(f):
    """
    Decorator to handle Google Ads API errors consistently
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            # Handle specific Google Ads errors
            error_message = str(e)
            
            if "AUTHENTICATION_ERROR" in error_message:
                return error_response("Google Ads authentication failed", 401)
            elif "AUTHORIZATION_ERROR" in error_message:
                return error_response("Insufficient Google Ads permissions", 403)
            elif "QUOTA_ERROR" in error_message:
                return error_response("Google Ads API quota exceeded", 429)
            elif "INVALID_CUSTOMER_ID" in error_message:
                return error_response("Invalid Google Ads customer ID", 400)
            else:
                logger.error(f"Google Ads API error in {f.__name__}: {error_message}")
                return error_response("Google Ads API error", 500)
    
    return decorated_function


# Utility function to combine decorators
def api_endpoint(methods=['GET'], auth_required=True, admin_required=False,
                validate_json=False, required_fields=None, permissions=None,
                paginated=False, log_calls=True):
    """
    Convenience function to combine common decorators
    """
    def decorator(f):
        # Apply decorators in reverse order (bottom-up)
        decorated = f
        
        if log_calls:
            decorated = log_api_call()(decorated)
        
        if permissions:
            decorated = require_permissions(*permissions)(decorated)
        
        if paginated:
            decorated = paginated_route()(decorated)
        
        if required_fields:
            decorated = validate_request_data(required_fields=required_fields)(decorated)
        
        decorated = api_route(
            methods=methods,
            auth_required=auth_required,
            admin_required=admin_required,
            validate_json=validate_json
        )(decorated)
        
        return decorated
    
    return decorator