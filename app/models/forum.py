"""
Forum models: Contains all forum-related database models.

This module includes:
- ForumTopic: Forum topics created by users
- ForumReply: User replies to forum topics
"""
from datetime import datetime
from app import db

class ForumTopic(db.Model):
    """
    Represents a forum topic created by a user.
    
    Forum topics can be general (course_id is null) or specific to a course.
    Topics can be pinned by admins to highlight important discussions.
    Each topic can have multiple replies.
    """
    __tablename__ = 'forum_topics'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))  # Null means general forum
    pinned = db.Column(db.Boolean, default=False)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('forum_topics', lazy='dynamic'))
    course = db.relationship('Course', backref=db.backref('forum_topics', lazy='dynamic'))
    replies = db.relationship('ForumReply', backref='topic', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        """String representation of the ForumTopic"""
        return f'<ForumTopic {self.title}>'


class ForumReply(db.Model):
    """
    Represents a user's reply to a forum topic.
    
    Each reply is associated with a specific topic and user.
    Replies are displayed in chronological order in the forum.
    """
    __tablename__ = 'forum_replies'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('forum_topics.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('forum_replies', lazy='dynamic'))
    
    def __repr__(self):
        """String representation of the ForumReply"""
        return f'<ForumReply {self.id} by user {self.user_id}>'