"""
Production-Ready Lane MCP Application
Fully configured with real authentication, database, and Google Ads integration
"""

import os
import sys
import logging
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, g, request
from flask_cors import CORS
from flask_migrate import Migrate
from flask_session import Session

# Import configuration
from src.config.settings import settings
from src.config.redis_config import redis_client, get_flask_session_config
from src.config.database import get_database_config

# Import database and models
from database import db, init_database

# Import API blueprints
from src.routes.user import user_bp
from src.routes.ai_agent import ai_agent_bp
from src.routes.google_ads import google_ads_bp
from src.routes.campaigns import campaigns_bp
from dashboard_apis import dashboard_bp

# Import new service APIs
from src.api.budget_pacing_api import budget_pacing_bp
from src.api.health_api import health_bp
from src.api.orchestrator_api import orchestrator_bp
from src.api.auth_api import auth_bp

# Import services
from src.services.budget_pacing import budget_pacing_service
from src.services.health_monitor import health_monitor
from src.services.analytics_engine import analytics_engine
from src.services.approval_workflow import approval_workflow
from src.services.campaign_orchestrator import CampaignOrchestrator
from src.services.real_google_ads import real_google_ads_service

# Import authentication
from src.auth.authentication import token_required


def create_app() -> Flask:
    """Application factory"""
    app = Flask(__name__, 
                static_folder=os.path.join(os.path.dirname(__file__), 'static'),
                instance_relative_config=True)
    
    # Load configuration
    app.config.update(settings.get_flask_config())
    
    # Load database configuration
    db_config = get_database_config(settings.database.url)
    app.config.update(db_config)
    
    # Configure Redis sessions if available
    if settings.is_redis_configured():
        try:
            if redis_client.ping():
                app.config.update(get_flask_session_config())
                Session(app)
                logging.info("Redis sessions enabled")
        except Exception as e:
            logging.warning(f"Redis not available, using default sessions: {e}")
    
    # Enable CORS
    CORS(app, origins=settings.app.cors_origins.split(','))
    
    # Initialize database
    init_database(app)
    
    # Initialize Flask-Migrate for database migrations
    migrate = Migrate(app, db)
    
    # Register blueprints
    register_blueprints(app)
    
    # Initialize services
    initialize_services(app)
    
    # Add error handlers
    register_error_handlers(app)
    
    # Add request hooks
    register_request_hooks(app)
    
    # Serve frontend
    register_frontend_routes(app)
    
    return app


def register_blueprints(app: Flask):
    """Register all API blueprints"""
    # Authentication (no prefix)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # Core APIs
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(ai_agent_bp, url_prefix='/api/ai')
    app.register_blueprint(google_ads_bp, url_prefix='/api/google-ads')
    app.register_blueprint(campaigns_bp, url_prefix='/api/campaigns')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    
    # Service APIs
    app.register_blueprint(budget_pacing_bp, url_prefix='/api/budget')
    app.register_blueprint(health_bp, url_prefix='/api/health')
    app.register_blueprint(orchestrator_bp, url_prefix='/api/orchestrator')


def initialize_services(app: Flask):
    """Initialize all background services"""
    with app.app_context():
        try:
            # Initialize database tables
            db.create_all()
            
            # Start services in background
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Start budget monitoring
            if settings.app.environment != 'testing':
                loop.run_until_complete(budget_pacing_service.start_monitoring())
                loop.run_until_complete(analytics_engine.start_monitoring())
                loop.run_until_complete(approval_workflow.start_monitoring())
                
                # Initialize campaign orchestrator
                global campaign_orchestrator
                campaign_orchestrator = CampaignOrchestrator(real_google_ads_service)
                
                logging.info("All services initialized successfully")
            
        except Exception as e:
            logging.error(f"Error initializing services: {str(e)}")
            raise


def register_error_handlers(app: Flask):
    """Register global error handlers"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Bad request', 'message': str(error)}, 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return {'error': 'Unauthorized', 'message': 'Authentication required'}, 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return {'error': 'Forbidden', 'message': 'Insufficient permissions'}, 403
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found', 'message': 'Resource not found'}, 404
    
    @app.errorhandler(429)
    def too_many_requests(error):
        return {'error': 'Too many requests', 'message': 'Rate limit exceeded'}, 429
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        logging.error(f"Internal server error: {str(error)}")
        return {'error': 'Internal server error'}, 500


def register_request_hooks(app: Flask):
    """Register request hooks for logging and monitoring"""
    
    @app.before_request
    def before_request():
        # Log request
        if not request.path.startswith('/static'):
            logging.debug(f"{request.method} {request.path} from {request.remote_addr}")
        
        # Initialize request context
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        # Log response time
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            if duration > 1.0:  # Log slow requests
                logging.warning(f"Slow request: {request.method} {request.path} took {duration:.2f}s")
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response


def register_frontend_routes(app: Flask):
    """Register routes for serving frontend application"""
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        """Serve React frontend application"""
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return "Static folder not configured", 404

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return "Frontend not built. Run 'npm run build' first.", 404


def setup_logging():
    """Setup application logging"""
    log_level = getattr(logging, settings.app.log_level.upper())
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific loggers
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    logging.info(f"Logging configured for {settings.environment} environment")


def validate_environment():
    """Validate environment configuration"""
    errors = []
    
    # Check Google Ads configuration
    if not settings.is_google_ads_configured():
        if settings.environment == 'production':
            errors.append("Google Ads API configuration is required in production")
        else:
            logging.warning("Google Ads API not configured - some features will be limited")
    
    # Check database configuration
    if settings.environment == 'production' and 'sqlite' in settings.database.url:
        errors.append("SQLite is not recommended for production - use PostgreSQL")
    
    # Check security settings
    if settings.environment == 'production':
        if settings.security.secret_key == 'your-secret-key-change-in-production':
            errors.append("SECRET_KEY must be changed in production")
        if settings.security.jwt_secret_key == 'your-jwt-secret-key-change-in-production':
            errors.append("JWT_SECRET_KEY must be changed in production")
    
    if errors:
        logging.error("Environment validation failed:")
        for error in errors:
            logging.error(f"  - {error}")
        if settings.environment == 'production':
            sys.exit(1)


# Create application instance
app = create_app()


if __name__ == '__main__':
    import time
    
    # Setup logging
    setup_logging()
    
    # Validate environment
    validate_environment()
    
    # Log startup information
    logging.info(f"Starting Lane MCP in {settings.environment} mode")
    logging.info(f"Configuration: {settings.to_dict()}")
    
    # Run application
    try:
        app.run(
            host=settings.app.host,
            port=settings.app.port,
            debug=settings.app.debug,
            threaded=True
        )
    except KeyboardInterrupt:
        logging.info("Application stopped by user")
    except Exception as e:
        logging.error(f"Application startup failed: {str(e)}")
        sys.exit(1)
    finally:
        # Cleanup services
        if 'budget_pacing_service' in globals():
            loop = asyncio.get_event_loop()
            loop.run_until_complete(budget_pacing_service.stop_monitoring())
            loop.run_until_complete(analytics_engine.stop_monitoring())
            loop.run_until_complete(approval_workflow.stop_monitoring())
        
        logging.info("Application shutdown complete")