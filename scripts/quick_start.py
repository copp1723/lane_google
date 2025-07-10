#!/usr/bin/env python3
"""
Quick Start Script for Lane Google Campaign Management
Initializes database and checks configuration
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking environment configuration...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    status = {
        'database': False,
        'google_ads': False,
        'ai_service': False,
        'flask': False
    }
    
    # Check Flask configuration
    secret_key = os.getenv('SECRET_KEY')
    jwt_secret = os.getenv('JWT_SECRET_KEY')
    if secret_key and jwt_secret and secret_key != 'dev-secret-key-change-in-production':
        status['flask'] = True
        print("✅ Flask configuration: Production ready")
    elif secret_key and jwt_secret:
        status['flask'] = True
        print("⚠️  Flask configuration: Development mode (change secrets for production)")
    else:
        print("❌ Flask configuration: Missing SECRET_KEY or JWT_SECRET_KEY")
    
    # Check database
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        status['database'] = True
        if 'sqlite' in db_url:
            print("✅ Database: SQLite configured (development)")
        else:
            print("✅ Database: External database configured")
    else:
        print("❌ Database: DATABASE_URL not configured")
    
    # Check Google Ads API
    google_ads_vars = [
        'GOOGLE_ADS_CLIENT_ID',
        'GOOGLE_ADS_CLIENT_SECRET', 
        'GOOGLE_ADS_REFRESH_TOKEN',
        'GOOGLE_ADS_DEVELOPER_TOKEN'
    ]
    
    google_ads_configured = all(
        os.getenv(var) and os.getenv(var) != f'your-{var.lower().replace("_", "-")}'
        for var in google_ads_vars
    )
    
    if google_ads_configured:
        status['google_ads'] = True
        print("✅ Google Ads API: Fully configured")
    elif any(os.getenv(var) for var in google_ads_vars):
        print("⚠️  Google Ads API: Partially configured (will use demo data)")
    else:
        print("⚠️  Google Ads API: Not configured (will use demo data)")
    
    # Check AI service
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if openrouter_key and openrouter_key != 'your-openrouter-api-key':
        status['ai_service'] = True
        print("✅ AI Service: OpenRouter configured")
    elif openai_key and openai_key != 'your-openai-api-key':
        status['ai_service'] = True
        print("✅ AI Service: OpenAI configured")
    else:
        print("⚠️  AI Service: Not configured (AI features limited)")
    
    return status

def initialize_database():
    """Initialize database with tables"""
    print("\n🗄️  Initializing database...")
    
    try:
        # Import Flask app
        from src.main import app, db
        
        with app.app_context():
            # Create database directory if it doesn't exist
            db_path = Path('src/database')
            db_path.mkdir(exist_ok=True)
            
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Check if we need to create admin user
            from src.models.user import User, UserRole
            admin_user = User.query.filter_by(username='admin').first()
            
            if not admin_user:
                # Create default admin user
                admin_user = User(
                    username='admin',
                    email='admin@example.com',
                    password='admin123',  # Change this!
                    first_name='Admin',
                    last_name='User',
                    role=UserRole.ADMIN
                )
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Default admin user created (username: admin, password: admin123)")
                print("⚠️  IMPORTANT: Change the admin password in production!")
            else:
                print("✅ Admin user already exists")
                
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        return False
    
    return True

def test_api_endpoints():
    """Test if key API endpoints are working"""
    print("\n🧪 Testing API endpoints...")
    
    try:
        from src.main import app
        
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/api/health')
            if response.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print(f"⚠️  Health endpoint returned {response.status_code}")
            
            # Test keyword research endpoint (should require auth)
            response = client.post('/api/keywords/research', 
                                 json={'seed_keyword': 'test'})
            if response.status_code == 401:
                print("✅ Keyword research endpoint secured (requires auth)")
            elif response.status_code == 200:
                print("⚠️  Keyword research endpoint working (no auth required)")
            else:
                print(f"⚠️  Keyword research endpoint returned {response.status_code}")
                
    except Exception as e:
        print(f"❌ API testing failed: {str(e)}")
        return False
    
    return True

def main():
    """Main setup function"""
    print("🚀 Lane Google Campaign Management - Quick Start\n")
    
    # Check environment
    status = check_environment()
    
    # Initialize database
    if status['database']:
        db_success = initialize_database()
    else:
        print("❌ Skipping database initialization due to configuration issues")
        db_success = False
    
    # Test APIs
    if status['flask'] and db_success:
        test_api_endpoints()
    
    print("\n" + "="*60)
    print("📋 SETUP SUMMARY")
    print("="*60)
    
    if status['flask'] and status['database']:
        print("✅ Core application ready")
        print("\n🎯 NEXT STEPS:")
        print("1. Run the application:")
        print("   python src/main.py")
        print("\n2. Open your browser to:")
        print("   http://localhost:5000")
        print("\n3. Login with:")
        print("   Username: admin")
        print("   Password: admin123")
        
        if not status['google_ads']:
            print("\n4. To enable real Google Ads data:")
            print("   - Get API credentials from Google Ads API")
            print("   - Update .env file with real credentials")
            print("   - See PRODUCTION_SETUP_CHECKLIST.md for details")
        
        if not status['ai_service']:
            print("\n5. To enable AI features:")
            print("   - Get API key from OpenRouter or OpenAI")
            print("   - Update OPENROUTER_API_KEY or OPENAI_API_KEY in .env")
    
    else:
        print("❌ Setup incomplete - check configuration issues above")
        print("\n📚 For help, see:")
        print("- PRODUCTION_SETUP_CHECKLIST.md")
        print("- .env.example for configuration template")

if __name__ == '__main__':
    main()