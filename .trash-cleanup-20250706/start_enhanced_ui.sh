#!/bin/bash

echo "🎨 Lane MCP Enhanced UI Restart"
echo "================================"
echo ""

# Navigate to project directory
cd /Users/copp1723/Desktop/lane_google

# Stop any running processes
echo "⏹️  Stopping current processes..."
pkill -f "vite" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true
sleep 2

# Clear cache
echo "🧹 Clearing cache..."
rm -rf node_modules/.vite 2>/dev/null || true
rm -rf dist 2>/dev/null || true

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo ""
echo "✨ Starting Enhanced Lane MCP UI..."
echo "🎯 Expected features:"
echo "   • Modern glass morphism design"
echo "   • Animated gradient backgrounds"  
echo "   • Professional AI chat interface"
echo "   • Smooth hover animations"
echo "   • Status indicators and badges"
echo ""
echo "🌐 Opening at: http://localhost:5174/"
echo ""
echo "🔧 If you see basic styling instead of enhanced UI:"
echo "   1. Hard refresh browser (Cmd+Shift+R / Ctrl+Shift+R)"
echo "   2. Check browser console for errors"
echo "   3. Ensure Tailwind CSS is compiling"
echo ""

# Start development server
npm run dev
