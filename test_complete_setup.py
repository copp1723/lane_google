#!/usr/bin/env python3.11
"""
Complete setup test for Lane Google
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔍 Lane Google Setup Verification")
print("=" * 50)

# 1. Python Version
print("\n1️⃣ Python Version:")
import platform
print(f"   ✅ Python {platform.python_version()}")

# 2. Core Dependencies
print("\n2️⃣ Core Dependencies:")
try:
    import flask
    print("   ✅ Flask installed")
    import flask_jwt_extended
    print("   ✅ Flask-JWT-Extended installed")
    import psycopg2
    print("   ✅ PostgreSQL driver installed")
    import redis
    print("   ✅ Redis client installed")
except ImportError as e:
    print(f"   ❌ Missing dependency: {e}")

# 3. Database Connection
print("\n3️⃣ Database Connection:")
try:
    import psycopg2
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
    table_count = cur.fetchone()[0]
    print(f"   ✅ Connected to Render PostgreSQL")
    print(f"   ✅ {table_count} tables in database")
    cur.close()
    conn.close()
except Exception as e:
    print(f"   ❌ Database error: {e}")

# 4. Redis Connection
print("\n4️⃣ Redis Connection:")
try:
    import redis
    r = redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379'))
    r.ping()
    print("   ✅ Connected to Redis")
except Exception as e:
    print(f"   ⚠️  Redis not available: {e}")

# 5. Google Ads Configuration
print("\n5️⃣ Google Ads Configuration:")
configs = {
    'Client ID': os.environ.get('GOOGLE_ADS_CLIENT_ID', ''),
    'Client Secret': os.environ.get('GOOGLE_ADS_CLIENT_SECRET', ''),
    'Developer Token': os.environ.get('GOOGLE_ADS_DEVELOPER_TOKEN', ''),
    'Customer ID': os.environ.get('GOOGLE_ADS_LOGIN_CUSTOMER_ID', ''),
    'Refresh Token': os.environ.get('GOOGLE_ADS_REFRESH_TOKEN', '')
}

for key, value in configs.items():
    if value:
        if key == 'Refresh Token':
            status = "✅ SET" if value else "❌ NOT SET"
            print(f"   {status} {key}")
        else:
            print(f"   ✅ {key}: ...{value[-10:]}")
    else:
        print(f"   ❌ {key}: NOT SET")

# 6. Application Test
print("\n6️⃣ Application Import Test:")
try:
    from src.main import app
    print("   ✅ Application imports successfully")
    
    # Test a simple route
    with app.test_client() as client:
        response = client.get('/ping')
        if response.status_code == 200:
            print("   ✅ API health check passed")
        else:
            print(f"   ⚠️  API health check returned {response.status_code}")
except Exception as e:
    print(f"   ❌ Application error: {e}")

# Summary
print("\n" + "=" * 50)
print("📊 SUMMARY:")

if all([
    os.environ.get('DATABASE_URL'),
    os.environ.get('GOOGLE_ADS_CLIENT_ID'),
    os.environ.get('GOOGLE_ADS_DEVELOPER_TOKEN')
]):
    if os.environ.get('GOOGLE_ADS_REFRESH_TOKEN'):
        print("✅ Your setup is COMPLETE! Ready to launch.")
        print("\nRun: ./start_app.sh")
    else:
        print("⚠️  Almost ready! Just need to generate Google Ads refresh token.")
        print("\nNext step: python3.11 generate_refresh_token.py")
        print("See GOOGLE_ADS_TOKEN_SETUP.md for instructions")
else:
    print("❌ Setup incomplete. Check the errors above.")

print("=" * 50)