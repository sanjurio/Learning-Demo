"""
Main application entry point.

This module creates the Flask application instance and runs the development server.
"""
from app import create_app

# Create the application instance
app = create_app()

# Run the development server when executing this file directly
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)