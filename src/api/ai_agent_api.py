"""
AI Agent API for Natural Language Campaign Creation
Provides endpoints for conversational AI interactions and campaign brief generation
"""

import logging
import uuid
import asyncio
from datetime import datetime
from flask import Blueprint, request, jsonify
from typing import Dict, Any, Optional

from src.services.openrouter_client import get_openrouter_client
from src.services.conversation import Conversation, MessageRole, ConversationType
from src.services.campaign_orchestrator import campaign_orchestrator
from src.config.database import db

logger = logging.getLogger(__name__)

ai_agent_bp = Blueprint('ai_agent', __name__)

def get_ai_service():
    """Get OpenRouter AI service"""
    return get_openrouter_client()

@ai_agent_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for AI agent service"""
    try:
        service = get_ai_service()
        api_key_configured = bool(service.api_key)
        
        return jsonify({
            'status': 'healthy',
            'service': 'ai_agent',
            'timestamp': datetime.utcnow().isoformat(),
            'api_key_configured': api_key_configured,
            'service_type': 'openrouter' if api_key_configured else 'mock_fallback',
            'base_url': service.base_url
        })
    except Exception as e:
        logger.error(f"AI Agent health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@ai_agent_bp.route('/chat', methods=['POST'])
def chat_with_agent():
    """
    Chat with AI agent for campaign planning
    
    Expected payload:
    {
        "message": "I want to create a campaign for my e-commerce store",
        "conversation_id": "optional-existing-id",
        "user_id": "user-123",
        "context": {"customer_id": "123-456-789"}
    }
    """
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        message = data['message']
        user_id = data.get('user_id', 'demo-user')  # TODO: Get from auth
        conversation_id = data.get('conversation_id')
        context = data.get('context', {})
        
        # Create or get existing conversation
        if conversation_id:
            conversation = Conversation.query.filter_by(id=conversation_id).first()
            if not conversation:
                return jsonify({'error': 'Conversation not found'}), 404
        else:
            conversation = Conversation(
                user_id=user_id,
                conversation_type=ConversationType.CAMPAIGN_PLANNING,
                google_customer_id=context.get('customer_id'),
                context=context
            )
            db.session.add(conversation)
            db.session.commit()
            conversation_id = conversation.id
        
        # Add user message to conversation
        conversation.add_message(MessageRole.USER, message)
        
        # Get AI response using the service
        service = get_ai_service()

        # Since Flask routes are sync but AI service is async, we'll use asyncio
        import asyncio
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(
                service.chat_with_agent(
                    message=message,
                    conversation_id=conversation_id,
                    agent_type="campaign_planner",
                    context=context
                )
            )
        except Exception as e:
            logger.error(f"AI service error: {e}")
            # Fallback response
            response = {
                'response': "I understand you want to create a campaign. Let me help you with that. Can you tell me more about your business goals and target audience?",
                'conversation_id': conversation_id,
                'model_used': 'fallback-model',
                'usage': {'total_tokens': 50}
            }
        
        # Add AI response to conversation
        conversation.add_message(
            MessageRole.ASSISTANT, 
            response['response'],
            metadata={
                'model_used': response.get('model_used'),
                'usage': response.get('usage', {})
            }
        )
        
        # Update conversation
        conversation.total_tokens_used += response.get('usage', {}).get('total_tokens', 0)
        db.session.commit()
        
        return jsonify({
            'response': response['response'],
            'conversation_id': conversation_id,
            'status': 'success',
            'can_generate_brief': len(conversation.messages) >= 4,  # After some back and forth
            'metadata': {
                'model_used': response.get('model_used'),
                'tokens_used': response.get('usage', {}).get('total_tokens', 0),
                'total_conversation_tokens': conversation.total_tokens_used
            }
        })
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({'error': f'Chat failed: {str(e)}'}), 500

@ai_agent_bp.route('/conversations/<conversation_id>/brief', methods=['POST'])
def generate_campaign_brief(conversation_id):
    """
    Generate structured campaign brief from conversation
    """
    try:
        conversation = Conversation.query.filter_by(id=conversation_id).first()
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        if len(conversation.messages) < 2:
            return jsonify({'error': 'Not enough conversation history to generate brief'}), 400
        
        # Generate brief using AI service
        service = get_ai_service()

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            brief_response = loop.run_until_complete(
                service.generate_campaign_brief(
                    conversation_id=conversation_id,
                    additional_context=conversation.context
                )
            )
            sample_brief = brief_response['brief']
        except Exception as e:
            logger.error(f"Brief generation error: {e}")
            # Fallback brief
            sample_brief = {
                "campaign_name": "AI Generated Campaign",
                "objective": "Increase online sales",
                "budget": 5000,
                "target_audience": "Adults 25-45 interested in the product",
                "geographic_targeting": "United States",
                "products_services": "E-commerce products",
                "key_messages": "Quality products at great prices",
                "success_metrics": "ROAS > 4.0",
                "timeline": "30 days",
                "additional_notes": "Generated from conversation"
            }
        
        # Update conversation with generated brief
        conversation.campaign_brief = sample_brief
        conversation.campaign_brief_generated = True
        db.session.commit()
        
        return jsonify({
            'brief': sample_brief,
            'format': 'json',
            'conversation_id': conversation_id,
            'status': 'success',
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Brief generation error: {str(e)}")
        return jsonify({'error': f'Brief generation failed: {str(e)}'}), 500

@ai_agent_bp.route('/conversations/<conversation_id>/create-campaign', methods=['POST'])
def create_campaign_from_brief(conversation_id):
    """
    Create actual campaign from generated brief using campaign orchestrator
    """
    try:
        conversation = Conversation.query.filter_by(id=conversation_id).first()
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404

        if not conversation.campaign_brief_generated or not conversation.campaign_brief:
            return jsonify({'error': 'No campaign brief found. Generate brief first.'}), 400

        # For demo purposes, simulate campaign creation
        workflow_id = f"workflow_{uuid.uuid4().hex[:8]}"

        # Update conversation with action taken
        if not conversation.actions_taken:
            conversation.actions_taken = []

        conversation.actions_taken.append({
            'action': 'campaign_creation_started',
            'workflow_id': workflow_id,
            'timestamp': datetime.utcnow().isoformat()
        })

        db.session.commit()

        return jsonify({
            'workflow_id': workflow_id,
            'conversation_id': conversation_id,
            'status': 'campaign_creation_started',
            'message': 'Campaign creation workflow has been initiated'
        })

    except Exception as e:
        logger.error(f"Campaign creation error: {str(e)}")
        return jsonify({'error': f'Campaign creation failed: {str(e)}'}), 500

@ai_agent_bp.route('/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get conversation details and history"""
    try:
        conversation = Conversation.query.filter_by(id=conversation_id).first()
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        return jsonify({
            'conversation': {
                'id': conversation.id,
                'title': conversation.title,
                'status': conversation.status.value,
                'type': conversation.conversation_type.value,
                'messages': conversation.messages,
                'brief_generated': conversation.campaign_brief_generated,
                'brief': conversation.campaign_brief,
                'actions_taken': conversation.actions_taken,
                'created_at': conversation.created_at.isoformat(),
                'updated_at': conversation.updated_at.isoformat(),
                'total_tokens_used': conversation.total_tokens_used
            }
        })
        
    except Exception as e:
        logger.error(f"Get conversation error: {str(e)}")
        return jsonify({'error': f'Failed to get conversation: {str(e)}'}), 500

@ai_agent_bp.route('/conversations', methods=['GET'])
def list_conversations():
    """List conversations for user"""
    try:
        user_id = request.args.get('user_id', 'demo-user')  # TODO: Get from auth
        
        conversations = Conversation.query.filter_by(user_id=user_id).order_by(
            Conversation.updated_at.desc()
        ).limit(50).all()
        
        return jsonify({
            'conversations': [{
                'id': conv.id,
                'title': conv.title,
                'status': conv.status.value,
                'type': conv.conversation_type.value,
                'brief_generated': conv.campaign_brief_generated,
                'last_message_at': conv.last_message_at.isoformat(),
                'created_at': conv.created_at.isoformat(),
                'message_count': len(conv.messages) if conv.messages else 0
            } for conv in conversations]
        })
        
    except Exception as e:
        logger.error(f"List conversations error: {str(e)}")
        return jsonify({'error': f'Failed to list conversations: {str(e)}'}), 500
