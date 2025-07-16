from ..models import User, UserInterest
from .. import db

def get_pending_users():
    """Get users pending approval"""
    return User.query.filter_by(is_approved=False, is_admin=False).all()

def approve_user(user_id, approved_by_id=None):
    """Approve a user"""
    user = User.query.get(user_id)
    if user:
        user.is_approved = True
        db.session.commit()
        return True
    return False

def reject_user(user_id, rejected_by_id=None):
    """Reject a user (delete their account)"""
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return True
    return False

def set_user_video_access(user_id, video_access):
    """Set video access for user (force override domain settings)"""
    user = User.query.get(user_id)
    if user:
        if video_access:
            user.access_level = 'full_access'
        else:
            user.access_level = 'text_only'
        db.session.commit()
        return True
    return False

def grant_interest_access(user_id, interest_id):
    """Grant user access to an interest"""
    user_interest = UserInterest.query.filter_by(
        user_id=user_id, 
        interest_id=interest_id
    ).first()
    
    if user_interest:
        user_interest.access_granted = True
        db.session.commit()
        return True
    return False

def revoke_interest_access(user_id, interest_id):
    """Revoke user access to an interest"""
    user_interest = UserInterest.query.filter_by(
        user_id=user_id, 
        interest_id=interest_id
    ).first()
    
    if user_interest:
        user_interest.access_granted = False
        db.session.commit()
        return True
    return False