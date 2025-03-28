"""
API Blueprint.

This module handles API endpoints for document analysis and other features.
"""
from flask import Blueprint

api_bp = Blueprint('api', __name__)

from app.api import routes