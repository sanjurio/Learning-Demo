"""
Script to create an admin user directly in the database
"""
import os
import sys
from datetime import datetime
from werkzeug.security import generate_password_hash
import psycopg2

def create_admin_user():
    """Create admin user directly in the database"""
    # Get database connection from environment variable
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("Error: DATABASE_URL environment variable not set")
        sys.exit(1)
    
    try:
        # Connect to the database
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        # Check if users table exists
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(64) NOT NULL UNIQUE,
            email VARCHAR(120) NOT NULL UNIQUE,
            password_hash VARCHAR(256) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            is_approved BOOLEAN DEFAULT FALSE,
            otp_secret VARCHAR(32),
            is_2fa_enabled BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Generate password hash
        password_hash = generate_password_hash("Admin123")
        created_at = datetime.utcnow()
        
        # Insert admin user
        cur.execute("""
        INSERT INTO users (username, email, password_hash, is_admin, is_approved, is_2fa_enabled, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (email) DO NOTHING
        """, ('admin', 'admin@example.com', password_hash, True, True, False, created_at))
        
        # Commit the transaction
        conn.commit()
        
        # Verify admin was created
        cur.execute("SELECT id, username, email, is_admin FROM users WHERE email = 'admin@example.com'")
        admin = cur.fetchone()
        
        if admin:
            print(f"Admin user created successfully: ID={admin[0]}, Username={admin[1]}, Email={admin[2]}, Is Admin={admin[3]}")
        else:
            print("Admin user already exists")
            
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
        conn.rollback()
        sys.exit(1)
    finally:
        # Close the database connection
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    create_admin_user()