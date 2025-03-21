from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_new_admin():
    with app.app_context():
        # Check if admin with this email exists
        admin = User.query.filter_by(email='admin@example.com').first()
        
        if admin:
            # Update password
            admin.password_hash = generate_password_hash('admin123')
            print("Admin password updated to 'admin123'")
        else:
            # Create new admin
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True,
                is_approved=True,
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            print("New admin user created with password 'admin123'")
        
        db.session.commit()
        print("Done!")

if __name__ == "__main__":
    create_new_admin()