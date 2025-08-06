#!/bin/bash

echo "🚀 Starting Lane Google Application"
echo "=================================="

# Check if we have the required Python packages
echo "📦 Checking Python dependencies..."
python3.11 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Flask not installed. Installing core dependencies..."
    python3.11 -m pip install Flask Flask-SQLAlchemy Flask-CORS PyJWT psycopg2-binary python-dotenv flask-jwt-extended
fi

# Start the backend
echo ""
echo "🔧 Starting backend server..."
echo "Note: Some packages may be missing due to Python 3.13 compatibility issues."
echo "The app will run with available features."
echo ""

# Export environment variables
export FLASK_APP=src/main.py
export FLASK_ENV=development
export FLASK_RUN_PORT=5001

# Start Flask in one terminal
echo "Starting Flask backend on http://localhost:5001"
python3.11 -m src.main &
BACKEND_PID=$!

# Give backend time to start
sleep 3

# Start frontend in another process
echo ""
echo "🎨 Starting frontend development server..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Application started!"
echo "   Backend:  http://localhost:5001"
echo "   Frontend: http://localhost:5174"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

# Keep script running
wait