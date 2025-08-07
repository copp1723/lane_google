from flask import Blueprint, request, jsonify
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import os
from dotenv import load_dotenv
import yaml

load_dotenv()

google_ads_bp = Blueprint('google_ads', __name__)

# Google Ads client will be initialized when needed
ads_client = None

def get_google_ads_client():
    """Initialize and return Google Ads client"""
    global ads_client
    if ads_client is None:
        try:
            # Create configuration dictionary with REST transport
            config = {
                'developer_token': os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN'),
                'client_id': os.getenv('GOOGLE_ADS_CLIENT_ID'),
                'client_secret': os.getenv('GOOGLE_ADS_CLIENT_SECRET'),
                'refresh_token': os.getenv('GOOGLE_ADS_REFRESH_TOKEN'),
                'login_customer_id': os.getenv('GOOGLE_ADS_LOGIN_CUSTOMER_ID'),
                'use_proto_plus': True,
                'transport': 'rest'  # Use REST transport to avoid gRPC issues
            }
            
            # Remove None values
            config = {k: v for k, v in config.items() if v is not None}
            
            ads_client = GoogleAdsClient.load_from_dict(config)
        except Exception as e:
            raise ValueError(f"Failed to initialize Google Ads client: {str(e)}")
    
    return ads_client

@google_ads_bp.route('/accounts', methods=['GET'])
def list_accounts():
    """List all accessible Google Ads accounts"""
    try:
        client = get_google_ads_client()
        customer_service = client.get_service("CustomerService")
        
        # Get accessible customers
        accessible_customers = customer_service.list_accessible_customers()
        
        accounts = []
        for customer_resource in accessible_customers.resource_names:
            customer_id = customer_resource.split('/')[-1]
            
            # Get customer details
            try:
                ga_service = client.get_service("GoogleAdsService")
                query = f"""
                    SELECT 
                        customer.id,
                        customer.descriptive_name,
                        customer.currency_code,
                        customer.time_zone,
                        customer.status
                    FROM customer 
                    WHERE customer.id = {customer_id}
                """
                
                response = ga_service.search(customer_id=customer_id, query=query)
                
                for row in response:
                    customer = row.customer
                    accounts.append({
                        'id': customer.id,
                        'name': customer.descriptive_name,
                        'currency': customer.currency_code,
                        'timezone': customer.time_zone,
                        'status': customer.status.name
                    })
                    break  # Only need first result
                    
            except GoogleAdsException as ex:
                # Skip accounts we can't access
                continue
        
        return jsonify({
            'accounts': accounts,
            'total_count': len(accounts),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to list accounts: {str(e)}'}), 500

@google_ads_bp.route('/campaigns/<customer_id>', methods=['GET'])
def list_campaigns(customer_id):
    """List campaigns for a specific customer"""
    try:
        client = get_google_ads_client()
        ga_service = client.get_service("GoogleAdsService")
        
        query = """
            SELECT 
                campaign.id,
                campaign.name,
                campaign.status,
                campaign.advertising_channel_type,
                campaign.start_date,
                campaign.end_date,
                campaign_budget.amount_micros,
                campaign_budget.delivery_method
            FROM campaign
            ORDER BY campaign.name
        """
        
        response = ga_service.search(customer_id=customer_id, query=query)
        
        campaigns = []
        for row in response:
            campaign = row.campaign
            budget = row.campaign_budget
            
            campaigns.append({
                'id': campaign.id,
                'name': campaign.name,
                'status': campaign.status.name,
                'type': campaign.advertising_channel_type.name,
                'start_date': campaign.start_date,
                'end_date': campaign.end_date,
                'budget_micros': budget.amount_micros,
                'budget_delivery': budget.delivery_method.name
            })
        
        return jsonify({
            'campaigns': campaigns,
            'customer_id': customer_id,
            'total_count': len(campaigns),
            'status': 'success'
        })
        
    except GoogleAdsException as ex:
        return jsonify({
            'error': f'Google Ads API error: {ex.error.message}',
            'details': str(ex)
        }), 400
    except Exception as e:
        return jsonify({'error': f'Failed to list campaigns: {str(e)}'}), 500

@google_ads_bp.route('/performance/<customer_id>', methods=['GET'])
def get_performance_data(customer_id):
    """Get performance metrics for campaigns"""
    try:
        client = get_google_ads_client()
        ga_service = client.get_service("GoogleAdsService")
        
        # Get date range from query parameters
        start_date = request.args.get('start_date', '2024-01-01')
        end_date = request.args.get('end_date', '2024-12-31')
        
        query = f"""
            SELECT 
                campaign.id,
                campaign.name,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.ctr,
                metrics.average_cpc,
                segments.date
            FROM campaign
            WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY campaign.name, segments.date
        """
        
        response = ga_service.search(customer_id=customer_id, query=query)
        
        performance_data = []
        for row in response:
            campaign = row.campaign
            metrics = row.metrics
            segments = row.segments
            
            performance_data.append({
                'campaign_id': campaign.id,
                'campaign_name': campaign.name,
                'date': segments.date,
                'impressions': metrics.impressions,
                'clicks': metrics.clicks,
                'cost_micros': metrics.cost_micros,
                'conversions': metrics.conversions,
                'ctr': metrics.ctr,
                'average_cpc': metrics.average_cpc
            })
        
        return jsonify({
            'performance_data': performance_data,
            'customer_id': customer_id,
            'date_range': {'start': start_date, 'end': end_date},
            'total_records': len(performance_data),
            'status': 'success'
        })
        
    except GoogleAdsException as ex:
        return jsonify({
            'error': f'Google Ads API error: {ex.error.message}',
            'details': str(ex)
        }), 400
    except Exception as e:
        return jsonify({'error': f'Failed to get performance data: {str(e)}'}), 500

@google_ads_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for Google Ads API connection"""
    try:
        # Check if required environment variables are set
        required_vars = [
            'GOOGLE_ADS_DEVELOPER_TOKEN',
            'GOOGLE_ADS_CLIENT_ID',
            'GOOGLE_ADS_CLIENT_SECRET',
            'GOOGLE_ADS_REFRESH_TOKEN'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            return jsonify({
                'status': 'error',
                'message': f'Missing environment variables: {", ".join(missing_vars)}'
            }), 500
        
        # Try to initialize client
        try:
            client = get_google_ads_client()
            return jsonify({
                'status': 'healthy',
                'service': 'Google Ads API',
                'client_initialized': True
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'service': 'Google Ads API',
                'message': f'Client initialization failed: {str(e)}'
            }), 500
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

