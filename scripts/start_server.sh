#!/bin/bash

echo "🚀 Starting Lane MCP Enhanced UI..."
echo "==================================="
echo ""

# Navigate to the project directory
cd /Users/copp1723/Desktop/lane_google

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Not in the correct project directory"
    echo "Please run this from /Users/copp1723/Desktop/lane_google"
    exit 1
fi

echo "📁 Current directory: $(pwd)"
echo "📦 Package manager detected: $(grep -o 'pnpm\|npm\|yarn' package.json | head -1)"

# Kill any existing processes on port 5174
echo "🛑 Stopping any running servers on port 5174..."
lsof -ti:5174 | xargs kill -9 2>/dev/null || true
sleep 2

# Clear cache
echo "🧹 Clearing development cache..."
rm -rf node_modules/.vite 2>/dev/null || true
rm -rf node_modules/.cache 2>/dev/null || true
rm -rf dist 2>/dev/null || true

# Check for node_modules
if [ ! -d "node_modules" ]; then
    echo "📥 Installing dependencies..."
    if command -v pnpm &> /dev/null; then
        echo "Using pnpm..."
        pnpm install
    elif command -v npm &> /dev/null; then
        echo "Using npm..."
        npm install
    else
        echo "❌ Neither npm nor pnpm found!"
        exit 1
    fi
else
    echo "✅ Dependencies already installed"
fi

echo ""
echo "🎨 Starting development server..."
echo "⏳ This may take a moment to compile..."
echo ""

# Try to start with the available package manager
if command -v pnpm &> /dev/null; then
    echo "🔧 Using pnpm to start server..."
    pnpm run dev
elif command -v npm &> /dev/null; then
    echo "🔧 Using npm to start server..."
    npm run dev
else
    echo "❌ No package manager available!"
    exit 1
fi
