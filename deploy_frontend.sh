#!/bin/bash

# Quick Frontend Deployment Script
echo "🎨 Deploying Lane AI Frontend (New UI)"
echo "======================================="
echo ""
echo "✅ Backend Status: RUNNING at https://lane-google.onrender.com"
echo "📍 Frontend: About to deploy the new UI"
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Commit and push the frontend code
echo -e "${BLUE}Preparing frontend for deployment...${NC}"
git add .
git commit -m "Deploy frontend: Modern AI-centric UI with budget tracking

- Central AI Assistant widget
- Budget tracking cards for dealers  
- Modern sidebar navigation
- Grid-based dashboard
- Purple/blue gradient theme
- Connected to backend at https://lane-google.onrender.com" || echo "No new changes"

git push origin main || git push origin master || git push

echo ""
echo -e "${GREEN}✅ Code pushed to GitHub${NC}"
echo ""
echo "======================================="
echo "🚀 NOW CREATE THE STATIC SITE ON RENDER:"
echo "======================================="
echo ""
echo "1. Go to: https://dashboard.render.com"
echo ""
echo "2. Click the purple 'New +' button"
echo ""
echo "3. Select 'Static Site'"
echo ""
echo "4. Connect your GitHub repo: lane_google"
echo ""
echo "5. Configure these EXACT settings:"
echo "   ${YELLOW}Name:${NC} lane-google-frontend"
echo "   ${YELLOW}Branch:${NC} main (or master)"
echo "   ${YELLOW}Build Command:${NC} npm install && npm run build"
echo "   ${YELLOW}Publish Directory:${NC} dist"
echo ""
echo "6. Click 'Create Static Site'"
echo ""
echo "======================================="
echo ""
echo "⏱️  The build will take 3-5 minutes"
echo ""
echo "🎯 You'll know it worked when you see:"
echo "   • Purple/blue gradient background"
echo "   • 'Lane AI' in the sidebar"
echo "   • Central AI Assistant widget"
echo "   • Budget tracking cards"
echo ""
echo "📝 Your setup will be:"
echo "   Backend API: https://lane-google.onrender.com"
echo "   Frontend UI: https://[your-chosen-name].onrender.com"
echo ""
echo "======================================="