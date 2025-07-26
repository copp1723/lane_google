#!/bin/bash

echo "🎨 Lane MCP - Quick Debug & Fix"
echo "==============================="
echo ""

cd /Users/copp1723/Desktop/lane_google

# Quick diagnostics
echo "📋 Running diagnostics..."
echo ""

# Check if enhanced UI files exist
echo "Checking enhanced UI files:"
if [ -f "src/App.jsx" ]; then
    echo "✅ App.jsx exists ($(wc -l < src/App.jsx) lines)"
    grep -q "bg-gradient-to-br from-slate-50" src/App.jsx && echo "✅ Enhanced gradient backgrounds found" || echo "❌ Missing gradient backgrounds"
    grep -q "animate-pulse" src/App.jsx && echo "✅ Animations found" || echo "❌ Missing animations"
    grep -q "backdrop-blur-lg" src/App.jsx && echo "✅ Glass morphism effects found" || echo "❌ Missing glass effects"
else
    echo "❌ App.jsx missing!"
fi

if [ -f "src/App.css" ]; then
    echo "✅ App.css exists ($(wc -l < src/App.css) lines)"
else
    echo "❌ App.css missing!"
fi

if [ -f "src/index.css" ]; then
    echo "✅ index.css exists ($(wc -l < src/index.css) lines)"
else
    echo "❌ index.css missing!"
fi

echo ""
echo "Package manager check:"
if command -v pnpm &> /dev/null; then
    echo "✅ pnpm is available"
    PACKAGE_MANAGER="pnpm"
elif command -v npm &> /dev/null; then
    echo "✅ npm is available"
    PACKAGE_MANAGER="npm"
else
    echo "❌ No package manager found!"
    exit 1
fi

echo ""
echo "Port 5174 status:"
if lsof -Pi :5174 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 5174 is in use. Killing process..."
    lsof -ti:5174 | xargs kill -9
    sleep 2
else
    echo "✅ Port 5174 is free"
fi

echo ""
echo "🚀 Starting server with enhanced UI..."
echo ""
echo "==================================="
echo "🌟 AFTER SERVER STARTS:"
echo "1. Open http://localhost:5174"
echo "2. Press Cmd+Shift+R (hard refresh)"
echo "3. Look for:"
echo "   - Gradient background (blue to indigo)"
echo "   - Animated floating orbs"
echo "   - Glass morphism cards"
echo "   - Professional UI elements"
echo "==================================="
echo ""

# Clear Vite cache and start
rm -rf node_modules/.vite
$PACKAGE_MANAGER run dev
