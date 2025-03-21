from app import app
from models import User

if __name__ == "__main__":
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print(f"Admin username: {admin.username}")
            print("Password: admin123")
        else:
            print("Admin user not found")