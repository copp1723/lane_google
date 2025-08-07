#!/usr/bin/env python3
"""
Quick test script to verify the application is working correctly
"""

import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all major imports work"""
    print("Testing imports...")
    try:
        from src.main import app
        print("✅ Main app import successful")
        
        from src.config.flask_database import db
        print("✅ Database import successful")
        
        from src.auth.authentication import AuthManager
        print("✅ Authentication import successful")
        
        from src.models.user import User
        print("✅ User model import successful")
        
        from src.models.campaign import Campaign
        print("✅ Campaign model import successful")
        
        print("\n✅ All imports successful!\n")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_app_creation():
    """Test that the Flask app can be created"""
    print("Testing app creation...")
    try:
        from src.main import app
        
        # Test basic app properties
        assert app is not None
        assert app.name == 'src.main'
        
        # List registered blueprints
        print("\nRegistered blueprints:")
        for name, blueprint in app.blueprints.items():
            print(f"  - {name}: {blueprint.url_prefix}")
        
        print("\n✅ App creation successful!\n")
        return True
    except Exception as e:
        print(f"❌ App creation error: {e}")
        return False

def test_endpoints():
    """Test that key endpoints exist"""
    print("Testing endpoints...")
    try:
        from src.main import app
        
        # Get all registered routes
        routes = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                routes.append({
                    'endpoint': rule.endpoint,
                    'methods': list(rule.methods - {'HEAD', 'OPTIONS'}),
                    'path': rule.rule
                })
        
        # Check for key endpoints
        key_endpoints = [
            '/ping',
            '/health',
            '/api/auth/login',
            '/api/auth/register',
            '/api/campaigns',
            '/api/ai-agent/chat'
        ]
        
        print("\nKey endpoints:")
        for endpoint in key_endpoints:
            found = any(r['path'] == endpoint for r in routes)
            status = "✅" if found else "❌"
            print(f"  {status} {endpoint}")
        
        # Show all available endpoints
        print("\nAll available endpoints:")
        for route in sorted(routes, key=lambda x: x['path']):
            methods = ', '.join(route['methods'])
            print(f"  - {route['path']} [{methods}]")
        
        print("\n✅ Endpoint test complete!\n")
        return True
    except Exception as e:
        print(f"❌ Endpoint test error: {e}")
        return False

def test_database():
    """Test database connection"""
    print("Testing database connection...")
    try:
        from src.main import app
        from src.config.flask_database import db
        
        with app.app_context():
            # Try to connect to database
            db.engine.execute('SELECT 1')
            print("✅ Database connection successful")
            
            # List tables
            tables = db.engine.table_names()
            print(f"\nDatabase tables ({len(tables)}):")
            for table in tables:
                print(f"  - {table}")
            
            if not tables:
                print("\n⚠️  No tables found. Run migrations to create tables.")
            
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        print("⚠️  Make sure PostgreSQL is running and database exists")
        return False

def test_environment():
    """Test environment configuration"""
    print("Testing environment configuration...")
    try:
        from src.config.settings import settings
        
        print(f"\nEnvironment: {settings.environment}")
        print(f"Debug mode: {settings.server.debug}")
        print(f"Server: {settings.server.host}:{settings.server.port}")
        
        # Check for critical environment variables
        env_vars = {
            'GOOGLE_ADS_CLIENT_ID': os.environ.get('GOOGLE_ADS_CLIENT_ID', 'Not set'),
            'GOOGLE_ADS_DEVELOPER_TOKEN': os.environ.get('GOOGLE_ADS_DEVELOPER_TOKEN', 'Not set'),
            'GOOGLE_ADS_REFRESH_TOKEN': os.environ.get('GOOGLE_ADS_REFRESH_TOKEN', 'Not set'),
            'DATABASE_URL': os.environ.get('DATABASE_URL', 'Not set'),
            'OPENROUTER_API_KEY': os.environ.get('OPENROUTER_API_KEY', 'Not set')
        }
        
        print("\nEnvironment variables:")
        for var, value in env_vars.items():
            status = "✅" if value != 'Not set' else "❌"
            display_value = '***' + value[-4:] if value != 'Not set' and len(value) > 4 else value
            print(f"  {status} {var}: {display_value}")
        
        return True
    except Exception as e:
        print(f"❌ Environment test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Lane Google Application Test Suite\n")
    print("=" * 50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    tests = [
        test_imports,
        test_app_creation,
        test_endpoints,
        test_environment,
        test_database
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        print("=" * 50)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n🎯 Test Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed! The application is ready to run.")
        print("\nTo start the application:")
        print("  1. Make sure PostgreSQL is running")
        print("  2. Run: python src/main.py")
        print("  3. In another terminal: npm run dev")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        
    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())