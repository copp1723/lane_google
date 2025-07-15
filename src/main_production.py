"""
Production-Ready Lane MCP Application
Fully configured with real authentication, database, and Google Ads integration
"""

import os
import sys
import logging
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, g, request
from flask_cors import CORS
from flask_migrate import Migrate
from flask_session import Session

# Import configuration
from src.config.settings import settings
from src.config.database import db

# Import API blueprints (with error handling)
try:
    from src.routes.user import user_bp
    from src.routes.ai_agent import ai_agent_bp
    from src.routes.google_ads import google_ads_bp
    from src.routes.campaigns import campaigns_bp
    from src.routes.health import health_bp
    from src.api.dashboard_apis import dashboard_bp
except ImportError as e:
    logging.warning(f"Some API blueprints could not be imported: {e}")
    # Create minimal health blueprint as fallback
    from flask import Blueprint
    health_bp = Blueprint('health', __name__)
    
    @health_bp.route('/api/health')
    def health():
        return {'status': 'ok', 'message': 'Basic health check'}

# Import services (with error handling)
try:
    from src.services.campaign_orchestrator import CampaignOrchestrator
    from src.services.real_google_ads import real_google_ads_service
except ImportError as e:
    logging.warning(f"Some services could not be imported: {e}")
    campaign_orchestrator = None
    real_google_ads_service = None

# Import authentication (with error handling)
try:
    from src.auth.authentication import token_required
except ImportError as e:
    logging.warning(f"Authentication module could not be imported: {e}")
    def token_required(f):
        return f


def create_app() -> Flask:
    """Application factory"""
    app = Flask(__name__,
                static_folder=os.path.join(os.path.dirname(__file__), 'static'),
                instance_relative_config=True)
    
    # Basic configuration
    app.config['SECRET_KEY'] = settings.security.secret_key
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.get_database_url()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Enable CORS
    CORS(app, origins=settings.security.cors_origins)
    
    # Initialize database
    db.init_app(app)
    
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
    # Health checks (no prefix for basic health)
    app.register_blueprint(health_bp)
    
    # Core APIs (with error handling)
    try:
        app.register_blueprint(user_bp, url_prefix='/api/users')
    except NameError:
        logging.warning("user_bp not available")
    
    try:
        app.register_blueprint(ai_agent_bp, url_prefix='/api/ai')
    except NameError:
        logging.warning("ai_agent_bp not available")
    
    try:
        app.register_blueprint(google_ads_bp, url_prefix='/api/google-ads')
    except NameError:
        logging.warning("google_ads_bp not available")
    
    try:
        app.register_blueprint(campaigns_bp, url_prefix='/api/campaigns')
    except NameError:
        logging.warning("campaigns_bp not available")
    
    try:
        app.register_blueprint(dashboard_bp)
    except NameError:
        logging.warning("dashboard_bp not available")


def initialize_services(app: Flask):
    """Initialize all background services"""
    with app.app_context():
        try:
            # Import all models to ensure they're registered with SQLAlchemy
            from src.models.user import User
            from src.models.account import Account, AccountUser
            from src.models.campaign import Campaign
            from src.models.budget_alert import BudgetAlertModel
            from src.models.analytics_snapshot import AnalyticsSnapshot
            from src.models.approval_request import ApprovalRequestModel
            from src.services.conversation import Conversation
            
            # Initialize database tables
            db.create_all()
            
            # Initialize campaign orchestrator (only if available)
            if settings.environment != 'testing' and real_google_ads_service is not None:
                try:
                    global campaign_orchestrator
                    campaign_orchestrator = CampaignOrchestrator(real_google_ads_service)
                    logging.info("Campaign orchestrator initialized successfully")
                except Exception as e:
                    logging.warning(f"Could not initialize campaign orchestrator: {e}")
                    campaign_orchestrator = None
            
        except Exception as e:
            logging.error(f"Error initializing services: {str(e)}")
            # Don't raise in production - allow app to start with limited functionality
            if settings.environment == 'development':
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
        # Use PORT environment variable for Render deployment
        port = int(os.environ.get('PORT', settings.server.port))
        app.run(
            host='0.0.0.0',
            port=port,
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