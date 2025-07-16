#!/usr/bin/env python3
"""
Create demo users for testing domain-specific access control
"""
from app import create_app
from app.models import db, User, Interest, UserInterest

def create_demo_users():
    """Create demo users for testing"""
    app = create_app()
    
    with app.app_context():
        # Delete existing test users
        User.query.filter(User.email.in_(['developer@thbs.com', 'engineer@bt.com', 'dev@external.com'])).delete()
        db.session.commit()
        
        # Create THBS domain user
        thbs_user = User(
            username='thbs_user',
            email='user@thbs.com',
            is_approved=True,
            is_admin=False,
            is_2fa_enabled=False  # Will be enabled after registration
        )
        thbs_user.set_password('password123')
        thbs_user.set_access_based_on_domain()
        db.session.add(thbs_user)
        
        # Create BT domain user
        bt_user = User(
            username='bt_user',
            email='user@bt.com',
            is_approved=True,
            is_admin=False,
            is_2fa_enabled=False  # Will be enabled after registration
        )
        bt_user.set_password('password123')
        bt_user.set_access_based_on_domain()
        db.session.add(bt_user)
        
        db.session.commit()
        
        # Grant access to Erlang/OTP interest for both users
        erlang_interest = Interest.query.filter_by(name='Erlang/OTP').first()
        if erlang_interest:
            for user in [thbs_user, bt_user]:
                user_interest = UserInterest(
                    user_id=user.id,
                    interest_id=erlang_interest.id,
                    access_granted=True
                )
                db.session.add(user_interest)
        
        db.session.commit()
        
        print("✓ Demo users created successfully!")
        print("\nTo test the domain access control:")
        print("1. Register new users with these email addresses:")
        print("   - user@thbs.com (password: password123)")
        print("   - user@bt.com (password: password123)")
        print("2. Complete 2FA setup during registration")
        print("3. Login as admin to approve the users")
        print("4. Test course access:")
        print("   - THBS user: Can access ALL courses (including erlang-l3)")
        print("   - BT user: Cannot access courses with 'erlang-l3' in title")
        
        print("\nAdmin login: admin@example.com / Admin123")

if __name__ == '__main__':
    create_demo_users()