
from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Import routes at the bottom to avoid circular imports
from app.auth import routes  # This should be at the bottom
