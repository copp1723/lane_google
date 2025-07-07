"""
Health Monitoring API Endpoints
Provides system health checks and monitoring endpoints
"""

from flask import Blueprint, jsonify, request
import logging
from src.services.health_monitor import health_monitor
from responses import api_response, api_error
import asyncio

logger = logging.getLogger(__name__)

# Create blueprint
health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint"""
    try:
        # Run async health check
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        health_status = loop.run_until_complete(health_monitor.get_health_status())
        
        # Return appropriate HTTP status code
        if health_status['status'] == 'unhealthy':
            return api_response(health_status, status_code=503)
        elif health_status['status'] == 'degraded':
            return api_response(health_status, status_code=200)
        else:
            return api_response(health_status)
            
    except Exception as e:
        logger.error(f'Health check error: {str(e)}')
        return api_error('Health check failed', 503)


@health_bp.route('/health/detailed', methods=['GET'])
def detailed_health_check():
    """Detailed health check with system information"""
    try:
        # Check for API key for security (optional)
        api_key = request.headers.get('X-API-Key')
        if api_key != 'your-monitoring-api-key':  # Replace with config
            # Still return health but without detailed info
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            basic_health = loop.run_until_complete(health_monitor.get_health_status(detailed=False))
            return api_response(basic_health)
        
        # Run detailed health check
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        detailed_health = loop.run_until_complete(health_monitor.get_health_status(detailed=True))
        
        return api_response(detailed_health)
        
    except Exception as e:
        logger.error(f'Detailed health check error: {str(e)}')
        return api_error('Health check failed', 503)


@health_bp.route('/health/metrics', methods=['GET'])
def health_metrics():
    """Get health metrics for monitoring dashboards"""
    try:
        metrics = health_monitor.get_health_metrics()
        return api_response(metrics)
        
    except Exception as e:
        logger.error(f'Health metrics error: {str(e)}')
        return api_error('Failed to get health metrics', 500)


@health_bp.route('/health/diagnostic', methods=['POST'])
def run_diagnostic():
    """Run comprehensive system diagnostic"""
    try:
        # Require authentication or API key
        api_key = request.headers.get('X-API-Key')
        if api_key != 'your-admin-api-key':  # Replace with config
            return api_error('Unauthorized', 401)
        
        # Run diagnostic
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        diagnostic_results = loop.run_until_complete(health_monitor.run_diagnostic())
        
        return api_response(diagnostic_results)
        
    except Exception as e:
        logger.error(f'Diagnostic error: {str(e)}')
        return api_error('Diagnostic failed', 500)


@health_bp.route('/health/services/<service_name>', methods=['GET'])
def check_service_health(service_name):
    """Check health of a specific service"""
    try:
        # Get current health status
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        health_status = loop.run_until_complete(health_monitor.get_health_status())
        
        # Extract service health
        if service_name in health_status.get('services', {}):
            service_health = health_status['services'][service_name]
            return api_response({
                'service': service_name,
                'health': service_health,
                'overall_status': health_status['status']
            })
        else:
            return api_error(f'Service {service_name} not found', 404)
            
    except Exception as e:
        logger.error(f'Service health check error: {str(e)}')
        return api_error('Health check failed', 503)


# Prometheus-style metrics endpoint
@health_bp.route('/metrics', methods=['GET'])
def prometheus_metrics():
    """Export metrics in Prometheus format"""
    try:
        # Get current health and metrics
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        health_status = loop.run_until_complete(health_monitor.get_health_status())
        metrics = health_monitor.get_health_metrics()
        
        # Build Prometheus format response
        prometheus_data = []
        
        # Overall health gauge (1=healthy, 0.5=degraded, 0=unhealthy)
        health_value = {'healthy': 1, 'degraded': 0.5, 'unhealthy': 0}.get(health_status['status'], 0)
        prometheus_data.append(f'lane_mcp_health_status {health_value}')
        
        # Uptime percentage
        prometheus_data.append(f'lane_mcp_uptime_percentage {metrics["uptime_percentage"]}')
        
        # Service-specific metrics
        for service, status in health_status.get('services', {}).items():
            service_healthy = 1 if status.get('status') == 'healthy' else 0
            prometheus_data.append(f'lane_mcp_service_health{{service="{service}"}} {service_healthy}')
            
            # Response time metrics if available
            if 'response_time' in status:
                prometheus_data.append(f'lane_mcp_service_response_time{{service="{service}"}} {status["response_time"]}')
        
        # System metrics if available
        system_health = health_status.get('services', {}).get('system', {})
        if 'cpu_percent' in system_health:
            prometheus_data.append(f'lane_mcp_cpu_usage_percent {system_health["cpu_percent"]}')
        if 'memory' in system_health:
            prometheus_data.append(f'lane_mcp_memory_usage_percent {system_health["memory"]["percent"]}')
        if 'disk' in system_health:
            prometheus_data.append(f'lane_mcp_disk_usage_percent {system_health["disk"]["percent"]}')
        
        return '\n'.join(prometheus_data), 200, {'Content-Type': 'text/plain'}
        
    except Exception as e:
        logger.error(f'Metrics export error: {str(e)}')
        return 'Error generating metrics', 503