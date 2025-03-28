"""
Authentication Blueprint.

This module handles user registration, login, and 2FA functionality.
"""
from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

from app.auth import routes