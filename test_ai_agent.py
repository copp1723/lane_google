#!/usr/bin/env python3.11
"""
Test the enhanced AI Agent Service with automotive-focused prompts
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from src.services.ai_agent_service import ai_agent_service

def test_ai_agent():
    """Test the AI agent service with various automotive scenarios"""
    
    print("🤖 Testing Lane MCP AI Agent Service")
    print("=" * 60)
    
    # Test 1: General Campaign Request
    print("\n1️⃣ Testing General Campaign Creation:")
    print("User: 'Push used Toyota SUVs this weekend, $1,500 budget in Houston'")
    
    response = ai_agent_service.chat(
        message="Push used Toyota SUVs this weekend, $1,500 budget in Houston",
        context_type="general"
    )
    
    if response['success']:
        print(f"\n✅ AI Response:\n{response['response']}")
    else:
        print(f"\n❌ Error: {response['error']}")
    
    # Test 2: Campaign Brief Generation
    print("\n" + "=" * 60)
    print("\n2️⃣ Testing Campaign Brief Generation:")
    
    conversation_history = [
        {"role": "user", "content": "I need to move 50 F-150s by month end"},
        {"role": "assistant", "content": "I'll help you create a campaign to move those F-150s. Let me gather some details:\n- What's your total budget for this campaign?\n- What's your dealership location?\n- Are these new or used F-150s?\n- Any specific model years or trims?"},
        {"role": "user", "content": "Budget is $5000, we're in Dallas, all 2023 new F-150s, mix of XLT and Lariat trims"},
    ]
    
    brief_response = ai_agent_service.generate_campaign_brief(conversation_history)
    
    if brief_response['success']:
        print(f"\n✅ Campaign Brief Generated:")
        print(f"Format: {brief_response['format']}")
        if brief_response['format'] == 'json':
            import json
            print(json.dumps(brief_response['brief'], indent=2))
        else:
            print(brief_response['brief'])
    else:
        print(f"\n❌ Error: {brief_response['error']}")
    
    # Test 3: Performance Analysis
    print("\n" + "=" * 60)
    print("\n3️⃣ Testing Performance Analysis:")
    
    campaign_data = {
        "campaign_name": "March Truck Event",
        "budget": "$10,000",
        "spend": "$3,200",
        "days_remaining": 3,
        "impressions": 45000,
        "clicks": 1200,
        "conversions": 24,
        "ctr": "2.67%",
        "cpc": "$2.67",
        "conversion_rate": "2%"
    }
    
    analysis_response = ai_agent_service.analyze_campaign_performance(campaign_data)
    
    if analysis_response['success']:
        print(f"\n✅ Performance Analysis:\n{analysis_response['analysis']}")
    else:
        print(f"\n❌ Error: {analysis_response['error']}")
    
    # Test 4: Keyword Generation
    print("\n" + "=" * 60)
    print("\n4️⃣ Testing Keyword Generation:")
    
    keyword_response = ai_agent_service.generate_keywords(
        business_description="Toyota dealership specializing in trucks and SUVs",
        target_audience="Contractors and families in Houston area"
    )
    
    if keyword_response['success']:
        print(f"\n✅ Keywords Generated:\n{keyword_response['keywords']}")
    else:
        print(f"\n❌ Error: {keyword_response['error']}")
    
    # Health Check
    print("\n" + "=" * 60)
    print("\n5️⃣ Service Health Check:")
    health = ai_agent_service.health_check()
    print(f"Status: {health['status']}")
    print(f"OpenRouter Configured: {health['openrouter_configured']}")
    print(f"Capabilities: {', '.join(health['capabilities'])}")
    
    print("\n" + "=" * 60)
    print("✅ AI Agent testing complete!")

if __name__ == "__main__":
    test_ai_agent()