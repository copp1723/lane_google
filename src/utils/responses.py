"""
Standardized API Response Utilities
Provides consistent response formats across all API endpoints
"""

import time
from typing import Any, Dict, Optional, List, Union
from flask import jsonify, request


def _create_response(success: bool, data: Any = None, message: str = None, 
                    errors: Dict = None, status_code: int = 200, 
                    meta: Dict = None) -> tuple:
    """
    Create a standardized API response
    
    Args:
        success: Whether the operation was successful
        data: Response data
        message: Response message
        errors: Error details
        status_code: HTTP status code
        meta: Additional metadata
    
    Returns:
        Tuple of (response, status_code)
    """
    response_data = {
        'success': success,
        'timestamp': int(time.time()),
        'request_id': getattr(request, 'id', None)
    }
    
    if message:
        response_data['message'] = message
    
    if data is not None:
        response_data['data'] = data
    
    if errors:
        response_data['errors'] = errors
    
    if meta:
        response_data['meta'] = meta
    
    return jsonify(response_data), status_code


def success_response(data: Any = None, message: str = "Success", 
                    status_code: int = 200, meta: Dict = None) -> tuple:
    """
    Create a success response
    
    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code (default: 200)
        meta: Additional metadata
    
    Returns:
        Tuple of (response, status_code)
    """
    return _create_response(
        success=True,
        data=data,
        message=message,
        status_code=status_code,
        meta=meta
    )


def error_response(message: str = "An error occurred", status_code: int = 400, 
                  errors: Dict = None, data: Any = None) -> tuple:
    """
    Create an error response
    
    Args:
        message: Error message
        status_code: HTTP status code (default: 400)
        errors: Detailed error information
        data: Additional data (optional)
    
    Returns:
        Tuple of (response, status_code)
    """
    return _create_response(
        success=False,
        message=message,
        errors=errors,
        data=data,
        status_code=status_code
    )


def validation_error_response(errors: Dict, message: str = "Validation failed") -> tuple:
    """
    Create a validation error response
    
    Args:
        errors: Field-specific validation errors
        message: General validation message
    
    Returns:
        Tuple of (response, status_code)
    """
    return _create_response(
        success=False,
        message=message,
        errors=errors,
        status_code=422
    )


def not_found_response(message: str = "Resource not found") -> tuple:
    """
    Create a not found response
    
    Args:
        message: Not found message
    
    Returns:
        Tuple of (response, status_code)
    """
    return _create_response(
        success=False,
        message=message,
        status_code=404
    )


def unauthorized_response(message: str = "Authentication required") -> tuple:
    """
    Create an unauthorized response
    
    Args:
        message: Unauthorized message
    
    Returns:
        Tuple of (response, status_code)
    """
    return _create_response(
        success=False,
        message=message,
        status_code=401
    )


def forbidden_response(message: str = "Access forbidden") -> tuple:
    """
    Create a forbidden response
    
    Args:
        message: Forbidden message
    
    Returns:
        Tuple of (response, status_code)
    """
    return _create_response(
        success=False,
        message=message,
        status_code=403
    )


def server_error_response(message: str = "Internal server error") -> tuple:
    """
    Create a server error response
    
    Args:
        message: Server error message
    
    Returns:
        Tuple of (response, status_code)
    """
    return _create_response(
        success=False,
        message=message,
        status_code=500
    )


def created_response(data: Any = None, message: str = "Resource created successfully") -> tuple:
    """
    Create a resource created response
    
    Args:
        data: Created resource data
        message: Creation message
    
    Returns:
        Tuple of (response, status_code)
    """
    return _create_response(
        success=True,
        data=data,
        message=message,
        status_code=201
    )


def no_content_response() -> tuple:
    """
    Create a no content response
    
    Returns:
        Tuple of (response, status_code)
    """
    return '', 204


def paginated_response(items: List, total: int, page: int, limit: int, 
                      message: str = "Success") -> tuple:
    """
    Create a paginated response
    
    Args:
        items: List of items for current page
        total: Total number of items
        page: Current page number
        limit: Items per page
        message: Response message
    
    Returns:
        Tuple of (response, status_code)
    """
    total_pages = (total + limit - 1) // limit  # Ceiling division
    
    meta = {
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }
    
    return _create_response(
        success=True,
        data=items,
        message=message,
        meta=meta,
        status_code=200
    )


def bulk_operation_response(successful: List, failed: List, 
                           message: str = "Bulk operation completed") -> tuple:
    """
    Create a bulk operation response
    
    Args:
        successful: List of successful operations
        failed: List of failed operations with error details
        message: Response message
    
    Returns:
        Tuple of (response, status_code)
    """
    data = {
        'successful': successful,
        'failed': failed,
        'summary': {
            'total': len(successful) + len(failed),
            'successful_count': len(successful),
            'failed_count': len(failed)
        }
    }
    
    # Determine status code based on results
    if len(failed) == 0:
        status_code = 200  # All successful
    elif len(successful) == 0:
        status_code = 400  # All failed
    else:
        status_code = 207  # Multi-status (partial success)
    
    return _create_response(
        success=len(failed) == 0,
        data=data,
        message=message,
        status_code=status_code
    )


def google_ads_response(data: Any = None, message: str = "Google Ads operation successful",
                       customer_id: str = None, operation_type: str = None) -> tuple:
    """
    Create a Google Ads specific response
    
    Args:
        data: Google Ads response data
        message: Response message
        customer_id: Google Ads customer ID
        operation_type: Type of operation performed
    
    Returns:
        Tuple of (response, status_code)
    """
    meta = {}
    if customer_id:
        meta['customer_id'] = customer_id
    if operation_type:
        meta['operation_type'] = operation_type
    
    return _create_response(
        success=True,
        data=data,
        message=message,
        meta=meta if meta else None,
        status_code=200
    )


def ai_agent_response(data: Any = None, message: str = "AI operation successful",
                     model_used: str = None, tokens_used: int = None,
                     processing_time: float = None) -> tuple:
    """
    Create an AI agent specific response
    
    Args:
        data: AI response data
        message: Response message
        model_used: AI model that was used
        tokens_used: Number of tokens consumed
        processing_time: Time taken to process
    
    Returns:
        Tuple of (response, status_code)
    """
    meta = {}
    if model_used:
        meta['model_used'] = model_used
    if tokens_used:
        meta['tokens_used'] = tokens_used
    if processing_time:
        meta['processing_time'] = processing_time
    
    return _create_response(
        success=True,
        data=data,
        message=message,
        meta=meta if meta else None,
        status_code=200
    )


def campaign_response(data: Any = None, message: str = "Campaign operation successful",
                     campaign_id: str = None, status: str = None) -> tuple:
    """
    Create a campaign specific response
    
    Args:
        data: Campaign response data
        message: Response message
        campaign_id: Campaign ID
        status: Campaign status
    
    Returns:
        Tuple of (response, status_code)
    """
    meta = {}
    if campaign_id:
        meta['campaign_id'] = campaign_id
    if status:
        meta['status'] = status
    
    return _create_response(
        success=True,
        data=data,
        message=message,
        meta=meta if meta else None,
        status_code=200
    )


def health_check_response(status: str = "healthy", checks: Dict = None) -> tuple:
    """
    Create a health check response
    
    Args:
        status: Overall health status
        checks: Individual component health checks
    
    Returns:
        Tuple of (response, status_code)
    """
    data = {
        'status': status,
        'timestamp': int(time.time())
    }
    
    if checks:
        data['checks'] = checks
    
    status_code = 200 if status == "healthy" else 503
    
    return _create_response(
        success=status == "healthy",
        data=data,
        message=f"Service is {status}",
        status_code=status_code
    )


# Response format validation
def validate_response_format(response_data: Dict) -> bool:
    """
    Validate that a response follows the standard format
    
    Args:
        response_data: Response data to validate
    
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['success', 'timestamp']
    
    for field in required_fields:
        if field not in response_data:
            return False
    
    if not isinstance(response_data['success'], bool):
        return False
    
    if not isinstance(response_data['timestamp'], int):
        return False
    
    return True


# Legacy response converter
def convert_legacy_response(legacy_response: Union[Dict, Any]) -> tuple:
    """
    Convert legacy response formats to standardized format
    
    Args:
        legacy_response: Legacy response data
    
    Returns:
        Standardized response tuple
    """
    if isinstance(legacy_response, dict):
        # Handle common legacy patterns
        if 'error' in legacy_response:
            return error_response(
                message=legacy_response.get('error', 'Unknown error'),
                status_code=legacy_response.get('status_code', 400)
            )
        elif 'message' in legacy_response and 'data' in legacy_response:
            return success_response(
                data=legacy_response['data'],
                message=legacy_response['message']
            )
        else:
            return success_response(data=legacy_response)
    else:
        return success_response(data=legacy_response)
