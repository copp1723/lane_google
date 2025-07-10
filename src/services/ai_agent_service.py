"""
AI Agent Service
Provides AI-powered campaign generation and chat functionality
"""

import logging
import os
from typing import Dict, List, Optional, Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class AIAgentService:
    """AI Agent service for campaign generation and chat"""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client"""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                logger.warning("OpenAI API key not found in environment variables")
                return
            
            self.client = OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            self.client = None
    
    def chat(self, message: str, conversation_history: List[Dict] = None, 
             context_type: str = "general") -> Dict[str, Any]:
        """Chat with AI agent"""
        if not self.client:
            return {
                'success': False,
                'error': 'AI service not available - OpenAI API key not configured'
            }
        
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
            
            # Make API call
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return {
                'success': True,
                'response': response.choices[0].message.content,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"AI chat error: {str(e)}")
            return {
                'success': False,
                'error': f'AI service error: {str(e)}'
            }
    
    def generate_campaign_brief(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Generate structured campaign brief from conversation"""
        if not self.client:
            return {
                'success': False,
                'error': 'AI service not available - OpenAI API key not configured'
            }
        
        try:
            system_prompt = """Based on the conversation history, generate a structured Google Ads campaign brief in JSON format.
            
            Extract and organize the following information:
            - campaign_name: A descriptive name for the campaign
            - objective: Primary campaign goal (leads, sales, awareness, etc.)
            - budget: Monthly budget amount and currency
            - target_audience: Description of target customers
            - geographic_targeting: Locations to target
            - products_services: What is being advertised
            - key_messages: Main selling points or value propositions
            - success_metrics: How success will be measured
            - timeline: Campaign duration or start date
            - additional_notes: Any special requirements or considerations
            
            Return only valid JSON format."""
            
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(conversation_history)
            messages.append({
                "role": "user", 
                "content": "Please generate a structured campaign brief based on our conversation."
            })
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=1500,
                temperature=0.3
            )
            
            brief_content = response.choices[0].message.content
            
            # Try to parse as JSON
            try:
                import json
                brief_json = json.loads(brief_content)
                return {
                    'success': True,
                    'brief': brief_json,
                    'format': 'json'
                }
            except json.JSONDecodeError:
                return {
                    'success': True,
                    'brief': brief_content,
                    'format': 'text'
                }
                
        except Exception as e:
            logger.error(f"Campaign brief generation error: {str(e)}")
            return {
                'success': False,
                'error': f'Brief generation error: {str(e)}'
            }
    
    def analyze_campaign_performance(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze campaign performance and provide recommendations"""
        if not self.client:
            return {
                'success': False,
                'error': 'AI service not available - OpenAI API key not configured'
            }
        
        try:
            system_prompt = """You are a Google Ads performance analyst. Analyze the provided campaign 
            data and provide actionable recommendations for optimization."""
            
            analysis_prompt = f"""
            Analyze this campaign performance data and provide recommendations:
            
            {campaign_data}
            
            Please provide:
            1. Performance assessment (good/needs improvement/poor)
            2. Key insights and trends
            3. Specific optimization recommendations
            4. Priority actions to take
            5. Expected impact of recommendations
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": analysis_prompt}
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=1200,
                temperature=0.4
            )
            
            return {
                'success': True,
                'analysis': response.choices[0].message.content
            }
            
        except Exception as e:
            logger.error(f"Performance analysis error: {str(e)}")
            return {
                'success': False,
                'error': f'Analysis error: {str(e)}'
            }
    
    def generate_keywords(self, business_description: str, target_audience: str = None) -> Dict[str, Any]:
        """Generate keyword suggestions for campaigns"""
        if not self.client:
            return {
                'success': False,
                'error': 'AI service not available - OpenAI API key not configured'
            }
        
        try:
            system_prompt = """You are a Google Ads keyword research specialist. Generate relevant 
            keywords for the given business and target audience."""
            
            keyword_prompt = f"""
            Generate keyword suggestions for:
            Business: {business_description}
            Target Audience: {target_audience or 'General audience'}
            
            Provide keywords in these categories:
            1. Broad keywords (high volume, competitive)
            2. Specific keywords (medium volume, targeted)
            3. Long-tail keywords (low volume, highly specific)
            4. Branded keywords (if applicable)
            
            Format as JSON with match types (broad, phrase, exact).
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": keyword_prompt}
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=1000,
                temperature=0.5
            )
            
            return {
                'success': True,
                'keywords': response.choices[0].message.content
            }
            
        except Exception as e:
            logger.error(f"Keyword generation error: {str(e)}")
            return {
                'success': False,
                'error': f'Keyword generation error: {str(e)}'
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        return {
            'service': 'AI Agent Service',
            'status': 'healthy' if self.client else 'degraded',
            'openai_configured': bool(self.client),
            'capabilities': [
                'chat',
                'campaign_brief_generation',
                'performance_analysis',
                'keyword_generation'
            ]
        }


# Global service instance
ai_agent_service = AIAgentService()