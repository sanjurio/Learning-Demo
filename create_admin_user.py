"""
Script to create an admin user for the LMS
"""
import os
import sys
from datetime import datetime
from werkzeug.security import generate_password_hash

# Import the app and models
from app import create_app, db
from app.models import User

def create_admin_user():
    """Create admin user in the database"""
    app = create_app()
    
    with app.app_context():
        # Check if admin exists
        admin = User.query.filter_by(email='admin@example.com').first()
        
        if admin:
            print(f"Admin user already exists: ID={admin.id}, Username={admin.username}, Email={admin.email}")
            print("You can log in with:")
            print("  Email: admin@example.com")
            print("  Password: Admin123")
        else:
            # Generate password hash
            password_hash = generate_password_hash("Admin123")
            
            # Create admin user
            admin = User(
                username='admin',
                email='admin@example.com', 
                password_hash=password_hash,
                is_admin=True,
                is_approved=True,
                is_2fa_enabled=False,
                created_at=datetime.utcnow()
            )
            
            # Add to database
            db.session.add(admin)
            db.session.commit()
            
            print(f"Admin user created successfully!")
            print(f"  ID: {admin.id}")
            print(f"  Username: {admin.username}")
            print(f"  Email: {admin.email}")
            print(f"  Password: Admin123")
            print("\nYou can now log in with these credentials.")

if __name__ == "__main__":
    create_admin_user()