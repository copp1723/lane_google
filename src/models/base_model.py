"""
Base Model Class
Provides common functionality and patterns for all database models
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates
from sqlalchemy.dialects.postgresql import UUID

from src.config.database import db

Base = declarative_base()


class TimestampMixin:
    """
    Mixin to add timestamp fields to models
    """
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class UUIDMixin:
    """
    Mixin to add UUID primary key
    """
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class SoftDeleteMixin:
    """
    Mixin to add soft delete functionality
    """
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    def soft_delete(self):
        """Mark record as deleted"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        """Restore soft deleted record"""
        self.is_deleted = False
        self.deleted_at = None


class AuditMixin:
    """
    Mixin to add audit fields
    """
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    version = Column(Integer, default=1, nullable=False)
    
    def increment_version(self):
        """Increment version number"""
        self.version += 1


class BaseModel(db.Model, TimestampMixin):
    """
    Base model class with common functionality
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
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
                # Handle UUID serialization
                elif hasattr(value, 'hex'):
                    result[column.name] = str(value)
                else:
                    result[column.name] = value
        
        # Include relationships if requested
        if include_relationships:
            for relationship in self.__mapper__.relationships:
                if relationship.key not in exclude_fields:
                    related_obj = getattr(self, relationship.key)
                    
                    if related_obj is not None:
                        if hasattr(related_obj, '__iter__') and not isinstance(related_obj, str):
                            # Handle collections
                            result[relationship.key] = [
                                item.to_dict() if hasattr(item, 'to_dict') else str(item)
                                for item in related_obj
                            ]
                        else:
                            # Handle single objects
                            result[relationship.key] = (
                                related_obj.to_dict() if hasattr(related_obj, 'to_dict') 
                                else str(related_obj)
                            )
        
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
    
    def validate(self) -> List[str]:
        """
        Validate model instance
        
        Returns:
            List of validation errors
        """
        errors = []
        
        # Override in subclasses for custom validation
        return errors
    
    def save(self, commit: bool = True) -> bool:
        """
        Save model instance to database
        
        Args:
            commit: Whether to commit the transaction
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate before saving
            validation_errors = self.validate()
            if validation_errors:
                raise ValueError(f"Validation failed: {', '.join(validation_errors)}")
            
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
    
    @classmethod
    def get_by_id(cls, id: int):
        """
        Get instance by ID
        
        Args:
            id: Instance ID
        
        Returns:
            Model instance or None
        """
        return cls.query.get(id)
    
    @classmethod
    def get_or_404(cls, id: int):
        """
        Get instance by ID or raise 404
        
        Args:
            id: Instance ID
        
        Returns:
            Model instance
        
        Raises:
            404 error if not found
        """
        return cls.query.get_or_404(id)
    
    @classmethod
    def find_by(cls, **kwargs):
        """
        Find instances by criteria
        
        Args:
            **kwargs: Search criteria
        
        Returns:
            Query object
        """
        return cls.query.filter_by(**kwargs)
    
    @classmethod
    def paginate(cls, page: int = 1, per_page: int = 20, **filters):
        """
        Paginate query results
        
        Args:
            page: Page number
            per_page: Items per page
            **filters: Additional filters
        
        Returns:
            Pagination object
        """
        query = cls.query
        
        # Apply filters
        for key, value in filters.items():
            if hasattr(cls, key):
                query = query.filter(getattr(cls, key) == value)
        
        return query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    
    def __repr__(self):
        """String representation of the model"""
        return f"<{self.__class__.__name__}(id={self.id})>"


class BaseModelWithUUID(db.Model, TimestampMixin, UUIDMixin):
    """
    Base model class with UUID primary key
    """
    __abstract__ = True
    
    def to_dict(self, include_relationships: bool = False, 
                exclude_fields: List[str] = None) -> Dict[str, Any]:
        """
        Convert model instance to dictionary
        """
        exclude_fields = exclude_fields or []
        result = {}
        
        for column in self.__table__.columns:
            if column.name not in exclude_fields:
                value = getattr(self, column.name)
                
                if isinstance(value, datetime):
                    result[column.name] = value.isoformat()
                elif hasattr(value, 'hex'):  # UUID
                    result[column.name] = str(value)
                else:
                    result[column.name] = value
        
        return result
    
    @classmethod
    def get_by_id(cls, id: str):
        """
        Get instance by UUID
        
        Args:
            id: Instance UUID
        
        Returns:
            Model instance or None
        """
        try:
            uuid_obj = uuid.UUID(id) if isinstance(id, str) else id
            return cls.query.get(uuid_obj)
        except (ValueError, TypeError):
            return None


class AuditableModel(BaseModel, AuditMixin, SoftDeleteMixin):
    """
    Base model with full audit trail and soft delete
    """
    __abstract__ = True
    
    def save(self, commit: bool = True, user_id: int = None) -> bool:
        """
        Save with audit information
        
        Args:
            commit: Whether to commit the transaction
            user_id: ID of user making the change
        
        Returns:
            True if successful, False otherwise
        """
        # Set audit fields
        if user_id:
            if not self.id:  # New record
                self.created_by = user_id
            else:  # Existing record
                self.updated_by = user_id
                self.increment_version()
        
        return super().save(commit)
    
    @classmethod
    def active_records(cls):
        """
        Get query for non-deleted records
        
        Returns:
            Query object for active records
        """
        return cls.query.filter(cls.is_deleted == False)


class ConfigurableModel(BaseModel):
    """
    Base model for configuration entities
    """
    __abstract__ = True
    
    key = Column(String(255), unique=True, nullable=False)
    value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    @validates('key')
    def validate_key(self, key, value):
        """Validate configuration key format"""
        if not value or not isinstance(value, str):
            raise ValueError("Key must be a non-empty string")
        
        # Key should be alphanumeric with dots and underscores
        import re
        if not re.match(r'^[a-zA-Z0-9._]+$', value):
            raise ValueError("Key can only contain letters, numbers, dots, and underscores")
        
        return value
    
    @classmethod
    def get_config(cls, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key
        
        Args:
            key: Configuration key
            default: Default value if not found
        
        Returns:
            Configuration value
        """
        config = cls.query.filter_by(key=key, is_active=True).first()
        if config:
            # Try to parse JSON values
            try:
                import json
                return json.loads(config.value)
            except (json.JSONDecodeError, TypeError):
                return config.value
        
        return default
    
    @classmethod
    def set_config(cls, key: str, value: Any, description: str = None) -> 'ConfigurableModel':
        """
        Set configuration value
        
        Args:
            key: Configuration key
            value: Configuration value
            description: Optional description
        
        Returns:
            Configuration instance
        """
        import json
        
        # Convert value to JSON string if it's not a string
        if not isinstance(value, str):
            value = json.dumps(value)
        
        config = cls.query.filter_by(key=key).first()
        if config:
            config.value = value
            if description:
                config.description = description
            config.is_active = True
        else:
            config = cls(key=key, value=value, description=description)
        
        config.save()
        return config


# Utility functions for model operations
def bulk_create(model_class, data_list: List[Dict], batch_size: int = 1000) -> List:
    """
    Bulk create model instances
    
    Args:
        model_class: Model class to create
        data_list: List of dictionaries with model data
        batch_size: Number of records to process at once
    
    Returns:
        List of created instances
    """
    created_instances = []
    
    for i in range(0, len(data_list), batch_size):
        batch = data_list[i:i + batch_size]
        instances = [model_class(**data) for data in batch]
        
        db.session.bulk_save_objects(instances, return_defaults=True)
        created_instances.extend(instances)
    
    db.session.commit()
    return created_instances


def bulk_update(model_class, updates: List[Dict], id_field: str = 'id') -> int:
    """
    Bulk update model instances
    
    Args:
        model_class: Model class to update
        updates: List of dictionaries with update data (must include ID field)
        id_field: Name of the ID field
    
    Returns:
        Number of updated records
    """
    if not updates:
        return 0
    
    # Group updates by ID
    update_mappings = []
    for update_data in updates:
        if id_field in update_data:
            update_mappings.append(update_data)
    
    if update_mappings:
        db.session.bulk_update_mappings(model_class, update_mappings)
        db.session.commit()
        return len(update_mappings)
    
    return 0


def get_model_schema(model_class) -> Dict:
    """
    Get schema information for a model
    
    Args:
        model_class: Model class
    
    Returns:
        Dictionary with schema information
    """
    schema = {
        'table_name': model_class.__tablename__,
        'columns': {},
        'relationships': {}
    }
    
    # Get column information
    for column in model_class.__table__.columns:
        schema['columns'][column.name] = {
            'type': str(column.type),
            'nullable': column.nullable,
            'primary_key': column.primary_key,
            'unique': column.unique,
            'default': str(column.default) if column.default else None
        }
    
    # Get relationship information
    for relationship in model_class.__mapper__.relationships:
        schema['relationships'][relationship.key] = {
            'target': relationship.mapper.class_.__name__,
            'direction': str(relationship.direction),
            'uselist': relationship.uselist
        }
    
    return schema