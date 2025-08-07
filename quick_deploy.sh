#!/bin/bash

# Quick Deploy Script for Lane AI Dashboard
echo "🚀 Lane AI - Quick Deploy to Render"
echo "===================================="
echo ""

# Set text colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Step 1: Check if we need to update the API URL
echo -e "${BLUE}Step 1: Checking API Configuration${NC}"
if grep -q "your-api.onrender.com\|lane-mcp-api.onrender.com" .env.production; then
    echo -e "${YELLOW}⚠️  Please update VITE_API_BASE_URL in .env.production with your actual API URL${NC}"
    echo "   Current value: $(grep VITE_API_BASE_URL .env.production)"
    echo ""
    read -p "Have you updated the API URL? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Please update .env.production and run this script again."
        exit 1
    fi
fi

# Step 2: Build the project
echo -e "${BLUE}Step 2: Building the project${NC}"
npm run build
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Build failed. Please fix errors and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Build successful!${NC}"
echo ""

# Step 3: Git operations
echo -e "${BLUE}Step 3: Committing changes${NC}"
git add .
git commit -m "Deploy: Modern AI-centric dashboard with budget tracking

Features deployed:
- Central AI Assistant widget
- Budget tracking cards for dealers
- Modern sidebar navigation
- Real-time performance stats
- Grid-based dashboard layout
- Responsive design
- Fixed environment configuration"

# Step 4: Push to remote
echo ""
echo -e "${BLUE}Step 4: Pushing to remote repository${NC}"
git push origin main || git push origin master || git push

echo ""
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo ""
echo "===================================="
echo "📍 Next Steps:"
echo "1. Go to https://dashboard.render.com"
echo "2. Watch the deployment progress"
echo "3. Your new UI will be live in ~5 minutes"
echo ""
echo "🎨 New Features Now Live:"
echo "   • AI Assistant front and center"
echo "   • Visual budget tracking"
echo "   • Modern, clean interface"
echo "   • Mobile responsive design"
echo ""
echo "🔗 If this is your first deployment:"
echo "   Create a new Static Site on Render with:"
echo "   Build Command: npm install && npm run build"
echo "   Publish Directory: dist"
echo "===================================="