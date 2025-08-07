#!/usr/bin/env python3
"""
Create database tables for Lane Google using SQLAlchemy
This will create all tables defined in the models
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

# Import Flask app and database
from src.main import app
from src.config.flask_database import db

# Import all models to ensure they're registered
try:
    from src.models.user import User, UserRole, UserStatus
    from src.models.campaign import Campaign
    from src.models.account import Account
    from src.models.analytics_snapshot import AnalyticsSnapshot
    from src.models.budget_alert import BudgetAlertModel as BudgetAlert
    from src.models.conversation import Conversation
    from src.models.approval_request import ApprovalRequestModel as ApprovalRequest
    print("✅ All models imported successfully")
except Exception as e:
    print(f"⚠️  Some models could not be imported: {e}")
    print("Continuing with available models...")

def create_all_tables():
    """Create all database tables"""
    with app.app_context():
        try:
            print("Creating database tables...")
            
            # Create all tables
            db.create_all()
            
            print("✅ All tables created successfully!")
            
            # List created tables
            from sqlalchemy import text
            result = db.session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"))
            tables = result.fetchall()
            
            print(f"\nCreated {len(tables)} tables:")
            for table in tables:
                print(f"  - {table[0]}")
                
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False
    
    return True

if __name__ == "__main__":
    success = create_all_tables()
    sys.exit(0 if success else 1)