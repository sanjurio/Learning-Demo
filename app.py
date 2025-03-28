import os
import logging
from datetime import datetime
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager

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
app.secret_key = os.environ.get("SESSION_SECRET", "dev-key-replace-in-production")

# Configure the database
database_url = os.environ.get("DATABASE_URL")
# Use SQLite locally if no DATABASE_URL environment variable is set or if there are connection issues
if not database_url or "ep-summer-wildflower" in database_url:  # Check for the problematic Neon DB
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

with app.app_context():
    # Import models after app is created to avoid circular imports
    from models import User, Course, Lesson, Interest, UserInterest, CourseInterest, UserCourse
    
    # Create all database tables
    db.create_all()
    logger.debug("Database tables created")
    
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
