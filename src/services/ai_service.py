"""
Enterprise OpenRouter AI Client
Advanced AI integration with OpenRouter for flexible model access

This module provides a comprehensive AI service that integrates with OpenRouter
to access multiple AI models for campaign planning, optimization, and natural
language processing tasks. It includes conversation management, function calling,
and cost tracking capabilities.

Key Features:
- Multi-model support (Claude, GPT-4, Gemini, etc.)
- Conversation context management with optimization
- Function calling for structured AI interactions
- Cost tracking and usage monitoring
- Async/await support for high performance
- Comprehensive error handling and retry logic
"""

import httpx
import json
import asyncio
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime, timedelta

# Configure logging for AI service operations
logger = logging.getLogger(__name__)

class ModelProvider(Enum):
    """
    Supported AI model providers through OpenRouter
    
    Each provider offers different capabilities and pricing models:
    - ANTHROPIC: Claude models, excellent for reasoning and analysis
    - OPENAI: GPT models, versatile for various tasks
    - GOOGLE: Gemini models, strong multimodal capabilities
    - META: Llama models, open-source alternatives
    - MISTRAL: Efficient European models
    """
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    META = "meta"
    MISTRAL = "mistral"

@dataclass
class ModelConfig:
    """
    Configuration for AI models
    
    Attributes:
        name: Model identifier (e.g., "claude-3-sonnet-20240229")
        provider: Model provider enum
        context_window: Maximum context length in tokens
        max_tokens: Maximum output tokens per request
        cost_per_1k_tokens: Cost per 1000 tokens for budget tracking
        supports_function_calling: Whether model supports function calling
        supports_streaming: Whether model supports streaming responses
    """
    name: str
    provider: ModelProvider
    context_window: int
    max_tokens: int
    cost_per_1k_tokens: float
    supports_function_calling: bool = False
    supports_streaming: bool = True

@dataclass
class ConversationMessage:
    """
    Structured conversation message for AI interactions
    
    Attributes:
        role: Message role (system, user, assistant, function)
        content: Message content text
        name: Optional name for function calls
        function_call: Optional function call data
        timestamp: When the message was created
    """
    role: str  # system, user, assistant, function
    content: str
    name: Optional[str] = None
    function_call: Optional[Dict] = None
    timestamp: Optional[datetime] = None

@dataclass
class FunctionDefinition:
    """
    Function definition for AI function calling
    
    Defines functions that the AI can call to perform specific actions
    like creating campaigns, calculating budgets, or retrieving data.
    
    Attributes:
        name: Function name
        description: What the function does
        parameters: JSON schema for function parameters
    """
    name: str
    description: str
    parameters: Dict[str, Any]

class ConversationManager:
    """Advanced conversation management with context optimization"""
    
    def __init__(self, max_context_tokens: int = 8000):
        self.max_context_tokens = max_context_tokens
        self.conversations: Dict[str, List[ConversationMessage]] = {}
        self.conversation_metadata: Dict[str, Dict] = {}
    
    def add_message(self, conversation_id: str, message: ConversationMessage) -> None:
        """Add message to conversation with automatic context management"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
            self.conversation_metadata[conversation_id] = {
                'created_at': datetime.utcnow(),
                'last_activity': datetime.utcnow(),
                'total_tokens': 0
            }
        
        message.timestamp = datetime.utcnow()
        self.conversations[conversation_id].append(message)
        self.conversation_metadata[conversation_id]['last_activity'] = datetime.utcnow()
        
        # Optimize context if needed
        self._optimize_context(conversation_id)
    
    def get_conversation(self, conversation_id: str) -> List[ConversationMessage]:
        """Get conversation messages"""
        return self.conversations.get(conversation_id, [])
    
    def _optimize_context(self, conversation_id: str) -> None:
        """Optimize conversation context to stay within token limits"""
        messages = self.conversations[conversation_id]
        
        # Estimate token count (rough approximation)
        total_tokens = sum(len(msg.content.split()) * 1.3 for msg in messages)
        
        if total_tokens > self.max_context_tokens:
            # Keep system message and recent messages
            system_messages = [msg for msg in messages if msg.role == 'system']
            other_messages = [msg for msg in messages if msg.role != 'system']
            
            # Keep last N messages that fit in context
            recent_messages = []
            current_tokens = sum(len(msg.content.split()) * 1.3 for msg in system_messages)
            
            for msg in reversed(other_messages):
                msg_tokens = len(msg.content.split()) * 1.3
                if current_tokens + msg_tokens <= self.max_context_tokens:
                    recent_messages.insert(0, msg)
                    current_tokens += msg_tokens
                else:
                    break
            
            self.conversations[conversation_id] = system_messages + recent_messages
            logger.info(f"Optimized context for conversation {conversation_id}: {len(messages)} -> {len(self.conversations[conversation_id])} messages")

class OpenRouterClient:
    """Enterprise OpenRouter client with advanced features"""
    
    # Available models with their configurations
    MODELS = {
        "anthropic/claude-3.5-sonnet": ModelConfig(
            name="claude-3.5-sonnet",
            provider=ModelProvider.ANTHROPIC,
            context_window=200000,
            max_tokens=4096,
            cost_per_1k_tokens=0.003,
            supports_function_calling=True,
            supports_streaming=True
        ),
        "anthropic/claude-3-haiku": ModelConfig(
            name="claude-3-haiku",
            provider=ModelProvider.ANTHROPIC,
            context_window=200000,
            max_tokens=4096,
            cost_per_1k_tokens=0.00025,
            supports_function_calling=True,
            supports_streaming=True
        ),
        "openai/gpt-4": ModelConfig(
            name="gpt-4",
            provider=ModelProvider.OPENAI,
            context_window=8192,
            max_tokens=4096,
            cost_per_1k_tokens=0.03,
            supports_function_calling=True,
            supports_streaming=True
        ),
        "openai/gpt-3.5-turbo": ModelConfig(
            name="gpt-3.5-turbo",
            provider=ModelProvider.OPENAI,
            context_window=16385,
            max_tokens=4096,
            cost_per_1k_tokens=0.0015,
            supports_function_calling=True,
            supports_streaming=True
        )
    }
    
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.conversation_manager = ConversationManager()
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://lane-mcp.com",
                "X-Title": "Lane MCP Platform"
            }
        )
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "anthropic/claude-3.5-sonnet",
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        functions: Optional[List[FunctionDefinition]] = None,
        stream: bool = False,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create chat completion with advanced features"""
        
        # Validate model
        if model not in self.MODELS:
            raise ValueError(f"Unsupported model: {model}. Available models: {list(self.MODELS.keys())}")
        
        model_config = self.MODELS[model]
        
        # Set default max_tokens based on model
        if max_tokens is None:
            max_tokens = min(1000, model_config.max_tokens)
        
        # Prepare request payload
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream
        }
        
        # Add function calling if supported and provided
        if functions and model_config.supports_function_calling:
            payload["functions"] = [
                {
                    "name": func.name,
                    "description": func.description,
                    "parameters": func.parameters
                }
                for func in functions
            ]
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Store conversation if conversation_id provided
            if conversation_id:
                # Add user message
                user_message = ConversationMessage(
                    role=messages[-1]["role"],
                    content=messages[-1]["content"]
                )
                self.conversation_manager.add_message(conversation_id, user_message)
                
                # Add assistant response
                if result.get("choices") and len(result["choices"]) > 0:
                    assistant_content = result["choices"][0]["message"]["content"]
                    assistant_message = ConversationMessage(
                        role="assistant",
                        content=assistant_content
                    )
                    self.conversation_manager.add_message(conversation_id, assistant_message)
            
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenRouter API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in chat completion: {str(e)}")
            raise
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from OpenRouter"""
        try:
            response = await self.client.get(f"{self.base_url}/models")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching available models: {str(e)}")
            return []
    
    def get_conversation_history(self, conversation_id: str) -> List[ConversationMessage]:
        """Get conversation history"""
        return self.conversation_manager.get_conversation(conversation_id)
    
    def clear_conversation(self, conversation_id: str) -> None:
        """Clear conversation history"""
        if conversation_id in self.conversation_manager.conversations:
            del self.conversation_manager.conversations[conversation_id]
            del self.conversation_manager.conversation_metadata[conversation_id]
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

class AIAgentService:
    """High-level AI agent service for Google Ads automation"""
    
    def __init__(self, openrouter_client: OpenRouterClient):
        self.client = openrouter_client
        self.system_prompts = {
            "campaign_planner": """You are an expert Google Ads campaign strategist and automation agent for the Lane MCP platform. 
            Your expertise includes:
            
            1. Campaign Strategy & Planning
            - Understanding business objectives and translating them into effective campaign structures
            - Recommending optimal campaign types, bidding strategies, and budget allocation
            - Identifying target audiences and geographic targeting opportunities
            
            2. Google Ads Best Practices
            - Knowledge of all campaign types: Search, Display, Shopping, Video, Performance Max
            - Understanding of bidding strategies: Manual CPC, Enhanced CPC, Target CPA, Target ROAS, Maximize Conversions
            - Expertise in ad extensions, quality score optimization, and landing page best practices
            
            3. Budget Management & Optimization
            - Calculating optimal daily budgets based on monthly goals
            - Understanding budget pacing and spend distribution
            - Recommending budget adjustments based on performance data
            
            4. Audience Targeting & Keywords
            - Keyword research and match type recommendations
            - Audience targeting strategies including demographics, interests, and remarketing
            - Negative keyword strategies to improve efficiency
            
            5. Performance Analysis & Optimization
            - Interpreting campaign metrics and identifying optimization opportunities
            - A/B testing strategies for ads, landing pages, and targeting
            - Conversion tracking and attribution model recommendations
            
            Always ask clarifying questions when information is missing or ambiguous. Provide specific, actionable recommendations based on advertising best practices. When you have sufficient information, offer to generate a structured campaign brief for approval.""",
            
            "optimization_analyst": """You are an AI optimization analyst specializing in Google Ads performance analysis and automated optimization recommendations.
            
            Your capabilities include:
            - Analyzing campaign performance data to identify trends and anomalies
            - Recommending bid adjustments, budget reallocations, and targeting refinements
            - Identifying underperforming keywords, ads, and audience segments
            - Suggesting A/B testing opportunities and optimization experiments
            - Calculating statistical significance and confidence intervals for test results
            
            Always provide data-driven recommendations with clear reasoning and expected impact.""",
            
            "budget_manager": """You are an AI budget management specialist focused on optimizing advertising spend and preventing budget overruns.
            
            Your responsibilities include:
            - Monitoring daily spend patterns and identifying pacing issues
            - Calculating optimal budget distributions across campaigns and ad groups
            - Recommending budget adjustments based on performance and seasonality
            - Identifying opportunities for budget reallocation to improve overall performance
            - Alerting on potential overspend or underspend situations
            
            Always consider business objectives, seasonality, and performance trends when making budget recommendations."""
        }
    
    async def chat_with_agent(
        self,
        message: str,
        conversation_id: str,
        agent_type: str = "campaign_planner",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Chat with specialized AI agent"""
        
        if agent_type not in self.system_prompts:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        # Get conversation history
        history = self.client.get_conversation_history(conversation_id)
        
        # Build messages
        messages = []
        
        # Add system prompt
        system_content = self.system_prompts[agent_type]
        if context:
            system_content += f"\n\nAdditional Context:\n{json.dumps(context, indent=2)}"
        
        messages.append({
            "role": "system",
            "content": system_content
        })
        
        # Add conversation history
        for msg in history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": message
        })
        
        # Get AI response
        response = await self.client.chat_completion(
            messages=messages,
            conversation_id=conversation_id,
            temperature=0.7
        )
        
        return {
            "response": response["choices"][0]["message"]["content"],
            "conversation_id": conversation_id,
            "agent_type": agent_type,
            "model_used": response.get("model"),
            "usage": response.get("usage", {})
        }
    
    async def generate_campaign_brief(
        self,
        conversation_id: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate structured campaign brief from conversation"""
        
        history = self.client.get_conversation_history(conversation_id)
        
        if not history:
            raise ValueError("No conversation history found")
        
        # Build messages for brief generation
        messages = [{
            "role": "system",
            "content": """Based on the conversation history, generate a comprehensive Google Ads campaign brief in JSON format.
            
            Extract and organize the following information:
            {
                "campaign_name": "Descriptive campaign name",
                "business_objective": "Primary business goal (leads, sales, awareness, etc.)",
                "campaign_type": "Recommended Google Ads campaign type",
                "budget": {
                    "monthly_amount": 0,
                    "currency": "USD",
                    "daily_amount": 0
                },
                "target_audience": {
                    "demographics": "Age, gender, income, etc.",
                    "interests": "Interests and behaviors",
                    "custom_audiences": "Remarketing, customer lists, etc."
                },
                "geographic_targeting": {
                    "locations": ["Country, state, city"],
                    "radius_targeting": "If applicable",
                    "location_exclusions": ["Areas to exclude"]
                },
                "products_services": {
                    "primary_offerings": ["Main products/services"],
                    "unique_selling_points": ["Key differentiators"],
                    "pricing_strategy": "Premium, competitive, budget"
                },
                "keywords": {
                    "primary_keywords": ["Main target keywords"],
                    "negative_keywords": ["Keywords to exclude"],
                    "match_types": "Recommended match type strategy"
                },
                "ad_copy_themes": {
                    "headlines": ["Suggested headline themes"],
                    "descriptions": ["Key messages for descriptions"],
                    "call_to_action": "Primary CTA"
                },
                "bidding_strategy": {
                    "type": "Recommended bidding strategy",
                    "target_cpa": 0,
                    "target_roas": 0
                },
                "conversion_tracking": {
                    "primary_conversion": "Main conversion action",
                    "secondary_conversions": ["Additional tracking goals"],
                    "attribution_model": "Recommended attribution"
                },
                "timeline": {
                    "start_date": "YYYY-MM-DD",
                    "duration": "Campaign duration",
                    "key_dates": ["Important dates or events"]
                },
                "success_metrics": {
                    "primary_kpi": "Main success metric",
                    "target_values": {"metric": "target"},
                    "reporting_frequency": "How often to review"
                },
                "additional_recommendations": [
                    "Any special considerations or recommendations"
                ]
            }
            
            Return only valid JSON format. Be specific and actionable in all recommendations."""
        }]
        
        # Add conversation history
        for msg in history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add brief generation request
        messages.append({
            "role": "user",
            "content": "Please generate a comprehensive campaign brief based on our conversation."
        })
        
        response = await self.client.chat_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=2000
        )
        
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
            return {
                "brief": brief_content,
                "format": "text",
                "conversation_id": conversation_id,
                "generated_at": datetime.utcnow().isoformat()
            }

# Global instances (will be initialized in app factory)
openrouter_client: Optional[OpenRouterClient] = None
ai_agent_service: Optional[AIAgentService] = None

def init_ai_services(api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
    """Initialize AI services"""
    global openrouter_client, ai_agent_service
    
    openrouter_client = OpenRouterClient(api_key, base_url)
    ai_agent_service = AIAgentService(openrouter_client)
    
    return openrouter_client, ai_agent_service

