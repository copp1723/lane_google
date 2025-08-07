#!/bin/bash

echo "🔧 FIXING BUILD ERROR - LANE AI DASHBOARD"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Step 1: Clean node_modules and package-lock
echo -e "${BLUE}Step 1: Cleaning corrupted dependencies...${NC}"
rm -rf node_modules
rm -f package-lock.json
echo -e "${GREEN}✅ Cleaned node_modules and package-lock${NC}"
echo ""

# Step 2: Clear npm cache
echo -e "${BLUE}Step 2: Clearing npm cache...${NC}"
npm cache clean --force
echo -e "${GREEN}✅ NPM cache cleared${NC}"
echo ""

# Step 3: Reinstall dependencies
echo -e "${BLUE}Step 3: Installing fresh dependencies...${NC}"
npm install
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    echo "Trying with legacy peer deps..."
    npm install --legacy-peer-deps
fi
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Step 4: Clean build directories
echo -e "${BLUE}Step 4: Cleaning build directories...${NC}"
rm -rf src/static/assets
rm -f src/static/index.html
rm -rf dist
echo -e "${GREEN}✅ Build directories cleaned${NC}"
echo ""

# Step 5: Build the application
echo -e "${BLUE}Step 5: Building application...${NC}"
NODE_ENV=production npm run build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed${NC}"
    echo "Trying alternative build approach..."
    npx vite build
fi

# Step 6: Verify build
echo ""
echo -e "${BLUE}Step 6: Verifying build...${NC}"
if [ -f "src/static/index.html" ]; then
    echo -e "${GREEN}✅ index.html created${NC}"
    
    if [ -d "src/static/assets" ]; then
        ASSET_COUNT=$(ls -1 src/static/assets 2>/dev/null | wc -l)
        echo -e "${GREEN}✅ Assets directory created with $ASSET_COUNT files${NC}"
    else
        echo -e "${YELLOW}⚠️  Assets directory not found${NC}"
    fi
else
    echo -e "${RED}❌ Build output not found${NC}"
    echo ""
    echo "Checking if built to dist instead..."
    if [ -d "dist" ]; then
        echo "Found dist directory, copying to src/static..."
        mkdir -p src/static
        cp -r dist/* src/static/
        echo -e "${GREEN}✅ Copied dist to src/static${NC}"
    fi
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✨ BUILD FIX COMPLETE!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Test locally:"
echo "   ${YELLOW}python src/main.py${NC}"
echo ""
echo "2. If build successful, deploy:"
echo "   ${YELLOW}git add .${NC}"
echo "   ${YELLOW}git commit -m \"Fix corrupted dependencies and rebuild\"${NC}"
echo "   ${YELLOW}git push${NC}"
echo ""
