"""
Validation Utilities
Common validation patterns and decorators
"""

from functools import wraps
from flask import request, jsonify
from typing import Callable, Any, Dict, List, Optional
import re


class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(message)


class Validator:
    """Common validation utilities"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password: str) -> bool:
        """Validate password strength"""
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        return True
    
    @staticmethod
    def validate_google_customer_id(customer_id: str) -> bool:
        """Validate Google Ads customer ID format"""
        # Google Ads customer IDs are typically 10 digits
        pattern = r'^\d{10}$'
        return re.match(pattern, customer_id.replace('-', '')) is not None
    
    @staticmethod
    def validate_campaign_name(name: str) -> bool:
        """Validate campaign name"""
        if not name or len(name.strip()) < 3:
            return False
        if len(name) > 100:
            return False
        # Check for invalid characters
        invalid_chars = ['<', '>', '"', '&']
        return not any(char in name for char in invalid_chars)
    
    @staticmethod
    def validate_budget_amount(amount: float) -> bool:
        """Validate budget amount"""
        return amount > 0 and amount <= 1000000  # Max $1M daily budget


def validate_json_request(required_fields: List[str] = None, 
                         optional_fields: List[str] = None,
                         field_validators: Dict[str, Callable] = None):
    """
    Decorator to validate JSON request data
    
    Args:
        required_fields (list): List of required field names
        optional_fields (list): List of optional field names
        field_validators (dict): Dict of field_name -> validator_function
    
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            # Check if request has JSON data
            if not request.is_json:
                return jsonify({
                    'error': 'Request must be JSON',
                    'status_code': 400
                }), 400
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'error': 'Request body cannot be empty',
                    'status_code': 400
                }), 400
            
            errors = []
            
            # Check required fields
            if required_fields:
                for field in required_fields:
                    if field not in data or data[field] is None:
                        errors.append(f"Field '{field}' is required")
                    elif isinstance(data[field], str) and not data[field].strip():
                        errors.append(f"Field '{field}' cannot be empty")
            
            # Validate field formats
            if field_validators:
                for field, validator in field_validators.items():
                    if field in data and data[field] is not None:
                        try:
                            if not validator(data[field]):
                                errors.append(f"Field '{field}' has invalid format")
                        except Exception as e:
                            errors.append(f"Field '{field}' validation error: {str(e)}")
            
            # Check for unexpected fields
            allowed_fields = set()
            if required_fields:
                allowed_fields.update(required_fields)
            if optional_fields:
                allowed_fields.update(optional_fields)
            
            if allowed_fields:
                unexpected_fields = set(data.keys()) - allowed_fields
                if unexpected_fields:
                    errors.append(f"Unexpected fields: {', '.join(unexpected_fields)}")
            
            if errors:
                return jsonify({
                    'error': 'Validation failed',
                    'validation_errors': errors,
                    'status_code': 400
                }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_query_params(param_validators: Dict[str, Callable]):
    """
    Decorator to validate query parameters
    
    Args:
        param_validators (dict): Dict of param_name -> validator_function
    
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            errors = []
            
            for param, validator in param_validators.items():
                value = request.args.get(param)
                if value is not None:
                    try:
                        if not validator(value):
                            errors.append(f"Query parameter '{param}' has invalid format")
                    except Exception as e:
                        errors.append(f"Query parameter '{param}' validation error: {str(e)}")
            
            if errors:
                return jsonify({
                    'error': 'Query parameter validation failed',
                    'validation_errors': errors,
                    'status_code': 400
                }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_campaign_data():
    """Decorator specifically for campaign data validation"""
    return validate_json_request(
        required_fields=['name', 'campaign_type', 'budget_amount'],
        optional_fields=['description', 'target_audience', 'keywords', 'google_customer_id'],
        field_validators={
            'name': Validator.validate_campaign_name,
            'budget_amount': lambda x: isinstance(x, (int, float)) and Validator.validate_budget_amount(float(x)),
            'google_customer_id': Validator.validate_google_customer_id
        }
    )

