"""
Admin Blueprint.

This module handles administrator functionality including user management,
content management, and API key configuration.
"""
from flask import Blueprint

admin_bp = Blueprint('admin', __name__)

from app.admin import routes