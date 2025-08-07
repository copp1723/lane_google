#!/bin/bash

# Quick fix to trigger Render rebuild
echo "🔄 QUICK FIX FOR STUCK DEPLOYMENT"
echo "=================================="
echo ""

# Just add a comment to trigger a rebuild
echo "# Build trigger: $(date)" >> README.md

git add .
git commit -m "🔄 Trigger rebuild with dependency fix

- Added react-router-dom dependency
- Build trigger for Render
- Timestamp: $(date)"

git push

echo ""
echo "✅ Pushed! Render should start building now."
echo ""
echo "If still stuck:"
echo "1. Go to https://dashboard.render.com"
echo "2. Click 'Manual Deploy' button"
echo "3. Select 'Deploy' on latest commit"