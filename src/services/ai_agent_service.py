"""
AI Agent Service
Provides AI-powered campaign generation and chat functionality
"""

import logging
import os
import asyncio
import json
from typing import Dict, List, Optional, Any, AsyncGenerator
from dotenv import load_dotenv

from src.services.openrouter_client import get_openrouter_client

load_dotenv()
logger = logging.getLogger(__name__)


class AIAgentService:
    """AI Agent service for campaign generation and chat"""
    
    def __init__(self):
        self.client = get_openrouter_client()
        self.model = "anthropic/claude-3.5-sonnet"  # Default model
        logger.info(f"AI Agent Service initialized with {'OpenRouter' if self.client.api_key else 'mock'} backend")
    
    def chat(self, message: str, conversation_history: List[Dict] = None, 
             context_type: str = "general") -> Dict[str, Any]:
        """Chat with AI agent (synchronous wrapper for async method)"""
        try:
            # Create new event loop for sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.chat_async(message, conversation_history, context_type)
            )
            return result
        except Exception as e:
            logger.error(f"AI chat error: {str(e)}")
            return {
                'success': False,
                'error': f'AI service error: {str(e)}'
            }
    
    async def chat_async(self, message: str, conversation_history: List[Dict] = None, 
                        context_type: str = "general") -> Dict[str, Any]:
        """Chat with AI agent (async version)"""
        try:
            # System prompts based on context
            system_prompts = {
                "general": """You are an expert Google Ads automation agent for the Lane MCP platform. 
                Help users create and manage Google Ads campaigns through natural conversation.""",
                
                "campaign_generation": """You are a Google Ads campaign strategist. Help users create 
                comprehensive campaign briefs by asking the right questions and providing expert guidance.""",
                
                "discovery_analysis": """You are a market research analyst. Analyze campaign requirements 
                and provide insights on target audience, competition, and optimization opportunities.""",
                
                "strategy_planning": """You are a campaign strategist. Create detailed campaign strategies 
                including structure, targeting, bidding, and creative approaches.""",
                
                "campaign_review": """You are a quality assurance specialist. Review campaign configurations 
                for compliance, best practices, and optimization opportunities."""
            }
            
            system_prompt = system_prompts.get(context_type, system_prompts["general"])
            
            # Build messages
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history)
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Make API call using OpenRouter
            response = await self.client.chat_completion(
                messages=messages,
                model=self.model,
                max_tokens=1000,
                temperature=0.7
            )
            
            # Extract content from response
            content = response['choices'][0]['message']['content']
            usage = response.get('usage', {})
            
            return {
                'success': True,
                'response': content,
                'usage': usage,
                'model_used': response.get('model', self.model)
            }
            
        except Exception as e:
            logger.error(f"AI chat error: {str(e)}")
            return {
                'success': False,
                'error': f'AI service error: {str(e)}'
            }
    
    async def stream_chat(self, message: str, conversation_history: List[Dict] = None,
                         context_type: str = "general") -> AsyncGenerator[Dict[str, Any], None]:
        """Stream chat responses from AI agent"""
        try:
            # System prompts based on context
            system_prompts = {
                "general": """You are an expert Google Ads automation agent for the Lane MCP platform. 
                Help users create and manage Google Ads campaigns through natural conversation.""",
                
                "campaign_generation": """You are a Google Ads campaign strategist. Help users create 
                comprehensive campaign briefs by asking the right questions and providing expert guidance."""
            }
            
            system_prompt = system_prompts.get(context_type, system_prompts["general"])
            
            # Build messages
            messages = [{"role": "system", "content": system_prompt}]
            
            if conversation_history:
                messages.extend(conversation_history)
                
            messages.append({"role": "user", "content": message})
            
            # Stream response
            async for chunk in self.client.chat_completion_stream(
                messages=messages,
                model=self.model,
                max_tokens=1000,
                temperature=0.7
            ):
                yield chunk
                
        except Exception as e:
            logger.error(f"Stream chat error: {str(e)}")
            yield {"error": str(e)}
    
    def generate_campaign_brief(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Generate structured campaign brief from conversation"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.generate_campaign_brief_async(conversation_history)
            )
            return result
        except Exception as e:
            logger.error(f"Campaign brief generation error: {str(e)}")
            return {
                'success': False,
                'error': f'Brief generation error: {str(e)}'
            }
    
    async def generate_campaign_brief_async(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Generate structured campaign brief from conversation (async)"""
        try:
            system_prompt = """Based on the conversation history, generate a structured Google Ads campaign brief in JSON format.
            
            Extract and organize the following information:
            {
                "campaign_name": "A descriptive name for the campaign",
                "objective": "Primary campaign goal (leads, sales, awareness, etc.)",
                "budget": {
                    "monthly_amount": 0,
                    "currency": "USD",
                    "daily_amount": 0
                },
                "target_audience": {
                    "demographics": "Age, gender, income level",
                    "interests": "Relevant interests and behaviors",
                    "intent_signals": "Search intent indicators"
                },
                "geographic_targeting": {
                    "locations": ["List of target locations"],
                    "radius_targeting": "If applicable",
                    "excluded_locations": []
                },
                "products_services": "What is being advertised",
                "key_messages": ["Main selling points", "Value propositions"],
                "keywords": {
                    "primary": ["Main keywords"],
                    "negative": ["Keywords to exclude"]
                },
                "success_metrics": {
                    "primary_kpi": "Main success metric",
                    "targets": {"conversions": 0, "cpa": 0, "roas": 0}
                },
                "timeline": "Campaign duration or start date",
                "bidding_strategy": "Recommended bidding approach",
                "ad_schedule": "When ads should run",
                "additional_notes": "Any special requirements"
            }
            
            Return ONLY valid JSON, no explanatory text."""
            
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(conversation_history)
            messages.append({
                "role": "user", 
                "content": "Please generate a structured campaign brief based on our conversation."
            })
            
            response = await self.client.chat_completion(
                messages=messages,
                model=self.model,
                max_tokens=1500,
                temperature=0.3
            )
            
            brief_content = response['choices'][0]['message']['content']
            
            # Try to parse as JSON
            try:
                import json
                # Clean the content to ensure it's valid JSON
                brief_content = brief_content.strip()
                if brief_content.startswith("```json"):
                    brief_content = brief_content[7:]
                if brief_content.endswith("```"):
                    brief_content = brief_content[:-3]
                
                brief_json = json.loads(brief_content.strip())
                return {
                    'success': True,
                    'brief': brief_json,
                    'format': 'json'
                }
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse brief as JSON: {e}")
                # Return a structured brief as fallback
                return {
                    'success': True,
                    'brief': self._create_fallback_brief(conversation_history),
                    'format': 'json'
                }
                
        except Exception as e:
            logger.error(f"Campaign brief generation error: {str(e)}")
            return {
                'success': False,
                'error': f'Brief generation error: {str(e)}'
            }
    
    def analyze_campaign_performance(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze campaign performance and provide recommendations"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.analyze_campaign_performance_async(campaign_data)
            )
            return result
        except Exception as e:
            logger.error(f"Performance analysis error: {str(e)}")
            return {
                'success': False,
                'error': f'Analysis error: {str(e)}'
            }
    
    async def analyze_campaign_performance_async(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze campaign performance and provide recommendations (async)"""
        try:
            system_prompt = """You are a Google Ads performance analyst. Analyze the provided campaign 
            data and provide actionable recommendations for optimization."""
            
            analysis_prompt = f"""
            Analyze this campaign performance data and provide recommendations:
            
            {json.dumps(campaign_data, indent=2)}
            
            Please provide:
            1. Performance assessment (good/needs improvement/poor)
            2. Key insights and trends
            3. Specific optimization recommendations
            4. Priority actions to take
            5. Expected impact of recommendations
            
            Format your response as structured sections for easy parsing.
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": analysis_prompt}
            ]
            
            response = await self.client.chat_completion(
                messages=messages,
                model=self.model,
                max_tokens=1200,
                temperature=0.4
            )
            
            return {
                'success': True,
                'analysis': response['choices'][0]['message']['content'],
                'model_used': response.get('model', self.model)
            }
            
        except Exception as e:
            logger.error(f"Performance analysis error: {str(e)}")
            return {
                'success': False,
                'error': f'Analysis error: {str(e)}'
            }
    
    def generate_keywords(self, business_description: str, target_audience: str = None) -> Dict[str, Any]:
        """Generate keyword suggestions for campaigns"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.generate_keywords_async(business_description, target_audience)
            )
            return result
        except Exception as e:
            logger.error(f"Keyword generation error: {str(e)}")
            return {
                'success': False,
                'error': f'Keyword generation error: {str(e)}'
            }
    
    async def generate_keywords_async(self, business_description: str, target_audience: str = None) -> Dict[str, Any]:
        """Generate keyword suggestions for campaigns (async)"""
        try:
            system_prompt = """You are a Google Ads keyword research specialist. Generate relevant 
            keywords for the given business and target audience. Return results in structured JSON format."""
            
            keyword_prompt = f"""
            Generate keyword suggestions for:
            Business: {business_description}
            Target Audience: {target_audience or 'General audience'}
            
            Provide keywords in this JSON structure:
            {{
                "broad_keywords": [
                    {{"keyword": "example", "match_type": "broad", "search_volume": "high", "competition": "medium"}}
                ],
                "phrase_keywords": [
                    {{"keyword": "example phrase", "match_type": "phrase", "search_volume": "medium", "competition": "low"}}
                ],
                "exact_keywords": [
                    {{"keyword": "[exact match]", "match_type": "exact", "search_volume": "low", "competition": "low"}}
                ],
                "long_tail_keywords": [
                    {{"keyword": "very specific long tail keyword", "match_type": "broad", "search_volume": "low", "competition": "low"}}
                ],
                "negative_keywords": ["irrelevant", "free", "cheap"]
            }}
            
            Generate 5-10 keywords per category. Return ONLY valid JSON.
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": keyword_prompt}
            ]
            
            response = await self.client.chat_completion(
                messages=messages,
                model=self.model,
                max_tokens=1500,
                temperature=0.5
            )
            
            content = response['choices'][0]['message']['content']
            
            try:
                import json
                # Clean JSON if needed
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                
                keywords_json = json.loads(content.strip())
                return {
                    'success': True,
                    'keywords': keywords_json,
                    'format': 'json'
                }
            except json.JSONDecodeError:
                # Return structured fallback
                return {
                    'success': True,
                    'keywords': self._create_fallback_keywords(business_description),
                    'format': 'json'
                }
            
        except Exception as e:
            logger.error(f"Keyword generation error: {str(e)}")
            return {
                'success': False,
                'error': f'Keyword generation error: {str(e)}'
            }
    
    def _create_fallback_brief(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Create a fallback campaign brief"""
        return {
            "campaign_name": "New Campaign",
            "objective": "Generate leads",
            "budget": {
                "monthly_amount": 5000,
                "currency": "USD",
                "daily_amount": 167
            },
            "target_audience": {
                "demographics": "Adults 25-54",
                "interests": "Relevant to business",
                "intent_signals": "High purchase intent"
            },
            "geographic_targeting": {
                "locations": ["United States"],
                "radius_targeting": None,
                "excluded_locations": []
            },
            "products_services": "Products or services",
            "key_messages": ["Quality service", "Competitive pricing", "Expert team"],
            "keywords": {
                "primary": ["main keyword", "product keyword"],
                "negative": ["free", "cheap"]
            },
            "success_metrics": {
                "primary_kpi": "conversions",
                "targets": {"conversions": 50, "cpa": 100, "roas": 4.0}
            },
            "timeline": "Ongoing",
            "bidding_strategy": "Maximize conversions",
            "ad_schedule": "All day",
            "additional_notes": "Generated from conversation"
        }
    
    def _create_fallback_keywords(self, business_description: str) -> Dict[str, Any]:
        """Create fallback keywords"""
        return {
            "broad_keywords": [
                {"keyword": business_description.lower(), "match_type": "broad", "search_volume": "medium", "competition": "medium"},
                {"keyword": f"{business_description.lower()} services", "match_type": "broad", "search_volume": "medium", "competition": "medium"}
            ],
            "phrase_keywords": [
                {"keyword": f'"{business_description.lower()}"', "match_type": "phrase", "search_volume": "low", "competition": "low"},
                {"keyword": f'"best {business_description.lower()}"', "match_type": "phrase", "search_volume": "low", "competition": "medium"}
            ],
            "exact_keywords": [
                {"keyword": f"[{business_description.lower()}]", "match_type": "exact", "search_volume": "low", "competition": "low"}
            ],
            "long_tail_keywords": [
                {"keyword": f"{business_description.lower()} near me", "match_type": "broad", "search_volume": "low", "competition": "low"},
                {"keyword": f"affordable {business_description.lower()} services", "match_type": "broad", "search_volume": "low", "competition": "low"}
            ],
            "negative_keywords": ["free", "cheap", "diy"]
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        return {
            'service': 'AI Agent Service',
            'status': 'healthy' if self.client.api_key else 'degraded',
            'backend': 'openrouter' if self.client.api_key else 'mock',
            'model': self.model,
            'capabilities': [
                'chat',
                'stream_chat',
                'campaign_brief_generation',
                'performance_analysis',
                'keyword_generation'
            ]
        }


# Global service instance
ai_agent_service = AIAgentService()