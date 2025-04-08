# Main entry point of the application
# Used by Gunicorn to find the Flask application

import os
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Create loggers for different components
app_logger = logging.getLogger('app')
document_logger = logging.getLogger('document_analysis')
auth_logger = logging.getLogger('auth')

# Import the app from app.py
from app import app

# Add logging configuration to app
app.logger.setLevel(logging.DEBUG)
app.logger.info("Application logger configured")

# Log important environment variables (without revealing values)
app.logger.info(f"OpenAI API key configured: {bool(os.environ.get('OPENAI_API_KEY'))}")
app.logger.info(f"Database URL configured: {bool(os.environ.get('DATABASE_URL'))}")

# Download NLTK data required for document analysis
try:
    app.logger.info("Downloading NLTK data for document analysis...")
    import nltk
    for resource in ['punkt', 'stopwords', 'wordnet']:
        try:
            nltk.download(resource, quiet=True)
            app.logger.info(f"Downloaded NLTK resource: {resource}")
        except Exception as e:
            app.logger.warning(f"Error downloading NLTK resource {resource}: {e}")
except Exception as e:
    app.logger.error(f"Error setting up NLTK: {e}")

# Keep a simple module-level variable 'app' for Gunicorn
# No need to redefine it - it's already imported from app.py

if __name__ == "__main__":
    # This only runs when executing the script directly, not via Gunicorn
    # Useful for development
    app.run(host="0.0.0.0", port=5000, debug=True)
