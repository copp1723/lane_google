#!/bin/bash

# Lane Google Frontend Fix Script
# This script fixes the TypeScript import issues and rebuilds the frontend

echo "🔧 Lane Google Frontend Fix Script"
echo "=================================="

# Navigate to project directory
cd "$(dirname "$0")"

echo "📍 Current directory: $(pwd)"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
else
    echo "✅ Dependencies already installed"
fi

# Clean old build
echo "🧹 Cleaning old build files..."
rm -rf src/static/*

# Build the frontend
echo "🔨 Building frontend..."
npm run build

# Check if build was successful
if [ -f "src/static/index.html" ]; then
    echo "✅ Build successful! Frontend files generated in src/static/"
    
    # List generated files
    echo "📁 Generated files:"
    ls -la src/static/
    ls -la src/static/assets/ 2>/dev/null || echo "   No assets directory"
    
else
    echo "❌ Build failed! Check the output above for errors."
    exit 1
fi

echo ""
echo "🎉 Frontend fix complete!"
echo "   The blank page issues should now be resolved."
echo "   If problems persist, check the browser console for runtime errors."
