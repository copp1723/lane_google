#!/usr/bin/env python3
"""
Test script to verify database schema creation without foreign key constraint errors
This script validates that all models can be created successfully with the new UUID-based schema
"""

import sys
import os
import traceback
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

# Import database configuration
from src.config.database import Base, get_engine

def test_model_imports():
    """Test that all models can be imported without errors"""
    print("=== Testing Model Imports ===")
    try:
        from src.models.user import User, UserRole, UserStatus
        print("✅ User models imported successfully")
        
        from src.models.account import Account, AccountUser, AccountRole
        print("✅ Account models imported successfully")
        
        from src.models.campaign import Campaign, AdGroup, Ad, CampaignStatus, CampaignType, BiddingStrategy
        print("✅ Campaign models imported successfully")
        
        from src.models.analytics_snapshot import AnalyticsSnapshot
        print("✅ AnalyticsSnapshot model imported successfully")
        
        from src.models.approval_request import ApprovalRequestModel
        print("✅ ApprovalRequest model imported successfully")
        
        from src.models.budget_alert import BudgetAlertModel
        print("✅ BudgetAlert model imported successfully")
        
        from src.models.conversation import Conversation, ConversationMessage
        print("✅ Conversation models imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing models: {e}")
        traceback.print_exc()
        return False

def test_schema_creation():
    """Test creating database schema"""
    print("\n=== Testing Schema Creation ===")
    
    try:
        # Create a test database URL (using SQLite for testing)
        test_db_url = "sqlite:///test_schema.db"
        
        # Create engine
        engine = create_engine(test_db_url, echo=True)
        
        # Import all models to ensure they're registered with Base.metadata
        from src.models.user import User
        from src.models.account import Account, AccountUser
        from src.models.campaign import Campaign, AdGroup, Ad
        from src.models.analytics_snapshot import AnalyticsSnapshot
        from src.models.approval_request import ApprovalRequestModel
        from src.models.budget_alert import BudgetAlertModel
        from src.models.conversation import Conversation, ConversationMessage
        
        print(f"Found {len(Base.metadata.tables)} tables to create:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")
        
        # Create all tables
        print("\nCreating tables...")
        Base.metadata.create_all(engine)
        print("✅ All tables created successfully!")
        
        # Test foreign key relationships by inspecting metadata
        print("\n=== Checking Foreign Key Relationships ===")
        for table_name, table in Base.metadata.tables.items():
            foreign_keys = []
            for column in table.columns:
                if column.foreign_keys:
                    for fk in column.foreign_keys:
                        foreign_keys.append(f"{column.name} -> {fk.target_fullname}")
            
            if foreign_keys:
                print(f"Table '{table_name}' foreign keys:")
                for fk in foreign_keys:
                    print(f"  - {fk}")
        
        # Clean up test database
        os.remove("test_schema.db") if os.path.exists("test_schema.db") else None
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        traceback.print_exc()
        return False

def test_model_instantiation():
    """Test creating model instances to verify UUID generation"""
    print("\n=== Testing Model Instantiation ===")
    
    try:
        from src.models.user import User
        from src.models.account import Account, AccountUser  
        from src.models.campaign import Campaign
        
        # Test User creation
        user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            hashed_password="hashed_password"
        )
        print(f"✅ User created with ID: {user.id} (type: {type(user.id)})")
        
        # Test Account creation
        account = Account(
            name="Test Account",
            google_customer_id="1234567890"
        )
        print(f"✅ Account created with ID: {account.id} (type: {type(account.id)})")
        
        # Test Campaign creation
        from datetime import datetime
        campaign = Campaign(
            name="Test Campaign",
            daily_budget=100.0,
            start_date=datetime(2024, 1, 1),
            account_id=account.id,
            created_by_id=user.id
        )
        print(f"✅ Campaign created with ID: {campaign.id} (type: {type(campaign.id)})")
        print(f"   - account_id: {campaign.account_id} (type: {type(campaign.account_id)})")
        print(f"   - created_by_id: {campaign.created_by_id} (type: {type(campaign.created_by_id)})")
        
        # Test AccountUser creation
        account_user = AccountUser(
            account_id=account.id,
            user_id=user.id
        )
        print(f"✅ AccountUser created with ID: {account_user.id} (type: {type(account_user.id)})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating model instances: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🔍 Testing Lane Google Database Schema Migration")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Model Imports
    if test_model_imports():
        tests_passed += 1
    
    # Test 2: Schema Creation
    if test_schema_creation():
        tests_passed += 1
    
    # Test 3: Model Instantiation
    if test_model_instantiation():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"🏁 Test Summary: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Schema migration is successful.")
        return True
    else:
        print("❌ Some tests failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)