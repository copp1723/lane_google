"""
Unified Application Entry Point
Consolidates development and production configurations into a single, environment-aware entry point
"""

import os
import sys
import logging
import asyncio
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, g, request
from flask_cors import CORS
from flask_migrate import Migrate

# Import configuration
from src.config.settings import settings
from src.config.database import db, init_database

# Import all blueprints
from src.routes.user import user_bp
from src.routes.ai_agent import ai_agent_bp
from src.routes.google_ads import google_ads_bp
from src.routes.campaigns import campaigns_bp
from src.routes.health import health_bp
from src.api.dashboard_apis import dashboard_bp

# Import additional API blueprints
from src.api.budget_pacing_api import budget_pacing_bp
from src.api.orchestrator_api import orchestrator_bp
from src.api.keyword_research_api import keyword_research_bp
from src.api.keyword_analytics_api import keyword_analytics_bp
from src.api.campaign_analytics_api import campaign_analytics_bp

# Import services
from src.services.campaign_orchestrator import CampaignOrchestrator
from src.services.real_google_ads import real_google_ads_service
from src.services.budget_pacing import budget_pacing_service

# Import authentication
from src.auth.authentication import token_required


def create_app() -> Flask:
    """Application factory with environment-aware configuration"""
    app = Flask(__name__,
                static_folder=os.path.join(os.path.dirname(__file__), 'static'),
                instance_relative_config=True)
    
    # Configure app based on environment
    configure_app(app)
    
    # Initialize extensions
    initialize_extensions(app)
    
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


def configure_app(app: Flask):
    """Configure Flask app based on environment"""
    # Basic configuration
    app.config['SECRET_KEY'] = settings.security.secret_key
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.get_database_url()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Environment-specific configurations
    if settings.is_development:
        app.config['DEBUG'] = True
        app.config['TESTING'] = False
    elif settings.is_production:
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
    else:  # testing
        app.config['DEBUG'] = False
        app.config['TESTING'] = True
    
    # Enable CORS
    CORS(app, origins=settings.security.cors_origins)


def initialize_extensions(app: Flask):
    """Initialize Flask extensions"""
    # Initialize database
    db.init_app(app)
    
    # Initialize Flask-Migrate for database migrations
    migrate = Migrate(app, db)


def register_blueprints(app: Flask):
    """Register all API blueprints"""
    # Health checks (no prefix for basic health)
    app.register_blueprint(health_bp)
    
    # Core APIs
    if settings.is_production:
        # Production: Register all blueprints
        app.register_blueprint(user_bp, url_prefix='/api/users')
        app.register_blueprint(ai_agent_bp, url_prefix='/api/ai')
        app.register_blueprint(google_ads_bp, url_prefix='/api/google-ads')
        app.register_blueprint(campaigns_bp, url_prefix='/api/campaigns')
    else:
        # Development: Register available blueprints only
        try:
            app.register_blueprint(user_bp, url_prefix='/api/users')
        except Exception as e:
            logging.warning(f"Could not register user_bp: {e}")
        
        app.register_blueprint(ai_agent_bp, url_prefix='/api/ai')
        
        try:
            app.register_blueprint(google_ads_bp, url_prefix='/api/google-ads')
        except Exception as e:
            logging.warning(f"Could not register google_ads_bp: {e}")
        
        try:
            app.register_blueprint(campaigns_bp, url_prefix='/api/campaigns')
        except Exception as e:
            logging.warning(f"Could not register campaigns_bp: {e}")
    
    # Dashboard APIs (always available)
    app.register_blueprint(dashboard_bp)
    
    # Additional service blueprints (if available)
    optional_blueprints = [
        (budget_pacing_bp, '/api/budget'),
        (orchestrator_bp, '/api/orchestrator'),
        (keyword_research_bp, '/api/keywords'),
        (keyword_analytics_bp, '/api/keyword-analytics'),
        (campaign_analytics_bp, '/api/campaign-analytics')
    ]
    
    for blueprint, prefix in optional_blueprints:
        try:
            app.register_blueprint(blueprint, url_prefix=prefix)
        except Exception as e:
            logging.warning(f"Could not register {blueprint.name}: {e}")


def initialize_services(app: Flask):
    """Initialize all background services"""
    with app.app_context():
        try:
            # Initialize database tables
            db.create_all()
            
            # Initialize campaign orchestrator (production only)
            if settings.is_production and not settings.is_testing:
                global campaign_orchestrator
                campaign_orchestrator = CampaignOrchestrator(real_google_ads_service)
                logging.info("Campaign orchestrator initialized successfully")
            
            # Start budget monitoring service (if available)
            if hasattr(budget_pacing_service, 'start_monitoring'):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(budget_pacing_service.start_monitoring())
                except Exception as e:
                    logging.warning(f"Could not start budget monitoring: {e}")
            
        except Exception as e:
            logging.error(f"Error initializing services: {str(e)}")
            if settings.is_production:
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
    log_level = getattr(logging, settings.logging.level.upper())
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format=settings.logging.format,
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
    validation_result = settings.validate_required_settings()
    
    # Log warnings
    for warning in validation_result['warnings']:
        logging.warning(warning)
    
    # Handle errors
    if validation_result['errors']:
        logging.error("Environment validation failed:")
        for category, error_list in validation_result['errors'].items():
            for error in error_list:
                logging.error(f"  - {category}: {error}")
        
        if settings.is_production:
            sys.exit(1)


# Create application instance
app = create_app()


if __name__ == '__main__':
    # Setup logging
    setup_logging()
    
    # Validate environment
    validate_environment()
    
    # Log startup information
    logging.info(f"Starting Lane MCP in {settings.environment} mode")
    logging.info(f"Configuration: {settings.to_dict()}")
    
    # Run application
    try:
        if settings.is_production:
            # Production: Use gunicorn (this is just for direct execution)
            app.run(
                host=settings.server.host,
                port=settings.server.port,
                debug=False,
                threaded=True
            )
        else:
            # Development: Use Flask dev server
            app.run(
                host=settings.server.host,
                port=settings.server.port,
                debug=settings.server.debug,
                threaded=True
            )
    except KeyboardInterrupt:
        logging.info("Application stopped by user")
    except Exception as e:
        logging.error(f"Application startup failed: {str(e)}")
        sys.exit(1)
    finally:
        logging.info("Application shutdown complete")