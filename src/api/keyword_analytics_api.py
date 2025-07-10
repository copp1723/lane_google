"""
Advanced Keyword Analytics API
Enterprise-level keyword intelligence and competitive analysis
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict
import re

from src.auth.auth import login_required, get_current_user
from src.utils.responses import success_response, error_response

logger = logging.getLogger(__name__)

keyword_analytics_bp = Blueprint('keyword_analytics', __name__)


class KeywordIntelligenceEngine:
    """Advanced keyword analytics and intelligence engine"""
    
    def __init__(self):
        self.intent_patterns = {
            'commercial': [
                r'\b(buy|purchase|price|cost|cheap|deal|discount|sale)\b',
                r'\b(best|top|review|compare|vs)\b',
                r'\b(shop|store|vendor|supplier)\b'
            ],
            'informational': [
                r'\b(how|what|why|when|where|guide|tutorial)\b',
                r'\b(learn|understand|explain|definition)\b',
                r'\b(tips|advice|help|information)\b'
            ],
            'transactional': [
                r'\b(order|checkout|cart|shipping)\b',
                r'\b(coupon|promo|code|free trial)\b',
                r'\b(download|sign up|subscribe)\b'
            ],
            'navigational': [
                r'\b(login|account|contact|support)\b',
                r'\b(official|website|homepage)\b',
                r'\b(location|near me|hours)\b'
            ]
        }
    
    def analyze_keyword_clusters(self, keywords: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Group keywords into semantic clusters"""
        
        # Simple clustering based on common words and patterns
        clusters = defaultdict(list)
        processed_keywords = set()
        
        for keyword in keywords:
            if keyword['keyword'] in processed_keywords:
                continue
                
            keyword_text = keyword['keyword'].lower()
            root_words = self._extract_root_words(keyword_text)
            
            # Find cluster based on common root words
            cluster_name = None
            for existing_cluster, cluster_keywords in clusters.items():
                if any(self._calculate_similarity(keyword_text, existing['keyword'].lower()) > 0.6 
                       for existing in cluster_keywords):
                    cluster_name = existing_cluster
                    break
            
            if not cluster_name:
                # Create new cluster
                main_word = max(root_words, key=len) if root_words else keyword_text.split()[0]
                cluster_name = f"{main_word.title()} Group"
            
            clusters[cluster_name].append(keyword)
            processed_keywords.add(keyword['keyword'])
        
        # Calculate cluster metrics
        cluster_analysis = {}
        for cluster_name, cluster_keywords in clusters.items():
            total_volume = sum(kw.get('search_volume', 0) for kw in cluster_keywords)
            avg_cpc = np.mean([kw.get('cpc', 0) for kw in cluster_keywords])
            avg_difficulty = np.mean([kw.get('difficulty', 0) for kw in cluster_keywords])
            
            cluster_analysis[cluster_name] = {
                'keywords': cluster_keywords,
                'keyword_count': len(cluster_keywords),
                'total_volume': total_volume,
                'average_cpc': round(avg_cpc, 2),
                'average_difficulty': round(avg_difficulty, 1),
                'opportunity_score': self._calculate_cluster_opportunity(cluster_keywords)
            }
        
        return cluster_analysis
    
    def classify_search_intent(self, keyword: str) -> Dict[str, Any]:
        """Classify keyword by search intent"""
        keyword_lower = keyword.lower()
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, keyword_lower))
                score += matches
            intent_scores[intent] = score
        
        # Normalize scores
        total_score = sum(intent_scores.values())
        if total_score > 0:
            intent_scores = {k: round(v/total_score, 2) for k, v in intent_scores.items()}
        
        primary_intent = max(intent_scores.items(), key=lambda x: x[1])[0] if total_score > 0 else 'informational'
        confidence = intent_scores.get(primary_intent, 0.5)
        
        return {
            'primary_intent': primary_intent,
            'confidence': confidence,
            'intent_breakdown': intent_scores
        }
    
    def generate_negative_keywords(self, keywords: List[str], business_type: str = 'general') -> List[Dict[str, Any]]:
        """Generate negative keyword suggestions"""
        
        negative_suggestions = []
        
        # Common negatives by business type
        negative_lists = {
            'ecommerce': ['free', 'diy', 'homemade', 'recipe', 'tutorial', 'how to make'],
            'b2b': ['cheap', 'free', 'diy', 'student', 'personal use'],
            'service': ['diy', 'free', 'volunteer', 'intern', 'course'],
            'general': ['free', 'pirated', 'crack', 'illegal', 'fake']
        }
        
        base_negatives = negative_lists.get(business_type, negative_lists['general'])
        
        for negative in base_negatives:
            negative_suggestions.append({
                'keyword': negative,
                'match_type': 'broad',
                'reason': f'Common irrelevant term for {business_type} businesses',
                'confidence': 0.8
            })
        
        # Analyze provided keywords for additional negatives
        all_words = ' '.join(keywords).lower()
        
        # Look for patterns that suggest irrelevant traffic
        if 'job' in all_words or 'career' in all_words:
            negative_suggestions.append({
                'keyword': 'jobs',
                'match_type': 'broad',
                'reason': 'Prevent job-seeking traffic',
                'confidence': 0.9
            })
        
        if any(word in all_words for word in ['learn', 'course', 'tutorial']):
            negative_suggestions.extend([
                {
                    'keyword': 'course',
                    'match_type': 'broad',
                    'reason': 'Prevent educational traffic if not selling courses',
                    'confidence': 0.7
                },
                {
                    'keyword': 'free tutorial',
                    'match_type': 'phrase',
                    'reason': 'Prevent free content seekers',
                    'confidence': 0.8
                }
            ])
        
        return negative_suggestions[:15]  # Limit to top suggestions
    
    def calculate_keyword_opportunity_score(self, keyword_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive opportunity score for keywords"""
        
        volume = keyword_data.get('search_volume', 0)
        cpc = keyword_data.get('cpc', 0)
        competition = keyword_data.get('competition', 'medium')
        difficulty = keyword_data.get('difficulty', 50)
        
        # Scoring factors
        scores = {}
        
        # Volume score (0-30 points)
        if volume >= 10000:
            scores['volume_score'] = 30
        elif volume >= 1000:
            scores['volume_score'] = 20 + (volume - 1000) / 900 * 10
        elif volume >= 100:
            scores['volume_score'] = 10 + (volume - 100) / 900 * 10
        else:
            scores['volume_score'] = volume / 100 * 10
        
        # Competition score (0-25 points) - lower competition = higher score
        competition_values = {'low': 25, 'medium': 15, 'high': 5}
        scores['competition_score'] = competition_values.get(competition, 15)
        
        # CPC score (0-20 points) - moderate CPC is good
        if 1 <= cpc <= 5:
            scores['cpc_score'] = 20
        elif 0.5 <= cpc < 1:
            scores['cpc_score'] = 15
        elif 5 < cpc <= 10:
            scores['cpc_score'] = 15
        else:
            scores['cpc_score'] = 5
        
        # Difficulty score (0-15 points) - lower difficulty = higher score  
        scores['difficulty_score'] = max(0, 15 - (difficulty / 100 * 15))
        
        # Intent score (0-10 points)
        intent_analysis = self.classify_search_intent(keyword_data.get('keyword', ''))
        if intent_analysis['primary_intent'] == 'commercial':
            scores['intent_score'] = 10
        elif intent_analysis['primary_intent'] == 'transactional':
            scores['intent_score'] = 8
        else:
            scores['intent_score'] = 5
        
        total_score = sum(scores.values())
        
        # Grade assignment
        if total_score >= 80:
            grade = 'A+'
        elif total_score >= 70:
            grade = 'A'
        elif total_score >= 60:
            grade = 'B+'
        elif total_score >= 50:
            grade = 'B'
        elif total_score >= 40:
            grade = 'C'
        else:
            grade = 'D'
        
        return {
            'total_score': round(total_score, 1),
            'grade': grade,
            'score_breakdown': {k: round(v, 1) for k, v in scores.items()},
            'recommendation': self._get_opportunity_recommendation(total_score, scores)
        }
    
    def analyze_competitive_landscape(self, keywords: List[str]) -> Dict[str, Any]:
        """Analyze competitive landscape for keywords"""
        
        # Simulated competitive analysis (would use real competitor data in production)
        competitive_insights = {
            'market_competition': 'medium',
            'average_competitor_count': np.random.randint(3, 15),
            'top_competitors': [
                {'domain': 'competitor1.com', 'estimated_traffic': 45000, 'ad_share': 0.23},
                {'domain': 'competitor2.com', 'estimated_traffic': 32000, 'ad_share': 0.18},
                {'domain': 'competitor3.com', 'estimated_traffic': 28000, 'ad_share': 0.15}
            ],
            'market_gaps': [],
            'opportunity_keywords': []
        }
        
        # Find potential gaps
        for keyword in keywords[:5]:  # Analyze top keywords
            if np.random.random() > 0.7:  # 30% chance of gap
                competitive_insights['market_gaps'].append({
                    'keyword': keyword,
                    'gap_type': 'low_competition',
                    'opportunity_score': np.random.randint(60, 90)
                })
        
        return competitive_insights
    
    def _extract_root_words(self, text: str) -> List[str]:
        """Extract meaningful root words from keyword"""
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'best', 'top'}
        words = text.lower().split()
        return [word for word in words if len(word) > 2 and word not in stop_words]
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union) if union else 0
    
    def _calculate_cluster_opportunity(self, keywords: List[Dict[str, Any]]) -> float:
        """Calculate opportunity score for keyword cluster"""
        if not keywords:
            return 0
        
        avg_volume = np.mean([kw.get('search_volume', 0) for kw in keywords])
        avg_difficulty = np.mean([kw.get('difficulty', 50) for kw in keywords])
        
        # Higher volume, lower difficulty = higher opportunity
        volume_factor = min(avg_volume / 1000, 10) / 10  # Normalize to 0-1
        difficulty_factor = (100 - avg_difficulty) / 100  # Invert difficulty
        
        return round((volume_factor + difficulty_factor) / 2 * 100, 1)
    
    def _get_opportunity_recommendation(self, total_score: float, scores: Dict[str, float]) -> str:
        """Generate recommendation based on opportunity score"""
        if total_score >= 70:
            return "High priority - Strong opportunity with good search volume and manageable competition"
        elif total_score >= 50:
            return "Medium priority - Decent opportunity, consider for secondary ad groups"
        elif scores.get('volume_score', 0) < 10:
            return "Low priority - Limited search volume may not justify investment"
        elif scores.get('competition_score', 0) < 10:
            return "Challenging - High competition may require larger budget for success"
        else:
            return "Consider alternative keywords with better opportunity metrics"


# Initialize engine
keyword_engine = KeywordIntelligenceEngine()


@keyword_analytics_bp.route('/clusters', methods=['POST'])
@login_required
def analyze_keyword_clusters():
    """Analyze and group keywords into semantic clusters"""
    try:
        data = request.get_json()
        
        if not data or not data.get('keywords'):
            return error_response('Keywords array is required', 400)
        
        keywords = data['keywords']
        clusters = keyword_engine.analyze_keyword_clusters(keywords)
        
        return success_response(
            data={'clusters': clusters},
            message=f"Analyzed {len(keywords)} keywords into {len(clusters)} clusters"
        )
        
    except Exception as e:
        logger.error(f"Error in keyword clustering: {str(e)}")
        return error_response('Clustering analysis failed', 500)


@keyword_analytics_bp.route('/intent-analysis', methods=['POST'])
@login_required
def analyze_search_intent():
    """Analyze search intent for keywords"""
    try:
        data = request.get_json()
        
        if not data or not data.get('keywords'):
            return error_response('Keywords array is required', 400)
        
        keywords = data['keywords']
        intent_analysis = {}
        
        for keyword in keywords:
            keyword_text = keyword if isinstance(keyword, str) else keyword.get('keyword', '')
            intent_analysis[keyword_text] = keyword_engine.classify_search_intent(keyword_text)
        
        return success_response(
            data={'intent_analysis': intent_analysis},
            message=f"Analyzed search intent for {len(keywords)} keywords"
        )
        
    except Exception as e:
        logger.error(f"Error in intent analysis: {str(e)}")
        return error_response('Intent analysis failed', 500)


@keyword_analytics_bp.route('/negative-keywords', methods=['POST'])
@login_required
def generate_negative_keywords():
    """Generate negative keyword suggestions"""
    try:
        data = request.get_json()
        
        if not data or not data.get('keywords'):
            return error_response('Keywords array is required', 400)
        
        keywords = data['keywords']
        business_type = data.get('business_type', 'general')
        
        # Extract keyword text if objects provided
        keyword_texts = []
        for kw in keywords:
            if isinstance(kw, str):
                keyword_texts.append(kw)
            else:
                keyword_texts.append(kw.get('keyword', ''))
        
        negative_suggestions = keyword_engine.generate_negative_keywords(keyword_texts, business_type)
        
        return success_response(
            data={'negative_keywords': negative_suggestions},
            message=f"Generated {len(negative_suggestions)} negative keyword suggestions"
        )
        
    except Exception as e:
        logger.error(f"Error generating negative keywords: {str(e)}")
        return error_response('Negative keyword generation failed', 500)


@keyword_analytics_bp.route('/opportunity-scores', methods=['POST'])
@login_required
def calculate_opportunity_scores():
    """Calculate comprehensive opportunity scores for keywords"""
    try:
        data = request.get_json()
        
        if not data or not data.get('keywords'):
            return error_response('Keywords array is required', 400)
        
        keywords = data['keywords']
        scored_keywords = []
        
        for keyword in keywords:
            opportunity_data = keyword_engine.calculate_keyword_opportunity_score(keyword)
            
            scored_keyword = {
                **keyword,
                'opportunity_score': opportunity_data['total_score'],
                'opportunity_grade': opportunity_data['grade'],
                'score_breakdown': opportunity_data['score_breakdown'],
                'recommendation': opportunity_data['recommendation']
            }
            scored_keywords.append(scored_keyword)
        
        # Sort by opportunity score
        scored_keywords.sort(key=lambda k: k['opportunity_score'], reverse=True)
        
        return success_response(
            data={'keywords': scored_keywords},
            message=f"Calculated opportunity scores for {len(keywords)} keywords"
        )
        
    except Exception as e:
        logger.error(f"Error calculating opportunity scores: {str(e)}")
        return error_response('Opportunity scoring failed', 500)


@keyword_analytics_bp.route('/competitive-analysis', methods=['POST'])
@login_required
def analyze_competitive_landscape():
    """Analyze competitive landscape for keywords"""
    try:
        data = request.get_json()
        
        if not data or not data.get('keywords'):
            return error_response('Keywords array is required', 400)
        
        keywords = data['keywords']
        
        # Extract keyword text if objects provided
        keyword_texts = []
        for kw in keywords:
            if isinstance(kw, str):
                keyword_texts.append(kw)
            else:
                keyword_texts.append(kw.get('keyword', ''))
        
        competitive_analysis = keyword_engine.analyze_competitive_landscape(keyword_texts)
        
        return success_response(
            data=competitive_analysis,
            message=f"Analyzed competitive landscape for {len(keywords)} keywords"
        )
        
    except Exception as e:
        logger.error(f"Error in competitive analysis: {str(e)}")
        return error_response('Competitive analysis failed', 500)


@keyword_analytics_bp.route('/comprehensive-analysis', methods=['POST'])
@login_required
def comprehensive_keyword_analysis():
    """Perform comprehensive keyword analysis including all intelligence features"""
    try:
        data = request.get_json()
        
        if not data or not data.get('keywords'):
            return error_response('Keywords array is required', 400)
        
        keywords = data['keywords']
        business_type = data.get('business_type', 'general')
        
        # Perform all analyses
        clusters = keyword_engine.analyze_keyword_clusters(keywords)
        
        # Calculate opportunity scores
        scored_keywords = []
        for keyword in keywords:
            opportunity_data = keyword_engine.calculate_keyword_opportunity_score(keyword)
            intent_data = keyword_engine.classify_search_intent(keyword.get('keyword', ''))
            
            scored_keyword = {
                **keyword,
                'opportunity_score': opportunity_data['total_score'],
                'opportunity_grade': opportunity_data['grade'],
                'score_breakdown': opportunity_data['score_breakdown'],
                'recommendation': opportunity_data['recommendation'],
                'search_intent': intent_data
            }
            scored_keywords.append(scored_keyword)
        
        # Generate negative keywords
        keyword_texts = [kw.get('keyword', '') for kw in keywords]
        negative_suggestions = keyword_engine.generate_negative_keywords(keyword_texts, business_type)
        
        # Competitive analysis
        competitive_analysis = keyword_engine.analyze_competitive_landscape(keyword_texts)
        
        # Summary insights
        summary = {
            'total_keywords': len(keywords),
            'total_clusters': len(clusters),
            'high_opportunity_keywords': len([k for k in scored_keywords if k['opportunity_score'] >= 70]),
            'average_opportunity_score': round(np.mean([k['opportunity_score'] for k in scored_keywords]), 1),
            'primary_intents': {},
            'recommended_negatives': len(negative_suggestions)
        }
        
        # Intent distribution
        intent_counts = defaultdict(int)
        for keyword in scored_keywords:
            intent_counts[keyword['search_intent']['primary_intent']] += 1
        summary['primary_intents'] = dict(intent_counts)
        
        return success_response(
            data={
                'keywords': scored_keywords,
                'clusters': clusters,
                'negative_keywords': negative_suggestions,
                'competitive_analysis': competitive_analysis,
                'summary': summary
            },
            message="Comprehensive keyword analysis completed"
        )
        
    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {str(e)}")
        return error_response('Comprehensive analysis failed', 500)