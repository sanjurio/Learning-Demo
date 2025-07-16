#!/usr/bin/env python3
"""
Set up 2FA for test users to enable login
"""
import os
from app import create_app
from app.models import db, User
from utils import generate_otp_secret

def setup_test_users_2fa():
    """Enable 2FA for test users"""
    app = create_app()
    
    with app.app_context():
        # Find test users
        thbs_user = User.query.filter_by(email='developer@thbs.com').first()
        bt_user = User.query.filter_by(email='engineer@bt.com').first()
        
        users_to_setup = []
        if thbs_user:
            users_to_setup.append(thbs_user)
        if bt_user:
            users_to_setup.append(bt_user)
        
        if not users_to_setup:
            print("No test users found. Please run create_test_users.py first")
            return
        
        for user in users_to_setup:
            if not user.is_2fa_enabled:
                # Generate OTP secret
                user.otp_secret = generate_otp_secret()
                user.is_2fa_enabled = True
                print(f"✓ Set up 2FA for {user.email}")
                print(f"  OTP Secret: {user.otp_secret}")
        
        db.session.commit()
        
        print("\nTest users with 2FA enabled:")
        for user in users_to_setup:
            print(f"  Email: {user.email}")
            print(f"  Password: TestPassword123")
            print(f"  2FA Secret: {user.otp_secret}")
            print(f"  Domain: {user.email_domain}")
            print(f"  Access Level: {user.access_level}")
            print()
        
        print("To login:")
        print("1. Use email address (not username)")
        print("2. Enter password: TestPassword123")
        print("3. Use the OTP secret above in a 2FA app (Google Authenticator, Authy, etc.)")
        print("4. Enter the 6-digit code from your 2FA app")

if __name__ == '__main__':
    setup_test_users_2fa()