#!/bin/bash
# One-command fix for Render deployment

cd /Users/copp1723/Desktop/lane_google && \
git add src/config/settings.py src/api/campaign_analytics_api.py src/api/keyword_analytics_api.py && \
git commit -m "FIX: Remove extra parenthesis in settings.py line 54, fix auth imports, configure OpenRouter" && \
git push origin main && \
echo "" && \
echo "✅ PUSHED! Render is now deploying the fix." && \
echo "" && \
echo "📋 NOW GO TO RENDER AND UPDATE THESE ENV VARS:" && \
echo "================================================" && \
echo "GOOGLE_ADS_CLIENT_ID=756901677789-lak300g2plkl57sdqn2ndvr005mp7tqm.apps.googleusercontent.com" && \
echo "ENVIRONMENT=production" && \
echo "SECRET_KEY=10b8f18f5519885649d3242b8c276679a7f83d3bbc011d6f232cdb00020a3810" && \
echo "JWT_SECRET_KEY=5b109c5d7680161bbd00485e9313ded4f2a0332254b612b1ab08428ee8ad7088" && \
echo "================================================"
