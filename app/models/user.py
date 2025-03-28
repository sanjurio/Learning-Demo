"""
User models: Contains all user-related database models.

This module includes:
- User: The main user model with authentication functions
- User loader for Flask-Login
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    """
    User loader function for Flask-Login.
    This function is required by Flask-Login to load a user from the database.
    
    Args:
        user_id: The ID of the user to load
        
    Returns:
        The User object or None if not found
    """
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    """
    User model representing registered users in the system.
    
    This model handles authentication, 2FA, and admin status.
    It has relationships with interests, courses, and forum content.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    otp_secret = db.Column(db.String(32))
    is_2fa_enabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships defined dynamically based on other models
    # These are now defined in their respective model files and reference back to User
    
    def set_password(self, password):
        """
        Set the password hash for a user based on the provided password.
        Uses Werkzeug's password hashing functionality.
        
        Args:
            password: Plain text password to hash
        """
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """
        Verify a provided password against the stored password hash.
        
        Args:
            password: Plain text password to check
            
        Returns:
            True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        """
        String representation of the User object.
        
        Returns:
            A string with the username
        """
        return f'<User {self.username}>'