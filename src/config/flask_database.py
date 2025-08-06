"""
Flask-SQLAlchemy database configuration for Lane Google.
Provides Flask-compatible database setup.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
import os

from .settings import settings

logger = logging.getLogger(__name__)

# Initialize Flask-SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()


def init_database(app):
    """
    Initialize Flask-SQLAlchemy with app context.
    
    Args:
        app: Flask application instance
    """
    try:
        # Configure database URI
        app.config['SQLALCHEMY_DATABASE_URI'] = settings.get_database_url()
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
        }
        
        # Initialize extensions
        db.init_app(app)
        migrate.init_app(app, db)
        
        # Create tables in app context
        with app.app_context():
            # Import all models to ensure they're registered
            try:
                from ..models.user import User
                from ..models.account import Account  
                from ..models.campaign import Campaign
                from ..models.analytics import Analytics
                from ..models.conversation import Conversation
                logger.info("Models imported successfully")
            except ImportError as e:
                logger.warning(f"Some models could not be imported: {e}")
            
            # Create all tables
            db.create_all()
            logger.info("Database tables created successfully")
        
        return db, migrate
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_db_session():
    """
    Get database session for manual operations.
    
    Returns:
        SQLAlchemy session
    """
    return db.session


# Async compatibility function  
async def init_db():
    """
    Async wrapper for database initialization.
    Used for compatibility with FastAPI-style initialization.
    """
    # This will be called from Flask context, so no actual async needed
    try:
        db.create_all()
        logger.info("Database initialized via async wrapper")
    except Exception as e:
        logger.error(f"Async database initialization failed: {e}")
        raise