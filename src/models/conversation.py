"""
Conversation Model
Handles AI chat conversations and message history
"""

from datetime import datetime
from src.config.database import db
import uuid
import json


class Conversation(db.Model):
    """AI conversation model"""
    
    __tablename__ = 'conversations'
    
    # Primary identification
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # User relationship
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Conversation metadata
    title = db.Column(db.String(200), nullable=True)
    context = db.Column(db.Text, nullable=True)  # JSON string for conversation context
    
    # Status and timestamps
    status = db.Column(db.String(20), default='active', nullable=False)  # active, archived, deleted
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_message_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    messages = db.relationship('ConversationMessage', backref='conversation', lazy='dynamic', cascade='all, delete-orphan')
    user = db.relationship('User', backref='conversations')
    
    def __init__(self, user_id, title=None, context=None):
        self.user_id = user_id
        self.title = title or f"Conversation {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        self.context = json.dumps(context) if context else None
    
    def add_message(self, content, role='user', metadata=None):
        """Add a message to the conversation"""
        message = ConversationMessage(
            conversation_id=self.id,
            content=content,
            role=role,
            message_metadata=json.dumps(metadata) if metadata else None
        )
        db.session.add(message)
        self.last_message_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return message
    
    def get_messages(self, limit=None):
        """Get conversation messages"""
        query = self.messages.order_by(ConversationMessage.created_at.asc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def get_context(self):
        """Get conversation context as dict"""
        if self.context:
            try:
                return json.loads(self.context)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_context(self, context_dict):
        """Set conversation context"""
        self.context = json.dumps(context_dict)
        self.updated_at = datetime.utcnow()
    
    def to_dict(self, include_messages=False):
        """Convert conversation to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'context': self.get_context(),
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_message_at': self.last_message_at.isoformat() if self.last_message_at else None,
            'message_count': self.messages.count()
        }
        
        if include_messages:
            data['messages'] = [msg.to_dict() for msg in self.get_messages()]
        
        return data
    
    def __repr__(self):
        return f'<Conversation {self.id} - {self.title}>'


class ConversationMessage(db.Model):
    """Individual message in a conversation"""
    
    __tablename__ = 'conversation_messages'
    
    # Primary identification
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Conversation relationship
    conversation_id = db.Column(db.String(36), db.ForeignKey('conversations.id'), nullable=False)
    
    # Message content
    content = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # user, assistant, system
    message_metadata = db.Column(db.Text, nullable=True)  # JSON string for additional data
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __init__(self, conversation_id, content, role='user', message_metadata=None):
        self.conversation_id = conversation_id
        self.content = content
        self.role = role
        self.message_metadata = message_metadata
    
    def get_message_metadata(self):
        """Get message metadata as dict"""
        if self.message_metadata:
            try:
                return json.loads(self.message_metadata)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_message_metadata(self, metadata_dict):
        """Set message metadata"""
        self.message_metadata = json.dumps(metadata_dict)
    
    def to_dict(self):
        """Convert message to dictionary"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'content': self.content,
            'role': self.role,
            'metadata': self.get_message_metadata(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ConversationMessage {self.id} - {self.role}>'