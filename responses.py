"""
Response Utilities
Standardized API response helpers
"""

from flask import jsonify
from typing import Any, Dict, Optional, List
from datetime import datetime


class APIResponse:
    """Standardized API response builder"""
    
    @staticmethod
    def success(data: Any = None, message: str = None, status_code: int = 200, **kwargs) -> tuple:
        """
        Create a successful API response
        
        Args:
            data: Response data
            message: Success message
            status_code: HTTP status code
            **kwargs: Additional response fields
        
        Returns:
            Tuple of (response, status_code)
        """
        response = {
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        
        if data is not None:
            response['data'] = data
        
        if message:
            response['message'] = message
        
        return jsonify(response), status_code
    
    @staticmethod
    def error(message: str, status_code: int = 400, error_code: str = None, 
              details: Dict = None, **kwargs) -> tuple:
        """
        Create an error API response
        
        Args:
            message: Error message
            status_code: HTTP status code
            error_code: Application-specific error code
            details: Additional error details
            **kwargs: Additional response fields
        
        Returns:
            Tuple of (response, status_code)
        """
        response = {
            'status': 'error',
            'error': message,
            'status_code': status_code,
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        
        if error_code:
            response['error_code'] = error_code
        
        if details:
            response['details'] = details
        
        return jsonify(response), status_code
    
    @staticmethod
    def validation_error(errors: List[str], message: str = "Validation failed") -> tuple:
        """
        Create a validation error response
        
        Args:
            errors: List of validation error messages
            message: Main error message
        
        Returns:
            Tuple of (response, status_code)
        """
        return APIResponse.error(
            message=message,
            status_code=400,
            error_code='VALIDATION_ERROR',
            details={'validation_errors': errors}
        )
    
    @staticmethod
    def not_found(resource: str = "Resource", resource_id: str = None) -> tuple:
        """
        Create a not found error response
        
        Args:
            resource: Resource type name
            resource_id: Resource identifier
        
        Returns:
            Tuple of (response, status_code)
        """
        message = f"{resource} not found"
        if resource_id:
            message += f" with ID: {resource_id}"
        
        return APIResponse.error(
            message=message,
            status_code=404,
            error_code='NOT_FOUND'
        )
    
    @staticmethod
    def unauthorized(message: str = "Authentication required") -> tuple:
        """
        Create an unauthorized error response
        
        Args:
            message: Error message
        
        Returns:
            Tuple of (response, status_code)
        """
        return APIResponse.error(
            message=message,
            status_code=401,
            error_code='UNAUTHORIZED'
        )
    
    @staticmethod
    def forbidden(message: str = "Insufficient permissions") -> tuple:
        """
        Create a forbidden error response
        
        Args:
            message: Error message
        
        Returns:
            Tuple of (response, status_code)
        """
        return APIResponse.error(
            message=message,
            status_code=403,
            error_code='FORBIDDEN'
        )
    
    @staticmethod
    def paginated(data: List, page: int, per_page: int, total: int, **kwargs) -> tuple:
        """
        Create a paginated response
        
        Args:
            data: List of items for current page
            page: Current page number
            per_page: Items per page
            total: Total number of items
            **kwargs: Additional response fields
        
        Returns:
            Tuple of (response, status_code)
        """
        total_pages = (total + per_page - 1) // per_page
        
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
        
        return APIResponse.success(
            data=data,
            pagination=pagination,
            **kwargs
        )


class ResponseHelper:
    """Helper functions for common response patterns"""
    
    @staticmethod
    def created(resource: Any, message: str = None) -> tuple:
        """Helper for resource creation responses"""
        return APIResponse.success(
            data=resource,
            message=message or "Resource created successfully",
            status_code=201
        )
    
    @staticmethod
    def updated(resource: Any, message: str = None) -> tuple:
        """Helper for resource update responses"""
        return APIResponse.success(
            data=resource,
            message=message or "Resource updated successfully"
        )
    
    @staticmethod
    def deleted(message: str = None) -> tuple:
        """Helper for resource deletion responses"""
        return APIResponse.success(
            message=message or "Resource deleted successfully",
            status_code=204
        )
    
    @staticmethod
    def campaign_response(campaign: Any, include_performance: bool = False) -> tuple:
        """Helper for campaign-specific responses"""
        data = campaign.to_dict(include_performance=include_performance)
        return APIResponse.success(data=data)
    
    @staticmethod
    def analytics_response(analytics_data: Dict, date_range: Dict = None) -> tuple:
        """Helper for analytics responses"""
        response_data = {
            'analytics': analytics_data
        }
        
        if date_range:
            response_data['date_range'] = date_range
        
        return APIResponse.success(data=response_data)

