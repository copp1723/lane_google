"""
Budget Pacing API Endpoints
Provides REST API for budget monitoring and pacing functionality
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import logging
from datetime import datetime
from src.services.budget_pacing import budget_pacing_service
from src.models.campaign import Campaign
from src.models.budget_alert import BudgetAlertModel
from src.config.database import db
from src.utils.flask_responses import APIResponse

logger = logging.getLogger(__name__)

# Create blueprint
budget_pacing_bp = Blueprint('budget_pacing', __name__)


@budget_pacing_bp.route('/campaigns/<campaign_id>/budget/status', methods=['GET'])
@login_required
def get_budget_status(campaign_id):
    """Get current budget status for a campaign"""
    try:
        # Check campaign ownership
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return APIResponse.error('Campaign not found', 404)
        
        if campaign.customer_id != current_user.customer_id:
            return APIResponse.error('Unauthorized', 403)
        
        # Get current pacing result
        pacing_result = budget_pacing_service.check_campaign_budget(campaign_id)
        
        return APIResponse.success(data={
            'campaign_id': campaign_id,
            'campaign_name': campaign.name,
            'budget_amount': campaign.budget_amount,
            'current_spend': pacing_result.current_spend,
            'projected_spend': pacing_result.projected_spend,
            'pacing_status': pacing_result.pacing_status.value,
            'days_remaining': pacing_result.days_remaining,
            'daily_budget': pacing_result.daily_budget,
            'recommended_budget': pacing_result.recommended_budget,
            'adjustment_factor': pacing_result.adjustment_factor,
            'confidence_score': pacing_result.confidence_score
        })
        
    except Exception as e:
        logger.error(f'Error getting budget status: {str(e)}')
        return APIResponse.error(f'Failed to get budget status: {str(e)}', 500)


@budget_pacing_bp.route('/campaigns/<campaign_id>/budget/recommendations', methods=['GET'])
@login_required
def get_budget_recommendations(campaign_id):
    """Get budget pacing recommendations"""
    try:
        # Check campaign ownership
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return APIResponse.error('Campaign not found', 404)
        
        if campaign.customer_id != current_user.customer_id:
            return APIResponse.error('Unauthorized', 403)
        
        # Get recommendations
        recommendations = budget_pacing_service.get_pacing_recommendations(campaign_id)
        
        return APIResponse.success(data=recommendations)
        
    except Exception as e:
        logger.error(f'Error getting recommendations: {str(e)}')
        return APIResponse.error(f'Failed to get recommendations: {str(e)}', 500)


@budget_pacing_bp.route('/campaigns/<campaign_id>/budget/alerts', methods=['GET'])
@login_required
def get_budget_alerts(campaign_id):
    """Get budget alerts for a campaign"""
    try:
        # Check campaign ownership
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return APIResponse.error('Campaign not found', 404)
        
        if campaign.customer_id != current_user.customer_id:
            return APIResponse.error('Unauthorized', 403)
        
        # Get alerts with optional filtering
        resolved = request.args.get('resolved', 'false').lower() == 'true'
        severity = request.args.get('severity')
        
        query = BudgetAlertModel.query.filter_by(campaign_id=campaign_id)
        
        if not resolved:
            query = query.filter_by(resolved=False)
        
        if severity:
            query = query.filter_by(severity=severity)
        
        alerts = query.order_by(BudgetAlertModel.created_at.desc()).limit(50).all()
        
        return APIResponse.success(data={
            'alerts': [alert.to_dict() for alert in alerts],
            'count': len(alerts)
        })
        
    except Exception as e:
        logger.error(f'Error getting alerts: {str(e)}')
        return APIResponse.error(f'Failed to get alerts: {str(e)}', 500)


@budget_pacing_bp.route('/campaigns/<campaign_id>/budget/alerts/<alert_id>/resolve', methods=['POST'])
@login_required
def resolve_budget_alert(campaign_id, alert_id):
    """Resolve a budget alert"""
    try:
        # Check campaign ownership
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return APIResponse.error('Campaign not found', 404)
        
        if campaign.customer_id != current_user.customer_id:
            return APIResponse.error('Unauthorized', 403)
        
        # Get and resolve alert
        alert = BudgetAlertModel.query.filter_by(
            id=alert_id,
            campaign_id=campaign_id
        ).first()
        
        if not alert:
            return APIResponse.error('Alert not found', 404)
        
        alert.resolve()
        db.session.commit()
        
        return APIResponse.success(data={
            'message': 'Alert resolved successfully',
            'alert': alert.to_dict()
        })
        
    except Exception as e:
        logger.error(f'Error resolving alert: {str(e)}')
        return APIResponse.error(f'Failed to resolve alert: {str(e)}', 500)


@budget_pacing_bp.route('/campaigns/<campaign_id>/budget/update', methods=['POST'])
@login_required
def update_campaign_budget(campaign_id):
    """Update campaign budget settings"""
    try:
        # Check campaign ownership
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return APIResponse.error('Campaign not found', 404)
        
        if campaign.customer_id != current_user.customer_id:
            return APIResponse.error('Unauthorized', 403)
        
        # Get update data
        data = request.get_json()
        
        # Update allowed fields
        if 'budget_amount' in data:
            campaign.budget_amount = float(data['budget_amount'])
        
        if 'pacing_strategy' in data:
            valid_strategies = ['linear', 'accelerated', 'conservative', 'adaptive']
            if data['pacing_strategy'] not in valid_strategies:
                return APIResponse.error(f'Invalid pacing strategy. Must be one of: {valid_strategies}', 400)
            campaign.pacing_strategy = data['pacing_strategy']
        
        if 'billing_period_start' in data:
            campaign.billing_period_start = datetime.fromisoformat(data['billing_period_start'])
        
        if 'billing_period_end' in data:
            campaign.billing_period_end = datetime.fromisoformat(data['billing_period_end'])
        
        db.session.commit()
        
        # Trigger immediate budget check
        pacing_result = budget_pacing_service.check_campaign_budget(campaign_id)
        
        return APIResponse.success(data={
            'message': 'Budget updated successfully',
            'campaign': campaign.to_dict(),
            'pacing_status': pacing_result.pacing_status.value
        })
        
    except Exception as e:
        logger.error(f'Error updating budget: {str(e)}')
        return APIResponse.error(f'Failed to update budget: {str(e)}', 500)


@budget_pacing_bp.route('/budget/overview', methods=['GET'])
@login_required
def get_budget_overview():
    """Get budget overview for all campaigns"""
    try:
        # Get all campaigns for the user
        campaigns = Campaign.query.filter_by(
            customer_id=current_user.customer_id
        ).all()
        
        overview = {
            'total_budget': 0,
            'total_spend': 0,
            'campaigns': []
        }
        
        for campaign in campaigns:
            if campaign.budget_amount:
                overview['total_budget'] += campaign.budget_amount
                overview['total_spend'] += campaign.current_spend or 0
                
                overview['campaigns'].append({
                    'id': campaign.id,
                    'name': campaign.name,
                    'budget_amount': campaign.budget_amount,
                    'current_spend': campaign.current_spend or 0,
                    'pacing_status': campaign.pacing_status,
                    'projected_spend': campaign.projected_spend
                })
        
        # Calculate overall metrics
        if overview['total_budget'] > 0:
            overview['utilization_rate'] = (overview['total_spend'] / overview['total_budget']) * 100
        else:
            overview['utilization_rate'] = 0
        
        # Count campaigns by status
        status_counts = {}
        for campaign in overview['campaigns']:
            status = campaign.get('pacing_status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        overview['status_distribution'] = status_counts
        
        return APIResponse.success(data=overview)
        
    except Exception as e:
        logger.error(f'Error getting budget overview: {str(e)}')
        return APIResponse.error(f'Failed to get budget overview: {str(e)}', 500)


# Alert webhook endpoint for external notifications
@budget_pacing_bp.route('/webhooks/budget-alert', methods=['POST'])
def budget_alert_webhook():
    """Webhook endpoint for external budget alert notifications"""
    try:
        # Verify webhook signature (implement based on your security requirements)
        # For now, we'll use a simple API key check
        api_key = request.headers.get('X-API-Key')
        if api_key != 'your-webhook-api-key':  # Replace with config value
            return APIResponse.error('Unauthorized', 401)
        
        data = request.get_json()
        
        # Process the alert
        logger.info(f"Received budget alert webhook: {data}")
        
        # You can add custom processing here
        # For example, send email notifications, update external systems, etc.
        
        return APIResponse.success(data={'message': 'Alert processed successfully'})
        
    except Exception as e:
        logger.error(f'Error processing webhook: {str(e)}')
        return APIResponse.error(f'Failed to process webhook: {str(e)}', 500)