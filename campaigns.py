from flask import Blueprint, request, jsonify
from src.models.campaign import Campaign, db
from src.routes.google_ads import get_google_ads_client
from google.ads.googleads.errors import GoogleAdsException
import json
from datetime import datetime

campaigns_bp = Blueprint('campaigns', __name__)

@campaigns_bp.route('/create', methods=['POST'])
def create_campaign():
    """Create a new Google Ads campaign from AI-generated brief"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        required_fields = ['customer_id', 'campaign_brief']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        customer_id = data['customer_id']
        campaign_brief = data['campaign_brief']
        
        # Extract campaign parameters from brief
        campaign_name = campaign_brief.get('campaign_name', 'AI Generated Campaign')
        budget_micros = int(float(campaign_brief.get('budget', 1000)) * 1000000)  # Convert to micros
        
        # Store campaign brief in database
        campaign_record = Campaign(
            name=campaign_name,
            customer_id=customer_id,
            brief=json.dumps(campaign_brief),
            status='draft',
            created_at=datetime.utcnow()
        )
        
        db.session.add(campaign_record)
        db.session.commit()
        
        return jsonify({
            'campaign_id': campaign_record.id,
            'name': campaign_name,
            'status': 'draft',
            'brief': campaign_brief,
            'message': 'Campaign brief saved. Ready for approval and Google Ads creation.',
            'status': 'success'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create campaign: {str(e)}'}), 500

@campaigns_bp.route('/approve/<int:campaign_id>', methods=['POST'])
def approve_campaign(campaign_id):
    """Approve a campaign and create it in Google Ads"""
    try:
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        if campaign.status != 'draft':
            return jsonify({'error': 'Campaign is not in draft status'}), 400
        
        # Parse campaign brief
        brief = json.loads(campaign.brief)
        
        # Create campaign in Google Ads
        client = get_google_ads_client()
        campaign_service = client.get_service("CampaignService")
        campaign_budget_service = client.get_service("CampaignBudgetService")
        
        # Create campaign budget first
        budget_operation = client.get_type("CampaignBudgetOperation")
        budget = budget_operation.create
        budget.name = f"{campaign.name} Budget"
        budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
        budget.amount_micros = int(float(brief.get('budget', 1000)) * 1000000)
        
        budget_response = campaign_budget_service.mutate_campaign_budgets(
            customer_id=campaign.customer_id,
            operations=[budget_operation]
        )
        
        budget_resource_name = budget_response.results[0].resource_name
        
        # Create campaign
        campaign_operation = client.get_type("CampaignOperation")
        new_campaign = campaign_operation.create
        new_campaign.name = campaign.name
        new_campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
        new_campaign.status = client.enums.CampaignStatusEnum.PAUSED  # Start paused for safety
        new_campaign.campaign_budget = budget_resource_name
        
        # Set bidding strategy
        new_campaign.manual_cpc.enhanced_cpc_enabled = True
        
        campaign_response = campaign_service.mutate_campaigns(
            customer_id=campaign.customer_id,
            operations=[campaign_operation]
        )
        
        google_campaign_id = campaign_response.results[0].resource_name.split('/')[-1]
        
        # Update campaign record
        campaign.google_campaign_id = google_campaign_id
        campaign.status = 'approved'
        campaign.approved_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'campaign_id': campaign.id,
            'google_campaign_id': google_campaign_id,
            'name': campaign.name,
            'status': 'approved',
            'message': 'Campaign approved and created in Google Ads',
            'status': 'success'
        })
        
    except GoogleAdsException as ex:
        db.session.rollback()
        return jsonify({
            'error': f'Google Ads API error: {ex.error.message}',
            'details': str(ex)
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to approve campaign: {str(e)}'}), 500

@campaigns_bp.route('/list', methods=['GET'])
def list_campaigns():
    """List all campaigns in the database"""
    try:
        campaigns = Campaign.query.order_by(Campaign.created_at.desc()).all()
        
        campaign_list = []
        for campaign in campaigns:
            brief = json.loads(campaign.brief) if campaign.brief else {}
            
            campaign_list.append({
                'id': campaign.id,
                'name': campaign.name,
                'customer_id': campaign.customer_id,
                'google_campaign_id': campaign.google_campaign_id,
                'status': campaign.status,
                'brief': brief,
                'created_at': campaign.created_at.isoformat() if campaign.created_at else None,
                'approved_at': campaign.approved_at.isoformat() if campaign.approved_at else None
            })
        
        return jsonify({
            'campaigns': campaign_list,
            'total_count': len(campaign_list),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to list campaigns: {str(e)}'}), 500

@campaigns_bp.route('/<int:campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    """Get details of a specific campaign"""
    try:
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        brief = json.loads(campaign.brief) if campaign.brief else {}
        
        campaign_data = {
            'id': campaign.id,
            'name': campaign.name,
            'customer_id': campaign.customer_id,
            'google_campaign_id': campaign.google_campaign_id,
            'status': campaign.status,
            'brief': brief,
            'created_at': campaign.created_at.isoformat() if campaign.created_at else None,
            'approved_at': campaign.approved_at.isoformat() if campaign.approved_at else None
        }
        
        return jsonify({
            'campaign': campaign_data,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get campaign: {str(e)}'}), 500

@campaigns_bp.route('/<int:campaign_id>/status', methods=['PUT'])
def update_campaign_status(campaign_id):
    """Update campaign status"""
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400
        
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        new_status = data['status']
        valid_statuses = ['draft', 'approved', 'active', 'paused', 'cancelled']
        
        if new_status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
        
        campaign.status = new_status
        db.session.commit()
        
        return jsonify({
            'campaign_id': campaign.id,
            'name': campaign.name,
            'status': campaign.status,
            'message': f'Campaign status updated to {new_status}',
            'status': 'success'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update campaign status: {str(e)}'}), 500

