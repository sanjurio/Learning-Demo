#!/usr/bin/env python3
"""
Create test users with different domain access levels
"""
import os
from app import create_app
from app.models import db, User, Interest, UserInterest

def create_test_users():
    """Create test users from different domains"""
    app = create_app()
    
    with app.app_context():
        # Create THBS domain user
        thbs_user = User(
            username='thbs_developer',
            email='developer@thbs.com',
            is_approved=True,
            is_admin=False
        )
        thbs_user.set_password('TestPassword123')
        thbs_user.set_access_based_on_domain()
        db.session.add(thbs_user)
        
        # Create BT domain user  
        bt_user = User(
            username='bt_engineer',
            email='engineer@bt.com',
            is_approved=True,
            is_admin=False
        )
        bt_user.set_password('TestPassword123')
        bt_user.set_access_based_on_domain()
        db.session.add(bt_user)
        
        # Create other domain user
        other_user = User(
            username='external_dev',
            email='dev@external.com',
            is_approved=True,
            is_admin=False
        )
        other_user.set_password('TestPassword123')
        other_user.set_access_based_on_domain()
        db.session.add(other_user)
        
        db.session.commit()
        
        # Grant access to Erlang/OTP interest for all users
        erlang_interest = Interest.query.filter_by(name='Erlang/OTP').first()
        if erlang_interest:
            users = [thbs_user, bt_user, other_user]
            for user in users:
                user_interest = UserInterest(
                    user_id=user.id,
                    interest_id=erlang_interest.id,
                    access_granted=True
                )
                db.session.add(user_interest)
        
        db.session.commit()
        
        print("✓ Created test users:")
        print(f"  - THBS user: {thbs_user.username} ({thbs_user.email}) - Access Level: {thbs_user.access_level}")
        print(f"  - BT user: {bt_user.username} ({bt_user.email}) - Access Level: {bt_user.access_level}")
        print(f"  - Other user: {other_user.username} ({other_user.email}) - Access Level: {other_user.access_level}")
        
        print("\nLogin credentials for testing:")
        print("  - THBS user: thbs_developer / TestPassword123")
        print("  - BT user: bt_engineer / TestPassword123")
        print("  - Other user: external_dev / TestPassword123")
        
        print("\nExpected access behavior:")
        print("  - THBS user: Can access ALL courses (including erlang-l3)")
        print("  - BT user: Cannot access erlang-l3 courses")
        print("  - Other user: Standard interest-based access")

if __name__ == '__main__':
    create_test_users()