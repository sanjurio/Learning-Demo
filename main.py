# Main entry point of the application
# Used by Gunicorn to find the Flask application

# Import the app from app.py
from app import app

# Keep a simple module-level variable 'app' for Gunicorn
# No need to redefine it - it's already imported from app.py

if __name__ == "__main__":
    # This only runs when executing the script directly, not via Gunicorn
    # Useful for development
    app.run(host="0.0.0.0", port=5000, debug=True)
