"""
Conversation Model for AI Agent Interactions
Comprehensive conversation tracking and management
"""

from datetime import datetime
from enum import Enum
import uuid
import json

from src.database import db

class ConversationStatus(Enum):
    """Conversation status"""
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    ABANDONED = "abandoned"

class ConversationType(Enum):
    """Type of conversation"""
    CAMPAIGN_PLANNING = "campaign_planning"
    OPTIMIZATION_ANALYSIS = "optimization_analysis"
    BUDGET_MANAGEMENT = "budget_management"
    PERFORMANCE_REVIEW = "performance_review"
    GENERAL_SUPPORT = "general_support"

class MessageRole(Enum):
    """Message roles in conversation"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"

class Conversation(db.Model):
    """Conversation model for AI agent interactions"""
    
    __tablename__ = 'conversations'
    
    # Primary identification
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=True)
    
    # Conversation metadata
    conversation_type = db.Column(db.Enum(ConversationType), nullable=False, default=ConversationType.CAMPAIGN_PLANNING)
    status = db.Column(db.Enum(ConversationStatus), nullable=False, default=ConversationStatus.ACTIVE)
    
    # User and context
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    google_customer_id = db.Column(db.String(50), nullable=True)  # Context for Google Ads operations
    
    # Conversation content
    messages = db.Column(db.JSON, nullable=False, default=list)  # List of conversation messages
    context = db.Column(db.JSON, nullable=True)  # Additional context data
    summary = db.Column(db.Text, nullable=True)  # AI-generated conversation summary
    
    # AI configuration
    ai_model_used = db.Column(db.String(100), nullable=True)
    ai_agent_type = db.Column(db.String(50), nullable=True)
    total_tokens_used = db.Column(db.Integer, default=0, nullable=False)
    
    # Outcomes and results
    campaign_brief_generated = db.Column(db.Boolean, default=False, nullable=False)
    campaign_brief = db.Column(db.JSON, nullable=True)  # Generated campaign brief
    actions_taken = db.Column(db.JSON, nullable=True)  # List of actions performed
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_message_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    campaigns = db.relationship('Campaign', backref='conversation', lazy='dynamic')
    
    def __init__(self, user_id, conversation_type=ConversationType.CAMPAIGN_PLANNING, **kwargs):
        self.user_id = user_id
        self.conversation_type = conversation_type
        self.messages = []
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def add_message(self, role: MessageRole, content: str, metadata: dict = None) -> None:
        """Add message to conversation"""
        message = {
            'id': str(uuid.uuid4()),
            'role': role.value,
            'content': content,
            'timestamp': datetime.utcnow().isoformat(),
            'metadata': metadata or {}
        }
        
        if not self.messages:
            self.messages = []
        
        self.messages.append(message)
        self.last_message_at = datetime.utcnow()
        
        # Auto-generate title from first user message
        if not self.title and role == MessageRole.USER and len(self.messages) <= 2:
            self.title = content[:100] + "..." if len(content) > 100 else content
    
    def get_messages_for_ai(self, max_messages: int = 20) -> list:
        """Get messages formatted for AI API"""
        if not self.messages:
            return []
        
        # Get recent messages
        recent_messages = self.messages[-max_messages:] if len(self.messages) > max_messages else self.messages
        
        # Format for AI API
        formatted_messages = []
        for msg in recent_messages:
            if msg['role'] in ['user', 'assistant', 'system']:
                formatted_messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
        
        return formatted_messages
    
    def update_ai_usage(self, model: str, agent_type: str, tokens_used: int) -> None:
        """Update AI usage tracking"""
        self.ai_model_used = model
        self.ai_agent_type = agent_type
        self.total_tokens_used += tokens_used
    
    def set_campaign_brief(self, brief: dict) -> None:
        """Set generated campaign brief"""
        self.campaign_brief = brief
        self.campaign_brief_generated = True
    
    def add_action(self, action_type: str, action_data: dict) -> None:
        """Add action taken during conversation"""
        if not self.actions_taken:
            self.actions_taken = []
        
        action = {
            'id': str(uuid.uuid4()),
            'type': action_type,
            'data': action_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.actions_taken.append(action)
    
    def complete(self, summary: str = None) -> None:
        """Mark conversation as completed"""
        self.status = ConversationStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        if summary:
            self.summary = summary
    
    def archive(self) -> None:
        """Archive conversation"""
        self.status = ConversationStatus.ARCHIVED
    
    def abandon(self) -> None:
        """Mark conversation as abandoned"""
        self.status = ConversationStatus.ABANDONED
    
    @property
    def message_count(self) -> int:
        """Get total message count"""
        return len(self.messages) if self.messages else 0
    
    @property
    def user_message_count(self) -> int:
        """Get user message count"""
        if not self.messages:
            return 0
        return len([msg for msg in self.messages if msg['role'] == 'user'])
    
    @property
    def duration_minutes(self) -> float:
        """Get conversation duration in minutes"""
        if self.completed_at:
            end_time = self.completed_at
        else:
            end_time = self.last_message_at or datetime.utcnow()
        
        duration = end_time - self.created_at
        return duration.total_seconds() / 60
    
    @property
    def is_active(self) -> bool:
        """Check if conversation is active"""
        return self.status == ConversationStatus.ACTIVE
    
    def to_dict(self, include_messages: bool = False, include_brief: bool = False) -> dict:
        """Convert conversation to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'conversation_type': self.conversation_type.value,
            'status': self.status.value,
            'user_id': self.user_id,
            'google_customer_id': self.google_customer_id,
            'message_count': self.message_count,
            'user_message_count': self.user_message_count,
            'duration_minutes': self.duration_minutes,
            'ai_model_used': self.ai_model_used,
            'ai_agent_type': self.ai_agent_type,
            'total_tokens_used': self.total_tokens_used,
            'campaign_brief_generated': self.campaign_brief_generated,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_message_at': self.last_message_at.isoformat() if self.last_message_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'summary': self.summary
        }
        
        if include_messages:
            data['messages'] = self.messages
            data['context'] = self.context
            data['actions_taken'] = self.actions_taken
        
        if include_brief and self.campaign_brief:
            data['campaign_brief'] = self.campaign_brief
        
        return data
    
    def __repr__(self):
        return f'<Conversation {self.id} ({self.conversation_type.value})>'

