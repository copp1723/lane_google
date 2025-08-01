"""
Google Ads API Routes
"""

from flask import Blueprint, request, jsonify
from src.auth.authentication import token_required, account_access_required
from src.services.real_google_ads import real_google_ads_service
import logging

logger = logging.getLogger(__name__)

# Create blueprint
google_ads_bp = Blueprint('google_ads', __name__)


@google_ads_bp.route('/customers', methods=['GET'])
@token_required
def get_accessible_customers():
    """Get list of accessible Google Ads customers"""
    try:
        customers = real_google_ads_service.get_accessible_customers()
        
        return jsonify({
            'success': True,
            'customers': customers
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting customers: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get accessible customers'
        }), 500


@google_ads_bp.route('/customers/<customer_id>/campaigns', methods=['GET'])
@token_required
def get_campaigns(customer_id):
    """Get campaigns for a specific customer"""
    try:
        campaigns = real_google_ads_service.get_campaigns(customer_id)
        
        return jsonify({
            'success': True,
            'campaigns': campaigns
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting campaigns: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get campaigns'
        }), 500


@google_ads_bp.route('/customers/<customer_id>/campaigns', methods=['POST'])
@token_required
def create_campaign(customer_id):
    """Create a new campaign"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'budget_amount']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        campaign = real_google_ads_service.create_campaign(customer_id, data)
        
        return jsonify({
            'success': True,
            'campaign': campaign
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating campaign: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create campaign'
        }), 500


@google_ads_bp.route('/customers/<customer_id>/campaigns/<campaign_id>/budget', methods=['PUT'])
@token_required
def update_campaign_budget(customer_id, campaign_id):
    """Update campaign budget"""
    try:
        data = request.get_json()
        new_budget = data.get('budget_amount')
        
        if not new_budget:
            return jsonify({
                'success': False,
                'error': 'Budget amount is required'
            }), 400
        
        success = real_google_ads_service.update_campaign_budget(
            customer_id, campaign_id, new_budget
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Budget updated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update budget'
            }), 500
        
    except Exception as e:
        logger.error(f"Error updating budget: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update campaign budget'
        }), 500


@google_ads_bp.route('/customers/<customer_id>/campaigns/<campaign_id>/pause', methods=['POST'])
@token_required
def pause_campaign(customer_id, campaign_id):
    """Pause a campaign"""
    try:
        success = real_google_ads_service.pause_campaign(customer_id, campaign_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Campaign paused successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to pause campaign'
            }), 500
        
    except Exception as e:
        logger.error(f"Error pausing campaign: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to pause campaign'
        }), 500


@google_ads_bp.route('/customers/<customer_id>/campaigns/<campaign_id>/enable', methods=['POST'])
@token_required
def enable_campaign(customer_id, campaign_id):
    """Enable a campaign"""
    try:
        success = real_google_ads_service.enable_campaign(customer_id, campaign_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Campaign enabled successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to enable campaign'
            }), 500
        
    except Exception as e:
        logger.error(f"Error enabling campaign: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to enable campaign'
        }), 500


@google_ads_bp.route('/customers/<customer_id>/performance', methods=['GET'])
@token_required
def get_performance_metrics(customer_id):
    """Get performance metrics for customer"""
    try:
        campaign_id = request.args.get('campaign_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        metrics = real_google_ads_service.get_performance_metrics(
            customer_id=customer_id,
            campaign_id=campaign_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'success': True,
            'metrics': metrics
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get performance metrics'
        }), 500


@google_ads_bp.route('/customers/<customer_id>/campaigns/<campaign_id>/performance', methods=['GET'])
@token_required
def get_campaign_performance(customer_id, campaign_id):
    """Get performance metrics for specific campaign"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        metrics = real_google_ads_service.get_performance_metrics(
            customer_id=customer_id,
            campaign_id=campaign_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'success': True,
            'metrics': metrics
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting campaign performance: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get campaign performance'
        }), 500