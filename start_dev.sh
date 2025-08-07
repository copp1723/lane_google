#!/bin/bash

# Start the Lane AI development server
echo "🚀 Starting Lane AI Dashboard with new UI..."
echo "================================"

cd /Users/copp1723/Desktop/lane_google

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start the development server
echo "✨ Starting development server..."
echo "📍 The app will be available at: http://localhost:5173"
echo "================================"

npm run dev