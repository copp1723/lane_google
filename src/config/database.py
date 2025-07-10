"""
Database initialization and configuration
Enterprise-grade database setup with proper connection management
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging

logger = logging.getLogger(__name__)

# Global database instance
db = SQLAlchemy()
migrate = Migrate()

def init_database(app):
    """Initialize database with Flask app"""
    
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Initialize Flask-Migrate
    migrate.init_app(app, db)
    
    # Create tables in application context
    with app.app_context():
        try:
            # Import all models to ensure they're registered
            from src.models.user import User
            from src.models.account import Account
            from src.models.campaign import Campaign
            from src.models.conversation import Conversation, ConversationMessage
            from src.utils.audit_log import AuditLog
            
            # Create all tables
            db.create_all()
            logger.info("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            raise
    
    return db

