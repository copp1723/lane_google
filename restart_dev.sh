#\!/bin/bash

echo "🔄 Restarting Lane MCP Development Server..."
echo ""

# Kill any existing npm/node processes on port 5173
echo "📌 Stopping existing processes..."
lsof -ti :5173 | xargs kill -9 2>/dev/null || true
lsof -ti :5001 | xargs kill -9 2>/dev/null || true

# Clear Vite cache
echo "🧹 Clearing Vite cache..."
rm -rf node_modules/.vite 2>/dev/null || true

# Ensure dependencies are installed
echo "📦 Checking dependencies..."
if [ \! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start the development server
echo ""
echo "🚀 Starting development server..."
echo "📍 Frontend: http://localhost:5173"
echo "📍 Backend API: http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run the dev server
npm run dev
EOF < /dev/null