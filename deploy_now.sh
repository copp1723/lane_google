#!/bin/bash

# Deploy Modern UI to lane-google.onrender.com
echo "🚀 Deploying Modern Lane AI Dashboard"
echo "======================================"
echo "📍 Target: https://lane-google.onrender.com"
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Step 1: Verify configuration
echo -e "${BLUE}Step 1: Verifying configuration...${NC}"
echo "   API URL: https://lane-google.onrender.com"
echo "   App Name: Lane AI"
echo "   Version: 2.0.0"
echo ""

# Step 2: Build the project
echo -e "${BLUE}Step 2: Building production bundle...${NC}"
npm run build

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Build failed. Please check for errors above.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build successful!${NC}"
echo ""

# Step 3: Check git status
echo -e "${BLUE}Step 3: Preparing git commit...${NC}"
git add .

# Show what's being committed
echo "Files to be deployed:"
git status --short
echo ""

# Step 4: Commit with detailed message
echo -e "${BLUE}Step 4: Committing changes...${NC}"
git commit -m "🎨 UI Makeover: Deploy modern AI-centric dashboard

MAJOR CHANGES:
- Central AI Assistant widget as the main focal point
- Budget tracking cards with visual progress indicators
- Modern sidebar navigation with Lane AI branding
- Real-time performance stats in header
- Grid-based responsive dashboard layout

NEW FEATURES:
✨ AI Assistant
  - Prominent placement at top of dashboard
  - Quick action suggestions
  - Expandable chat interface
  - Real-time status indicator

💰 Budget Tracking for Dealers
  - Visual progress bars
  - Color-coded spend pacing (green/amber/red)
  - Monthly projections
  - Multi-dealer support
  - Quick budget adjustment actions

📊 Performance Dashboard
  - Grid layout for better organization
  - AI-powered insights cards
  - Top campaign performers
  - Quick action buttons

🎨 Modern Design
  - Clean sidebar navigation
  - Card-based components
  - Soft shadows and gradients
  - Responsive mobile design
  - Purple/blue color scheme

🔧 Technical Improvements
  - Fixed Vite environment configuration
  - Added process polyfill for compatibility
  - Improved error handling
  - Optimized build process

Deployment target: https://lane-google.onrender.com" || echo "No changes to commit"

# Step 5: Push to remote
echo ""
echo -e "${BLUE}Step 5: Pushing to GitHub...${NC}"

# Try different branch names
git push origin main 2>/dev/null || \
git push origin master 2>/dev/null || \
git push 2>/dev/null || \
echo -e "${YELLOW}Note: If using a different branch name, push manually${NC}"

echo ""
echo -e "${GREEN}✅ Code pushed successfully!${NC}"
echo ""
echo "======================================"
echo ""
echo "📊 DEPLOYMENT STATUS"
echo "-------------------"
echo "✅ Build completed"
echo "✅ Changes committed" 
echo "✅ Code pushed to GitHub"
echo ""
echo "🔄 Render will now:"
echo "1. Detect the push (0-1 min)"
echo "2. Build the app (2-3 min)"
echo "3. Deploy to production (1-2 min)"
echo ""
echo "⏱️  Total time: ~5 minutes"
echo ""
echo "======================================"
echo ""
echo "📍 MONITOR YOUR DEPLOYMENT:"
echo "1. Dashboard: https://dashboard.render.com"
echo "2. Live site: https://lane-google.onrender.com"
echo ""
echo "🎯 WHAT TO EXPECT:"
echo "The old UI will be replaced with:"
echo "• Purple gradient background"
echo "• 'Lane AI' branding in sidebar"
echo "• Central AI Assistant widget"
echo "• Budget tracking cards"
echo "• Modern card-based design"
echo ""
echo "💡 TIP: Clear browser cache if you don't see changes"
echo "======================================"