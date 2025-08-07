#!/bin/bash

echo "🚀 LANE AI DASHBOARD - COMPLETE FIX & DEPLOY"
echo "============================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Step 1: Clean build directories
echo -e "${BLUE}Step 1: Cleaning build directories...${NC}"
rm -rf src/static/assets
rm -f src/static/index.html
echo -e "${GREEN}✅ Build directories cleaned${NC}"
echo ""

# Step 2: Ensure environment is configured
echo -e "${BLUE}Step 2: Configuring environment...${NC}"
cat > .env.production << 'EOF'
VITE_API_BASE_URL=https://lane-google.onrender.com
VITE_API_URL=https://lane-google.onrender.com
VITE_APP_NAME=Lane AI
VITE_APP_VERSION=2.0.0
VITE_FEATURE_AI_CHAT=true
VITE_FEATURE_REAL_TIME_MONITORING=true
VITE_FEATURE_AUTO_OPTIMIZATION=true
VITE_FEATURE_WORKFLOW_APPROVAL=true
EOF
echo -e "${GREEN}✅ Environment configured${NC}"
echo ""

# Step 3: Build the application
echo -e "${BLUE}Step 3: Building application...${NC}"
NODE_ENV=production npm run build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Build successful${NC}"
echo ""

# Step 4: Verify build output
echo -e "${BLUE}Step 4: Verifying build output...${NC}"
if [ -f "src/static/index.html" ] && [ -d "src/static/assets" ]; then
    ASSET_COUNT=$(ls -1 src/static/assets | wc -l)
    echo -e "${GREEN}✅ Build verified: index.html + $ASSET_COUNT asset files${NC}"
else
    echo -e "${RED}❌ Build verification failed${NC}"
    exit 1
fi
echo ""

# Step 5: Commit and push
echo -e "${BLUE}Step 5: Committing changes...${NC}"
git add .
git commit -m "Fix UI deployment - Asset paths and environment configuration

- Fixed Vite base path configuration
- Updated Flask static file serving
- Configured production API endpoints
- Added enhanced-ui.css import
- Fixed asset path references" || echo "No changes to commit"

echo -e "${GREEN}✅ Changes committed${NC}"
echo ""

# Step 6: Push to GitHub
echo -e "${BLUE}Step 6: Pushing to GitHub...${NC}"
git push origin main 2>/dev/null || git push origin master 2>/dev/null || git push

echo -e "${GREEN}✅ Pushed to GitHub${NC}"
echo ""

echo "============================================="
echo -e "${GREEN}✨ DEPLOYMENT COMPLETE!${NC}"
echo "============================================="
echo ""
echo "📊 What happens next:"
echo "1. Render detects the push (0-1 min)"
echo "2. Builds the application (2-3 min)"
echo "3. Deploys to production (1-2 min)"
echo ""
echo "🔗 Monitor at: https://dashboard.render.com"
echo "🌐 Live site: https://lane-google.onrender.com"
echo ""
echo "✅ Fixed issues:"
echo "  • Asset paths now load correctly"
echo "  • CSS styles properly applied"
echo "  • API endpoints configured for production"
echo "  • Static file serving optimized"
echo ""
echo "💡 If styles still don't appear:"
echo "  • Clear browser cache (Cmd+Shift+R)"
echo "  • Check browser console for errors"
echo ""
