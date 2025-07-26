"""
Base Service Class
Provides common functionality and patterns for all service classes
"""

import logging
import time
from typing import Any, Dict, List, Optional, Union, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ServiceResult:
    """
    Standardized service result wrapper
    """
    def __init__(self, success: bool = True, data: Any = None, 
                 message: str = None, errors: Dict = None, 
                 metadata: Dict = None):
        self.success = success
        self.data = data
        self.message = message
        self.errors = errors or {}
        self.metadata = metadata or {}
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict:
        """Convert result to dictionary"""
        return {
            'success': self.success,
            'data': self.data,
            'message': self.message,
            'errors': self.errors,
            'metadata': self.metadata,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def success_result(cls, data: Any = None, message: str = "Success", 
                      metadata: Dict = None) -> 'ServiceResult':
        """Create a success result"""
        return cls(success=True, data=data, message=message, metadata=metadata)
    
    @classmethod
    def error_result(cls, message: str = "An error occurred", 
                    errors: Dict = None, data: Any = None,
                    metadata: Dict = None) -> 'ServiceResult':
        """Create an error result"""
        return cls(success=False, message=message, errors=errors, 
                  data=data, metadata=metadata)


class RetryPolicy:
    """
    Retry policy configuration
    """
    def __init__(self, max_attempts: int = 3, delay: float = 1.0, 
                 backoff_factor: float = 2.0, max_delay: float = 60.0):
        self.max_attempts = max_attempts
        self.delay = delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay


class BaseService(ABC):
    """
    Base service class with common functionality
    """
    
    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
        self.logger = logging.getLogger(f"services.{self.name}")
        self._metrics = {
            'calls': 0,
            'successes': 0,
            'failures': 0,
            'total_time': 0.0
        }
    
    def _log_operation(self, operation: str, **kwargs):
        """Log service operation"""
        self.logger.info(f"{self.name}.{operation}", extra=kwargs)
    
    def _log_error(self, operation: str, error: Exception, **kwargs):
        """Log service error"""
        self.logger.error(f"{self.name}.{operation} failed: {str(error)}", 
                         exc_info=True, extra=kwargs)
    
    def _update_metrics(self, success: bool, duration: float):
        """Update service metrics"""
        self._metrics['calls'] += 1
        self._metrics['total_time'] += duration
        if success:
            self._metrics['successes'] += 1
        else:
            self._metrics['failures'] += 1
    
    def get_metrics(self) -> Dict:
        """Get service metrics"""
        metrics = self._metrics.copy()
        if metrics['calls'] > 0:
            metrics['average_time'] = metrics['total_time'] / metrics['calls']
            metrics['success_rate'] = metrics['successes'] / metrics['calls']
        else:
            metrics['average_time'] = 0.0
            metrics['success_rate'] = 0.0
        return metrics
    
    def _execute_with_retry(self, operation: Callable, retry_policy: RetryPolicy = None,
                           operation_name: str = None, **kwargs) -> ServiceResult:
        """
        Execute an operation with retry logic
        
        Args:
            operation: Function to execute
            retry_policy: Retry configuration
            operation_name: Name for logging
            **kwargs: Arguments to pass to operation
        
        Returns:
            ServiceResult
        """
        if retry_policy is None:
            retry_policy = RetryPolicy()
        
        if operation_name is None:
            operation_name = operation.__name__
        
        last_error = None
        delay = retry_policy.delay
        
        for attempt in range(retry_policy.max_attempts):
            start_time = time.time()
            
            try:
                self._log_operation(operation_name, attempt=attempt + 1)
                result = operation(**kwargs)
                
                duration = time.time() - start_time
                self._update_metrics(True, duration)
                
                if isinstance(result, ServiceResult):
                    return result
                else:
                    return ServiceResult.success_result(data=result)
                
            except Exception as e:
                duration = time.time() - start_time
                self._update_metrics(False, duration)
                
                last_error = e
                self._log_error(operation_name, e, attempt=attempt + 1)
                
                # Don't retry on the last attempt
                if attempt < retry_policy.max_attempts - 1:
                    time.sleep(min(delay, retry_policy.max_delay))
                    delay *= retry_policy.backoff_factor
        
        # All attempts failed
        return ServiceResult.error_result(
            message=f"Operation {operation_name} failed after {retry_policy.max_attempts} attempts",
            errors={'last_error': str(last_error)},
            metadata={'attempts': retry_policy.max_attempts}
        )
    
    def _validate_input(self, data: Dict, required_fields: List[str] = None,
                       field_types: Dict = None, custom_validators: Dict = None) -> ServiceResult:
        """
        Validate input data
        
        Args:
            data: Data to validate
            required_fields: List of required field names
            field_types: Dict mapping field names to expected types
            custom_validators: Dict mapping field names to validation functions
        
        Returns:
            ServiceResult indicating validation success/failure
        """
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
        
        if errors:
            return ServiceResult.error_result(
                message="Validation failed",
                errors=errors
            )
        
        return ServiceResult.success_result(message="Validation passed")
    
    def _paginate_results(self, items: List, page: int, limit: int) -> Dict:
        """
        Paginate a list of items
        
        Args:
            items: List of items to paginate
            page: Page number (1-based)
            limit: Items per page
        
        Returns:
            Dict with paginated data and metadata
        """
        total = len(items)
        total_pages = (total + limit - 1) // limit
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        paginated_items = items[start_idx:end_idx]
        
        return {
            'items': paginated_items,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }
    
    def _cache_key(self, *args, **kwargs) -> str:
        """
        Generate a cache key from arguments
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Cache key string
        """
        import hashlib
        import json
        
        # Create a deterministic string from arguments
        key_data = {
            'service': self.name,
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    @abstractmethod
    def health_check(self) -> ServiceResult:
        """
        Check service health
        
        Returns:
            ServiceResult indicating service health
        """
        pass
    
    def get_service_info(self) -> Dict:
        """
        Get service information
        
        Returns:
            Dict with service information
        """
        return {
            'name': self.name,
            'class': self.__class__.__name__,
            'metrics': self.get_metrics(),
            'health': self.health_check().to_dict()
        }


class DatabaseService(BaseService):
    """
    Base class for database-related services
    """
    
    def __init__(self, db_session=None, name: str = None):
        super().__init__(name)
        self.db = db_session
    
    def _safe_commit(self) -> ServiceResult:
        """
        Safely commit database transaction
        
        Returns:
            ServiceResult indicating commit success/failure
        """
        try:
            if self.db:
                self.db.commit()
            return ServiceResult.success_result(message="Database commit successful")
        except Exception as e:
            if self.db:
                self.db.rollback()
            self._log_error("commit", e)
            return ServiceResult.error_result(
                message="Database commit failed",
                errors={'commit_error': str(e)}
            )
    
    def _safe_rollback(self) -> ServiceResult:
        """
        Safely rollback database transaction
        
        Returns:
            ServiceResult indicating rollback success/failure
        """
        try:
            if self.db:
                self.db.rollback()
            return ServiceResult.success_result(message="Database rollback successful")
        except Exception as e:
            self._log_error("rollback", e)
            return ServiceResult.error_result(
                message="Database rollback failed",
                errors={'rollback_error': str(e)}
            )


class APIService(BaseService):
    """
    Base class for external API services
    """
    
    def __init__(self, base_url: str = None, api_key: str = None, 
                 timeout: int = 30, name: str = None):
        super().__init__(name)
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self._session = None
    
    def _get_session(self):
        """Get or create HTTP session"""
        if self._session is None:
            import requests
            self._session = requests.Session()
            if self.api_key:
                self._session.headers.update({'Authorization': f'Bearer {self.api_key}'})
        return self._session
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> ServiceResult:
        """
        Make HTTP request with error handling
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request parameters
        
        Returns:
            ServiceResult with response data
        """
        try:
            session = self._get_session()
            url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
            
            response = session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            
            response.raise_for_status()
            
            try:
                data = response.json()
            except ValueError:
                data = response.text
            
            return ServiceResult.success_result(
                data=data,
                metadata={
                    'status_code': response.status_code,
                    'headers': dict(response.headers)
                }
            )
            
        except Exception as e:
            self._log_error("api_request", e, method=method, endpoint=endpoint)
            return ServiceResult.error_result(
                message=f"API request failed: {str(e)}",
                errors={'api_error': str(e)}
            )
    
    def health_check(self) -> ServiceResult:
        """
        Check API service health
        
        Returns:
            ServiceResult indicating API health
        """
        try:
            # Try a simple request to check connectivity
            result = self._make_request('GET', '/health')
            if result.success:
                return ServiceResult.success_result(message="API service is healthy")
            else:
                return ServiceResult.error_result(message="API service is unhealthy")
        except Exception as e:
            return ServiceResult.error_result(
                message="API health check failed",
                errors={'health_check_error': str(e)}
            )