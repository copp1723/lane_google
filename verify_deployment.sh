#!/bin/bash

# Quick verification before deployment
echo "✅ Pre-Deployment Checklist"
echo "==========================="
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

READY=true

# Check if App.css is imported
if grep -q "import './App.css'" src/App.jsx; then
    echo -e "${GREEN}✅${NC} App.css is imported"
else
    echo -e "${RED}❌${NC} App.css not imported - FIXING..."
    # Add the import
    sed -i '' "1a\\
import './App.css'" src/App.jsx 2>/dev/null || sed -i "1a import './App.css'" src/App.jsx
    READY=false
fi

# Check if App.css exists
if [ -f "src/App.css" ]; then
    echo -e "${GREEN}✅${NC} App.css exists"
else
    echo -e "${RED}❌${NC} App.css missing"
    READY=false
fi

# Check if vite config is correct
if grep -q "outDir: 'src/static'" vite.config.js; then
    echo -e "${GREEN}✅${NC} Vite outputs to src/static"
else
    echo -e "${RED}❌${NC} Vite config incorrect"
    READY=false
fi

# Check if package.json has build script
if grep -q '"build":' package.json; then
    echo -e "${GREEN}✅${NC} Build script exists"
else
    echo -e "${RED}❌${NC} Build script missing"
    READY=false
fi

# Test build
echo ""
echo "Testing build..."
npm run build > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅${NC} Build successful"
else
    echo -e "${RED}❌${NC} Build failed"
    READY=false
fi

echo ""
if [ "$READY" = true ]; then
    echo -e "${GREEN}✅ READY TO DEPLOY!${NC}"
    echo ""
    echo "Run: ./deploy_monolithic.sh"
else
    echo -e "${RED}Issues found. Fixing...${NC}"
    echo "Run this script again after fixes."
fi