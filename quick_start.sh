#!/bin/bash

echo "🚀 Lane Google Quick Start"
echo "========================="
echo ""
echo "📦 Installing minimal required packages..."
pip3 install Flask Flask-SQLAlchemy Flask-CORS PyJWT psycopg2-binary python-dotenv werkzeug==2.3.6 flask-jwt-extended redis 2>/dev/null

echo ""
echo "🌐 Your app is connected to:"
echo "   Database: Render PostgreSQL (Production)"
echo "   Redis: Render Redis (Production)"
echo ""
echo "⚠️  Note: Some features may be limited due to:"
echo "   - Python 3.13 compatibility issues"
echo "   - Missing Google Ads refresh token"
echo "   - Database schema issues (will create basic tables)"
echo ""
echo "Starting servers..."
echo ""

# Start the app using the startup script
./start_app.sh