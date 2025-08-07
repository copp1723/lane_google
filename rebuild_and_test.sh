#!/bin/bash

echo "🔧 Rebuilding and Testing Lane AI Dashboard"
echo "==========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Step 1: Clean old build
echo -e "${BLUE}Step 1: Cleaning old build...${NC}"
rm -rf src/static/assets
rm -f src/static/index.html
echo -e "${GREEN}✅ Old build cleaned${NC}"
echo ""

# Step 2: Build the frontend
echo -e "${BLUE}Step 2: Building frontend...${NC}"
npm run build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed! Check the errors above.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build successful!${NC}"
echo ""

# Step 3: Check build output
echo -e "${BLUE}Step 3: Verifying build output...${NC}"
if [ -f "src/static/index.html" ]; then
    echo -e "${GREEN}✅ index.html found${NC}"
else
    echo -e "${RED}❌ index.html not found!${NC}"
    exit 1
fi

if [ -d "src/static/assets" ]; then
    ASSET_COUNT=$(ls -1 src/static/assets | wc -l)
    echo -e "${GREEN}✅ Assets directory found with $ASSET_COUNT files${NC}"
else
    echo -e "${RED}❌ Assets directory not found!${NC}"
    exit 1
fi
echo ""

# Step 4: Test the server
echo -e "${BLUE}Step 4: Starting test server...${NC}"
echo -e "${YELLOW}The server will start on http://localhost:5000${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the server when done testing${NC}"
echo ""

# Start the server
python src/main.py
