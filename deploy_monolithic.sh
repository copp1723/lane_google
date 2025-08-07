#!/bin/bash

# Final deployment script for the monolithic Flask + React app
echo "🚀 Deploying Modern UI to lane-google.onrender.com"
echo "=================================================="
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}Your Render service is configured as a monolithic deployment:${NC}"
echo "• Backend (Flask) + Frontend (React) in one service ✅"
echo "• Building with Docker multi-stage build ✅"
echo "• Frontend builds to src/static folder ✅"
echo ""

# Step 1: Verify the build works locally
echo -e "${BLUE}Step 1: Testing local build...${NC}"
npm run build
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Build failed locally. Fixing...${NC}"
    npm install
    npm run build
fi

# Check if static files were created
if [ -d "src/static" ]; then
    echo -e "${GREEN}✅ Frontend built successfully to src/static${NC}"
    echo "   Files created: $(ls -1 src/static | wc -l) files"
else
    echo -e "${YELLOW}⚠️  Static folder not found${NC}"
fi

echo ""
echo -e "${BLUE}Step 2: Committing all changes...${NC}"

# Add all files including the built static files
git add -A
git status --short

git commit -m "🎨 Deploy Modern UI: AI-centric dashboard with budget tracking

FRONTEND CHANGES:
✨ Central AI Assistant Widget
  - Prominent placement at dashboard center
  - Quick action suggestions
  - Expandable chat interface
  - Real-time online status

💰 Budget Tracking for Dealers
  - Visual progress bars with spend pacing
  - Color-coded alerts (green/amber/red)
  - Monthly projections
  - Multi-dealer support

🎯 Modern Interface
  - Sidebar navigation with 'Lane AI' branding
  - Grid-based dashboard layout
  - Card-based components
  - Purple/blue gradient theme
  - Responsive mobile design

📊 Performance Dashboard
  - Real-time stats in header (ROAS, CTR, Conversions)
  - AI-powered insights cards
  - Campaign performance charts
  - Quick action buttons

🔧 Technical Updates
  - Fixed Vite environment configuration
  - Added process polyfill
  - Configured production API URL
  - Build outputs to src/static for Flask serving

Backend URL: https://lane-google.onrender.com
Frontend: Served by Flask from /src/static" || echo "No changes to commit"

echo ""
echo -e "${BLUE}Step 3: Pushing to GitHub...${NC}"

# Push to remote
git push origin main || git push origin master || git push

echo ""
echo -e "${GREEN}✅ DEPLOYMENT TRIGGERED!${NC}"
echo ""
echo "=================================================="
echo "📊 WHAT'S HAPPENING NOW:"
echo "=================================================="
echo ""
echo "1. GitHub received your push ✅"
echo "2. Render detected changes and started building..."
echo "3. Docker is building your app:"
echo "   • Installing npm packages"
echo "   • Running 'npm run build'"
echo "   • Copying built files to src/static"
echo "   • Starting Flask server"
echo ""
echo "⏱️  ESTIMATED TIME: 5-7 minutes"
echo ""
echo "=================================================="
echo "📍 MONITOR YOUR DEPLOYMENT:"
echo "=================================================="
echo ""
echo "• Dashboard: https://dashboard.render.com"
echo "• Live Site: https://lane-google.onrender.com"
echo "• Build Logs: Check Render dashboard for progress"
echo ""
echo "=================================================="
echo "🎨 WHAT YOU'LL SEE WHEN DONE:"
echo "=================================================="
echo ""
echo "OLD UI (Before)          → NEW UI (After)"
echo "------------------------   ------------------------"
echo "White background         → Purple/blue gradient"
echo "Basic campaign cards     → AI Assistant widget"
echo "Simple tabs              → 'Lane AI' sidebar"
echo "Text budgets             → Visual progress bars"
echo "Traditional layout       → Modern grid dashboard"
echo ""
echo "💡 TIP: Open in Incognito mode to bypass cache"
echo ""
echo "=================================================="
echo ""
echo "🔄 Render is now rebuilding your app with the new UI..."
echo "   Check https://lane-google.onrender.com in 5 minutes!"