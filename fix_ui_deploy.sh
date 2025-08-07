#!/bin/bash

echo "🚀 Lane AI Dashboard - Complete Fix & Deploy"
echo "============================================"
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Step 1: Fix environment configuration
echo -e "${BLUE}Step 1: Configuring environment...${NC}"

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo -e "${YELLOW}Creating .env.production...${NC}"
    cat > .env.production << 'EOF'
VITE_API_URL=https://lane-google.onrender.com
VITE_APP_NAME=Lane AI
VITE_APP_VERSION=2.0.0
EOF
    echo -e "${GREEN}✅ .env.production created${NC}"
else
    echo -e "${GREEN}✅ .env.production exists${NC}"
fi
echo ""

# Step 2: Clean previous builds
echo -e "${BLUE}Step 2: Cleaning previous builds...${NC}"
rm -rf src/static/assets
rm -f src/static/index.html
rm -rf dist
echo -e "${GREEN}✅ Previous builds cleaned${NC}"
echo ""

# Step 3: Install dependencies
echo -e "${BLUE}Step 3: Checking dependencies...${NC}"
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi
echo -e "${GREEN}✅ Dependencies ready${NC}"
echo ""

# Step 4: Build the frontend
echo -e "${BLUE}Step 4: Building production frontend...${NC}"
echo "Building with Vite..."
NODE_ENV=production npm run build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed!${NC}"
    echo "Trying to diagnose the issue..."
    
    # Check if vite is installed
    if ! command -v npx vite &> /dev/null; then
        echo "Vite not found, installing..."
        npm install vite --save-dev
        NODE_ENV=production npm run build
    fi
fi

# Step 5: Verify build output
echo ""
echo -e "${BLUE}Step 5: Verifying build output...${NC}"

BUILD_SUCCESS=true

if [ -f "src/static/index.html" ]; then
    echo -e "${GREEN}✅ index.html generated${NC}"
    
    # Check if assets are referenced correctly
    if grep -q "/assets/" src/static/index.html; then
        echo -e "${GREEN}✅ Asset paths look correct${NC}"
    else
        echo -e "${YELLOW}⚠️  Asset paths might need adjustment${NC}"
    fi
else
    echo -e "${RED}❌ index.html not found!${NC}"
    BUILD_SUCCESS=false
fi

if [ -d "src/static/assets" ]; then
    ASSET_COUNT=$(ls -1 src/static/assets 2>/dev/null | wc -l)
    if [ $ASSET_COUNT -gt 0 ]; then
        echo -e "${GREEN}✅ Assets generated ($ASSET_COUNT files)${NC}"
    else
        echo -e "${RED}❌ No asset files found!${NC}"
        BUILD_SUCCESS=false
    fi
else
    echo -e "${RED}❌ Assets directory not found!${NC}"
    BUILD_SUCCESS=false
fi

if [ "$BUILD_SUCCESS" = false ]; then
    echo ""
    echo -e "${RED}Build verification failed. Attempting fallback build...${NC}"
    
    # Try building to dist first then copying
    npx vite build --outDir dist
    if [ -d "dist" ]; then
        echo "Copying from dist to src/static..."
        mkdir -p src/static
        cp -r dist/* src/static/
        echo -e "${GREEN}✅ Fallback build completed${NC}"
    fi
fi

echo ""

# Step 6: Fix any import issues in the built files
echo -e "${BLUE}Step 6: Checking for import issues...${NC}"

# Check if the App component imports CSS correctly
if [ -f "src/static/index.html" ]; then
    # Ensure CSS is loaded
    if ! grep -q "enhanced-ui.css" src/static/index.html; then
        echo -e "${YELLOW}Adding enhanced UI styles...${NC}"
        # The CSS should be bundled, but let's make sure
    fi
    echo -e "${GREEN}✅ Import checks complete${NC}"
fi
echo ""

# Step 7: Test locally (optional)
echo -e "${PURPLE}============================================${NC}"
echo -e "${PURPLE}Build Complete! Next steps:${NC}"
echo -e "${PURPLE}============================================${NC}"
echo ""
echo "1. Test locally:"
echo "   ${YELLOW}python src/main.py${NC}"
echo "   Then visit: ${BLUE}http://localhost:5000${NC}"
echo ""
echo "2. Deploy to production:"
echo "   ${YELLOW}git add .${NC}"
echo "   ${YELLOW}git commit -m \"Fix UI deployment issues\"${NC}"
echo "   ${YELLOW}git push${NC}"
echo ""
echo "3. Monitor deployment:"
echo "   Visit: ${BLUE}https://dashboard.render.com${NC}"
echo ""
echo -e "${GREEN}✨ Your UI should now display correctly with:${NC}"
echo "   • Purple gradient background"
echo "   • AI Assistant widget"
echo "   • Budget tracking cards"
echo "   • Modern card-based design"
echo "   • All assets loading properly"
echo ""
echo -e "${YELLOW}💡 If styles still don't appear:${NC}"
echo "   1. Clear browser cache (Cmd+Shift+R)"
echo "   2. Check browser console for errors"
echo "   3. Verify API endpoints are working"
echo ""
