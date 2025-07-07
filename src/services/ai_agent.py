from flask import Blueprint, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

ai_agent_bp = Blueprint('ai_agent', __name__)

# Initialize OpenAI client (will be configured with API key from environment)
client = None

def get_openai_client():
    global client
    if client is None:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        client = OpenAI(api_key=api_key)
    return client

@ai_agent_bp.route('/chat', methods=['POST'])
def chat_with_agent():
    """
    Main chat endpoint for conversing with the AI agent about campaign objectives
    """
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message']
        conversation_history = data.get('conversation_history', [])
        
        # System prompt for the Google Ads automation agent
        system_prompt = """You are an expert Google Ads automation agent for the Lane MCP (Marketing Control Panel) platform. 
        Your role is to help users create and manage Google Ads campaigns through natural language conversation.
        
        Key responsibilities:
        1. Understand campaign objectives expressed in conversational language
        2. Extract key parameters: budget, target audience, geographic location, products/services, goals
        3. Ask clarifying questions when information is missing or ambiguous
        4. Provide recommendations based on Google Ads best practices
        5. Generate structured campaign briefs for approval
        
        Always be helpful, professional, and focused on achieving the user's advertising goals.
        When you have enough information, offer to generate a campaign brief for review."""
        
        # Build conversation messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in conversation_history:
            messages.append(msg)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Get OpenAI client and make request
        openai_client = get_openai_client()
        
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        
        assistant_message = response.choices[0].message.content
        
        return jsonify({
            'response': assistant_message,
            'conversation_id': data.get('conversation_id'),
            'status': 'success'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@ai_agent_bp.route('/generate-campaign-brief', methods=['POST'])
def generate_campaign_brief():
    """
    Generate a structured campaign brief from conversation context
    """
    try:
        data = request.get_json()
        if not data or 'conversation_history' not in data:
            return jsonify({'error': 'Conversation history is required'}), 400
        
        conversation_history = data['conversation_history']
        
        # System prompt for campaign brief generation
        system_prompt = """Based on the conversation history, generate a structured Google Ads campaign brief in JSON format.
        
        Extract and organize the following information:
        - campaign_name: A descriptive name for the campaign
        - objective: Primary campaign goal (leads, sales, awareness, etc.)
        - budget: Monthly budget amount and currency
        - target_audience: Description of target customers
        - geographic_targeting: Locations to target
        - products_services: What is being advertised
        - key_messages: Main selling points or value propositions
        - success_metrics: How success will be measured
        - timeline: Campaign duration or start date
        - additional_notes: Any special requirements or considerations
        
        Return only valid JSON format."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in conversation_history:
            messages.append(msg)
        
        # Add request for brief generation
        messages.append({
            "role": "user", 
            "content": "Please generate a structured campaign brief based on our conversation."
        })
        
        openai_client = get_openai_client()
        
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=1500,
            temperature=0.3
        )
        
        brief_content = response.choices[0].message.content
        
        # Try to parse as JSON, fallback to text if parsing fails
        try:
            import json
            brief_json = json.loads(brief_content)
            return jsonify({
                'brief': brief_json,
                'format': 'json',
                'status': 'success'
            })
        except json.JSONDecodeError:
            return jsonify({
                'brief': brief_content,
                'format': 'text',
                'status': 'success'
            })
        
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@ai_agent_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for the AI agent service
    """
    try:
        # Check if OpenAI API key is configured
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return jsonify({
                'status': 'error',
                'message': 'OpenAI API key not configured'
            }), 500
        
        return jsonify({
            'status': 'healthy',
            'service': 'AI Agent',
            'openai_configured': True
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

