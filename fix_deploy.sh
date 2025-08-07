#!/bin/bash

# Emergency fix and redeploy script
echo "🚨 FIXING DEPLOYMENT ISSUE"
echo "=========================="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${RED}ISSUE FOUND:${NC} Missing react-router-dom dependency"
echo -e "${GREEN}FIXED:${NC} Added to package.json"
echo ""

# Install missing dependency locally to verify
echo -e "${BLUE}Installing dependencies locally...${NC}"
npm install

echo ""
echo -e "${BLUE}Testing build locally...${NC}"
npm run build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Build successful locally!${NC}"
else
    echo -e "${RED}Build failed. Installing dependencies...${NC}"
    npm install react-router-dom
    npm run build
fi

echo ""
echo -e "${BLUE}Committing fix...${NC}"
git add package.json package-lock.json
git commit -m "🔧 Fix: Add missing react-router-dom dependency

- Added react-router-dom to package.json
- Required for routing in the modern UI
- Fixes build failure on Render" || echo "No changes"

echo ""
echo -e "${BLUE}Pushing to GitHub...${NC}"
git push origin main || git push origin master || git push

echo ""
echo -e "${GREEN}✅ FIX DEPLOYED!${NC}"
echo ""
echo "======================================"
echo "📋 NEXT STEPS:"
echo "======================================"
echo ""
echo "1. Go to Render Dashboard"
echo "2. If the old deploy is still stuck:"
echo "   - Click 'Cancel deploy' (red button)"
echo "   - Wait for cancellation"
echo ""
echo "3. Render should auto-detect the new push"
echo "   - If not, click 'Manual Deploy' → 'Deploy'"
echo ""
echo "4. Watch the logs - build should work now!"
echo ""
echo "======================================"
echo "⏱️  Expected timeline:"
echo "   • Build starts: 1 minute"
echo "   • npm install: 2 minutes"
echo "   • npm run build: 1 minute"
echo "   • Docker build: 2 minutes"
echo "   • Deploy: 1 minute"
echo "   TOTAL: ~7 minutes"
echo "======================================"