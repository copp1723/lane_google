"""
Analytics and Reporting Routes
Advanced analytics and performance reporting endpoints
"""

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
from sqlalchemy import func, and_

from src.database import db
from src.models.user import User
from src.models.campaign import Campaign, CampaignStatus
from src.models.conversation import Conversation
from src.models.audit_log import AuditLog
from src.config import config

analytics_bp = Blueprint('analytics', __name__)

def require_permission(permission):
    """Decorator to check user permissions"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            if not g.current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            if not g.current_user.has_permission(permission):
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

@analytics_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@require_permission('analytics.view')
def get_dashboard_data():
    """Get comprehensive dashboard analytics"""
    try:
        # Get date range from query parameters
        days = request.args.get('days', 30, type=int)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Build base query with user access restrictions
        campaign_query = Campaign.query
        if g.current_user.role.value != 'admin':
            if g.current_user.google_ads_customer_ids:
                campaign_query = campaign_query.filter(
                    Campaign.google_customer_id.in_(g.current_user.google_ads_customer_ids)
                )
            else:
                campaign_query = campaign_query.filter(Campaign.id == None)
        
        # Filter by date range
        campaign_query = campaign_query.filter(
            Campaign.created_at >= start_date,
            Campaign.created_at <= end_date
        )
        
        # Campaign metrics
        total_campaigns = campaign_query.count()
        active_campaigns = campaign_query.filter_by(status=CampaignStatus.ACTIVE).count()
        pending_campaigns = campaign_query.filter_by(status=CampaignStatus.PENDING_APPROVAL).count()
        
        # Performance metrics
        performance_campaigns = campaign_query.filter(
            Campaign.status.in_([CampaignStatus.ACTIVE, CampaignStatus.PAUSED])
        ).all()
        
        total_impressions = sum(c.impressions for c in performance_campaigns)
        total_clicks = sum(c.clicks for c in performance_campaigns)
        total_conversions = sum(c.conversions for c in performance_campaigns)
        total_cost = sum(c.cost for c in performance_campaigns)
        total_conversion_value = sum(c.conversion_value for c in performance_campaigns)
        
        # Calculate aggregated metrics
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        avg_cpc = (total_cost / total_clicks) if total_clicks > 0 else 0
        avg_cpa = (total_cost / total_conversions) if total_conversions > 0 else 0
        total_roas = (total_conversion_value / total_cost) if total_cost > 0 else 0
        
        # AI usage metrics
        conversation_query = Conversation.query.filter_by(user_id=g.current_user.id)
        if g.current_user.role.value == 'admin':
            conversation_query = Conversation.query
        
        conversation_query = conversation_query.filter(
            Conversation.created_at >= start_date,
            Conversation.created_at <= end_date
        )
        
        total_conversations = conversation_query.count()
        completed_conversations = conversation_query.filter_by(
            status=Conversation.ConversationStatus.COMPLETED
        ).count()
        
        total_tokens = db.session.query(func.sum(Conversation.total_tokens_used)).filter(
            Conversation.id.in_([c.id for c in conversation_query.all()])
        ).scalar() or 0
        
        briefs_generated = conversation_query.filter_by(campaign_brief_generated=True).count()
        
        # Top performing campaigns
        top_campaigns = sorted(
            performance_campaigns,
            key=lambda c: c.roas,
            reverse=True
        )[:5]
        
        # Campaign type distribution
        campaign_types = db.session.query(
            Campaign.campaign_type,
            func.count(Campaign.id).label('count')
        ).filter(
            Campaign.id.in_([c.id for c in campaign_query.all()])
        ).group_by(Campaign.campaign_type).all()
        
        # Daily performance trend (last 7 days)
        daily_trends = []
        for i in range(7):
            day = end_date - timedelta(days=i)
            day_campaigns = [c for c in performance_campaigns 
                           if c.last_sync_at and c.last_sync_at.date() == day.date()]
            
            daily_trends.append({
                'date': day.strftime('%Y-%m-%d'),
                'impressions': sum(c.impressions for c in day_campaigns),
                'clicks': sum(c.clicks for c in day_campaigns),
                'cost': sum(c.cost for c in day_campaigns),
                'conversions': sum(c.conversions for c in day_campaigns)
            })
        
        dashboard_data = {
            'date_range': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'days': days
            },
            'campaign_metrics': {
                'total_campaigns': total_campaigns,
                'active_campaigns': active_campaigns,
                'pending_campaigns': pending_campaigns,
                'completion_rate': (active_campaigns / total_campaigns * 100) if total_campaigns > 0 else 0
            },
            'performance_metrics': {
                'total_impressions': total_impressions,
                'total_clicks': total_clicks,
                'total_conversions': total_conversions,
                'total_cost': round(total_cost, 2),
                'total_conversion_value': round(total_conversion_value, 2),
                'avg_ctr': round(avg_ctr, 2),
                'avg_cpc': round(avg_cpc, 2),
                'avg_cpa': round(avg_cpa, 2),
                'total_roas': round(total_roas, 2)
            },
            'ai_metrics': {
                'total_conversations': total_conversations,
                'completed_conversations': completed_conversations,
                'completion_rate': (completed_conversations / total_conversations * 100) if total_conversations > 0 else 0,
                'total_tokens_used': total_tokens,
                'briefs_generated': briefs_generated,
                'avg_tokens_per_conversation': (total_tokens / total_conversations) if total_conversations > 0 else 0
            },
            'top_campaigns': [
                {
                    'id': c.id,
                    'name': c.name,
                    'roas': round(c.roas, 2),
                    'cost': round(c.cost, 2),
                    'conversions': c.conversions,
                    'status': c.status.value
                } for c in top_campaigns
            ],
            'campaign_type_distribution': [
                {
                    'type': ct[0].value,
                    'count': ct[1]
                } for ct in campaign_types
            ],
            'daily_trends': list(reversed(daily_trends))
        }
        
        return jsonify({
            'dashboard': dashboard_data,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get dashboard data: {str(e)}'}), 500

@analytics_bp.route('/campaigns/<campaign_id>/performance', methods=['GET'])
@jwt_required()
@require_permission('analytics.view')
def get_campaign_performance(campaign_id):
    """Get detailed campaign performance analytics"""
    try:
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        # Check access permissions
        if not g.current_user.can_access_customer(campaign.google_customer_id):
            return jsonify({'error': 'Access denied to this campaign'}), 403
        
        # Get date range from query parameters
        days = request.args.get('days', 30, type=int)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Mock historical performance data - replace with actual data storage
        historical_data = []
        for i in range(days):
            day = start_date + timedelta(days=i)
            # Generate mock daily performance
            daily_impressions = int(campaign.impressions / days * (0.8 + 0.4 * (i % 7) / 7))
            daily_clicks = int(daily_impressions * campaign.ctr / 100)
            daily_cost = daily_clicks * campaign.cpc
            daily_conversions = daily_clicks * 0.05  # 5% conversion rate
            
            historical_data.append({
                'date': day.strftime('%Y-%m-%d'),
                'impressions': daily_impressions,
                'clicks': daily_clicks,
                'cost': round(daily_cost, 2),
                'conversions': round(daily_conversions, 1),
                'ctr': round(campaign.ctr, 2),
                'cpc': round(campaign.cpc, 2),
                'cpa': round(daily_cost / daily_conversions, 2) if daily_conversions > 0 else 0
            })
        
        # Performance insights
        insights = []
        
        if campaign.ctr < 2.0:
            insights.append({
                'type': 'warning',
                'title': 'Low Click-Through Rate',
                'message': f'CTR of {campaign.ctr:.2f}% is below industry average. Consider improving ad copy or targeting.',
                'recommendation': 'Review ad copy and keywords for relevance'
            })
        
        if campaign.quality_score < 7.0:
            insights.append({
                'type': 'warning',
                'title': 'Quality Score Opportunity',
                'message': f'Quality score of {campaign.quality_score:.1f} can be improved.',
                'recommendation': 'Optimize landing page experience and ad relevance'
            })
        
        if campaign.roas > 4.0:
            insights.append({
                'type': 'success',
                'title': 'Excellent ROAS',
                'message': f'ROAS of {campaign.roas:.2f} is performing very well.',
                'recommendation': 'Consider increasing budget to scale performance'
            })
        
        performance_data = {
            'campaign': campaign.to_dict(include_performance=True),
            'date_range': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'days': days
            },
            'historical_data': historical_data,
            'insights': insights,
            'benchmarks': {
                'industry_avg_ctr': 2.5,
                'industry_avg_cpc': 2.0,
                'industry_avg_conversion_rate': 3.5,
                'target_quality_score': 8.0
            }
        }
        
        return jsonify({
            'performance': performance_data,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get campaign performance: {str(e)}'}), 500

@analytics_bp.route('/reports/export', methods=['POST'])
@jwt_required()
@require_permission('analytics.export')
def export_report():
    """Export analytics report"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        report_type = data.get('type', 'campaign_performance')
        format_type = data.get('format', 'csv')
        date_range = data.get('date_range', {})
        
        # Validate parameters
        valid_types = ['campaign_performance', 'ai_usage', 'user_activity']
        valid_formats = ['csv', 'xlsx', 'pdf']
        
        if report_type not in valid_types:
            return jsonify({
                'error': 'Invalid report type',
                'valid_types': valid_types
            }), 400
        
        if format_type not in valid_formats:
            return jsonify({
                'error': 'Invalid format',
                'valid_formats': valid_formats
            }), 400
        
        # Generate report (mock implementation)
        report_id = f"report_{uuid.uuid4().hex[:8]}"
        
        # Log export
        AuditLog.log_user_action(
            action=AuditAction.DATA_EXPORTED,
            user_id=g.current_user.id,
            description=f"Analytics report exported: {report_type}",
            additional_metadata={
                'report_type': report_type,
                'format': format_type,
                'report_id': report_id
            }
        )
        
        return jsonify({
            'report_id': report_id,
            'type': report_type,
            'format': format_type,
            'status': 'generating',
            'download_url': f'/api/analytics/reports/{report_id}/download',
            'estimated_completion': (datetime.now() + timedelta(minutes=5)).isoformat(),
            'message': 'Report generation started',
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to export report: {str(e)}'}), 500

@analytics_bp.route('/optimization-suggestions', methods=['GET'])
@jwt_required()
@require_permission('analytics.view')
def get_optimization_suggestions():
    """Get AI-powered optimization suggestions"""
    try:
        # Get user's campaigns
        campaign_query = Campaign.query
        if g.current_user.role.value != 'admin':
            if g.current_user.google_ads_customer_ids:
                campaign_query = campaign_query.filter(
                    Campaign.google_customer_id.in_(g.current_user.google_ads_customer_ids)
                )
            else:
                campaign_query = campaign_query.filter(Campaign.id == None)
        
        active_campaigns = campaign_query.filter_by(status=CampaignStatus.ACTIVE).all()
        
        suggestions = []
        
        for campaign in active_campaigns:
            campaign_suggestions = []
            
            # Budget optimization
            if campaign.cost > 0 and campaign.roas > 3.0:
                campaign_suggestions.append({
                    'type': 'budget_increase',
                    'priority': 'high',
                    'title': 'Increase Budget',
                    'description': f'Campaign has strong ROAS of {campaign.roas:.2f}. Consider increasing budget by 20-30%.',
                    'impact': 'Potential 25% increase in conversions',
                    'effort': 'low'
                })
            
            # Keyword optimization
            if campaign.ctr < 2.0:
                campaign_suggestions.append({
                    'type': 'keyword_optimization',
                    'priority': 'medium',
                    'title': 'Improve Keywords',
                    'description': f'CTR of {campaign.ctr:.2f}% suggests keyword relevance issues.',
                    'impact': 'Potential 15% CTR improvement',
                    'effort': 'medium'
                })
            
            # Bidding strategy optimization
            if campaign.cpa > 0 and campaign.conversions > 10:
                campaign_suggestions.append({
                    'type': 'bidding_strategy',
                    'priority': 'medium',
                    'title': 'Switch to Target CPA',
                    'description': f'With {campaign.conversions:.0f} conversions, Target CPA bidding could improve efficiency.',
                    'impact': 'Potential 10% CPA reduction',
                    'effort': 'low'
                })
            
            if campaign_suggestions:
                suggestions.append({
                    'campaign_id': campaign.id,
                    'campaign_name': campaign.name,
                    'suggestions': campaign_suggestions
                })
        
        # Account-level suggestions
        account_suggestions = []
        
        total_campaigns = len(active_campaigns)
        if total_campaigns > 0:
            avg_roas = sum(c.roas for c in active_campaigns) / total_campaigns
            
            if avg_roas > 4.0:
                account_suggestions.append({
                    'type': 'account_expansion',
                    'priority': 'high',
                    'title': 'Expand to New Markets',
                    'description': f'Strong average ROAS of {avg_roas:.2f} suggests opportunity for expansion.',
                    'impact': 'Potential 40% revenue increase',
                    'effort': 'high'
                })
        
        return jsonify({
            'suggestions': {
                'campaign_level': suggestions,
                'account_level': account_suggestions,
                'generated_at': datetime.now().isoformat(),
                'total_suggestions': sum(len(s['suggestions']) for s in suggestions) + len(account_suggestions)
            },
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get optimization suggestions: {str(e)}'}), 500

@analytics_bp.route('/health', methods=['GET'])
def health_check():
    """Analytics service health check"""
    try:
        return jsonify({
            'status': 'healthy',
            'service': 'Analytics and Reporting',
            'features': {
                'dashboard_analytics': True,
                'campaign_performance': True,
                'ai_usage_tracking': True,
                'optimization_suggestions': True,
                'report_export': config.features.advanced_analytics_enabled,
                'real_time_monitoring': config.features.real_time_monitoring_enabled
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

