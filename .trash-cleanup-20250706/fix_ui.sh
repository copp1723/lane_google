#!/bin/bash

echo "🎨 Lane MCP UI Fix Script"
echo "========================="
echo ""

# Navigate to the project directory
cd /Users/copp1723/Desktop/lane_google

echo "📁 Working directory: $(pwd)"
echo ""

# Step 1: Kill any existing processes
echo "🛑 Step 1: Stopping any running servers..."
pkill -f "vite" 2>/dev/null || true
lsof -ti:5174 | xargs kill -9 2>/dev/null || true
sleep 2
echo "✅ Servers stopped"
echo ""

# Step 2: Clear ALL caches and build artifacts
echo "🧹 Step 2: Clearing all caches and build artifacts..."
rm -rf node_modules/.vite 2>/dev/null || true
rm -rf node_modules/.cache 2>/dev/null || true
rm -rf dist 2>/dev/null || true
rm -rf .next 2>/dev/null || true
rm -rf .turbo 2>/dev/null || true
rm -rf .parcel-cache 2>/dev/null || true

# Clear browser cache hint
echo "💡 TIP: Clear your browser cache (Cmd+Shift+R) when the server starts!"
echo ""

# Step 3: Reinstall dependencies (clean install)
echo "📦 Step 3: Performing clean dependency install..."
if command -v pnpm &> /dev/null; then
    echo "Using pnpm..."
    pnpm store prune
    rm -rf node_modules
    pnpm install
elif command -v npm &> /dev/null; then
    echo "Using npm..."
    npm cache clean --force
    rm -rf node_modules package-lock.json
    npm install
else
    echo "❌ No package manager found!"
    exit 1
fi
echo "✅ Dependencies installed"
echo ""

# Step 4: Verify critical files
echo "🔍 Step 4: Verifying critical files..."
if [ -f "src/App.jsx" ] && [ -f "src/App.css" ] && [ -f "src/index.css" ]; then
    echo "✅ All UI files present"
else
    echo "❌ Missing critical UI files!"
    exit 1
fi
echo ""

# Step 5: Start the development server
echo "🚀 Step 5: Starting fresh development server..."
echo "==================================="
echo "🌟 IMPORTANT STEPS:"
echo "1. Wait for the server to fully start"
echo "2. Open http://localhost:5174 in your browser"
echo "3. Press Cmd+Shift+R to clear browser cache"
echo "4. You should see the beautiful enhanced UI!"
echo "==================================="
echo ""

# Start the server
if command -v pnpm &> /dev/null; then
    VITE_CJS_TRACE=true pnpm run dev --force
elif command -v npm &> /dev/null; then
    VITE_CJS_TRACE=true npm run dev -- --force
fi
