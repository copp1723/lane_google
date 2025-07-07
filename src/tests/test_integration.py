"""
Integration Tests for Lane MCP Components
Tests the interaction between all major services
"""

import pytest
import asyncio
from datetime import datetime, timedelta
import json
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.services.budget_pacing import budget_pacing_service, BudgetStatus
from src.services.health_monitor import health_monitor
from src.services.campaign_orchestrator import CampaignOrchestrator
from src.services.analytics_engine import analytics_engine
from src.services.approval_workflow import approval_workflow, ApprovalType, Priority
from campaign import Campaign
from database import db


class TestLaneMCPIntegration:
    """Integration tests for Lane MCP platform"""
    
    @pytest.fixture
    def sample_campaign(self):
        """Create a sample campaign for testing"""
        campaign = Campaign(
            name="Test Campaign",
            customer_id="test_customer_123",
            brief=json.dumps({
                "campaign_name": "Test Campaign",
                "budget": 1000,
                "keywords": ["test", "integration"],
                "target_audience": "developers"
            }),
            status="draft",
            budget_amount=1000.0,
            pacing_strategy="linear",
            billing_period_start=datetime.utcnow(),
            billing_period_end=datetime.utcnow() + timedelta(days=30)
        )
        db.session.add(campaign)
        db.session.commit()
        return campaign
    
    @pytest.mark.asyncio
    async def test_budget_pacing_service(self, sample_campaign):
        """Test budget pacing service functionality"""
        # Start the service
        await budget_pacing_service.start_monitoring()
        
        # Check campaign budget
        pacing_result = await budget_pacing_service.check_campaign_budget(
            str(sample_campaign.id)
        )
        
        # Verify results
        assert pacing_result is not None
        assert pacing_result.current_spend >= 0
        assert pacing_result.days_remaining >= 0
        assert pacing_result.pacing_status in [status for status in BudgetStatus]
        
        # Test recommendations
        recommendations = await budget_pacing_service.get_pacing_recommendations(
            str(sample_campaign.id)
        )
        
        assert 'status' in recommendations
        assert 'actions' in recommendations
        assert 'confidence_score' in recommendations
        
        # Stop the service
        await budget_pacing_service.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_health_monitoring(self):
        """Test health monitoring service"""
        # Get basic health status
        health_status = await health_monitor.get_health_status()
        
        assert 'status' in health_status
        assert 'timestamp' in health_status
        assert 'services' in health_status
        
        # Check specific services
        services = health_status['services']
        assert 'database' in services
        assert 'system' in services
        
        # Get detailed health status
        detailed_health = await health_monitor.get_health_status(detailed=True)
        
        assert 'environment' in detailed_health
        assert 'system' in detailed_health
        
        # Run diagnostic
        diagnostic = await health_monitor.run_diagnostic()
        
        assert 'health_status' in diagnostic
        assert 'metrics' in diagnostic
        assert 'recommendations' in diagnostic
    
    @pytest.mark.asyncio
    async def test_campaign_orchestrator(self, sample_campaign):
        """Test campaign orchestration workflow"""
        from google_ads import GoogleAdsService
        
        # Initialize orchestrator
        google_ads_service = GoogleAdsService()
        orchestrator = CampaignOrchestrator(google_ads_service)
        
        # Create workflow
        brief = json.loads(sample_campaign.brief)
        workflow_id = await orchestrator.create_campaign_workflow(
            brief, str(sample_campaign.id)
        )
        
        assert workflow_id is not None
        
        # Check workflow status
        status = orchestrator.get_workflow_status(workflow_id)
        assert status is not None
        assert status.workflow_id == workflow_id
        assert status.campaign_id == str(sample_campaign.id)
        
        # Get workflow tasks
        tasks = orchestrator.get_workflow_tasks(workflow_id)
        assert len(tasks) > 0
        
        # Wait a bit for some tasks to process
        await asyncio.sleep(2)
        
        # Check updated status
        updated_status = orchestrator.get_workflow_status(workflow_id)
        assert updated_status.progress >= 0
    
    @pytest.mark.asyncio
    async def test_analytics_engine(self, sample_campaign):
        """Test analytics engine functionality"""
        # Start analytics monitoring
        await analytics_engine.start_monitoring()
        
        # Capture initial snapshot
        await analytics_engine._capture_analytics_snapshot()
        
        # Get trend analysis
        trend = await analytics_engine.get_trend_analysis(
            str(sample_campaign.id), 'impressions', days=7
        )
        
        assert trend.metric_type == 'impressions'
        assert trend.trend in ['increasing', 'decreasing', 'stable', 'insufficient_data']
        
        # Generate forecast
        forecast = await analytics_engine.generate_forecast(
            str(sample_campaign.id), 'clicks', forecast_days=7
        )
        
        assert forecast.metric_type == 'clicks'
        assert isinstance(forecast.forecast_values, list)
        assert forecast.confidence_score >= 0
        
        # Export analytics
        export_data = await analytics_engine.export_analytics(
            str(sample_campaign.id),
            datetime.utcnow() - timedelta(days=7),
            datetime.utcnow(),
            format='json'
        )
        
        assert 'campaign_id' in export_data
        assert 'metrics' in export_data
        
        # Stop analytics monitoring
        await analytics_engine.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_approval_workflow(self, sample_campaign):
        """Test approval workflow functionality"""
        # Start approval monitoring
        await approval_workflow.start_monitoring()
        
        # Submit approval request
        request_id = await approval_workflow.submit_approval_request(
            ApprovalType.BUDGET_INCREASE,
            "test_user",
            str(sample_campaign.id),
            "Budget Increase Request",
            "Need to increase budget for better performance",
            {"new_budget": 1500, "increase_amount": 500},
            Priority.MEDIUM
        )
        
        # Should not be auto-approved due to amount
        assert request_id != "auto_approved"
        
        # Get pending requests
        pending = approval_workflow.get_pending_requests()
        assert len(pending) > 0
        
        # Get specific request status
        request_status = approval_workflow.get_request_status(request_id)
        assert request_status is not None
        assert request_status.campaign_id == str(sample_campaign.id)
        
        # Approve the request
        success = await approval_workflow.approve_request(
            request_id, "campaign_manager", "Approved for performance improvement"
        )
        assert success is True
        
        # Verify campaign was updated
        updated_campaign = Campaign.query.get(sample_campaign.id)
        assert updated_campaign.budget_amount == 1500
        
        # Test auto-approval
        auto_request_id = await approval_workflow.submit_approval_request(
            ApprovalType.BUDGET_INCREASE,
            "test_user",
            str(sample_campaign.id),
            "Small Budget Increase",
            "Small increase for testing",
            {"new_budget": 1550, "increase_amount": 50},
            Priority.LOW
        )
        
        # Should be auto-approved
        assert auto_request_id == "auto_approved"
        
        # Stop approval monitoring
        await approval_workflow.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_full_campaign_lifecycle(self, sample_campaign):
        """Test complete campaign lifecycle with all services"""
        # 1. Start all services
        await budget_pacing_service.start_monitoring()
        await analytics_engine.start_monitoring()
        await approval_workflow.start_monitoring()
        
        # 2. Create campaign workflow
        from google_ads import GoogleAdsService
        google_ads_service = GoogleAdsService()
        orchestrator = CampaignOrchestrator(google_ads_service)
        
        brief = json.loads(sample_campaign.brief)
        workflow_id = await orchestrator.create_campaign_workflow(
            brief, str(sample_campaign.id)
        )
        
        # 3. Submit approval for campaign launch
        approval_id = await approval_workflow.submit_approval_request(
            ApprovalType.CAMPAIGN_LAUNCH,
            "test_user",
            str(sample_campaign.id),
            "Launch Test Campaign",
            "Ready to launch test campaign",
            {"budget_amount": 1000},
            Priority.HIGH
        )
        
        # 4. Auto-approve small budget (should auto-approve)
        if approval_id != "auto_approved":
            await approval_workflow.approve_request(
                approval_id, "campaign_manager", "Approved for launch"
            )
        
        # 5. Check budget pacing
        pacing_result = await budget_pacing_service.check_campaign_budget(
            str(sample_campaign.id)
        )
        assert pacing_result is not None
        
        # 6. Generate analytics
        trend = await analytics_engine.get_trend_analysis(
            str(sample_campaign.id), 'cost', days=7
        )
        assert trend is not None
        
        # 7. Check system health
        health = await health_monitor.get_health_status()
        assert health['status'] in ['healthy', 'degraded', 'unhealthy']
        
        # 8. Verify campaign status
        updated_campaign = Campaign.query.get(sample_campaign.id)
        # Campaign should be active if auto-approved
        if approval_id == "auto_approved":
            assert updated_campaign.status == 'active'
        
        # 9. Stop all services
        await budget_pacing_service.stop_monitoring()
        await analytics_engine.stop_monitoring()
        await approval_workflow.stop_monitoring()
    
    def test_service_integration_health(self):
        """Test that all services can be imported and initialized"""
        # Test budget pacing
        assert budget_pacing_service is not None
        assert hasattr(budget_pacing_service, 'start_monitoring')
        
        # Test health monitor
        assert health_monitor is not None
        assert hasattr(health_monitor, 'get_health_status')
        
        # Test analytics engine
        assert analytics_engine is not None
        assert hasattr(analytics_engine, 'get_trend_analysis')
        
        # Test approval workflow
        assert approval_workflow is not None
        assert hasattr(approval_workflow, 'submit_approval_request')
        
        print("✅ All services integrated successfully")
    
    def test_api_endpoints_structure(self):
        """Test that API endpoints are properly structured"""
        from src.api.budget_pacing_api import budget_pacing_bp
        from src.api.health_api import health_bp
        from src.api.orchestrator_api import orchestrator_bp
        
        # Test blueprints exist
        assert budget_pacing_bp is not None
        assert health_bp is not None
        assert orchestrator_bp is not None
        
        # Test they have rules (endpoints)
        assert len(budget_pacing_bp.deferred_functions) > 0
        assert len(health_bp.deferred_functions) > 0
        assert len(orchestrator_bp.deferred_functions) > 0
        
        print("✅ All API endpoints properly structured")


# Run basic integration test
if __name__ == "__main__":
    test = TestLaneMCPIntegration()
    test.test_service_integration_health()
    test.test_api_endpoints_structure()
    print("🎉 Lane MCP Integration Test Complete!")