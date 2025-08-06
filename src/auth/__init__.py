"""Authentication module."""

try:
    from .flask_auth import AuthManager
except ImportError:
    AuthManager = None

try:
    from .authentication import (
        token_required,
        admin_required,
        get_current_user
    )
except ImportError:
    # Provide fallback decorators
    def token_required(f):
        return f
    
    def admin_required(f):
        return f
    
    def get_current_user():
        return None

__all__ = [
    "AuthManager",
    "token_required",
    "admin_required",
    "get_current_user"
]
