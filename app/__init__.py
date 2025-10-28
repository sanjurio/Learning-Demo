import os
import logging
from datetime import datetime
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix
from .config import Config

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Starting Learning Management System")

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Initialize other extensions
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(Config)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Configure the database
    database_url = app.config['DATABASE_URL']
    if 'sqlite' in database_url.lower():
        logger.info("Using SQLite database for local development")
    else:
        logger.info(f"Using database: {database_url.split('@')[0].split('://')[0]}://...")
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    with app.app_context():
        # Import models to create tables
        from . import models
        db.create_all()
        logger.info("Database tables created successfully")
        
        # Download NLTK data for document analysis
        try:
            import nltk
            logger.info("Downloading NLTK data for document analysis...")
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True) 
            nltk.download('wordnet', quiet=True)
            logger.info("Downloaded NLTK resource: punkt")
            logger.info("Downloaded NLTK resource: stopwords")
            logger.info("Downloaded NLTK resource: wordnet")
        except Exception as e:
            logger.warning(f"Could not download NLTK data: {e}")

        # Import and register routes
        from . import routes
        routes.register_routes(app)
        logger.debug("Routes imported successfully")
        
        # Register context processors
        register_context_processors(app)

    return app

# Template context processors
def inject_now():
    return {'now': datetime.utcnow()}

def register_context_processors(app):
    """Register template context processors"""
    @app.context_processor
    def utility_processor():
        return {'now': datetime.utcnow()}

# Error handlers
def page_not_found(e):
    return render_template('errors/404.html'), 404

def internal_server_error(e):
    return render_template('errors/500.html'), 500