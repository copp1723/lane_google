import os
import sys
import secrets
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.config.database import db
# from src.routes.user import user_bp  # Route not found
# from src.routes.ai_agent import ai_agent_bp  # Route not found
# from src.routes.google_ads import google_ads_bp  # Route not found
# from src.routes.campaigns import campaigns_bp  # Route not found
from src.api.dashboard_apis import dashboard_bp

# Import new services and APIs
from src.api.budget_pacing_api import budget_pacing_bp
from src.api.health_api import health_bp
from src.api.orchestrator_api import orchestrator_bp
from src.api.ai_agent_api import ai_agent_bp
from src.api.keyword_research_api import keyword_research_bp
from src.api.keyword_analytics_api import keyword_analytics_bp
from src.api.campaign_analytics_api import campaign_analytics_bp
from src.services.budget_pacing import budget_pacing_service
from src.services.campaign_orchestrator import CampaignOrchestrator, campaign_orchestrator
from src.services.real_google_ads import RealGoogleAdsService
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_urlsafe(32))

# Enable CORS for all routes
CORS(app, origins="*")

# Register blueprints
# app.register_blueprint(user_bp, url_prefix='/api')  # Route not found
app.register_blueprint(ai_agent_bp, url_prefix='/api/ai')
# app.register_blueprint(google_ads_bp, url_prefix='/api/google-ads')  # Route not found
# app.register_blueprint(campaigns_bp, url_prefix='/api/campaigns')  # Route not found
app.register_blueprint(dashboard_bp)

# Register new service blueprints
app.register_blueprint(budget_pacing_bp, url_prefix='/api/budget')
app.register_blueprint(health_bp, url_prefix='/api')
app.register_blueprint(orchestrator_bp, url_prefix='/api/orchestrator')
app.register_blueprint(keyword_research_bp, url_prefix='/api/keywords')
app.register_blueprint(keyword_analytics_bp, url_prefix='/api/keyword-analytics')
app.register_blueprint(campaign_analytics_bp, url_prefix='/api/campaign-analytics')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Import all models before creating tables
from src.models.user import User
from src.models.account import Account
from src.models.campaign import Campaign
from src.models.budget_alert import BudgetAlertModel
from src.models.analytics_snapshot import AnalyticsSnapshot
from src.models.approval_request import ApprovalRequestModel
from src.services.conversation import Conversation

with app.app_context():
    db.create_all()
    
    # Initialize services
    google_ads_service = RealGoogleAdsService()
    
    # Initialize campaign orchestrator
    from src.services.campaign_orchestrator import campaign_orchestrator
    campaign_orchestrator = CampaignOrchestrator(google_ads_service)
    
    # Start budget monitoring service
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(budget_pacing_service.start_monitoring())

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

