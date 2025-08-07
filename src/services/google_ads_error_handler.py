"""
Google Ads API Error Handler
Provides comprehensive error handling and retry logic for Google Ads API calls
"""

import logging
import time
from functools import wraps
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)

# Error categories
RATE_LIMIT_ERRORS = [
    'RATE_EXCEEDED',
    'RESOURCE_EXHAUSTED',
    'QUOTA_ERROR'
]

AUTH_ERRORS = [
    'AUTHENTICATION_ERROR',
    'AUTHORIZATION_ERROR',
    'USER_PERMISSION_DENIED',
    'OAUTH_TOKEN_INVALID',
    'OAUTH_TOKEN_EXPIRED',
    'OAUTH_TOKEN_DISABLED',
    'OAUTH_TOKEN_REVOKED'
]

RETRYABLE_ERRORS = [
    'INTERNAL_ERROR',
    'TRANSIENT_ERROR',
    'CONCURRENT_MODIFICATION',
    'DATABASE_ERROR'
]

class GoogleAdsAPIError(Exception):
    """Custom exception for Google Ads API errors"""
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}

def parse_google_ads_exception(exception) -> Dict[str, Any]:
    """Parse Google Ads exception to extract error details"""
    error_details = {
        'message': str(exception),
        'errors': []
    }
    
    if hasattr(exception, 'failure'):
        failure = exception.failure
        if hasattr(failure, 'errors'):
            for error in failure.errors:
                error_info = {
                    'error_code': error.error_code.name if hasattr(error.error_code, 'name') else str(error.error_code),
                    'message': error.message,
                    'trigger': getattr(error, 'trigger', None),
                    'location': []
                }
                
                # Extract field path information
                if hasattr(error, 'location'):
                    for field_path_element in error.location.field_path_elements:
                        error_info['location'].append(field_path_element.field_name)
                
                error_details['errors'].append(error_info)
    
    return error_details

def handle_google_ads_error(func: Callable) -> Callable:
    """Decorator to handle Google Ads API errors with retry logic"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        max_retries = 3
        retry_delay = 1  # Start with 1 second
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
                
            except Exception as e:
                # Check if it's a Google Ads exception
                if hasattr(e, '__class__') and 'GoogleAdsException' in e.__class__.__name__:
                    error_details = parse_google_ads_exception(e)
                    
                    # Check error types
                    is_rate_limit = any(
                        any(err in error['error_code'] for err in RATE_LIMIT_ERRORS)
                        for error in error_details['errors']
                    )
                    
                    is_auth_error = any(
                        any(err in error['error_code'] for err in AUTH_ERRORS)
                        for error in error_details['errors']
                    )
                    
                    is_retryable = any(
                        any(err in error['error_code'] for err in RETRYABLE_ERRORS)
                        for error in error_details['errors']
                    )
                    
                    # Handle rate limiting
                    if is_rate_limit and attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"Rate limit hit. Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    
                    # Handle auth errors (don't retry)
                    if is_auth_error:
                        logger.error(f"Authentication error: {error_details}")
                        raise GoogleAdsAPIError(
                            "Authentication failed. Please check your credentials.",
                            error_code="AUTH_ERROR",
                            details=error_details
                        )
                    
                    # Handle retryable errors
                    if is_retryable and attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        logger.warning(f"Transient error. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    
                    # For other errors or final attempt
                    logger.error(f"Google Ads API error: {error_details}")
                    raise GoogleAdsAPIError(
                        f"Google Ads API error: {error_details['message']}",
                        error_code="API_ERROR",
                        details=error_details
                    )
                
                # For non-Google Ads exceptions
                logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
                raise
        
        # If we've exhausted all retries
        raise GoogleAdsAPIError(
            f"Failed after {max_retries} attempts",
            error_code="MAX_RETRIES_EXCEEDED"
        )
    
    return wrapper

class GoogleAdsErrorHandler:
    """Utility class for handling Google Ads API errors"""
    
    @staticmethod
    def get_error_message(exception) -> str:
        """Get user-friendly error message from exception"""
        if isinstance(exception, GoogleAdsAPIError):
            if exception.error_code == "AUTH_ERROR":
                return (
                    "Authentication failed. Please ensure you have:\n"
                    "1. Valid OAuth2 credentials (not Customer ID)\n"
                    "2. Active Google Ads developer token\n"
                    "3. Proper API access permissions\n"
                    "Run: python scripts/generate_google_ads_credentials.py"
                )
            elif exception.error_code == "RATE_LIMIT":
                return (
                    "API rate limit exceeded. Please wait a moment and try again.\n"
                    "Consider implementing request batching for bulk operations."
                )
            elif exception.error_code == "MAX_RETRIES_EXCEEDED":
                return "Operation failed after multiple retries. The service may be temporarily unavailable."
        
        # Parse Google Ads specific exceptions
        if hasattr(exception, '__class__') and 'GoogleAdsException' in exception.__class__.__name__:
            details = parse_google_ads_exception(exception)
            if details['errors']:
                first_error = details['errors'][0]
                return f"Google Ads API Error: {first_error['message']} (Code: {first_error['error_code']})"
        
        # Generic error message
        return f"An error occurred: {str(exception)}"
    
    @staticmethod
    def is_retryable_error(exception) -> bool:
        """Check if an error is retryable"""
        if hasattr(exception, '__class__') and 'GoogleAdsException' in exception.__class__.__name__:
            details = parse_google_ads_exception(exception)
            return any(
                any(err in error['error_code'] for err in RETRYABLE_ERRORS + RATE_LIMIT_ERRORS)
                for error in details['errors']
            )
        return False
    
    @staticmethod
    def log_error_details(exception, context: Optional[str] = None):
        """Log detailed error information for debugging"""
        if context:
            logger.error(f"Error context: {context}")
        
        if hasattr(exception, '__class__') and 'GoogleAdsException' in exception.__class__.__name__:
            details = parse_google_ads_exception(exception)
            logger.error(f"Google Ads API Error Details: {details}")
            
            # Log specific field errors
            for error in details['errors']:
                if error['location']:
                    logger.error(f"Field error at: {' > '.join(error['location'])}")
        else:
            logger.error(f"Error: {str(exception)}", exc_info=True)