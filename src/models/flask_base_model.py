"""
Flask-SQLAlchemy Base Model Class
Provides common functionality for Flask-based models
"""

from datetime import datetime
from typing import Dict, List, Any
from src.config.flask_database import db


class FlaskBaseModel(db.Model):
    """
    Base model class for Flask-SQLAlchemy
    """
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self, include_relationships: bool = False, 
                exclude_fields: List[str] = None) -> Dict[str, Any]:
        """
        Convert model instance to dictionary
        
        Args:
            include_relationships: Whether to include relationship data
            exclude_fields: List of fields to exclude
        
        Returns:
            Dictionary representation of the model
        """
        exclude_fields = exclude_fields or []
        result = {}
        
        # Get all columns
        for column in self.__table__.columns:
            if column.name not in exclude_fields:
                value = getattr(self, column.name)
                
                # Handle datetime serialization
                if isinstance(value, datetime):
                    result[column.name] = value.isoformat()
                else:
                    result[column.name] = value
        
        return result
    
    def update_from_dict(self, data: Dict[str, Any], 
                        allowed_fields: List[str] = None) -> None:
        """
        Update model instance from dictionary
        
        Args:
            data: Dictionary with update data
            allowed_fields: List of fields that can be updated
        """
        if allowed_fields is None:
            # Get all column names except id and timestamps
            allowed_fields = [
                column.name for column in self.__table__.columns
                if column.name not in ['id', 'created_at', 'updated_at']
            ]
        
        for key, value in data.items():
            if key in allowed_fields and hasattr(self, key):
                setattr(self, key, value)
    
    def save(self, commit: bool = True) -> bool:
        """
        Save model instance to database
        
        Args:
            commit: Whether to commit the transaction
        
        Returns:
            True if successful, False otherwise
        """
        try:
            db.session.add(self)
            
            if commit:
                db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def delete(self, commit: bool = True) -> bool:
        """
        Delete model instance from database
        
        Args:
            commit: Whether to commit the transaction
        
        Returns:
            True if successful, False otherwise
        """
        try:
            db.session.delete(self)
            
            if commit:
                db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @classmethod
    def create(cls, **kwargs):
        """
        Create and save a new instance
        
        Args:
            **kwargs: Model field values
        
        Returns:
            Created model instance
        """
        instance = cls(**kwargs)
        instance.save()
        return instance
    
    def __repr__(self):
        """String representation of the model"""
        return f"<{self.__class__.__name__}(id={self.id})>"