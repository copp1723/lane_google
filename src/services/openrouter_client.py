"""
OpenRouter Client for Flask Backend
Adapted from TypeScript Foundation service for lane_google integration
"""

import httpx
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class OpenRouterClient:
    """
    Professional OpenRouter client for lane_google backend
    Replaces MockAIService with real AI integration
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        self.site_url = os.getenv('SITE_URL', 'http://localhost:5000')
        self.site_name = os.getenv('SITE_NAME', 'Lane MCP Platform')
        
        if not self.api_key:
            logger.warning('OpenRouter API key not configured - falling back to mock service')
            
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
                "Content-Type": "application/json",
                "HTTP-Referer": self.site_url,
                "X-Title": self.site_name
            }
        )
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "anthropic/claude-3.5-sonnet",
        max_tokens: int = 4000,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Create chat completion with OpenRouter
        Compatible with existing ai_agent_api.py interface
        """
        
        if not self.api_key:
            # Fallback to mock response for development
            return self._mock_response(messages, model)
        
        try:
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": stream
            }
            
            if stream:
                # Handle streaming response
                return await self._handle_streaming_response(payload)
            else:
                response = await self.client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                
                logger.info(f"OpenRouter API call successful - Model: {model}, Usage: {result.get('usage', {})}")
                
                return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenRouter API error: {e.response.status_code} - {e.response.text}")
            # Fallback to mock on API error
            return self._mock_response(messages, model)
            
        except Exception as e:
            logger.error(f"Unexpected OpenRouter error: {str(e)}")
            # Fallback to mock on any error
            return self._mock_response(messages, model)
    
    async def _handle_streaming_response(self, payload: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """Handle streaming response from OpenRouter"""
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        if line == "data: [DONE]":
                            break
                        
                        try:
                            chunk_data = json.loads(line[6:])  # Remove "data: " prefix
                            yield chunk_data
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse streaming chunk: {e}")
                            continue
                            
        except httpx.HTTPStatusError as e:
            logger.error(f"Streaming error: {e.response.status_code} - {e.response.text}")
            yield {"error": f"API error: {e.response.status_code}"}
        except Exception as e:
            logger.error(f"Unexpected streaming error: {str(e)}")
            yield {"error": str(e)}
    
    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        model: str = "anthropic/claude-3.5-sonnet",
        max_tokens: int = 4000,
        temperature: float = 0.7
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Create streaming chat completion with OpenRouter
        """
        
        if not self.api_key:
            # Fallback to mock streaming response
            async for chunk in self._mock_streaming_response(messages, model):
                yield chunk
            return
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True
        }
        
        async for chunk in self._handle_streaming_response(payload):
            yield chunk
    
    async def chat_with_agent(
        self, 
        message: str, 
        conversation_id: str, 
        agent_type: str = "campaign_planner", 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compatible interface with existing AIAgentService
        """
        
        # Build system prompt based on agent type
        system_prompts = {
            "campaign_planner": """You are an expert Google Ads campaign strategist for the Lane MCP platform. 
            Help users create effective campaigns by asking clarifying questions and providing specific recommendations.
            When you have enough information, offer to generate a structured campaign brief.""",
            
            "optimization_analyst": """You are an AI optimization analyst specializing in Google Ads performance analysis.
            Analyze campaign data and provide actionable optimization recommendations.""",
            
            "budget_manager": """You are an AI budget management specialist for Google Ads campaigns.
            Help optimize advertising spend and prevent budget overruns."""
        }
        
        system_prompt = system_prompts.get(agent_type, system_prompts["campaign_planner"])
        if context:
            system_prompt += f"\n\nAdditional Context:\n{json.dumps(context, indent=2)}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        response = await self.chat_completion(messages, temperature=0.7)
        
        return {
            "response": response["choices"][0]["message"]["content"],
            "conversation_id": conversation_id,
            "agent_type": agent_type,
            "model_used": response.get("model", "openrouter-model"),
            "usage": response.get("usage", {})
        }
    
    async def generate_campaign_brief(
        self, 
        conversation_id: str, 
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate structured campaign brief - compatible with existing interface
        """
        
        # For now, return a structured brief - in full integration, 
        # we'd use conversation history from the database
        brief_prompt = """Generate a comprehensive Google Ads campaign brief in JSON format with these fields:
        
        {
            "campaign_name": "Descriptive campaign name",
            "business_objective": "Primary business goal",
            "campaign_type": "Recommended Google Ads campaign type",
            "budget": {"monthly_amount": 0, "currency": "USD", "daily_amount": 0},
            "target_audience": {"demographics": "", "interests": "", "custom_audiences": ""},
            "geographic_targeting": {"locations": [], "radius_targeting": "", "location_exclusions": []},
            "products_services": {"primary_offerings": [], "unique_selling_points": [], "pricing_strategy": ""},
            "keywords": {"primary_keywords": [], "negative_keywords": [], "match_types": ""},
            "ad_copy_themes": {"headlines": [], "descriptions": [], "call_to_action": ""},
            "bidding_strategy": {"type": "", "target_cpa": 0, "target_roas": 0},
            "success_metrics": {"primary_kpi": "", "target_values": {}, "reporting_frequency": ""}
        }
        
        Provide specific, actionable recommendations."""
        
        messages = [{"role": "user", "content": brief_prompt}]
        response = await self.chat_completion(messages, temperature=0.3, max_tokens=2000)
        
        brief_content = response["choices"][0]["message"]["content"]
        
        # Try to parse as JSON
        try:
            brief_json = json.loads(brief_content)
            return {
                "brief": brief_json,
                "format": "json",
                "conversation_id": conversation_id,
                "generated_at": datetime.utcnow().isoformat()
            }
        except json.JSONDecodeError:
            # Return fallback structured brief
            return {
                "brief": {
                    "campaign_name": "AI Generated Campaign",
                    "business_objective": "Increase online sales and brand awareness",
                    "budget": {"monthly_amount": 5000, "currency": "USD", "daily_amount": 167},
                    "target_audience": "Adults 25-45 interested in the product category",
                    "geographic_targeting": "United States, Canada",
                    "success_metrics": "ROAS > 4.0, CTR > 2%, Conversion Rate > 3%"
                },
                "format": "json",
                "conversation_id": conversation_id,
                "generated_at": datetime.utcnow().isoformat()
            }
    
    def _mock_response(self, messages: List[Dict], model: str) -> Dict[str, Any]:
        """Fallback mock response when OpenRouter is unavailable"""
        
        user_message = messages[-1].get('content', '') if messages else ''
        
        mock_responses = [
            "I understand you want to create a campaign. Can you tell me more about your business and target audience?",
            "That sounds great! What's your budget range for this campaign?",
            "Perfect! What geographic areas would you like to target?",
            "Excellent! Based on our conversation, I have enough information to generate a campaign brief for you.",
            "I can help you optimize that campaign. What specific goals are you trying to achieve?"
        ]
        
        import random
        response_content = random.choice(mock_responses)
        
        return {
            "choices": [{
                "message": {
                    "role": "assistant", 
                    "content": response_content
                },
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 50, "completion_tokens": 30, "total_tokens": 80},
            "model": f"mock-{model}"
        }
    
    async def _mock_streaming_response(self, messages: List[Dict], model: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Mock streaming response for development"""
        import random
        
        responses = [
            "I understand you want to create a campaign. Let me help you with that.",
            "Based on your requirements, I recommend a Search campaign targeting high-intent keywords.",
            "For your budget, I suggest starting with $50-100 per day to test performance.",
            "Your target audience should focus on users actively searching for your products.",
            "I'll create a comprehensive campaign structure with multiple ad groups for better targeting."
        ]
        
        response = random.choice(responses)
        words = response.split()
        
        # Simulate streaming by yielding words
        for i, word in enumerate(words):
            chunk = {
                "choices": [{
                    "delta": {
                        "content": word + " " if i < len(words) - 1 else word
                    },
                    "finish_reason": None if i < len(words) - 1 else "stop"
                }],
                "model": f"mock-{model}"
            }
            yield chunk
            await asyncio.sleep(0.05)  # Simulate network delay
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Global instance
openrouter_client = None

def get_openrouter_client() -> OpenRouterClient:
    """Get or create OpenRouter client instance"""
    global openrouter_client
    if openrouter_client is None:
        openrouter_client = OpenRouterClient()
    return openrouter_client