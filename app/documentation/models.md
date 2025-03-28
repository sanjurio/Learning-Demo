# Database Models Documentation

This document provides a detailed explanation of the database models used in the AI Learning Platform. The application uses SQLAlchemy ORM to manage database interactions.

## Overview of Model Relationships

![Database ERD Diagram](../documentation/images/database_schema.png)

The diagram above shows the relationships between the models in the database.

## User Model

**File: `app/models/user.py`**

The User model represents registered users in the system and handles authentication.

```python
class User(UserMixin, db.Model):
    """
    User model representing registered users in the system.
    
    This model handles authentication, 2FA, and admin status.
    It has relationships with interests, courses, and forum content.
    """
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
```

### Key Fields:

- `id`: Primary key
- `username`: Unique username for each user
- `email`: Unique email address used for login
- `password_hash`: Securely hashed password (never stored in plain text)
- `is_admin`: Boolean flag indicating admin privileges
- `is_approved`: Boolean flag indicating whether user has been approved by an admin
- `otp_secret`: Secret key for two-factor authentication
- `is_2fa_enabled`: Boolean flag indicating whether 2FA is enabled
- `created_at`: Timestamp of user creation

### Methods:

- `set_password(password)`: Hashes and sets the user's password
- `check_password(password)`: Verifies a password against the stored hash
- `__repr__()`: String representation of the user

### Relationships:

- `interests`: Many-to-many relationship with Interest model through UserInterest
- `courses`: Many-to-many relationship with Course model through UserCourse
- `lesson_progress`: One-to-many relationship with UserLessonProgress
- `forum_topics`: One-to-many relationship with ForumTopic
- `forum_replies`: One-to-many relationship with ForumReply

## Content Models

**File: `app/models/content.py`**

### Interest Model

The Interest model represents a topic or subject area that organizes courses.

```python
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
```

### Key Fields:

- `id`: Primary key
- `name`: Unique name of the interest
- `description`: Detailed description of the interest
- `created_at`: Timestamp of interest creation
- `created_by`: FK to User who created the interest

### UserInterest Model

Association model that connects users with interests and manages access control.

```python
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
```

### Key Fields:

- `user_id`: Part of composite primary key, FK to User
- `interest_id`: Part of composite primary key, FK to Interest
- `access_granted`: Boolean indicating whether access is granted
- `granted_at`: Timestamp when access was granted
- `granted_by`: FK to User (admin) who granted access

### Course Model

The Course model represents an educational course containing lessons.

```python
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
```

### Key Fields:

- `id`: Primary key
- `title`: Course title
- `description`: Detailed description of the course
- `cover_image_url`: URL to the course's cover image
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `created_by`: FK to User who created the course

### Relationships:

- `lessons`: One-to-many relationship with Lesson
- `enrolled_users`: Many-to-many relationship with User through UserCourse
- `interests`: Many-to-many relationship with Interest through CourseInterest

### CourseInterest Model

Association model connecting courses with interests for categorization.

```python
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
```

### UserCourse Model

Tracks user enrollment in courses.

```python
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
```

### Lesson Model

Represents an individual lesson within a course.

```python
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
```

### Key Fields:

- `id`: Primary key
- `title`: Lesson title
- `content`: HTML content of the lesson
- `course_id`: FK to Course the lesson belongs to
- `order`: Integer defining the order of lessons within a course
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### UserLessonProgress Model

Tracks a user's progress through individual lessons.

```python
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
```

### Key Fields:

- `user_id`: Part of composite primary key, FK to User
- `lesson_id`: Part of composite primary key, FK to Lesson
- `status`: Current progress status ('not_started', 'in_progress', 'completed')
- `started_at`: Timestamp when the user started the lesson
- `completed_at`: Timestamp when the user completed the lesson
- `last_interaction`: Timestamp of the user's last interaction with the lesson

## Forum Models

**File: `app/models/forum.py`**

### ForumTopic Model

Represents a discussion topic created by a user.

```python
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
```

### Key Fields:

- `id`: Primary key
- `title`: Topic title
- `content`: Topic content (HTML formatted)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `user_id`: FK to User who created the topic
- `course_id`: Optional FK to Course (null for general forum topics)
- `pinned`: Boolean indicating whether the topic is pinned

### Relationships:

- `user`: Many-to-one relationship with User
- `course`: Many-to-one relationship with Course
- `replies`: One-to-many relationship with ForumReply

### ForumReply Model

Represents a user's reply to a forum topic.

```python
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
```

### Key Fields:

- `id`: Primary key
- `content`: Reply content (HTML formatted)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `user_id`: FK to User who wrote the reply
- `topic_id`: FK to ForumTopic the reply belongs to

### Relationships:

- `user`: Many-to-one relationship with User
- `topic`: Many-to-one relationship with ForumTopic

## API Key Model

**File: `app/models/api_key.py`**

### ApiKey Model

Stores API keys for external services like OpenAI.

```python
class ApiKey(db.Model):
    """
    Represents an API key for an external service.
    
    This model stores API keys for services like OpenAI that are used by the application.
    Keys are encrypted in the database for security.
    Only admins can manage API keys.
    """
    __tablename__ = 'api_keys'
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(50), nullable=False, unique=True)
    key_value = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
```

### Key Fields:

- `id`: Primary key
- `service_name`: Unique name of the service the API key is for
- `key_value`: The API key value (should be encrypted in production)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `created_by`: FK to User (admin) who created the API key