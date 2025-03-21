from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    otp_secret = db.Column(db.String(32))
    is_2fa_enabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    interests = db.relationship('Interest', 
                              secondary='user_interest',
                              primaryjoin="User.id==UserInterest.user_id",
                              secondaryjoin="Interest.id==UserInterest.interest_id",
                              backref='users')
    courses = db.relationship('Course', 
                              secondary='user_course',
                              primaryjoin="User.id==UserCourse.user_id",
                              secondaryjoin="Course.id==UserCourse.course_id",
                              backref='enrolled_users')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Interest(db.Model):
    __tablename__ = 'interests'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    courses = db.relationship('Course', 
                           secondary='course_interest',
                           primaryjoin="Interest.id==CourseInterest.interest_id",
                           secondaryjoin="Course.id==CourseInterest.course_id",
                           backref='interests')
    
    def __repr__(self):
        return f'<Interest {self.name}>'


class UserInterest(db.Model):
    __tablename__ = 'user_interest'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    interest_id = db.Column(db.Integer, db.ForeignKey('interests.id'), primary_key=True)
    access_granted = db.Column(db.Boolean, default=False)
    granted_at = db.Column(db.DateTime)
    granted_by = db.Column(db.Integer, db.ForeignKey('users.id'))


class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    cover_image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    lessons = db.relationship('Lesson', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Course {self.title}>'


class CourseInterest(db.Model):
    __tablename__ = 'course_interest'
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), primary_key=True)
    interest_id = db.Column(db.Integer, db.ForeignKey('interests.id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))


class UserCourse(db.Model):
    __tablename__ = 'user_course'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), primary_key=True)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<UserCourse user_id={self.user_id} course_id={self.course_id}>'


class Lesson(db.Model):
    __tablename__ = 'lessons'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Lesson {self.title}>'
