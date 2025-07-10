"""
Standard API Response Utilities
Provides consistent response formatting across all API endpoints
"""

from typing import Any, Dict, Optional
from flask import jsonify
from datetime import datetime


def success_response(data: Any = None, message: str = "Success", 
                    status_code: int = 200, meta: Dict = None) -> tuple:
    """
    Generate a standardized success response
    
    Args:
        data: The response data payload
        message: Success message
        status_code: HTTP status code (default: 200)
        meta: Additional metadata
    
    Returns:
        tuple: (jsonify response, status_code)
    """
    response = {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    if meta:
        response["meta"] = meta
    
    return jsonify(response), status_code


def error_response(message: str = "An error occurred", 
                  status_code: int = 400, 
                  error_code: str = None,
                  details: Dict = None) -> tuple:
    """
    Generate a standardized error response
    
    Args:
        message: Error message
        status_code: HTTP status code (default: 400)
        error_code: Optional error code for client handling
        details: Additional error details
    
    Returns:
        tuple: (jsonify response, status_code)
    """
    response = {
        "success": False,
        "message": message,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    if error_code:
        response["error_code"] = error_code
    
    if details:
        response["details"] = details
    
    return jsonify(response), status_code


def paginated_response(data: list, page: int = 1, limit: int = 20, 
                      total: int = None, message: str = "Success") -> tuple:
    """
    Generate a paginated response
    
    Args:
        data: List of items for current page
        page: Current page number
        limit: Items per page
        total: Total number of items (if known)
        message: Success message
    
    Returns:
        tuple: (jsonify response, status_code)
    """
    meta = {
        "pagination": {
            "page": page,
            "limit": limit,
            "count": len(data)
        }
    }
    
    if total is not None:
        meta["pagination"]["total"] = total
        meta["pagination"]["pages"] = (total + limit - 1) // limit
        meta["pagination"]["has_next"] = page * limit < total
        meta["pagination"]["has_prev"] = page > 1
    
    return success_response(data=data, message=message, meta=meta)


def validation_error_response(errors: Dict[str, list]) -> tuple:
    """
    Generate a validation error response
    
    Args:
        errors: Dictionary of field validation errors
    
    Returns:
        tuple: (jsonify response, status_code)
    """
    return error_response(
        message="Validation failed",
        status_code=422,
        error_code="VALIDATION_ERROR",
        details={"field_errors": errors}
    )


def not_found_response(resource: str = "Resource") -> tuple:
    """
    Generate a 404 not found response
    
    Args:
        resource: Name of the resource that wasn't found
    
    Returns:
        tuple: (jsonify response, status_code)
    """
    return error_response(
        message=f"{resource} not found",
        status_code=404,
        error_code="NOT_FOUND"
    )


def unauthorized_response(message: str = "Authentication required") -> tuple:
    """
    Generate a 401 unauthorized response
    
    Args:
        message: Custom unauthorized message
    
    Returns:
        tuple: (jsonify response, status_code)
    """
    return error_response(
        message=message,
        status_code=401,
        error_code="UNAUTHORIZED"
    )


def forbidden_response(message: str = "Access denied") -> tuple:
    """
    Generate a 403 forbidden response
    
    Args:
        message: Custom forbidden message
    
    Returns:
        tuple: (jsonify response, status_code)
    """
    return error_response(
        message=message,
        status_code=403,
        error_code="FORBIDDEN"
    )


def rate_limit_response(retry_after: int = 60) -> tuple:
    """
    Generate a 429 rate limit response
    
    Args:
        retry_after: Seconds until client can retry
    
    Returns:
        tuple: (jsonify response, status_code)
    """
    return error_response(
        message="Rate limit exceeded",
        status_code=429,
        error_code="RATE_LIMIT_EXCEEDED",
        details={"retry_after": retry_after}
    )


def server_error_response(message: str = "Internal server error") -> tuple:
    """
    Generate a 500 server error response
    
    Args:
        message: Custom error message
    
    Returns:
        tuple: (jsonify response, status_code)
    """
    return error_response(
        message=message,
        status_code=500,
        error_code="INTERNAL_ERROR"
    )
