"""
Health Check Routes
Provides application health and status endpoints
"""

from flask import Blueprint, jsonify
from datetime import datetime
from src.config.settings import settings
from src.config.database import db
import logging

logger = logging.getLogger(__name__)

# Create blueprint
health_bp = Blueprint('health', __name__)


@health_bp.route('/health')
def health_check():
    """Basic health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'Lane MCP',
        'version': settings.app_version
    })


@health_bp.route('/api/health')
def api_health_check():
    """Comprehensive API health check with service status"""
    try:
        # Check database connectivity
        db_status = 'healthy'
        try:
            with db.engine.connect() as connection:
                connection.execute(db.text('SELECT 1'))
        except Exception as e:
            db_status = f'unhealthy: {str(e)}'
            logger.error(f"Database health check failed: {str(e)}")
        
        # Check external service configurations
        services = {
            'database': db_status,
            'google_ads': 'configured' if settings.google_ads.client_id else 'not_configured',
            'openai': 'configured' if settings.openai.api_key else 'not_configured',
            'redis': 'configured' if 'redis://' in settings.redis.url else 'not_configured'
        }
        
        # Determine overall health
        overall_status = 'healthy'
        if db_status != 'healthy':
            overall_status = 'degraded'
        
        return jsonify({
            'status': overall_status,
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'Lane MCP API',
            'version': settings.app_version,
            'environment': settings.environment,
            'services': services,
            'features': {
                'ai_chat': settings.features.ai_chat_enabled,
                'real_time_monitoring': settings.features.real_time_monitoring,
                'auto_optimization': settings.features.auto_optimization,
                'workflow_approval': settings.features.workflow_approval,
                'performance_analytics': settings.features.performance_analytics
            }
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'Lane MCP API',
            'error': str(e)
        }), 500


@health_bp.route('/api/health/ready')
def readiness_check():
    """Kubernetes readiness probe endpoint"""
    try:
        # Check if application is ready to serve requests
        with db.engine.connect() as connection:
            connection.execute(db.text('SELECT 1'))
        
        return jsonify({
            'status': 'ready',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return jsonify({
            'status': 'not_ready',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 503


@health_bp.route('/api/health/live')
def liveness_check():
    """Kubernetes liveness probe endpoint"""
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.utcnow().isoformat()
    })


@health_bp.route('/api/config')
def config_info():
    """Get non-sensitive configuration information"""
    return jsonify(settings.to_dict())