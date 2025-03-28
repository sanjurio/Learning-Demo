"""
Content models: Contains all content-related database models.

This module includes:
- Interest: Subject areas that users can explore
- Course: Educational courses offered on the platform
- Lesson: Individual lessons within courses
- UserInterest: Association between users and interests with access control
- CourseInterest: Association between courses and interests
- UserCourse: Tracks user enrollment in courses
- UserLessonProgress: Tracks user progress through lessons
"""
from datetime import datetime
from app import db

class Interest(db.Model):
    """
    Represents a topic or subject area that users can be interested in.
    
    Interests are used to categorize courses and control user access to content.
    Admins create and manage interests, and can grant users access to specific interests.
    """
    __tablename__ = 'interests'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships with courses through the course_interest table
    courses = db.relationship('Course', 
                         secondary='course_interest',
                         primaryjoin="Interest.id==CourseInterest.interest_id",
                         secondaryjoin="Course.id==CourseInterest.course_id",
                         backref='interests')
    
    # Relationships with users through the user_interest table
    users = db.relationship('User',
                          secondary='user_interest',
                          primaryjoin="Interest.id==UserInterest.interest_id",
                          secondaryjoin="User.id==UserInterest.user_id",
                          backref='interests')
    
    def __repr__(self):
        """String representation of the Interest"""
        return f'<Interest {self.name}>'


class UserInterest(db.Model):
    """
    Association model that connects users with interests they have access to.
    
    This model includes access control - admins can grant or revoke access to interests.
    When access is granted, the user can see all courses associated with that interest.
    """
    __tablename__ = 'user_interest'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    interest_id = db.Column(db.Integer, db.ForeignKey('interests.id'), primary_key=True)
    access_granted = db.Column(db.Boolean, default=False)
    granted_at = db.Column(db.DateTime)
    granted_by = db.Column(db.Integer, db.ForeignKey('users.id'))


class Course(db.Model):
    """
    Represents an educational course offered on the platform.
    
    Courses contain multiple lessons and are categorized by interests.
    Users must have access to at least one of the course's interests to enroll.
    """
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    cover_image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    lessons = db.relationship('Lesson', backref='course', lazy='dynamic', 
                             cascade='all, delete-orphan')
    
    # Enrolled users through user_course table
    enrolled_users = db.relationship('User',
                                 secondary='user_course',
                                 primaryjoin="Course.id==UserCourse.course_id",
                                 secondaryjoin="User.id==UserCourse.user_id",
                                 backref='courses')
    
    def __repr__(self):
        """String representation of the Course"""
        return f'<Course {self.title}>'


class CourseInterest(db.Model):
    """
    Association model that connects courses with interests.
    
    Each course can be associated with multiple interests, and
    users with access to any of those interests can enroll in the course.
    """
    __tablename__ = 'course_interest'
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), primary_key=True)
    interest_id = db.Column(db.Integer, db.ForeignKey('interests.id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))


class UserCourse(db.Model):
    """
    Association model that tracks user enrollment in courses.
    
    This model records when a user enrolls in a course and whether they've completed it.
    """
    __tablename__ = 'user_course'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), primary_key=True)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        """String representation of the UserCourse"""
        return f'<UserCourse user_id={self.user_id} course_id={self.course_id}>'


class Lesson(db.Model):
    """
    Represents an individual lesson within a course.
    
    Lessons contain educational content and are presented in a specific order.
    User progress through lessons is tracked via the UserLessonProgress model.
    """
    __tablename__ = 'lessons'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with user progress
    user_progress = db.relationship('UserLessonProgress', backref='lesson', 
                                  lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        """String representation of the Lesson"""
        return f'<Lesson {self.title}>'


class UserLessonProgress(db.Model):
    """
    Tracks a user's progress through a lesson.
    
    This model records when a user starts and completes a lesson,
    as well as their current status (not started, in progress, completed).
    """
    __tablename__ = 'user_lesson_progress'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), primary_key=True)
    status = db.Column(db.String(20), default='not_started')  # not_started, in_progress, completed
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    last_interaction = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with user
    user = db.relationship('User', backref=db.backref('lesson_progress', lazy='dynamic'))
    
    def __repr__(self):
        """String representation of the UserLessonProgress"""
        return f'<UserLessonProgress user_id={self.user_id} lesson_id={self.lesson_id} status={self.status}>'