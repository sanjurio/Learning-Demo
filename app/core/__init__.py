"""
Core Blueprint.

This module handles the main functionality of the application,
including the homepage, user dashboard, and forum.
"""
from flask import Blueprint

core_bp = Blueprint('core', __name__)

from app.core import routes