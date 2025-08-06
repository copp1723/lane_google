#!/usr/bin/env python3
"""
Quick test to verify settings.py loads correctly
"""

import sys
import os
sys.path.insert(0, '/Users/copp1723/Desktop/lane_google')

try:
    from src.config.settings import settings
    print("✅ settings.py loaded successfully!")
    print(f"   - Environment: {settings.environment}")
    print(f"   - OpenRouter configured: {bool(settings.openrouter.api_key)}")
    print(f"   - Google Ads configured: {bool(settings.google_ads.client_id)}")
except SyntaxError as e:
    print(f"❌ Syntax Error in settings.py: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error loading settings.py: {e}")
    sys.exit(1)

print("\n✅ All syntax checks passed! Ready to deploy.")
