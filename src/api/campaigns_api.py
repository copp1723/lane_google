"""
Basic campaigns API for demo purposes
"""

from flask import Blueprint, jsonify, request
import random
from datetime import datetime, timedelta

campaigns_api_bp = Blueprint('campaigns_api', __name__)

@campaigns_api_bp.route('/api/google-ads/campaigns', methods=['GET'])
def get_campaigns():
    """Get campaigns for demo purposes"""
    try:
        # Return demo campaign data
        campaigns = [
            {
                "id": "camp_001",
                "name": "Demo Campaign 1",
                "status": "ENABLED",
                "advertising_channel_type": "SEARCH",
                "budget_amount_micros": 5000000000,  # $5000
                "created_at": "2024-01-15T10:30:00Z",
                "metrics": {
                    "impressions": random.randint(10000, 100000),
                    "clicks": random.randint(500, 5000),
                    "cost_micros": random.randint(1000000000, 5000000000),  # $1000-5000
                    "conversions": random.randint(50, 500)
                }
            },
            {
                "id": "camp_002", 
                "name": "Demo Campaign 2",
                "status": "PAUSED",
                "advertising_channel_type": "DISPLAY",
                "budget_amount_micros": 3000000000,  # $3000
                "created_at": "2024-01-10T14:20:00Z",
                "metrics": {
                    "impressions": random.randint(10000, 100000),
                    "clicks": random.randint(500, 5000),
                    "cost_micros": random.randint(1000000000, 5000000000),
                    "conversions": random.randint(50, 500)
                }
            },
            {
                "id": "camp_003",
                "name": "Demo Campaign 3", 
                "status": "ENABLED",
                "advertising_channel_type": "VIDEO",
                "budget_amount_micros": 8000000000,  # $8000
                "created_at": "2024-01-05T09:15:00Z",
                "metrics": {
                    "impressions": random.randint(10000, 100000),
                    "clicks": random.randint(500, 5000),
                    "cost_micros": random.randint(1000000000, 5000000000),
                    "conversions": random.randint(50, 500)
                }
            }
        ]
        
        return jsonify({
            "success": True,
            "data": {
                "campaigns": campaigns
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@campaigns_api_bp.route('/api/orchestrator/workflows', methods=['GET'])
def get_workflows():
    """Get workflows for demo purposes"""
    try:
        workflows = [
            {
                "workflow_id": "wf_001",
                "campaign_id": "camp_001",
                "current_phase": "completed",
                "progress": 100
            },
            {
                "workflow_id": "wf_002", 
                "campaign_id": "camp_002",
                "current_phase": "in_progress",
                "progress": 65
            },
            {
                "workflow_id": "wf_003",
                "campaign_id": "camp_003", 
                "current_phase": "review_required",
                "progress": 85
            }
        ]
        
        return jsonify({
            "success": True,
            "data": {
                "workflows": workflows
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@campaigns_api_bp.route('/api/google-ads/campaigns/<campaign_id>/status', methods=['PUT'])
def update_campaign_status(campaign_id):
    """Update campaign status"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        return jsonify({
            "success": True,
            "data": {
                "campaign_id": campaign_id,
                "status": new_status,
                "updated_at": datetime.utcnow().isoformat()
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@campaigns_api_bp.route('/api/orchestrator/campaigns/create-workflow', methods=['POST'])
def create_workflow():
    """Create workflow for campaign"""
    try:
        data = request.get_json()
        
        return jsonify({
            "success": True,
            "data": {
                "workflow_id": f"wf_{random.randint(1000, 9999)}",
                "status": "created",
                "created_at": datetime.utcnow().isoformat()
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500