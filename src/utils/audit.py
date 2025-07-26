"""
Audit Logging Utilities
Centralized audit logging helpers and decorators
"""

from functools import wraps
from flask import g, request
from typing import Callable, Any, Dict, Optional
from datetime import datetime

from src.utils.audit_log import AuditLog, AuditAction


def audit_action(action: AuditAction, description: Optional[str] = None):
    """
    Decorator to automatically audit function calls
    
    Args:
        action (AuditAction): The audit action type
        description (str, optional): Custom description
    
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            # Execute the function
            result = f(*args, **kwargs)
            
            # Log the action if user is authenticated
            if hasattr(g, 'current_user') and g.current_user:
                audit_description = description or f"Function {f.__name__} executed"
                
                AuditLog.log_user_action(
                    action=action,
                    user_id=g.current_user.id,
                    description=audit_description,
                    additional_metadata={
                        'function': f.__name__,
                        'args_count': len(args),
                        'kwargs_keys': list(kwargs.keys()),
                        'endpoint': request.endpoint,
                        'method': request.method
                    }
                )
            
            return result
        
        return decorated_function
    return decorator


class AuditHelper:
    """Helper class for common audit logging patterns"""
    
    @staticmethod
    def log_campaign_action(action: AuditAction, campaign_id: str, campaign_name: str, 
                          description: str, old_values: Optional[Dict] = None, 
                          new_values: Optional[Dict] = None, **metadata):
        """
        Log campaign-related actions with standardized format
        
        Args:
            action (AuditAction): The audit action type
            campaign_id (str): Campaign ID
            campaign_name (str): Campaign name
            description (str): Action description
            old_values (dict, optional): Previous values
            new_values (dict, optional): New values
            **metadata: Additional metadata
        """
        user_id = g.current_user.id if hasattr(g, 'current_user') and g.current_user else None
        
        AuditLog.log_campaign_action(
            action=action,
            user_id=user_id,
            campaign_id=campaign_id,
            campaign_name=campaign_name,
            description=description,
            old_values=old_values,
            new_values=new_values,
            additional_metadata={
                'timestamp': datetime.utcnow().isoformat(),
                'user_ip': getattr(g, 'user_ip', None),
                'user_agent': getattr(g, 'user_agent', None),
                **metadata
            }
        )
    
    @staticmethod
    def log_security_event(action: AuditAction, description: str, severity: str = 'medium', **metadata):
        """
        Log security-related events with standardized format
        
        Args:
            action (AuditAction): The audit action type
            description (str): Event description
            severity (str): Event severity (low, medium, high, critical)
            **metadata: Additional metadata
        """
        user_id = g.current_user.id if hasattr(g, 'current_user') and g.current_user else None
        
        AuditLog.log_security_event(
            action=action,
            user_id=user_id,
            description=description,
            additional_metadata={
                'severity': severity,
                'timestamp': datetime.utcnow().isoformat(),
                'user_ip': getattr(g, 'user_ip', None),
                'user_agent': getattr(g, 'user_agent', None),
                'endpoint': request.endpoint if request else None,
                'method': request.method if request else None,
                **metadata
            }
        )
    
    @staticmethod
    def log_data_access(resource_type: str, resource_id: str, action: str = 'read', **metadata):
        """
        Log data access events
        
        Args:
            resource_type (str): Type of resource accessed
            resource_id (str): ID of the resource
            action (str): Type of access (read, write, delete)
            **metadata: Additional metadata
        """
        user_id = g.current_user.id if hasattr(g, 'current_user') and g.current_user else None
        
        AuditLog.log_user_action(
            action=AuditAction.DATA_ACCESSED,
            user_id=user_id,
            description=f"Data {action} access: {resource_type} {resource_id}",
            additional_metadata={
                'resource_type': resource_type,
                'resource_id': resource_id,
                'access_type': action,
                'timestamp': datetime.utcnow().isoformat(),
                'user_ip': getattr(g, 'user_ip', None),
                'user_agent': getattr(g, 'user_agent', None),
                **metadata
            }
        )


def track_data_access(resource_type: str, resource_id_param: str = 'id'):
    """
    Decorator to automatically track data access
    
    Args:
        resource_type (str): Type of resource being accessed
        resource_id_param (str): Parameter name containing resource ID
    
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            # Get resource ID from parameters
            resource_id = kwargs.get(resource_id_param, 'unknown')
            
            # Log data access
            AuditHelper.log_data_access(
                resource_type=resource_type,
                resource_id=str(resource_id),
                action='read' if request.method == 'GET' else 'write'
            )
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

