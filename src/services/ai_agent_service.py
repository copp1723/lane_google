"""
AI Agent Service
Provides AI-powered campaign generation and chat functionality with response caching
"""

import logging
import os
import time
import hashlib
import json
from typing import Dict, List, Optional, Any, Tuple
import requests
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()
logger = logging.getLogger(__name__)


class ResponseCache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self, ttl: int = 3600, max_size: int = 100):
        self.cache = {}
        self.ttl = ttl
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def _generate_key(self, message: str, context_type: str) -> str:
        """Generate a unique cache key from request parameters"""
        content = f"{message}:{context_type}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, message: str, context_type: str) -> Optional[Dict]:
        """Get cached response if available and not expired"""
        key = self._generate_key(message, context_type)
        
        if key in self.cache:
            response, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                self.hits += 1
                logger.debug(f"Cache hit for key {key[:8]}... (hits: {self.hits}, misses: {self.misses})")
                return response
            else:
                # Expired entry, remove it
                del self.cache[key]
                logger.debug(f"Cache entry expired for key {key[:8]}...")
        
        self.misses += 1
        return None
    
    def set(self, message: str, context_type: str, response: Dict):
        """Store response in cache"""
        key = self._generate_key(message, context_type)
        
        # Implement LRU eviction if cache is full
        if len(self.cache) >= self.max_size:
            # Remove oldest entries (20% of cache)
            entries_to_remove = max(1, self.max_size // 5)
            sorted_items = sorted(self.cache.items(), key=lambda x: x[1][1])
            for old_key, _ in sorted_items[:entries_to_remove]:
                del self.cache[old_key]
                logger.debug(f"Evicted old cache entry {old_key[:8]}...")
        
        self.cache[key] = (response, time.time())
        logger.debug(f"Cached response for key {key[:8]}... (cache size: {len(self.cache)})")
    
    def clear(self):
        """Clear all cached responses"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.1f}%",
            'ttl': self.ttl
        }


class AIAgentService:
    """AI Agent service for campaign generation and chat with caching"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY') or os.getenv('OPENAI_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://lane-google.onrender.com",
            "X-Title": "Lane MCP Google Ads Agent",
            "Content-Type": "application/json"
        }
        
        # Initialize cache with configurable TTL
        cache_ttl = int(os.getenv('AI_CACHE_TTL', '3600'))  # 1 hour default
        cache_size = int(os.getenv('AI_CACHE_SIZE', '100'))  # 100 entries default
        self.cache = ResponseCache(ttl=cache_ttl, max_size=cache_size)
        
        if not self.api_key:
            logger.warning("OpenRouter API key not found in environment variables")
        else:
            logger.info(f"OpenRouter client initialized with cache (TTL: {cache_ttl}s, Size: {cache_size})")
    
    def _make_api_call(self, message: str, conversation_history: List[Dict], 
                       context_type: str) -> Dict[str, Any]:
        """Make the actual API call to OpenRouter"""
        try:
            # System prompts based on context
            system_prompts = {
                "general": """You are Lane MCP, an autonomous Google Ads operations AI that transforms plain-language business goals into optimized campaigns while maintaining 24/7 vigilance over performance and spend.

🎯 Primary Directive
Operate as a proactive, always-on advertising specialist that eliminates manual grind while maintaining human oversight for critical decisions. Your goal: 95-100% budget utilization with ±5% accuracy, zero overspends, and <15 minutes from brief to live campaign.

🧠 Core Operating Principles
1. Autonomous Campaign Operations
   - Convert goals to campaigns in <15 minutes with full policy compliance
   - Auto-generate keywords, ad copy, budgets, and tracking configurations
   - Maintain complete audit trails for every action taken
   - Request human approval only at critical decision points

2. Intelligent Budget Management
   - Monitor accounts every 2 hours using ML-based pacing algorithms
   - Maintain spend accuracy within ±5% of target
   - Auto-pause at budget limits to prevent overspends
   - Redistribute underperforming budget automatically with notification

3. Proactive Issue Resolution
   - Detect anomalies before they impact performance
   - Auto-remediate routine issues (disapprovals, feed errors, zero spend)
   - Escalate complex issues with pre-diagnosed solutions
   - Maintain <30 minute average resolution time

4. Performance Intelligence
   - Generate plain-language insights, not spreadsheet dumps
   - Identify waste and opportunities proactively
   - Provide trend analysis with actionable next steps
   - Track success metrics: CTR, CPC, CPA, ROAS, inventory velocity

📊 Operational Workflows
Phase 1: Goal Capture & Clarification
Example:
User: "Push used Toyota SUVs this weekend, $1,500 budget in Houston"
You: "Campaign brief confirmed:
- Target: Used Toyota RAV4, Highlander (2020-2024)
- Geo: Houston DMA + 25mi radius
- Budget: $500/day Fri-Sun
- Keywords: 24 high-intent terms identified
- Ad copy: 3 responsive ads emphasizing weekend pricing
- Tracking: Form fills + calls from ads
Ready to launch? [Approve/Edit/Cancel]"

📝 Communication Standards
Always Include:
- Current spend vs. budget ($ and %)
- Pacing status (on-track/ahead/behind)
- Performance delta from previous period
- Specific next action with impact estimate

Remember: You're not just a tool—you're the competitive edge that lets operators manage 10x more accounts with higher consistency and total budget control. Be proactive, be precise, and always prioritize performance.""",
                
                "campaign_generation": """You are Lane MCP's Campaign Generation specialist. Your role is to transform plain-language business goals into fully-configured Google Ads campaigns in under 15 minutes.

🎯 Your Mission
Convert automotive advertising goals into launch-ready campaigns with zero manual configuration needed. Focus on dealership-specific needs: inventory turnover, service appointments, and seasonal promotions.

📋 Campaign Brief Workflow
1. Goal Extraction
   - Parse natural language for: budget, timeline, target vehicles/services, geographic area
   - Identify campaign type: inventory push, service special, brand awareness, event promotion
   - Determine urgency level and pacing requirements

2. Automatic Configuration
   - Generate 20-30 high-intent keywords with match types
   - Create 3-5 responsive search ads with automotive-specific CTAs
   - Set bid strategies based on goal (Max Conversions for leads, Target ROAS for sales)
   - Configure location targeting with dealership-appropriate radius
   - Set up conversion tracking for forms, calls, and directions

3. Compliance & Best Practices
   - Ensure all ads include required disclaimers (pricing, availability, etc.)
   - Validate against Google Ads automotive policies
   - Check for trademark conflicts with manufacturer guidelines
   - Include dynamic inventory feeds where applicable

🚗 Automotive-Specific Intelligence
- Understand model years, trim levels, and inventory categories
- Know seasonal patterns (tax season, model year-end, holidays)
- Recognize co-op advertising requirements
- Account for manufacturer incentives and restrictions

Remember: Every second saved in setup is a second earning for the dealership. Be fast, be accurate, be ready to launch.""",
                
                "discovery_analysis": """You are Lane MCP's Market Intelligence Analyst. Your role is to analyze automotive market conditions and provide actionable insights for campaign optimization.

🔍 Analysis Framework
1. Competitive Landscape
   - Monitor competing dealerships' digital presence
   - Track auction insights for bid competition
   - Identify market share opportunities
   - Analyze seasonal and regional trends

2. Audience Intelligence
   - Profile in-market automotive shoppers
   - Identify high-value customer segments
   - Track purchase journey touchpoints
   - Understand local market preferences

3. Inventory Alignment
   - Match campaign focus to available inventory
   - Identify slow-moving stock for targeted pushes
   - Highlight high-margin opportunities
   - Sync with manufacturer promotions

4. Performance Benchmarking
   - Compare metrics to automotive industry standards
   - Track cost-per-lead by vehicle category
   - Monitor conversion rates by campaign type
   - Identify optimization opportunities

📈 Insight Delivery
Provide insights that are:
- Specific to automotive retail
- Actionable within 24-48 hours
- Tied to revenue impact
- Supported by data trends
- Formatted for quick decisions

Remember: Great analysis drives great campaigns. Focus on insights that directly impact inventory turnover and service revenue.""",
                
                "strategy_planning": """You are Lane MCP's Strategic Campaign Architect. Your role is to design comprehensive Google Ads strategies that align with dealership business objectives.

🎯 Strategic Framework
1. Business Goal Alignment
   - Map campaigns to sales targets and inventory needs
   - Balance new vs. used, sales vs. service
   - Account for manufacturer requirements
   - Plan for seasonal fluctuations

2. Campaign Architecture
   - Design account structure for maximum efficiency
   - Set up shared budgets for flexible spending
   - Configure bid strategies by objective
   - Plan negative keyword lists proactively

3. Full-Funnel Approach
   - Awareness: Model/brand campaigns
   - Consideration: Comparison and research terms
   - Decision: VIN-specific and incentive ads
   - Retention: Service and loyalty campaigns

4. Budget Optimization
   - Allocate spend based on historical performance
   - Plan for day-of-week and time-of-day adjustments
   - Account for month-end push periods
   - Reserve budget for opportunistic campaigns

Remember: Strategy without execution is hallucination. Every plan must be actionable, measurable, and tied to dealership revenue.""",
                
                "campaign_review": """You are Lane MCP's Quality Assurance Specialist. Your role is to ensure all campaigns meet Google Ads policies, automotive best practices, and performance standards.

✅ Review Checklist
1. Policy Compliance
   - Google Ads automotive policies
   - Manufacturer advertising guidelines  
   - Legal disclaimers and disclosures
   - Trademark and copyright usage

2. Technical Setup
   - Conversion tracking implementation
   - Landing page experience scores
   - Mobile optimization status
   - Feed connectivity and accuracy

3. Performance Optimization
   - Keyword Quality Scores
   - Ad Relevance ratings
   - Landing page alignment
   - Negative keyword coverage

4. Budget Efficiency
   - Bid strategy appropriateness
   - Geographic waste elimination
   - Dayparting optimization
   - Search term relevance

🚨 Red Flags to Catch
- Missing price disclaimers
- Expired promotional dates
- Broken inventory links
- Overlapping keyword conflicts
- Insufficient negative keywords
- Poor mobile experience

Remember: Perfect campaigns prevent problems. Your review is the last line of defense against wasted spend and compliance issues."""
            }
            
            system_prompt = system_prompts.get(context_type, system_prompts["general"])
            
            # Build messages
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history)
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Make API call to OpenRouter
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": "anthropic/claude-3.5-sonnet",
                    "messages": messages,
                    "max_tokens": 2000,
                    "temperature": 0.7
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'response': data['choices'][0]['message']['content'],
                    'usage': data.get('usage', {}),
                    'from_cache': False
                }
            else:
                return {
                    'success': False,
                    'error': f'OpenRouter API error: {response.status_code} - {response.text}'
                }
            
        except Exception as e:
            logger.error(f"AI API call error: {str(e)}")
            return {
                'success': False,
                'error': f'AI service error: {str(e)}'
            }
    
    def chat(self, message: str, conversation_history: List[Dict] = None, 
             context_type: str = "general", use_cache: bool = True) -> Dict[str, Any]:
        """Chat with AI agent with optional caching"""
        if not self.api_key:
            return {
                'success': False,
                'error': 'AI service not available - OpenRouter API key not configured'
            }
        
        try:
            # Check cache for simple queries without conversation history
            if use_cache and not conversation_history:
                cached_response = self.cache.get(message, context_type)
                if cached_response:
                    # Add cache indicator to response
                    cached_response['from_cache'] = True
                    cached_response['cache_stats'] = self.cache.get_stats()
                    logger.info(f"Returning cached response for query: {message[:50]}...")
                    return cached_response
            
            # Make API call if not cached
            response = self._make_api_call(message, conversation_history, context_type)
            
            # Cache successful responses for simple queries
            if use_cache and response.get('success') and not conversation_history:
                self.cache.set(message, context_type, response)
            
            # Add cache stats to response
            response['cache_stats'] = self.cache.get_stats()
            
            return response
            
        except Exception as e:
            logger.error(f"AI chat error: {str(e)}")
            return {
                'success': False,
                'error': f'AI service error: {str(e)}'
            }
    
    def generate_campaign_brief(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Generate structured campaign brief from conversation"""
        if not self.api_key:
            return {
                'success': False,
                'error': 'AI service not available - OpenRouter API key not configured'
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
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": "anthropic/claude-3.5-sonnet",
                    "messages": messages,
                    "max_tokens": 2000,
                    "temperature": 0.3
                }
            )
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'OpenRouter API error: {response.status_code} - {response.text}'
                }
                
            brief_content = response.json()['choices'][0]['message']['content']
            
            # Try to parse as JSON
            try:
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
        if not self.api_key:
            return {
                'success': False,
                'error': 'AI service not available - OpenRouter API key not configured'
            }
        
        try:
            # Create a cache key for performance analysis
            cache_key = json.dumps(campaign_data, sort_keys=True)
            context_type = "performance_analysis"
            
            # Check cache
            if hasattr(self, 'cache'):
                cached_response = self.cache.get(cache_key, context_type)
                if cached_response:
                    cached_response['from_cache'] = True
                    return cached_response
            
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
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": "anthropic/claude-3.5-sonnet",
                    "messages": messages,
                    "max_tokens": 2000,
                    "temperature": 0.4
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    'success': True,
                    'analysis': data['choices'][0]['message']['content'],
                    'from_cache': False
                }
                
                # Cache the result
                if hasattr(self, 'cache'):
                    self.cache.set(cache_key, context_type, result)
                
                return result
            else:
                return {
                    'success': False,
                    'error': f'OpenRouter API error: {response.status_code} - {response.text}'
                }
            
        except Exception as e:
            logger.error(f"Performance analysis error: {str(e)}")
            return {
                'success': False,
                'error': f'Analysis error: {str(e)}'
            }
    
    def generate_keywords(self, business_description: str, target_audience: str = None,
                         use_cache: bool = True) -> Dict[str, Any]:
        """Generate keyword suggestions for campaigns with caching"""
        if not self.api_key:
            return {
                'success': False,
                'error': 'AI service not available - OpenRouter API key not configured'
            }
        
        try:
            # Check cache
            cache_key = f"{business_description}:{target_audience or 'general'}"
            if use_cache:
                cached_response = self.cache.get(cache_key, "keyword_generation")
                if cached_response:
                    cached_response['from_cache'] = True
                    return cached_response
            
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
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": "anthropic/claude-3.5-sonnet",
                    "messages": messages,
                    "max_tokens": 1500,
                    "temperature": 0.5
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    'success': True,
                    'keywords': data['choices'][0]['message']['content'],
                    'from_cache': False
                }
                
                # Cache the result
                if use_cache:
                    self.cache.set(cache_key, "keyword_generation", result)
                
                return result
            else:
                return {
                    'success': False,
                    'error': f'OpenRouter API error: {response.status_code} - {response.text}'
                }
            
        except Exception as e:
            logger.error(f"Keyword generation error: {str(e)}")
            return {
                'success': False,
                'error': f'Keyword generation error: {str(e)}'
            }
    
    def clear_cache(self):
        """Clear the response cache"""
        self.cache.clear()
        return {'success': True, 'message': 'Cache cleared successfully'}
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache.get_stats()
    
    def health_check(self) -> Dict[str, Any]:
        """Check service health including cache status"""
        cache_stats = self.cache.get_stats()
        
        return {
            'service': 'AI Agent Service',
            'status': 'healthy' if self.api_key else 'degraded',
            'openrouter_configured': bool(self.api_key),
            'cache': {
                'enabled': True,
                'stats': cache_stats
            },
            'capabilities': [
                'chat',
                'campaign_brief_generation',
                'performance_analysis',
                'keyword_generation',
                'response_caching'
            ]
        }


# Global service instance
ai_agent_service = AIAgentService()