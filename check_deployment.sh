#!/bin/bash

# Pre-deployment verification script
echo "🔍 Lane AI Dashboard - Pre-Deployment Check"
echo "==========================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check function
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} $2"
        return 0
    else
        echo -e "${RED}❌${NC} $2"
        return 1
    fi
}

# Check directory
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅${NC} $2"
        return 0
    else
        echo -e "${RED}❌${NC} $2"
        return 1
    fi
}

echo "📁 Checking Essential Files..."
echo "------------------------------"
check_file "src/App.jsx" "App.jsx (Modern UI)"
check_file "src/App.css" "App.css (Styling)"
check_file "src/components/views/ErrorView.jsx" "ErrorView component"
check_file "src/config/environment.js" "Environment config"
check_file "src/utils/processPolyfill.js" "Process polyfill"
check_file ".env.production" "Production environment"
check_file "render.yaml" "Render configuration"
check_file "package.json" "Package.json"
check_file "vite.config.js" "Vite config"

echo ""
echo "📦 Checking Dependencies..."
echo "---------------------------"
check_dir "node_modules" "Node modules installed"

echo ""
echo "🔧 Checking Build..."
echo "-------------------"
echo "Running build test..."
npm run build > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅${NC} Build successful"
    check_dir "dist" "Dist folder created"
else
    echo -e "${RED}❌${NC} Build failed - run 'npm run build' to see errors"
fi

echo ""
echo "🌍 Checking Git Status..."
echo "------------------------"
# Check if git repo exists
if [ -d ".git" ]; then
    echo -e "${GREEN}✅${NC} Git repository found"
    
    # Check for uncommitted changes
    if [[ -n $(git status -s) ]]; then
        echo -e "${YELLOW}⚠️${NC}  Uncommitted changes detected:"
        git status --short
    else
        echo -e "${GREEN}✅${NC} All changes committed"
    fi
    
    # Check current branch
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    echo -e "📌 Current branch: ${BRANCH}"
    
    # Check if remote is set
    if git remote -v | grep -q origin; then
        echo -e "${GREEN}✅${NC} Remote origin configured"
    else
        echo -e "${RED}❌${NC} No remote origin set"
    fi
else
    echo -e "${RED}❌${NC} Not a git repository"
fi

echo ""
echo "🚀 Deployment Readiness"
echo "----------------------"

# Count successes
READY=true

if [ ! -f ".env.production" ]; then
    echo -e "${YELLOW}⚠️${NC}  Update .env.production with your API URL"
    READY=false
fi

if [ ! -d "dist" ]; then
    echo -e "${YELLOW}⚠️${NC}  Run 'npm run build' before deploying"
    READY=false
fi

if [ "$READY" = true ]; then
    echo -e "${GREEN}✅ Ready to deploy!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Update VITE_API_BASE_URL in .env.production"
    echo "2. Run: ./deploy_to_render.sh"
    echo "3. Monitor deployment at https://dashboard.render.com"
else
    echo -e "${YELLOW}⚠️  Address the issues above before deploying${NC}"
fi

echo ""
echo "==========================================="