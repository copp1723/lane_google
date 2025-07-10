"""
Health Check Routes
Comprehensive system health monitoring endpoints
"""

from flask import Blueprint, jsonify
from datetime import datetime
import psutil
import os

from src.config.config import config
from src.services.ai_service import openrouter_client
from src.config.database import db

health_bp = Blueprint('health', __name__)

@health_bp.route('/', methods=['GET'])
def health_check():
    """Basic health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'Lane MCP Platform',
        'version': '1.0.0'
    })

@health_bp.route('/detailed', methods=['GET'])
def detailed_health_check():
    """Detailed health check with system metrics"""
    
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'Lane MCP Platform',
        'version': '1.0.0',
        'checks': {}
    }
    
    # Database health check
    try:
        db.session.execute('SELECT 1')
        health_status['checks']['database'] = {
            'status': 'healthy',
            'message': 'Database connection successful'
        }
    except Exception as e:
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'message': f'Database connection failed: {str(e)}'
        }
        health_status['status'] = 'unhealthy'
    
    # AI service health check
    try:
        if openrouter_client:
            health_status['checks']['ai_service'] = {
                'status': 'healthy',
                'message': 'OpenRouter client initialized'
            }
        else:
            health_status['checks']['ai_service'] = {
                'status': 'unhealthy',
                'message': 'OpenRouter client not initialized'
            }
            health_status['status'] = 'degraded'
    except Exception as e:
        health_status['checks']['ai_service'] = {
            'status': 'unhealthy',
            'message': f'AI service error: {str(e)}'
        }
        health_status['status'] = 'unhealthy'
    
    # System metrics
    try:
        health_status['system_metrics'] = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
        }
    except Exception as e:
        health_status['checks']['system_metrics'] = {
            'status': 'error',
            'message': f'Failed to get system metrics: {str(e)}'
        }
    
    # Feature flags status
    health_status['features'] = {
        'budget_pacing_enabled': config.features.budget_pacing_enabled,
        'automated_optimization_enabled': config.features.automated_optimization_enabled,
        'real_time_monitoring_enabled': config.features.real_time_monitoring_enabled,
        'advanced_analytics_enabled': config.features.advanced_analytics_enabled
    }
    
    return jsonify(health_status)

@health_bp.route('/readiness', methods=['GET'])
def readiness_check():
    """Kubernetes readiness probe endpoint"""
    
    # Check critical dependencies
    checks = []
    
    # Database check
    try:
        db.session.execute('SELECT 1')
        checks.append(True)
    except:
        checks.append(False)
    
    # AI service check
    try:
        if openrouter_client:
            checks.append(True)
        else:
            checks.append(False)
    except:
        checks.append(False)
    
    if all(checks):
        return jsonify({'status': 'ready'}), 200
    else:
        return jsonify({'status': 'not ready'}), 503

@health_bp.route('/liveness', methods=['GET'])
def liveness_check():
    """Kubernetes liveness probe endpoint"""
    return jsonify({'status': 'alive'}), 200

