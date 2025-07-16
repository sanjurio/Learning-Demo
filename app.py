import os
import logging
from datetime import datetime
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Starting application")

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the database
database_url = os.environ.get("DATABASE_URL")
# Use SQLite locally if no DATABASE_URL environment variable is set
if not database_url:
    database_url = "sqlite:///app.db"
    logger.debug("Using local SQLite database")

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Print debug info
logger.debug(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Initialize the app with the extension
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Initialize CSRF Protection
csrf = CSRFProtect()
csrf.init_app(app)

with app.app_context():
    # Import models after app is created to avoid circular imports
    import models  # noqa: F401
    
    # Create all database tables
    db.create_all()
    logger.debug("Database tables created")
    
    # Download NLTK data required for document analysis
    try:
        logger.info("Downloading NLTK data for document analysis...")
        import nltk
        for resource in ['punkt', 'stopwords', 'wordnet']:
            try:
                nltk.download(resource, quiet=True)
                logger.info(f"Downloaded NLTK resource: {resource}")
            except Exception as e:
                logger.warning(f"Error downloading NLTK resource {resource}: {e}")
    except Exception as e:
        logger.error(f"Error setting up NLTK: {e}")
    
    # Import routes after database is set up
    import routes  # Import routes at the end to avoid circular imports
    logger.debug("Routes imported successfully")

# Context processors
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500
