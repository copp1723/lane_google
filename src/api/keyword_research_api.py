"""
Keyword Research API
Provides keyword research functionality using Google Keyword Planner API
"""

import logging
import os
from typing import Dict, List, Any, Optional
from flask import Blueprint, request, jsonify
from datetime import datetime
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

from src.auth.authentication import token_required as login_required, get_current_user
from src.utils.flask_responses import success_response, error_response

logger = logging.getLogger(__name__)

keyword_research_bp = Blueprint('keyword_research', __name__)


class KeywordResearchService:
    """Service for keyword research operations"""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Ads client"""
        try:
            from dotenv import load_dotenv
            load_dotenv()

            # Check for required environment variables
            required_vars = [
                'GOOGLE_ADS_CLIENT_ID',
                'GOOGLE_ADS_CLIENT_SECRET',
                'GOOGLE_ADS_REFRESH_TOKEN',
                'GOOGLE_ADS_DEVELOPER_TOKEN'
            ]

            missing_vars = [var for var in required_vars if not os.getenv(var)]
            if missing_vars:
                logger.error(f"Missing Google Ads API variables: {missing_vars}")
                return

            # Create configuration dict (consistent with other services)
            config = {
                "use_proto_plus": True,
                "developer_token": os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN'),
                "client_id": os.getenv('GOOGLE_ADS_CLIENT_ID'),
                "client_secret": os.getenv('GOOGLE_ADS_CLIENT_SECRET'),
                "refresh_token": os.getenv('GOOGLE_ADS_REFRESH_TOKEN'),
                "transport": "rest"  # Use REST transport to avoid gRPC issues
            }

            # Add login customer ID if available
            login_customer_id = os.getenv('GOOGLE_ADS_LOGIN_CUSTOMER_ID')
            if login_customer_id:
                config["login_customer_id"] = login_customer_id

            self.client = GoogleAdsClient.load_from_dict(config)
            logger.info("Google Ads client initialized for keyword research")

        except Exception as e:
            logger.error(f"Failed to initialize Google Ads client: {str(e)}")
            self.client = None
    
    def research_keywords(self, seed_keyword: str, customer_id: str, 
                         filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Research keywords using Google Keyword Planner"""
        if not self.client:
            return self._generate_demo_keywords(seed_keyword, filters)
        
        try:
            # Get keyword plan idea service
            keyword_plan_idea_service = self.client.get_service("KeywordPlanIdeaService")
            
            # Set up request
            request_payload = self.client.get_type("GenerateKeywordIdeasRequest")
            request_payload.customer_id = customer_id
            request_payload.language = self.client.get_type("LanguageConstant").name
            request_payload.geo_target_constants.append(
                self.client.get_type("GeoTargetConstant").name
            )
            
            # Set keyword seed
            request_payload.keyword_seed.keywords.append(seed_keyword)
            
            # Set filters if provided
            if filters:
                if filters.get('location') and filters['location'] != 'global':
                    # Set geographic targeting
                    location_id = self._get_location_id(filters['location'])
                    if location_id:
                        request_payload.geo_target_constants.clear()
                        request_payload.geo_target_constants.append(
                            f"geoTargetConstants/{location_id}"
                        )
            
            # Make the request
            response = keyword_plan_idea_service.generate_keyword_ideas(
                request=request_payload
            )
            
            # Process results
            keywords = []
            for idea in response:
                keyword_data = {
                    'id': f"kw_{hash(idea.text)}",
                    'keyword': idea.text,
                    'search_volume': idea.keyword_idea_metrics.avg_monthly_searches or 0,
                    'cpc': (idea.keyword_idea_metrics.high_top_of_page_bid_micros or 0) / 1_000_000,
                    'competition': self._map_competition_level(idea.keyword_idea_metrics.competition),
                    'difficulty': self._calculate_difficulty(idea.keyword_idea_metrics),
                    'trend': 'stable',  # Would need historical data for real trends
                    'seasonal': False,  # Would need seasonal analysis
                    'related_keywords': []
                }
                
                # Apply filters
                if self._passes_filters(keyword_data, filters):
                    keywords.append(keyword_data)
            
            # Sort by search volume descending
            keywords.sort(key=lambda k: k['search_volume'], reverse=True)
            
            # Limit results
            limit = filters.get('limit', 50) if filters else 50
            keywords = keywords[:limit]
            
            return {
                'success': True,
                'data': {
                    'keywords': keywords,
                    'seed_keyword': seed_keyword,
                    'total_results': len(keywords),
                    'source': 'google_keyword_planner'
                }
            }
            
        except GoogleAdsException as ex:
            logger.error(f"Google Ads API error in keyword research: {ex}")
            return self._generate_demo_keywords(seed_keyword, filters)
        except Exception as e:
            logger.error(f"Error in keyword research: {str(e)}")
            return self._generate_demo_keywords(seed_keyword, filters)
    
    def _generate_demo_keywords(self, seed_keyword: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate demo keyword data when API is not available"""
        import random
        
        # Base keyword variations
        variations = [
            seed_keyword,
            f"{seed_keyword} online",
            f"{seed_keyword} near me", 
            f"best {seed_keyword}",
            f"{seed_keyword} reviews",
            f"{seed_keyword} price",
            f"buy {seed_keyword}",
            f"{seed_keyword} comparison",
            f"{seed_keyword} guide",
            f"top {seed_keyword}",
            f"{seed_keyword} 2024",
            f"cheap {seed_keyword}",
            f"{seed_keyword} service",
            f"{seed_keyword} company",
            f"professional {seed_keyword}"
        ]
        
        keywords = []
        for i, keyword in enumerate(variations):
            # Generate realistic metrics
            base_volume = random.randint(500, 50000)
            competition_level = random.choice(['low', 'medium', 'high'])
            
            keyword_data = {
                'id': f"demo_kw_{i}_{hash(keyword)}",
                'keyword': keyword,
                'search_volume': base_volume,
                'cpc': round(random.uniform(0.5, 8.0), 2),
                'competition': competition_level,
                'difficulty': random.randint(20, 90),
                'trend': random.choice(['up', 'down', 'stable']),
                'seasonal': random.random() > 0.8,
                'related_keywords': [f"{keyword} tips", f"{keyword} cost", f"{keyword} free"]
            }
            
            # Apply filters
            if self._passes_filters(keyword_data, filters):
                keywords.append(keyword_data)
        
        # Sort by search volume
        keywords.sort(key=lambda k: k['search_volume'], reverse=True)
        
        # Apply limit
        limit = filters.get('limit', 50) if filters else 50
        keywords = keywords[:limit]
        
        return {
            'success': True,
            'data': {
                'keywords': keywords,
                'seed_keyword': seed_keyword,
                'total_results': len(keywords),
                'source': 'demo_data'
            }
        }
    
    def _map_competition_level(self, competition_enum) -> str:
        """Map Google Ads competition enum to string"""
        if not competition_enum:
            return 'medium'
        
        competition_map = {
            1: 'low',      # UNSPECIFIED
            2: 'low',      # UNKNOWN  
            3: 'low',      # LOW
            4: 'medium',   # MEDIUM
            5: 'high'      # HIGH
        }
        
        return competition_map.get(competition_enum, 'medium')
    
    def _calculate_difficulty(self, metrics) -> int:
        """Calculate keyword difficulty score (0-100)"""
        if not metrics:
            return 50
        
        # Simple calculation based on competition and CPC
        competition_score = {
            'low': 20,
            'medium': 50, 
            'high': 80
        }
        
        base_score = competition_score.get(
            self._map_competition_level(metrics.competition), 
            50
        )
        
        # Adjust based on CPC (higher CPC = higher difficulty)
        cpc = (metrics.high_top_of_page_bid_micros or 0) / 1_000_000
        if cpc > 5:
            base_score += 10
        elif cpc > 2:
            base_score += 5
        
        return min(base_score, 100)
    
    def _get_location_id(self, location_code: str) -> Optional[str]:
        """Get Google Ads location ID for country code"""
        location_map = {
            'US': '2840',
            'UK': '2826', 
            'CA': '2124',
            'AU': '2036',
            'DE': '2276',
            'FR': '2250',
            'global': None
        }
        return location_map.get(location_code.upper())
    
    def _passes_filters(self, keyword_data: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if keyword passes the specified filters"""
        if not filters:
            return True
        
        # Volume filter
        min_volume = filters.get('minVolume', 0)
        if keyword_data['search_volume'] < min_volume:
            return False
        
        # CPC filter  
        max_cpc = filters.get('maxCpc', float('inf'))
        if keyword_data['cpc'] > max_cpc:
            return False
        
        # Competition filter
        competition_filter = filters.get('competition', 'all')
        if competition_filter != 'all' and keyword_data['competition'] != competition_filter:
            return False
        
        return True


# Initialize service
keyword_service = KeywordResearchService()


@keyword_research_bp.route('/research', methods=['POST'])
@login_required
def research_keywords():
    """Research keywords endpoint"""
    try:
        data = request.get_json()
        
        if not data or not data.get('seed_keyword'):
            return error_response('Seed keyword is required', 400)
        
        seed_keyword = data['seed_keyword']
        filters = data.get('filters', {})
        
        # Get user's default customer ID or use demo
        current_user = get_current_user()
        customer_id = getattr(current_user, 'google_ads_customer_id', None) or 'demo-customer'
        
        # Research keywords
        result = keyword_service.research_keywords(
            seed_keyword=seed_keyword,
            customer_id=customer_id,
            filters=filters
        )
        
        if result['success']:
            return success_response(
                data=result['data'],
                message=f"Found {len(result['data']['keywords'])} keywords for '{seed_keyword}'"
            )
        else:
            return error_response('Keyword research failed', 500)
        
    except Exception as e:
        logger.error(f"Error in keyword research endpoint: {str(e)}")
        return error_response('Internal server error', 500)


@keyword_research_bp.route('/suggestions', methods=['GET'])
@login_required 
def get_keyword_suggestions():
    """Get keyword suggestions for a seed term"""
    try:
        seed = request.args.get('seed', '')
        if not seed:
            return error_response('Seed parameter is required', 400)
        
        # Generate quick suggestions (could be cached)
        suggestions = [
            f"{seed} tips",
            f"{seed} guide", 
            f"best {seed}",
            f"{seed} reviews",
            f"how to {seed}",
            f"{seed} cost",
            f"{seed} near me",
            f"{seed} online"
        ]
        
        return success_response(
            data={'suggestions': suggestions[:5]},
            message='Keyword suggestions generated'
        )
        
    except Exception as e:
        logger.error(f"Error getting keyword suggestions: {str(e)}")
        return error_response('Internal server error', 500)


@keyword_research_bp.route('/trending', methods=['GET'])
@login_required
def get_trending_keywords():
    """Get trending keywords by industry"""
    try:
        industry = request.args.get('industry', 'general')
        
        # Demo trending keywords by industry
        trending_data = {
            'general': ['AI tools', 'sustainability', 'remote work', 'electric vehicles'],
            'technology': ['machine learning', 'cloud computing', 'cybersecurity', 'blockchain'],
            'marketing': ['content marketing', 'social media automation', 'influencer partnerships'],
            'ecommerce': ['omnichannel retail', 'mobile shopping', 'subscription services'],
            'finance': ['fintech solutions', 'cryptocurrency trading', 'digital banking']
        }
        
        keywords = trending_data.get(industry, trending_data['general'])
        
        return success_response(
            data={'trending_keywords': keywords, 'industry': industry},
            message=f'Trending keywords for {industry}'
        )
        
    except Exception as e:
        logger.error(f"Error getting trending keywords: {str(e)}")
        return error_response('Internal server error', 500)