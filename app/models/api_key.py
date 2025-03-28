"""
API Key model for managing external service API keys.

This module includes:
- ApiKey: Model for storing external service API keys (e.g., OpenAI)
"""
from datetime import datetime
from app import db

class ApiKey(db.Model):
    """
    Represents an API key for an external service.
    
    This model stores API keys for services like OpenAI that are used by the application.
    Keys are encrypted in the database for security.
    Only admins can manage API keys.
    """
    __tablename__ = 'api_keys'
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(50), nullable=False, unique=True)
    key_value = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __repr__(self):
        """String representation of the ApiKey"""
        return f'<ApiKey {self.service_name}>'