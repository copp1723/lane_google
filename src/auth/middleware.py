"""
Enterprise middleware for security, monitoring, and performance
"""

from flask import request, g, jsonify
from datetime import datetime
import uuid
import logging
import time

logger = logging.getLogger(__name__)

def init_middleware(app):
    """Initialize all middleware components"""
    
    @app.before_request
    def before_request():
        """Pre-request middleware"""
        # Generate request ID for tracing
        g.request_id = str(uuid.uuid4())
        g.start_time = time.time()
        
        # Log request details
        logger.info(f"Request {g.request_id}: {request.method} {request.url}")
        
        # Security headers
        if request.endpoint and not request.endpoint.startswith('static'):
            # Add security context
            g.user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            g.user_agent = request.headers.get('User-Agent', '')
    
    @app.after_request
    def after_request(response):
        """Post-request middleware"""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            logger.info(f"Request {g.request_id}: {response.status_code} in {duration:.3f}s")
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Add request ID to response
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
        
        return response

