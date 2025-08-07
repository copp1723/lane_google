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

from flask import Flask, send_from_directory, g, request, send_file
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
    from src.api.campaign_analytics_api import campaign_analytics_bp
    from src.api.keyword_analytics_api import keyword_analytics_bp
    from src.api.campaigns_api import campaigns_api_bp
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
                static_url_path='',
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

    # Create tables if they don't exist (for production deployment)
    with app.app_context():
        try:
            # Import all models to ensure they're registered
            from src.models.user import User
            from src.models.account import Account
            from src.models.campaign import Campaign
            from src.models.conversation import Conversation, ConversationMessage

            # Create all tables
            db.create_all()
            logging.info("Database tables created/verified successfully")

        except Exception as e:
            logging.warning(f"Database table creation warning: {str(e)}")
            # Don't fail the app if tables already exist

    # Initialize Flask-Session (if Redis is available)
    try:
        from src.config.redis_config import get_flask_session_config
        session_config = get_flask_session_config()
        app.config.update(session_config)
        Session(app)
        logging.info("Flask-Session initialized with Redis backend")
    except Exception as e:
        logging.warning(f"Could not initialize Flask-Session: {e}")
        # Fall back to filesystem sessions
        app.config['SESSION_TYPE'] = 'filesystem'
        Session(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Initialize services
    initialize_services(app)
    
    # Register frontend routes (must be last!)
    register_frontend_routes(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register request hooks
    register_request_hooks(app)
    
    return app


def register_blueprints(app: Flask):
    """Register all API blueprints"""
    # Try to import and register blueprints
    blueprints = []
    
    # Core blueprints (always try to register)
    try:
        from src.routes.user import user_bp
        blueprints.append(('user_bp', user_bp, '/api'))
    except ImportError:
        logging.warning("user_bp not available")
    
    # Auth API blueprint
    try:
        from src.api.auth_api import auth_bp
        blueprints.append(('auth_bp', auth_bp, '/api/auth'))
    except ImportError:
        logging.warning("auth_bp not available")
    
    try:
        from src.routes.ai_agent import ai_agent_bp
        blueprints.append(('ai_agent_bp', ai_agent_bp, '/api'))
    except ImportError:
        logging.warning("ai_agent_bp not available")
    
    try:
        from src.routes.google_ads import google_ads_bp
        blueprints.append(('google_ads_bp', google_ads_bp, '/api'))
    except ImportError:
        logging.warning("google_ads_bp not available")
    
    try:
        from src.routes.campaigns import campaigns_bp
        blueprints.append(('campaigns_bp', campaigns_bp, '/api'))
    except ImportError:
        logging.warning("campaigns_bp not available")
    
    try:
        from src.routes.health import health_bp
        blueprints.append(('health_bp', health_bp, ''))
    except ImportError:
        logging.warning("health_bp not available")
    
    # API blueprints (optional)
    try:
        from src.api.dashboard_apis import dashboard_bp
        blueprints.append(('dashboard_bp', dashboard_bp, '/api'))
    except ImportError:
        logging.warning("dashboard_bp not available")
    
    try:
        from src.api.campaign_analytics_api import campaign_analytics_bp
        blueprints.append(('campaign_analytics_bp', campaign_analytics_bp, '/api'))
    except ImportError:
        logging.warning("campaign_analytics_bp not available")
    
    try:
        from src.api.keyword_analytics_api import keyword_analytics_bp
        blueprints.append(('keyword_analytics_bp', keyword_analytics_bp, '/api'))
    except ImportError:
        logging.warning("keyword_analytics_bp not available")
    
    try:
        from src.api.campaigns_api import campaigns_api_bp
        blueprints.append(('campaigns_api_bp', campaigns_api_bp, '/api'))
    except ImportError:
        logging.warning("campaigns_api_bp not available")
    
    # Register all available blueprints
    for name, blueprint, url_prefix in blueprints:
        try:
            app.register_blueprint(blueprint, url_prefix=url_prefix)
            logging.info(f"Registered blueprint: {name}")
        except Exception as e:
            logging.warning(f"Could not register blueprint {name}: {e}")


def initialize_services(app: Flask):
    """Initialize application services"""
    
    # Initialize Google Ads service
    try:
        from src.services.real_google_ads import real_google_ads_service
        if real_google_ads_service:
            real_google_ads_service.test_connection()
            logging.info("Google Ads service initialized successfully")
    except Exception as e:
        logging.warning(f"Could not initialize Google Ads service: {e}")
    
    # Initialize Campaign Orchestrator
    try:
        from src.services.campaign_orchestrator import CampaignOrchestrator
        if CampaignOrchestrator:
            logging.info("Campaign Orchestrator service available")
    except Exception as e:
        logging.warning(f"Could not initialize Campaign Orchestrator: {e}")


def register_error_handlers(app: Flask):
    """Register application error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        # Return JSON for API routes, HTML for others
        if request.path.startswith('/api'):
            return {'error': 'Not found', 'message': 'Resource not found'}, 404
        else:
            # Serve index.html for frontend routes
            return serve_frontend('')
    
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
        if not request.path.startswith('/static') and not request.path.startswith('/assets'):
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
        
        # Add cache headers for static assets
        if request.path.startswith('/assets') or request.path.endswith(('.js', '.css', '.png', '.jpg', '.svg')):
            response.headers['Cache-Control'] = 'public, max-age=31536000'
        
        return response


def serve_frontend(path):
    """Serve React frontend application"""
    static_folder = os.path.join(os.path.dirname(__file__), 'static')
    
    # Always serve index.html for frontend routes
    index_path = os.path.join(static_folder, 'index.html')
    if os.path.exists(index_path):
        return send_file(index_path)
    else:
        return "Frontend not built. Run 'npm run build' first.", 404


def register_frontend_routes(app: Flask):
    """Register routes for serving frontend application"""
    
    # Serve static assets (JS, CSS, images, etc.)
    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        static_folder = os.path.join(os.path.dirname(__file__), 'static', 'assets')
        return send_from_directory(static_folder, filename)
    
    # Serve other static files
    @app.route('/<path:filename>')
    def serve_static_file(filename):
        # List of static file extensions
        static_extensions = ('.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot')
        
        if filename.endswith(static_extensions) or '.' in filename.split('/')[-1]:
            static_folder = os.path.join(os.path.dirname(__file__), 'static')
            if os.path.exists(os.path.join(static_folder, filename)):
                return send_from_directory(static_folder, filename)
        
        # For all other routes, serve the React app
        return serve_frontend(filename)
    
    # Catch-all route for React Router
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        # Don't catch API routes
        if path.startswith('api/'):
            return {'error': 'Not found'}, 404
        
        # Serve the React app
        return serve_frontend(path)


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
        
        # Only exit for critical security errors, not missing API keys
        critical_errors = [error for error_list in validation_result['errors'].values() for error in error_list 
                          if 'SECRET_KEY' in error or 'JWT_SECRET_KEY' in error]
        
        if settings.is_production and critical_errors:
            logging.error("Critical security configuration missing. Exiting.")
            sys.exit(1)
        else:
            logging.warning("Non-critical configuration errors detected. Continuing with limited functionality.")


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