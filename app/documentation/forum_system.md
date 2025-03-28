# Forum System Documentation

This document details the forum system implemented in the AI Learning Platform, which enables discussions between users in both general and course-specific contexts.

## Overview

The forum system provides a space for users to:

- Engage in general discussions about platform topics
- Participate in course-specific discussions related to learning content
- Ask questions and share insights with other users
- Interact with course instructors and administrators

The forum is divided into two main sections:
1. **General forum** - Open to all approved users
2. **Course forums** - Accessible only to users enrolled in specific courses

## Models

**File: `app/models/forum.py`**

### Forum Topic Model

```python
class ForumTopic(db.Model):
    """
    Represents a forum topic created by a user.
    
    Topics can be general or course-specific, and can contain multiple replies.
    Admins can pin important topics to make them more visible.
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
    replies = db.relationship('ForumReply', backref='topic', lazy='dynamic', cascade='all, delete-orphan')
```

Key fields include:
- `title`: The topic title
- `content`: The main text of the topic (supports HTML formatting)
- `user_id`: Creator of the topic
- `course_id`: Optional reference to a specific course (null for general forum)
- `pinned`: Boolean flag for pinned topics (prioritized in display)

### Forum Reply Model

```python
class ForumReply(db.Model):
    """
    Represents a user's reply to a forum topic.
    
    Replies are displayed chronologically within their parent topic.
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
```

Key fields include:
- `content`: The text of the reply (supports HTML formatting)
- `user_id`: Creator of the reply
- `topic_id`: Reference to the parent topic

## Forms

**File: `app/forms.py`**

### Forum Topic Form

```python
class ForumTopicForm(FlaskForm):
    """Form for creating and editing forum topics"""
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=5, max=200, message='Title must be between 5 and 200 characters')
    ])
    content = TextAreaField('Content', validators=[
        DataRequired(),
        Length(min=10, message='Content must be at least 10 characters')
    ])
    course_id = HiddenField('Course ID')
    submit = SubmitField('Post Topic')
```

### Forum Reply Form

```python
class ForumReplyForm(FlaskForm):
    """Form for posting replies to forum topics"""
    content = TextAreaField('Reply', validators=[
        DataRequired(),
        Length(min=2, message='Reply must be at least 2 characters')
    ])
    submit = SubmitField('Post Reply')
```

## Routes

**File: `app/core/routes.py`**

### Main Forum Routes

```python
@core_bp.route('/forum')
@login_required
def forum_index():
    """Show the forum index with general and course-specific sections"""
    # Get all general topics
    # Get user's enrolled courses
    # Get pinned topics
    # Return forum index template
    
@core_bp.route('/forum/topic/<int:topic_id>', methods=['GET', 'POST'])
@login_required
def forum_topic(topic_id):
    """Show a specific forum topic and handle replies"""
    # Get topic by ID
    # Check access permission
    # Handle new reply form
    # Return topic template with replies
    
@core_bp.route('/forum/new-topic', methods=['GET', 'POST'])
@login_required
def forum_new_topic():
    """Create a new general forum topic"""
    # Handle topic form submission
    # Create new topic
    # Redirect to new topic
```

### Course-Specific Forum Routes

```python
@core_bp.route('/course/<int:course_id>/forum', methods=['GET', 'POST'])
@login_required
def course_forum(course_id):
    """Show forum topics for a specific course"""
    # Get course by ID
    # Check enrollment
    # Get course topics
    # Handle new topic form
    # Return course forum template
```

## Access Control

Forum access is controlled by several mechanisms:

### General Forum Access

All approved users can access the general forum, which is controlled by:
- `@login_required` decorator on routes
- User approval status check in route handlers

### Course Forum Access

Course-specific forums are restricted to enrolled users:

```python
def check_course_access(course_id):
    """Check if current user has access to a course"""
    # Get course
    # Check if user is enrolled or has interest access
    # Return boolean
```

This access control ensures that users can only participate in discussions for courses they are enrolled in.

### Admin Privileges

Administrators have additional capabilities in the forum:

```python
@core_bp.route('/forum/admin/pin-topic/<int:topic_id>', methods=['POST'])
@login_required
@admin_required
def admin_pin_topic(topic_id):
    """Toggle pin status for a topic (admin only)"""
    # Get topic
    # Toggle pin status
    # Update database
    # Redirect back to topic
    
@core_bp.route('/forum/admin/delete-topic/<int:topic_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_topic(topic_id):
    """Delete a forum topic and all its replies (admin only)"""
    # Get topic
    # Delete topic and cascade to replies
    # Redirect to forum index
    
@core_bp.route('/forum/admin/delete-reply/<int:reply_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_reply(reply_id):
    """Delete a forum reply (admin only)"""
    # Get reply
    # Delete reply
    # Redirect back to topic
```

## Templates

**Directory: `templates/forum/`**

The forum system uses several templates:

### Forum Index Template

**File: `templates/forum/index.html`**

Displays:
- List of pinned topics
- General forum topics
- Links to course-specific forums
- New topic button

### Forum Topic Template

**File: `templates/forum/topic.html`**

Shows:
- Topic title and content
- Author information and timestamp
- All replies in chronological order
- Reply form for posting new replies
- Admin controls (for admin users)

### Course Forum Template

**File: `templates/forum/course_forum.html`**

Displays:
- Course information and banner
- Topics specific to the course
- New topic form
- Back to course link

## Features

### Pinned Topics

Important topics can be pinned by administrators:
- Pinned topics appear at the top of forum listings
- Visual indicator shows pinned status
- Only admins can pin/unpin topics

### Rich Text Formatting

Forum content supports basic HTML formatting:
- Rich text editor for topic creation and replies
- Support for text formatting (bold, italic, etc.)
- List support (ordered and unordered)
- Link embedding

### User Identification

Posts in the forum clearly identify the author:
- Username display
- Optional user avatar
- Special indicators for admin posts
- Timestamp for all content

### Sorting and Filtering

Forum topics can be sorted and filtered:
- Sort by creation date
- Sort by activity (latest reply)
- Filter by course (for course forums)
- Search functionality for topics and content

## Implementation Details

### Pagination

Forum listings implement pagination to handle large numbers of topics:

```python
def forum_index():
    """Paginated forum index"""
    page = request.args.get('page', 1, type=int)
    topics_per_page = 20
    
    # Get paginated topics
    topics = ForumTopic.query.filter_by(course_id=None).order_by(
        ForumTopic.pinned.desc(),
        ForumTopic.updated_at.desc()
    ).paginate(page=page, per_page=topics_per_page)
```

### Content Sanitization

User-generated content is sanitized to prevent XSS attacks:

```python
def sanitize_html(content):
    """Sanitize HTML content to prevent XSS"""
    # Use HTML sanitizer library
    # Allow safe tags and attributes
    # Strip unsafe content
    return sanitized_content
```

### Last Activity Tracking

Topics track the latest activity for sorting purposes:

```python
@core_bp.route('/forum/topic/<int:topic_id>', methods=['GET', 'POST'])
def forum_topic(topic_id):
    # When a new reply is added:
    if form.validate_on_submit():
        # Create reply
        # Update topic's updated_at timestamp
        topic.updated_at = datetime.utcnow()
        db.session.commit()
```

## User Interface

### Forum Navigation

The forum interface includes:
- Breadcrumb navigation
- Section headers
- Clear visual hierarchy
- Responsive design for mobile use

### Topic Display

Topics are displayed with:
- Title and preview of content
- Author information
- Reply count
- Last activity timestamp
- Visual indicators for pinned status

### Reply Interface

The reply section includes:
- Threaded display of all replies
- User information for each reply
- Rich text editor for new replies
- Quote functionality for referencing previous posts

## Best Practices

### Forum Moderation

Guidelines for effective forum moderation:

1. **Regular monitoring**: Admins should regularly check forum activity
2. **Clear guidelines**: Forum rules should be clearly communicated
3. **Prompt responses**: Address inappropriate content quickly
4. **Constructive intervention**: Focus on education rather than punishment
5. **Pin useful information**: Use pinning for FAQs and important announcements

### User Engagement

Strategies for increasing forum engagement:

1. **Seed discussions**: Create initial topics to encourage participation
2. **Highlight quality content**: Pin exemplary discussions
3. **Respond promptly**: Ensure questions receive timely answers
4. **Encourage peer support**: Foster a community of mutual assistance
5. **Recognize contributions**: Acknowledge helpful users

## Integration with Learning Platform

The forum system integrates with other aspects of the platform:

### Course Integration

Course forums are directly accessible from course pages:
- Forum tab in course navigation
- Recent discussions displayed on course dashboard
- Lesson-specific discussion links

### Notification System

Users can receive notifications about forum activity:
- New replies to their topics
- Mentions in forum posts
- Updates to pinned topics