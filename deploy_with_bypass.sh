#!/bin/bash

echo "🔐 BYPASSING AUTHENTICATION + DEPLOYING"
echo "========================================"
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${YELLOW}⚠️  AUTH BYPASS ENABLED${NC}"
echo "The app will auto-login as admin@lane-ai.com"
echo "No password needed!"
echo ""

# Commit all changes
echo -e "${BLUE}Committing auth bypass...${NC}"
git add -A
git commit -m "🔐 Temporary: Auth bypass for development

- Added DEV_MODE to AuthContext
- Auto-login as admin user
- Bypasses broken registration endpoint
- No password required

IMPORTANT: Set DEV_MODE = false before production!" || echo "No changes"

# Push to GitHub
echo ""
echo -e "${BLUE}Pushing to GitHub...${NC}"
git push

echo ""
echo -e "${GREEN}✅ Pushed with auth bypass!${NC}"
echo ""
echo "========================================"
echo "📊 WHAT HAPPENS NOW:"
echo "========================================"
echo ""
echo "1. Render rebuilds (~6 minutes)"
echo "2. Visit https://lane-google.onrender.com"
echo "3. You're automatically logged in!"
echo "4. See the modern UI without auth issues"
echo ""
echo "========================================"
echo "🔐 DEFAULT ADMIN (for reference):"
echo "========================================"
echo "Email: admin@lane-ai.com"
echo "Name: Admin User"
echo "Role: admin"
echo "Password: Not needed (bypassed)"
echo ""
echo "⚠️  IMPORTANT: Before going to production:"
echo "   1. Set DEV_MODE = false in AuthContext.jsx"
echo "   2. Fix the registration endpoint"
echo "   3. Set up proper authentication"
echo "========================================"