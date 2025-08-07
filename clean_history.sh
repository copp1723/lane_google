#!/bin/bash

echo "🧹 COMPLETE GIT HISTORY CLEANUP"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${RED}⚠️  WARNING: This will rewrite git history!${NC}"
echo -e "${YELLOW}Make sure you have a backup of important files.${NC}"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

# Step 1: Install git-filter-repo if needed
echo -e "${BLUE}Step 1: Checking for git-filter-repo...${NC}"
if ! command -v git-filter-repo &> /dev/null; then
    echo "Installing git-filter-repo..."
    pip3 install git-filter-repo || {
        echo -e "${RED}Failed to install git-filter-repo${NC}"
        echo "Try: brew install git-filter-repo"
        exit 1
    }
fi
echo -e "${GREEN}✅ git-filter-repo available${NC}"
echo ""

# Step 2: Create a backup
echo -e "${BLUE}Step 2: Creating backup...${NC}"
cp -r . ../lane_google_backup_$(date +%Y%m%d_%H%M%S)
echo -e "${GREEN}✅ Backup created${NC}"
echo ""

# Step 3: Remove sensitive files from all history
echo -e "${BLUE}Step 3: Removing sensitive files from history...${NC}"

# Create a paths file to remove
cat > /tmp/paths-to-remove.txt << 'EOF'
GOOGLE_ADS_FIX.md
GOOGLE_ADS_TOKEN_SETUP.md
EOF

# Remove the files from history
git filter-repo --paths-from-file /tmp/paths-to-remove.txt --invert-paths --force

echo -e "${GREEN}✅ Sensitive files removed from history${NC}"
echo ""

# Step 4: Re-add remote
echo -e "${BLUE}Step 4: Re-adding remote...${NC}"
git remote add origin https://github.com/copp1723/lane_google.git
echo -e "${GREEN}✅ Remote added${NC}"
echo ""

# Step 5: Force push
echo -e "${BLUE}Step 5: Force pushing clean history...${NC}"
git push --force origin main || git push --force origin master

echo ""
echo "================================"
echo -e "${GREEN}✨ HISTORY CLEANED!${NC}"
echo "================================"
echo ""
echo "✅ All secrets removed from git history"
echo "✅ Repository is clean"
echo "✅ Ready for deployment"
echo ""
echo -e "${YELLOW}⚠️  Important:${NC}"
echo "- All collaborators need to re-clone the repository"
echo "- Old pull requests may be affected"
echo ""
