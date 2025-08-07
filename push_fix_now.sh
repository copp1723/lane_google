#!/bin/bash
# URGENT: Push the syntax fix to Render

echo "=================================================="
echo "🚨 URGENT: PUSH THE SYNTAX FIX TO RENDER"
echo "=================================================="
echo ""
echo "✅ LOCAL FILE IS FIXED - Line 54 of settings.py is correct"
echo "❌ RENDER STILL HAS THE BROKEN VERSION"
echo ""
echo "RUN THESE COMMANDS NOW:"
echo "=================================================="

cd /Users/copp1723/Desktop/lane_google

echo ""
echo "1. Check git status:"
git status --short

echo ""
echo "2. Add all fixed files:"
git add src/config/settings.py src/api/campaign_analytics_api.py src/api/keyword_analytics_api.py

echo ""
echo "3. Commit the fixes:"
git commit -m "URGENT FIX: Remove extra parenthesis in settings.py line 54, fix auth imports, configure OpenRouter"

echo ""
echo "4. Push to trigger Render deployment:"
git push origin main

echo ""
echo "=================================================="
echo "📋 AFTER PUSHING, UPDATE RENDER ENV VARS:"
echo "=================================================="
echo ""
echo "FIX THIS (it's truncated):"
echo "GOOGLE_ADS_CLIENT_ID=756901677789-lak300g2plkl57sdqn2ndvr005mp7tqm.apps.googleusercontent.com"
echo ""
echo "ADD THESE:"
echo "ENVIRONMENT=production"
echo "SECRET_KEY=10b8f18f5519885649d3242b8c276679a7f83d3bbc011d6f232cdb00020a3810"
echo "JWT_SECRET_KEY=5b109c5d7680161bbd00485e9313ded4f2a0332254b612b1ab08428ee8ad7088"
echo ""
echo "✨ Render will auto-deploy after you push!"
