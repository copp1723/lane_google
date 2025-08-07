#!/bin/bash

# Deploy script for Lane AI Dashboard to Render
echo "🚀 Deploying Lane AI Dashboard to Render"
echo "========================================="

# Navigate to project directory
cd /Users/copp1723/Desktop/lane_google

# Check git status
echo "📊 Checking git status..."
git status --short

echo ""
echo "📝 Adding all changes..."
git add .

echo ""
echo "💾 Committing changes..."
git commit -m "UI Makeover: Modern AI-centric dashboard with budget tracking

- Added central AI Assistant widget as the main focus
- Implemented budget tracking cards for dealers with visual indicators
- Created modern sidebar navigation with clean design
- Added real-time stats in header (ROAS, conversions, CTR)
- Implemented grid-based dashboard layout
- Fixed Vite environment configuration
- Added process polyfill for compatibility
- Created ErrorView component for better error handling
- Modern styling with gradients, shadows, and card-based design
- Responsive design for mobile and tablet devices"

echo ""
echo "📤 Pushing to remote repository..."
git push origin main || git push origin master

echo ""
echo "✅ Deployment initiated!"
echo ""
echo "📍 Render will automatically detect the push and deploy."
echo "   Check your Render dashboard at: https://dashboard.render.com"
echo ""
echo "⏱️  Deployment usually takes 3-5 minutes."
echo "   Your app will be available at your Render URL once complete."
echo ""
echo "🎨 New Features Deployed:"
echo "   • AI Assistant center stage"
echo "   • Budget tracking for dealers"
echo "   • Modern, clean interface"
echo "   • Performance insights"
echo "   • Quick action buttons"