"""
Application initialization package.
This module initializes the Flask application with all required extensions and configurations.
"""
import os
import logging
from datetime import datetime
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("app")

# Configure base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(test_config=None):
    """
    Application factory function that creates and configures the Flask app.
    Args:
        test_config: Optional configuration to use for testing
    Returns:
        The configured Flask application instance
    """
    # Create Flask app
    app = Flask(__name__, static_folder="../static", template_folder="../templates")
    
    # Set up configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SESSION_SECRET", "dev-secret-key"),
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///../instance/app.db"),
        SQLALCHEMY_ENGINE_OPTIONS={
            "pool_recycle": 300,
            "pool_pre_ping": True,
        }
    )
    
    # Override config if testing
    if test_config:
        app.config.update(test_config)
    
    # Log configuration status
    logger.debug("Starting application")
    if "sqlite" in app.config["SQLALCHEMY_DATABASE_URI"]:
        logger.debug("Using local SQLite database")
    else:
        logger.debug("Using PostgreSQL database")
    logger.debug(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Configure login
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"
    
    # Create database tables
    with app.app_context():
        # Import models here to ensure they're registered with SQLAlchemy
        from app.models.user import User
        from app.models.content import (
            Interest, Course, Lesson, 
            UserInterest, CourseInterest, UserCourse, UserLessonProgress
        )
        from app.models.forum import ForumTopic, ForumReply
        from app.models.api_key import ApiKey
        
        db.create_all()
        logger.debug("Database tables created")
    
    # Register blueprints
    from app.auth import auth_bp
    from app.admin import admin_bp
    from app.core import core_bp
    from app.api import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(core_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500
    
    # Register context processor for templates
    @app.context_processor
    def inject_now():
        return {"now": datetime.utcnow()}
    
    # Download required NLTK data
    try:
        import nltk
        nltk.download("punkt")
        logger.info("Downloaded NLTK resource: punkt")
        nltk.download("stopwords")
        logger.info("Downloaded NLTK resource: stopwords")
        nltk.download("wordnet")
        logger.info("Downloaded NLTK resource: wordnet")
    except Exception as e:
        logger.warning(f"Failed to download NLTK data: {e}")
    
    # Log configuration status
    logger.info("Application logger configured")
    logger.info(f"OpenAI API key configured: {bool(os.environ.get('OPENAI_API_KEY'))}")
    logger.info(f"Database URL configured: {bool(os.environ.get('DATABASE_URL'))}")
    
    return app