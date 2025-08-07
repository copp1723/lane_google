"""
Campaign Orchestrator API Endpoints
Provides API for campaign workflow management
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import logging
from src.services.campaign_orchestrator import campaign_orchestrator, TaskStatus
from src.models.campaign import Campaign
from src.config.database import db
from src.utils.responses import success_response, error_response, server_error_response, unauthorized_response, not_found_response, forbidden_response
import json

logger = logging.getLogger(__name__)

# Create blueprint
orchestrator_bp = Blueprint('orchestrator', __name__)


@orchestrator_bp.route('/campaigns/<campaign_id>/workflow', methods=['POST'])
@login_required
def create_campaign_workflow(campaign_id):
    """Create a workflow to build and launch a campaign"""
    try:
        # Get campaign
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return not_found_response('Campaign not found')

        if campaign.customer_id != current_user.customer_id:
            return forbidden_response('Unauthorized')
        
        # Parse campaign brief
        brief = json.loads(campaign.brief) if campaign.brief else {}
        
        # Create workflow
        workflow_id = campaign_orchestrator.create_campaign_workflow(
            campaign_brief=brief,
            campaign_id=campaign_id
        )
        
        # Update campaign status
        campaign.status = 'in_progress'
        db.session.commit()
        
        return success_response(data={
            'message': 'Campaign workflow created',
            'workflow_id': workflow_id,
            'campaign_id': campaign_id
        })

    except Exception as e:
        logger.error(f'Error creating workflow: {str(e)}')
        return server_error_response(f'Failed to create workflow: {str(e)}')


@orchestrator_bp.route('/workflows/<workflow_id>/status', methods=['GET'])
@login_required
def get_workflow_status(workflow_id):
    """Get current status of a workflow"""
    try:
        status = campaign_orchestrator.get_workflow_status(workflow_id)
        if not status:
            return not_found_response('Workflow not found')
        
        return success_response(data={
            'workflow_id': status.workflow_id,
            'campaign_id': status.campaign_id,
            'current_phase': status.current_phase.value,
            'progress': status.progress,
            'active_tasks': status.active_tasks,
            'completed_tasks': status.completed_tasks,
            'failed_tasks': status.failed_tasks,
            'message': status.message,
            'start_time': status.start_time.isoformat(),
            'estimated_completion': status.estimated_completion.isoformat() if status.estimated_completion else None
        })
        
    except Exception as e:
        logger.error(f'Error getting workflow status: {str(e)}')
        return server_error_response(f'Failed to get workflow status: {str(e)}')


@orchestrator_bp.route('/workflows/<workflow_id>/tasks', methods=['GET'])
@login_required
def get_workflow_tasks(workflow_id):
    """Get all tasks for a workflow"""
    try:
        tasks = campaign_orchestrator.get_workflow_tasks(workflow_id)
        if not tasks:
            return not_found_response('Workflow not found')
        
        task_list = []
        for task in tasks:
            task_list.append({
                'id': task.id,
                'agent_role': task.agent_role.value,
                'phase': task.phase.value,
                'description': task.description,
                'status': task.status.value,
                'dependencies': task.dependencies,
                'created_at': task.created_at.isoformat(),
                'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                'error': task.error
            })
        
        return success_response(data={
            'workflow_id': workflow_id,
            'tasks': task_list,
            'total_tasks': len(task_list)
        })
        
    except Exception as e:
        logger.error(f'Error getting workflow tasks: {str(e)}')
        return server_error_response(f'Failed to get workflow tasks: {str(e)}')


@orchestrator_bp.route('/workflows/<workflow_id>/cancel', methods=['POST'])
@login_required
def cancel_workflow(workflow_id):
    """Cancel a running workflow"""
    try:
        success = campaign_orchestrator.cancel_workflow(workflow_id)
        if not success:
            return not_found_response('Workflow not found')
        
        return success_response(data={
            'message': 'Workflow cancelled',
            'workflow_id': workflow_id
        })
        
    except Exception as e:
        logger.error(f'Error cancelling workflow: {str(e)}')
        return server_error_response(f'Failed to cancel workflow: {str(e)}')


@orchestrator_bp.route('/workflows', methods=['GET'])
@login_required
def list_workflows():
    """List all workflows for the user's campaigns"""
    try:
        # Get user's campaigns
        campaigns = Campaign.query.filter_by(
            customer_id=current_user.customer_id
        ).all()
        
        campaign_ids = [c.id for c in campaigns]
        
        # Get workflows for these campaigns
        workflows = []
        for workflow_id, workflow in campaign_orchestrator.workflows.items():
            if workflow['campaign_id'] in campaign_ids:
                status = workflow['status']
                workflows.append({
                    'workflow_id': workflow_id,
                    'campaign_id': workflow['campaign_id'],
                    'current_phase': status.current_phase.value,
                    'progress': status.progress,
                    'status': 'active' if status.active_tasks > 0 else 'completed',
                    'start_time': status.start_time.isoformat()
                })
        
        return success_response(data={
            'workflows': workflows,
            'total': len(workflows)
        })
        
    except Exception as e:
        logger.error(f'Error listing workflows: {str(e)}')
        return server_error_response(f'Failed to list workflows: {str(e)}')


@orchestrator_bp.route('/workflows/<workflow_id>/task/<task_id>/result', methods=['GET'])
@login_required
def get_task_result(workflow_id, task_id):
    """Get the result of a specific task"""
    try:
        tasks = campaign_orchestrator.get_workflow_tasks(workflow_id)
        if not tasks:
            return not_found_response('Workflow not found')
        
        task = next((t for t in tasks if t.id == task_id), None)
        if not task:
            return not_found_response('Task not found')
        
        return success_response(data={
            'task_id': task.id,
            'status': task.status.value,
            'result': task.result,
            'error': task.error,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None
        })
        
    except Exception as e:
        logger.error(f'Error getting task result: {str(e)}')
        return server_error_response(f'Failed to get task result: {str(e)}')


# Webhook for workflow status updates
@orchestrator_bp.route('/webhooks/workflow-status', methods=['POST'])
def workflow_status_webhook():
    """Webhook endpoint for workflow status notifications"""
    try:
        # Verify webhook signature
        api_key = request.headers.get('X-API-Key')
        if api_key != 'your-webhook-api-key':  # Replace with config
            return unauthorized_response('Unauthorized')
        
        data = request.get_json()
        
        # Process status update
        logger.info(f"Received workflow status webhook: {data}")
        
        # You can add custom processing here
        # For example, update external systems, send notifications, etc.
        
        return success_response(data={'message': 'Status update processed'})
        
    except Exception as e:
        logger.error(f'Error processing webhook: {str(e)}')
        return server_error_response(f'Failed to process webhook: {str(e)}')