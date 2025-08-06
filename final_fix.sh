#!/bin/bash

echo "🚀 FIXING & REDEPLOYING LANE AI"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Installing dependencies...${NC}"
npm install

echo ""
echo -e "${BLUE}Building locally to verify...${NC}"
npm run build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Build works!${NC}"
else
    echo "Build failed - check errors above"
    exit 1
fi

echo ""
echo -e "${BLUE}Committing all changes...${NC}"
git add -A
git commit -m "✅ Fixed deployment: Added react-router-dom dependency

- Added missing react-router-dom to package.json
- Modern UI with AI Assistant ready to deploy
- Budget tracking cards included
- All dependencies verified

This fixes the stuck build issue on Render." || echo "Already committed"

echo ""
echo -e "${BLUE}Pushing to GitHub...${NC}"
git push

echo ""
echo -e "${GREEN}✅ DONE! Fix pushed to GitHub${NC}"
echo ""
echo "================================"
echo "NOW ON RENDER DASHBOARD:"
echo "================================"
echo ""
echo "1. ⏸️  Cancel the stuck deployment (red button)"
echo ""
echo "2. 🔄 Wait for auto-deploy OR"
echo "   📦 Click 'Manual Deploy' → 'Deploy'"
echo ""
echo "3. 👀 Watch the logs - you'll see:"
echo "   • Installing packages..."
echo "   • Building React app..."
echo "   • Starting Flask server..."
echo ""
echo "4. 🎉 In ~7 minutes: Modern UI live!"
echo ""
echo "================================"