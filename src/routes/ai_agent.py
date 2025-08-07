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
        conversation_history = data.get('conversation_history', [])
        context_type = data.get('context_type', 'general')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        def generate():
            try:
                # Create async event loop for streaming
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                async def stream_wrapper():
                    async for chunk in ai_agent_service.stream_chat(
                        message=message,
                        conversation_history=conversation_history,
                        context_type=context_type
                    ):
                        yield chunk
                
                # Run the async generator
                gen = stream_wrapper()
                while True:
                    try:
                        chunk = loop.run_until_complete(gen.__anext__())
                        yield f"data: {json.dumps(chunk)}\n\n"
                    except StopAsyncIteration:
                        break
                    
            except Exception as e:
                logger.error(f"Error in streaming: {str(e)}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'X-Accel-Buffering': 'no'  # Disable Nginx buffering
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
    """Generate campaign from conversation or brief"""
    try:
        data = request.get_json()
        conversation_id = data.get('conversation_id')
        messages = data.get('messages', [])
        brief = data.get('brief')
        
        if not conversation_id and not messages and not brief:
            return jsonify({
                'success': False,
                'error': 'Either conversation_id, messages, or brief is required'
            }), 400
        
        # Import campaign generator
        from src.services.campaign_generator import get_campaign_generator
        generator = get_campaign_generator()
        
        # Generate campaign using AI workflow
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        if messages or conversation_id:
            # Generate from conversation
            result = loop.run_until_complete(
                generator.generate_from_conversation(
                    conversation_id=conversation_id or 'new',
                    messages=messages
                )
            )
        else:
            # Generate from brief directly
            result = loop.run_until_complete(
                generator._create_campaign_structure({'strategy': brief}, brief)
            )
        
        return jsonify(result), 200 if result.get('success') else 400
        
    except Exception as e:
        logger.error(f"Error generating campaign: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to generate campaign: {str(e)}'
        }), 500


@ai_agent_bp.route('/keyword-research', methods=['POST'])
@token_required
def keyword_research():
    """AI-powered keyword research"""
    try:
        data = request.get_json()
        business_info = data.get('business_info')
        target_market = data.get('target_market')
        competitors = data.get('competitors', [])
        
        if not business_info:
            return jsonify({
                'success': False,
                'error': 'Business information is required'
            }), 400
        
        # Import keyword research service
        from src.services.keyword_research_ai import ai_keyword_research
        
        # Run keyword research
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            ai_keyword_research.research_keywords(
                business_info=business_info,
                target_market=target_market,
                competitors=competitors
            )
        )
        
        return jsonify(result), 200 if result.get('success') else 400
        
    except Exception as e:
        logger.error(f"Error in keyword research: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Keyword research failed: {str(e)}'
        }), 500


@ai_agent_bp.route('/optimize-keywords', methods=['POST'])
@token_required
def optimize_keywords():
    """Optimize existing keywords using AI"""
    try:
        data = request.get_json()
        performance_data = data.get('performance_data', [])
        business_goals = data.get('business_goals', {})
        
        if not performance_data:
            return jsonify({
                'success': False,
                'error': 'Performance data is required'
            }), 400
        
        # Import keyword research service
        from src.services.keyword_research_ai import ai_keyword_research
        
        # Run optimization
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            ai_keyword_research.optimize_existing_keywords(
                performance_data=performance_data,
                business_goals=business_goals
            )
        )
        
        return jsonify(result), 200 if result.get('success') else 400
        
    except Exception as e:
        logger.error(f"Error optimizing keywords: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Keyword optimization failed: {str(e)}'
        }), 500