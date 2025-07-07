"""
Real Google Ads API Integration
Replaces mock implementation with actual Google Ads API calls
"""

import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.api_core import retry
import json

logger = logging.getLogger(__name__)


class RealGoogleAdsService:
    """Production Google Ads API service"""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize Google Ads client with credentials"""
        try:
            # Check for required environment variables
            required_env_vars = [
                'GOOGLE_ADS_CLIENT_ID',
                'GOOGLE_ADS_CLIENT_SECRET', 
                'GOOGLE_ADS_REFRESH_TOKEN',
                'GOOGLE_ADS_DEVELOPER_TOKEN'
            ]
            
            missing_vars = [var for var in required_env_vars if not os.getenv(var)]
            if missing_vars:
                logger.error(f"Missing required environment variables: {missing_vars}")
                return
                
            # Initialize client
            self.client = GoogleAdsClient.load_from_env()
            logger.info("Google Ads client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Ads client: {str(e)}")
            self.client = None
    
    @retry.Retry(predicate=retry.if_transient_error)
    def get_accessible_customers(self) -> List[Dict[str, Any]]:
        """Get list of accessible Google Ads accounts"""
        if not self.client:
            raise Exception("Google Ads client not initialized")
            
        try:
            customer_service = self.client.get_service("CustomerService")
            accessible_customers = customer_service.list_accessible_customers()
            
            customers = []
            for customer_resource in accessible_customers.resource_names:
                customer_id = customer_resource.split('/')[-1]
                
                # Get customer details
                customer_info = self._get_customer_info(customer_id)
                if customer_info:
                    customers.append(customer_info)
                    
            return customers
            
        except GoogleAdsException as ex:
            logger.error(f"Google Ads API error: {ex}")
            raise
        except Exception as e:
            logger.error(f"Error getting accessible customers: {str(e)}")
            raise
    
    def _get_customer_info(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed customer information"""
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = f"""
                SELECT 
                    customer.id,
                    customer.descriptive_name,
                    customer.currency_code,
                    customer.time_zone,
                    customer.test_account,
                    customer.manager,
                    customer.optimization_score
                FROM customer 
                WHERE customer.id = {customer_id}
            """
            
            response = ga_service.search(customer_id=customer_id, query=query)
            
            for row in response:
                customer = row.customer
                return {
                    'id': str(customer.id),
                    'name': customer.descriptive_name,
                    'currency_code': customer.currency_code,
                    'time_zone': customer.time_zone,
                    'is_test_account': customer.test_account,
                    'is_manager_account': customer.manager,
                    'optimization_score': customer.optimization_score
                }
                
            return None
            
        except Exception as e:
            logger.warning(f"Could not get customer info for {customer_id}: {str(e)}")
            return None
    
    @retry.Retry(predicate=retry.if_transient_error)
    def get_campaigns(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get campaigns for a customer"""
        if not self.client:
            raise Exception("Google Ads client not initialized")
            
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = """
                SELECT 
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    campaign.advertising_channel_type,
                    campaign.bidding_strategy_type,
                    campaign_budget.amount_micros,
                    campaign_budget.delivery_method,
                    campaign.start_date,
                    campaign.end_date,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions
                FROM campaign 
                WHERE campaign.status != 'REMOVED'
            """
            
            response = ga_service.search(customer_id=customer_id, query=query)
            
            campaigns = []
            for row in response:
                campaign = row.campaign
                metrics = row.metrics
                budget = row.campaign_budget
                
                campaigns.append({
                    'id': str(campaign.id),
                    'name': campaign.name,
                    'status': campaign.status.name,
                    'channel_type': campaign.advertising_channel_type.name,
                    'bidding_strategy': campaign.bidding_strategy_type.name,
                    'budget_amount': budget.amount_micros / 1_000_000,  # Convert from micros
                    'delivery_method': budget.delivery_method.name,
                    'start_date': campaign.start_date,
                    'end_date': campaign.end_date,
                    'performance': {
                        'impressions': metrics.impressions,
                        'clicks': metrics.clicks,
                        'cost': metrics.cost_micros / 1_000_000,  # Convert from micros
                        'conversions': metrics.conversions
                    }
                })
                
            return campaigns
            
        except GoogleAdsException as ex:
            logger.error(f"Google Ads API error getting campaigns: {ex}")
            raise
        except Exception as e:
            logger.error(f"Error getting campaigns: {str(e)}")
            raise
    
    @retry.Retry(predicate=retry.if_transient_error)
    def create_campaign(self, customer_id: str, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Google Ads campaign"""
        if not self.client:
            raise Exception("Google Ads client not initialized")
            
        try:
            # Get services
            campaign_service = self.client.get_service("CampaignService")
            campaign_budget_service = self.client.get_service("CampaignBudgetService")
            
            # Create budget first
            budget_operation = self.client.get_type("CampaignBudgetOperation")
            budget = budget_operation.create
            budget.name = f"Budget for {campaign_data['name']}"
            budget.amount_micros = int(campaign_data['budget_amount'] * 1_000_000)  # Convert to micros
            budget.delivery_method = self.client.enums.BudgetDeliveryMethodEnum.STANDARD
            
            budget_response = campaign_budget_service.mutate_campaign_budgets(
                customer_id=customer_id, operations=[budget_operation]
            )
            budget_resource_name = budget_response.results[0].resource_name
            
            # Create campaign
            campaign_operation = self.client.get_type("CampaignOperation")
            campaign = campaign_operation.create
            campaign.name = campaign_data['name']
            campaign.advertising_channel_type = getattr(
                self.client.enums.AdvertisingChannelTypeEnum, 
                campaign_data.get('channel_type', 'SEARCH')
            )
            campaign.status = self.client.enums.CampaignStatusEnum.PAUSED  # Start paused
            campaign.campaign_budget = budget_resource_name
            
            # Set bidding strategy
            bidding_strategy = campaign_data.get('bidding_strategy', 'MAXIMIZE_CLICKS')
            if bidding_strategy == 'MAXIMIZE_CLICKS':
                campaign.maximize_clicks.target_spend_micros = int(campaign_data['budget_amount'] * 1_000_000)
            elif bidding_strategy == 'TARGET_CPA':
                campaign.target_cpa.target_cpa_micros = int(campaign_data.get('target_cpa', 10) * 1_000_000)
            elif bidding_strategy == 'TARGET_ROAS':
                campaign.target_roas.target_roas = campaign_data.get('target_roas', 4.0)
            
            # Set dates if provided
            if campaign_data.get('start_date'):
                campaign.start_date = campaign_data['start_date']
            if campaign_data.get('end_date'):
                campaign.end_date = campaign_data['end_date']
                
            # Create campaign
            campaign_response = campaign_service.mutate_campaigns(
                customer_id=customer_id, operations=[campaign_operation]
            )
            
            campaign_resource_name = campaign_response.results[0].resource_name
            campaign_id = campaign_resource_name.split('/')[-1]
            
            logger.info(f"Created campaign {campaign_id} for customer {customer_id}")
            
            return {
                'campaign_id': campaign_id,
                'campaign_resource_name': campaign_resource_name,
                'budget_resource_name': budget_resource_name,
                'status': 'PAUSED'
            }
            
        except GoogleAdsException as ex:
            logger.error(f"Google Ads API error creating campaign: {ex}")
            raise
        except Exception as e:
            logger.error(f"Error creating campaign: {str(e)}")
            raise
    
    @retry.Retry(predicate=retry.if_transient_error)
    def update_campaign_budget(self, customer_id: str, campaign_id: str, 
                              new_budget_amount: float) -> bool:
        """Update campaign budget"""
        if not self.client:
            raise Exception("Google Ads client not initialized")
            
        try:
            # Get campaign budget resource name
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = f"""
                SELECT campaign_budget.resource_name
                FROM campaign 
                WHERE campaign.id = {campaign_id}
            """
            
            response = ga_service.search(customer_id=customer_id, query=query)
            budget_resource_name = None
            
            for row in response:
                budget_resource_name = row.campaign_budget.resource_name
                break
                
            if not budget_resource_name:
                raise Exception(f"Could not find budget for campaign {campaign_id}")
            
            # Update budget
            campaign_budget_service = self.client.get_service("CampaignBudgetService")
            
            budget_operation = self.client.get_type("CampaignBudgetOperation")
            budget = budget_operation.update
            budget.resource_name = budget_resource_name
            budget.amount_micros = int(new_budget_amount * 1_000_000)  # Convert to micros
            
            budget_operation.update_mask = self.client.get_type("FieldMask")
            budget_operation.update_mask.paths.append("amount_micros")
            
            response = campaign_budget_service.mutate_campaign_budgets(
                customer_id=customer_id, operations=[budget_operation]
            )
            
            logger.info(f"Updated budget for campaign {campaign_id} to ${new_budget_amount}")
            return True
            
        except GoogleAdsException as ex:
            logger.error(f"Google Ads API error updating budget: {ex}")
            raise
        except Exception as e:
            logger.error(f"Error updating campaign budget: {str(e)}")
            raise
    
    @retry.Retry(predicate=retry.if_transient_error)
    def get_performance_metrics(self, customer_id: str, campaign_id: str = None,
                               start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Get performance metrics for campaigns"""
        if not self.client:
            raise Exception("Google Ads client not initialized")
            
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            # Default to last 30 days if no dates provided
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            # Build query
            where_clause = f"segments.date BETWEEN '{start_date}' AND '{end_date}'"
            if campaign_id:
                where_clause += f" AND campaign.id = {campaign_id}"
                
            query = f"""
                SELECT 
                    campaign.id,
                    campaign.name,
                    segments.date,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.conversions_value,
                    metrics.ctr,
                    metrics.average_cpc,
                    metrics.cost_per_conversion
                FROM campaign 
                WHERE {where_clause}
                ORDER BY segments.date DESC
            """
            
            response = ga_service.search(customer_id=customer_id, query=query)
            
            # Aggregate metrics
            daily_metrics = {}
            total_metrics = {
                'impressions': 0,
                'clicks': 0,
                'cost': 0,
                'conversions': 0,
                'conversions_value': 0
            }
            
            for row in response:
                date = row.segments.date
                metrics = row.metrics
                
                if date not in daily_metrics:
                    daily_metrics[date] = {
                        'impressions': 0,
                        'clicks': 0,
                        'cost': 0,
                        'conversions': 0,
                        'conversions_value': 0
                    }
                
                daily_metrics[date]['impressions'] += metrics.impressions
                daily_metrics[date]['clicks'] += metrics.clicks
                daily_metrics[date]['cost'] += metrics.cost_micros / 1_000_000
                daily_metrics[date]['conversions'] += metrics.conversions
                daily_metrics[date]['conversions_value'] += metrics.conversions_value
                
                # Add to totals
                total_metrics['impressions'] += metrics.impressions
                total_metrics['clicks'] += metrics.clicks
                total_metrics['cost'] += metrics.cost_micros / 1_000_000
                total_metrics['conversions'] += metrics.conversions
                total_metrics['conversions_value'] += metrics.conversions_value
            
            # Calculate derived metrics
            if total_metrics['impressions'] > 0:
                total_metrics['ctr'] = (total_metrics['clicks'] / total_metrics['impressions']) * 100
            else:
                total_metrics['ctr'] = 0
                
            if total_metrics['clicks'] > 0:
                total_metrics['cpc'] = total_metrics['cost'] / total_metrics['clicks']
            else:
                total_metrics['cpc'] = 0
                
            if total_metrics['conversions'] > 0:
                total_metrics['cpa'] = total_metrics['cost'] / total_metrics['conversions']
                total_metrics['conversion_rate'] = (total_metrics['conversions'] / total_metrics['clicks']) * 100
            else:
                total_metrics['cpa'] = 0
                total_metrics['conversion_rate'] = 0
            
            return {
                'period': {'start_date': start_date, 'end_date': end_date},
                'total_metrics': total_metrics,
                'daily_metrics': daily_metrics
            }
            
        except GoogleAdsException as ex:
            logger.error(f"Google Ads API error getting metrics: {ex}")
            raise
        except Exception as e:
            logger.error(f"Error getting performance metrics: {str(e)}")
            raise
    
    def pause_campaign(self, customer_id: str, campaign_id: str) -> bool:
        """Pause a campaign"""
        return self._update_campaign_status(customer_id, campaign_id, 'PAUSED')
    
    def enable_campaign(self, customer_id: str, campaign_id: str) -> bool:
        """Enable a campaign"""
        return self._update_campaign_status(customer_id, campaign_id, 'ENABLED')
    
    def _update_campaign_status(self, customer_id: str, campaign_id: str, status: str) -> bool:
        """Update campaign status"""
        if not self.client:
            raise Exception("Google Ads client not initialized")
            
        try:
            campaign_service = self.client.get_service("CampaignService")
            
            campaign_operation = self.client.get_type("CampaignOperation")
            campaign = campaign_operation.update
            campaign.resource_name = f"customers/{customer_id}/campaigns/{campaign_id}"
            campaign.status = getattr(self.client.enums.CampaignStatusEnum, status)
            
            campaign_operation.update_mask = self.client.get_type("FieldMask")
            campaign_operation.update_mask.paths.append("status")
            
            response = campaign_service.mutate_campaigns(
                customer_id=customer_id, operations=[campaign_operation]
            )
            
            logger.info(f"Updated campaign {campaign_id} status to {status}")
            return True
            
        except GoogleAdsException as ex:
            logger.error(f"Google Ads API error updating status: {ex}")
            raise
        except Exception as e:
            logger.error(f"Error updating campaign status: {str(e)}")
            raise


# Global instance
real_google_ads_service = RealGoogleAdsService()