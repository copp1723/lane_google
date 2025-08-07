#!/usr/bin/env python3
"""
Quick script to create demo user for immediate login
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from src.config.database import db
from src.models.user import User, UserRole, UserStatus
from src.main_production import create_app

def create_demo_user():
    """Create demo user for immediate login"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create tables if they don't exist
            db.create_all()
            
            # Check if demo user exists
            demo_user = User.query.filter_by(email='demo@lane-mcp.com').first()
            
            if not demo_user:
                # Create demo user
                demo_user = User(
                    email='demo@lane-mcp.com',
                    username='demo',
                    password='demo123456',
                    first_name='Demo',
                    last_name='User',
                    role=UserRole.ADMIN,
                    status=UserStatus.ACTIVE
                )
                db.session.add(demo_user)
                db.session.commit()
                print("✅ Demo user created successfully!")
            else:
                print("✅ Demo user already exists")
            
            # Also create admin user
            admin_user = User.query.filter_by(email='admin@lane-ai.com').first()
            if not admin_user:
                admin_user = User(
                    email='admin@lane-ai.com',
                    username='admin',
                    password='LaneAI2025!',
                    first_name='Admin',
                    last_name='User',
                    role=UserRole.ADMIN,
                    status=UserStatus.ACTIVE
                )
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Admin user created successfully!")
            else:
                print("✅ Admin user already exists")
                
            print("\n🎉 LOGIN CREDENTIALS:")
            print("Email: demo@lane-mcp.com")
            print("Password: demo123456")
            print("\nOR")
            print("Email: admin@lane-ai.com") 
            print("Password: LaneAI2025!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    return True

if __name__ == '__main__':
    create_demo_user()
