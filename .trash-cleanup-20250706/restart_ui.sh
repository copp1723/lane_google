#!/bin/bash

# Lane MCP UI Restart Script
echo "🚀 Restarting Lane MCP with Enhanced UI..."
echo ""

# Stop any running processes
echo "⏹️  Stopping any running development servers..."
pkill -f "vite"
pkill -f "npm run dev"

# Clear any build cache
echo "🧹 Clearing build cache..."
rm -rf node_modules/.vite
rm -rf dist

# Reinstall dependencies if needed
echo "📦 Checking dependencies..."
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start the development server
echo "🎨 Starting enhanced UI development server..."
echo "✨ Your beautiful Lane MCP interface will be available at:"
echo "   http://localhost:5174/"
echo ""
echo "🎯 Expected features:"
echo "   • Glass morphism design with blur effects"
echo "   • Animated gradient backgrounds"
echo "   • Professional chat interface with typing indicators"
echo "   • Smooth hover animations on cards"
echo "   • Modern tab navigation"
echo "   • Status badges with color coding"
echo ""
echo "🔄 Starting server..."

npm run dev
