"""
AI Agent Routes
"""

from flask import Blueprint, request, jsonify, stream_with_context, Response
from src.auth.authentication import token_required
from src.services.ai_agent_service import ai_agent_service
import logging
import json

logger = logging.getLogger(__name__)

# Create blueprint
ai_agent_bp = Blueprint('ai_agent', __name__)


@ai_agent_bp.route('/chat', methods=['POST'])
@token_required
def chat():
    """Chat with AI agent"""
    try:
        data = request.get_json()
        message = data.get('message')
        conversation_id = data.get('conversation_id')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        # Get AI response
        response = ai_agent_service.process_message(
            message=message,
            conversation_id=conversation_id
        )
        
        return jsonify({
            'success': True,
            'response': response
        }), 200
        
    except Exception as e:
        logger.error(f"Error in AI chat: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to process message'
        }), 500


@ai_agent_bp.route('/chat/stream', methods=['POST'])
@token_required
def chat_stream():
    """Stream chat response from AI agent"""
    try:
        data = request.get_json()
        message = data.get('message')
        conversation_id = data.get('conversation_id')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        def generate():
            try:
                for chunk in ai_agent_service.stream_message(
                    message=message,
                    conversation_id=conversation_id
                ):
                    yield f"data: {json.dumps(chunk)}\n\n"
            except Exception as e:
                logger.error(f"Error in streaming: {str(e)}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*'
            }
        )
        
    except Exception as e:
        logger.error(f"Error in AI chat stream: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to start stream'
        }), 500


@ai_agent_bp.route('/conversations', methods=['GET'])
@token_required
def list_conversations():
    """List user's conversations"""
    try:
        conversations = ai_agent_service.get_user_conversations()
        
        return jsonify({
            'success': True,
            'conversations': conversations
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing conversations: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to list conversations'
        }), 500


@ai_agent_bp.route('/conversations/<conversation_id>', methods=['GET'])
@token_required
def get_conversation(conversation_id):
    """Get specific conversation"""
    try:
        conversation = ai_agent_service.get_conversation(conversation_id)
        
        if not conversation:
            return jsonify({
                'success': False,
                'error': 'Conversation not found'
            }), 404
        
        return jsonify({
            'success': True,
            'conversation': conversation
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting conversation: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get conversation'
        }), 500


@ai_agent_bp.route('/conversations/<conversation_id>', methods=['DELETE'])
@token_required
def delete_conversation(conversation_id):
    """Delete conversation"""
    try:
        success = ai_agent_service.delete_conversation(conversation_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Conversation not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Conversation deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete conversation'
        }), 500


@ai_agent_bp.route('/generate-campaign', methods=['POST'])
@token_required
def generate_campaign():
    """Generate campaign from AI brief"""
    try:
        data = request.get_json()
        brief = data.get('brief')
        
        if not brief:
            return jsonify({
                'success': False,
                'error': 'Campaign brief is required'
            }), 400
        
        campaign = ai_agent_service.generate_campaign_from_brief(brief)
        
        return jsonify({
            'success': True,
            'campaign': campaign
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating campaign: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate campaign'
        }), 500