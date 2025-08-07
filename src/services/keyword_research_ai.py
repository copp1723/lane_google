"""
AI-Powered Keyword Research Service
Automates keyword research and optimization using AI
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from src.services.google_ads_agent import GoogleAdsAgent, AgentRole, create_agent
from src.services.ai_agent_service import ai_agent_service

logger = logging.getLogger(__name__)


@dataclass
class KeywordMetrics:
    """Keyword performance metrics"""
    keyword: str
    match_type: str
    search_volume: str  # high/medium/low
    competition: str    # high/medium/low
    relevance_score: float
    commercial_intent: str  # high/medium/low
    estimated_cpc: Optional[float] = None
    trend: Optional[str] = None  # rising/stable/declining


class AIKeywordResearch:
    """AI-powered keyword research and optimization"""
    
    def __init__(self):
        self.strategist = create_agent(AgentRole.STRATEGIST)
        self.optimizer = create_agent(AgentRole.OPTIMIZER)
        self.base_service = ai_agent_service
        
    async def research_keywords(self, business_info: Dict[str, Any], 
                              target_market: Dict[str, Any] = None,
                              competitors: List[str] = None) -> Dict[str, Any]:
        """Comprehensive keyword research using AI"""
        try:
            # Step 1: Understand the business
            business_analysis = await self._analyze_business(business_info)
            
            # Step 2: Generate seed keywords
            seed_keywords = await self._generate_seed_keywords(
                business_analysis, target_market
            )
            
            # Step 3: Expand keywords
            expanded_keywords = await self._expand_keywords(
                seed_keywords, business_info
            )
            
            # Step 4: Analyze competitors
            if competitors:
                competitor_keywords = await self._analyze_competitor_keywords(
                    competitors, business_info
                )
                expanded_keywords['competitor_inspired'] = competitor_keywords
            
            # Step 5: Categorize and score keywords
            categorized = await self._categorize_keywords(expanded_keywords)
            
            # Step 6: Generate negative keywords
            negative_keywords = await self._generate_negative_keywords(
                categorized, business_info
            )
            
            # Step 7: Create keyword groups
            keyword_groups = await self._create_keyword_groups(categorized)
            
            # Step 8: Generate recommendations
            recommendations = await self._generate_recommendations(
                keyword_groups, business_info
            )
            
            return {
                'success': True,
                'analysis': business_analysis,
                'keywords': categorized,
                'negative_keywords': negative_keywords,
                'keyword_groups': keyword_groups,
                'recommendations': recommendations,
                'total_keywords': self._count_keywords(categorized),
                'research_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Keyword research failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _analyze_business(self, business_info: Dict[str, Any]) -> Dict[str, Any]:
        """Deep analysis of business for keyword insights"""
        prompt = f"""Analyze this business for keyword research insights:

{json.dumps(business_info, indent=2)}

Provide:
1. Core business themes and topics
2. Unique value propositions
3. Target customer search intent patterns
4. Industry-specific terminology
5. Service/product categories
6. Geographic relevance factors
7. Seasonal considerations

Return analysis as structured JSON."""
        
        response = await self.strategist.chat(prompt, "business_analysis")
        
        try:
            content = response['response'].strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            return json.loads(content.strip())
        except:
            return {
                'themes': ['general business'],
                'value_props': business_info.get('key_messages', []),
                'search_intents': ['informational', 'transactional'],
                'terminology': []
            }
    
    async def _generate_seed_keywords(self, business_analysis: Dict[str, Any],
                                    target_market: Dict[str, Any] = None) -> List[str]:
        """Generate initial seed keywords"""
        context = {
            'analysis': business_analysis,
            'target_market': target_market or {}
        }
        
        prompt = f"""Based on this business analysis, generate 20-30 seed keywords:

{json.dumps(context, indent=2)}

Focus on:
1. Primary business terms
2. Service/product names
3. Customer problem keywords
4. Solution-based keywords
5. Local intent keywords (if applicable)

Return as JSON array of keywords."""
        
        response = await self.strategist.chat(prompt, "seed_generation")
        
        try:
            content = response['response'].strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            return json.loads(content.strip())
        except:
            # Fallback seed keywords
            return [
                business_analysis.get('themes', ['business'])[0],
                f"{business_analysis.get('themes', ['business'])[0]} services",
                f"best {business_analysis.get('themes', ['business'])[0]}"
            ]
    
    async def _expand_keywords(self, seed_keywords: List[str], 
                             business_info: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """Expand seed keywords into comprehensive keyword sets"""
        prompt = f"""Expand these seed keywords into comprehensive keyword variations:

Seed Keywords:
{json.dumps(seed_keywords, indent=2)}

Business Context:
{json.dumps(business_info, indent=2)}

Generate keyword variations in these categories:
{{
    "broad_match": [
        {{"keyword": "example", "intent": "informational/transactional/navigational", "priority": "high/medium/low"}}
    ],
    "phrase_match": [
        {{"keyword": "example phrase", "intent": "...", "priority": "..."}}
    ],
    "exact_match": [
        {{"keyword": "[exact example]", "intent": "...", "priority": "..."}}
    ],
    "long_tail": [
        {{"keyword": "very specific example query", "intent": "...", "priority": "..."}}
    ],
    "question_based": [
        {{"keyword": "how to example", "intent": "informational", "priority": "..."}}
    ],
    "local_intent": [
        {{"keyword": "example near me", "intent": "transactional", "priority": "..."}}
    ]
}}

Generate 10-15 keywords per category. Return ONLY valid JSON."""
        
        response = await self.optimizer.chat(prompt, "keyword_expansion")
        
        try:
            content = response['response'].strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            return json.loads(content.strip())
        except:
            # Fallback expansion
            expanded = {}
            for category in ['broad_match', 'phrase_match', 'exact_match', 'long_tail']:
                expanded[category] = []
                for seed in seed_keywords[:3]:
                    expanded[category].append({
                        'keyword': seed if category == 'broad_match' else f'"{seed}"',
                        'intent': 'transactional',
                        'priority': 'medium'
                    })
            return expanded
    
    async def _analyze_competitor_keywords(self, competitors: List[str], 
                                         business_info: Dict[str, Any]) -> List[Dict]:
        """Analyze competitor keywords for opportunities"""
        prompt = f"""Analyze these competitors and suggest keywords they might be targeting:

Competitors:
{json.dumps(competitors, indent=2)}

Our Business:
{json.dumps(business_info, indent=2)}

Suggest:
1. Keywords competitors likely target
2. Gap opportunities they might miss
3. Differentiation keywords
4. Competitive advantage keywords

Return as JSON array with format:
[
    {{
        "keyword": "example",
        "strategy": "compete/differentiate/gap",
        "difficulty": "high/medium/low",
        "opportunity_score": 1-10
    }}
]"""
        
        response = await self.strategist.chat(prompt, "competitor_analysis")
        
        try:
            content = response['response'].strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            return json.loads(content.strip())
        except:
            return []
    
    async def _categorize_keywords(self, keywords: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Categorize and score keywords"""
        all_keywords = []
        for category, keyword_list in keywords.items():
            for kw_data in keyword_list:
                if isinstance(kw_data, dict):
                    all_keywords.append(kw_data)
        
        prompt = f"""Categorize and score these keywords for Google Ads:

{json.dumps(all_keywords, indent=2)}

For each keyword provide:
{{
    "keyword": "the keyword",
    "category": "brand/product/service/informational/competitor",
    "match_type": "broad/phrase/exact",
    "metrics": {{
        "search_volume": "high/medium/low",
        "competition": "high/medium/low",
        "commercial_intent": "high/medium/low",
        "relevance_score": 0.0-1.0,
        "priority": "high/medium/low"
    }},
    "recommended_bid": "aggressive/moderate/conservative",
    "ad_group_suggestion": "suggested ad group name"
}}

Return categorized keywords as JSON."""
        
        response = await self.optimizer.chat(prompt, "keyword_categorization")
        
        try:
            content = response['response'].strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            categorized = json.loads(content.strip())
            
            # Organize by category
            organized = {}
            for kw in categorized:
                category = kw.get('category', 'uncategorized')
                if category not in organized:
                    organized[category] = []
                organized[category].append(kw)
            
            return organized
        except:
            # Simple categorization fallback
            return {
                'general': all_keywords[:10]
            }
    
    async def _generate_negative_keywords(self, categorized_keywords: Dict[str, Any],
                                        business_info: Dict[str, Any]) -> List[str]:
        """Generate negative keywords to exclude irrelevant traffic"""
        prompt = f"""Generate negative keywords based on this keyword research:

Keywords:
{json.dumps(categorized_keywords, indent=2)}

Business Info:
{json.dumps(business_info, indent=2)}

Generate negative keywords to exclude:
1. Irrelevant search intents
2. Wrong audience segments
3. Competitor brand names (if not bidding on them)
4. Free/cheap seekers (if premium service)
5. DIY/Tutorial seekers (if professional service)
6. Wrong geographic locations
7. Irrelevant product/service variations

Return as JSON array of negative keywords."""
        
        response = await self.strategist.chat(prompt, "negative_generation")
        
        try:
            content = response['response'].strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            return json.loads(content.strip())
        except:
            # Default negative keywords
            return ['free', 'cheap', 'diy', 'tutorial', 'how to', 'jobs', 'careers']
    
    async def _create_keyword_groups(self, categorized_keywords: Dict[str, Any]) -> List[Dict]:
        """Organize keywords into ad groups"""
        prompt = f"""Organize these keywords into logical ad groups:

{json.dumps(categorized_keywords, indent=2)}

Create ad groups with:
{{
    "name": "Ad Group Name",
    "theme": "What this group focuses on",
    "keywords": [
        {{"text": "keyword", "match_type": "BROAD/PHRASE/EXACT"}}
    ],
    "negative_keywords": ["group-specific negatives"],
    "recommended_ads": 2-3,
    "landing_page_suggestion": "Type of landing page needed"
}}

Create 3-8 ad groups based on themes. Return as JSON array."""
        
        response = await self.optimizer.chat(prompt, "group_creation")
        
        try:
            content = response['response'].strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            return json.loads(content.strip())
        except:
            # Simple grouping fallback
            groups = []
            for category, keywords in categorized_keywords.items():
                if keywords:
                    groups.append({
                        'name': f"{category.title()} Keywords",
                        'theme': category,
                        'keywords': [
                            {'text': kw.get('keyword', kw), 'match_type': 'BROAD'}
                            for kw in keywords[:10]
                        ],
                        'negative_keywords': [],
                        'recommended_ads': 3
                    })
            return groups
    
    async def _generate_recommendations(self, keyword_groups: List[Dict],
                                      business_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate strategic recommendations"""
        prompt = f"""Generate keyword strategy recommendations:

Keyword Groups:
{json.dumps(keyword_groups, indent=2)}

Business Context:
{json.dumps(business_info, indent=2)}

Provide recommendations for:
1. Initial keyword testing strategy
2. Budget allocation across groups
3. Bid strategy per group
4. Expected performance benchmarks
5. Optimization timeline
6. Expansion opportunities

Format as actionable JSON recommendations."""
        
        response = await self.strategist.chat(prompt, "recommendations")
        
        try:
            content = response['response'].strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            return json.loads(content.strip())
        except:
            return {
                'testing_strategy': 'Start with high-priority keywords',
                'budget_allocation': 'Distribute evenly initially',
                'optimization_timeline': '2-week initial test, then optimize'
            }
    
    def _count_keywords(self, categorized: Dict[str, Any]) -> int:
        """Count total keywords"""
        total = 0
        for category, keywords in categorized.items():
            total += len(keywords)
        return total
    
    async def optimize_existing_keywords(self, performance_data: List[Dict],
                                       business_goals: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize existing keyword performance"""
        prompt = f"""Analyze keyword performance and provide optimization recommendations:

Performance Data:
{json.dumps(performance_data, indent=2)}

Business Goals:
{json.dumps(business_goals, indent=2)}

Provide:
1. Keywords to pause (poor performance)
2. Keywords to increase bids (high performance)
3. New keywords to test (based on search terms)
4. Match type adjustments
5. Negative keywords to add
6. Budget reallocation suggestions

Return structured optimization plan as JSON."""
        
        response = await self.optimizer.chat(prompt, "keyword_optimization")
        
        try:
            content = response['response'].strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            return {
                'success': True,
                'optimizations': json.loads(content.strip())
            }
        except:
            return {
                'success': True,
                'optimizations': {
                    'pause': [],
                    'increase_bids': [],
                    'new_keywords': [],
                    'add_negatives': []
                }
            }


# Global instance
ai_keyword_research = AIKeywordResearch()