# Course System Documentation

This document explains the course system in the AI Learning Platform, which provides the structure for educational content and learning progression.

## Overview

The course system is designed to:

- Organize educational content into structured courses
- Provide a sequential learning experience through ordered lessons
- Track user progress through course material
- Restrict access based on user interests and permissions
- Enable discussion around course topics

Key components include:
- Courses: Collections of related educational content
- Lessons: Individual units of learning within courses
- Interests: Categories that group related courses
- Enrollment: User registration in specific courses
- Progress Tracking: Monitoring user advancement through lessons

## Models

**File: `app/models/content.py`**

### Course Model

```python
class Course(db.Model):
    """
    Represents an educational course offered on the platform.
    
    Courses are the main content containers and consist of multiple lessons.
    They are categorized by interests and accessible to users with appropriate permissions.
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
    lessons = db.relationship('Lesson', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    forum_topics = db.relationship('ForumTopic', backref='course', lazy='dynamic')
```

Key fields include:
- `title`: Course name
- `description`: Detailed description of the course content
- `cover_image_url`: URL to the course's cover image
- `created_by`: Reference to the admin who created the course

### Lesson Model

```python
class Lesson(db.Model):
    """
    Represents an individual lesson within a course.
    
    Lessons contain the actual educational content and are presented in a specific order.
    User progress through lessons is tracked to monitor course completion.
    """
    __tablename__ = 'lessons'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_progress = db.relationship('UserLessonProgress', backref='lesson', lazy='dynamic', cascade='all, delete-orphan')
```

Key fields include:
- `title`: Lesson name
- `content`: The actual lesson content (HTML format)
- `course_id`: Reference to the parent course
- `order`: Numerical position within the course sequence

### CourseInterest Model

```python
class CourseInterest(db.Model):
    """
    Association model connecting courses with interests.
    
    This model allows courses to be categorized under multiple interests,
    enabling interest-based access control and content organization.
    """
    __tablename__ = 'course_interest'
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), primary_key=True)
    interest_id = db.Column(db.Integer, db.ForeignKey('interests.id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
```

This association table connects courses with interests, enabling categorization and access control.

### UserCourse Model

```python
class UserCourse(db.Model):
    """
    Association model tracking user enrollment in courses.
    
    Records when a user enrolls in a course and their completion status.
    """
    __tablename__ = 'user_course'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), primary_key=True)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
```

This model tracks:
- Which users are enrolled in which courses
- When they enrolled
- Whether they have completed the course

### UserLessonProgress Model

```python
class UserLessonProgress(db.Model):
    """
    Tracks a user's progress through individual lessons.
    
    Records the status of each lesson for a user (not started, in progress, completed)
    along with timing information about their interaction with the lesson.
    """
    __tablename__ = 'user_lesson_progress'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), primary_key=True)
    status = db.Column(db.String(20), default='not_started')  # not_started, in_progress, completed
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    last_interaction = db.Column(db.DateTime, default=datetime.utcnow)
```

This model tracks:
- The status of each lesson for each user
- When the user started the lesson
- When they completed it (if applicable)
- Their last interaction with the lesson

## Forms

**File: `app/forms.py`**

### Course Form

```python
class CourseForm(FlaskForm):
    """Form for creating and editing courses"""
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    cover_image_url = StringField('Cover Image URL', validators=[Length(max=500)])
    interests = MultiCheckboxField('Interests', coerce=int)
    submit = SubmitField('Save Course')
```

### Lesson Form

```python
class LessonForm(FlaskForm):
    """Form for creating and editing lessons"""
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    order = IntegerField('Order', default=0)
    submit = SubmitField('Save Lesson')
```

## Routes

**File: `app/core/routes.py` and `app/admin/routes.py`**

### User Course Routes

```python
@core_bp.route('/dashboard')
@login_required
def user_dashboard():
    """Show user dashboard with enrolled courses and progress"""
    # Get user's enrolled courses
    # Calculate progress for each course
    # Show available interests and courses
    
@core_bp.route('/course/<int:course_id>')
@login_required
def view_course(course_id):
    """View a course and its lessons"""
    # Get course by ID
    # Check access permission
    # Get lessons in order
    # Get user progress data
    # Display course information
    
@core_bp.route('/lesson/<int:lesson_id>')
@login_required
def view_lesson(lesson_id):
    """View a specific lesson and track progress"""
    # Get lesson by ID
    # Check course access permission
    # Update user progress (start or complete)
    # Get next and previous lessons
    # Display lesson content
```

### Admin Course Management Routes

```python
@admin_bp.route('/courses')
@login_required
@admin_required
def admin_courses():
    """List all courses for admin management"""
    
@admin_bp.route('/courses/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_course():
    """Add a new course"""
    
@admin_bp.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_course(course_id):
    """Edit an existing course"""
    
@admin_bp.route('/courses/<int:course_id>/lessons')
@login_required
@admin_required
def admin_lessons(course_id):
    """Manage lessons for a course"""
    
@admin_bp.route('/courses/<int:course_id>/lessons/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_lesson(course_id):
    """Add a new lesson to a course"""
    
@admin_bp.route('/lessons/<int:lesson_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_lesson(lesson_id):
    """Edit an existing lesson"""
```

## Access Control

### Interest-Based Access

Course access is controlled through a user's interests:

```python
def user_has_access_to_course(user, course):
    """Check if a user has access to a course based on interests"""
    # Get user's interests with access_granted=True
    # Get course's interests
    # Check for intersection
    # Return boolean
```

A user can access a course if they have been granted access to at least one of the interests associated with the course.

### Enrollment

Users need to enroll in a course to track progress:

```python
@core_bp.route('/course/<int:course_id>/enroll', methods=['POST'])
@login_required
def enroll_in_course(course_id):
    """Enroll the current user in a course"""
    # Check if user has access to the course
    # Create UserCourse record if not already enrolled
    # Redirect to course page
```

## Course Content

### Content Structure

Course content is structured hierarchically:

1. **Course**: The top-level container with metadata
2. **Lessons**: Ordered content units within a course
3. **Lesson Content**: Rich HTML content including text, images, and embedded media

### Rich Text Content

Lesson content supports rich HTML formatting:

- Text formatting (headings, paragraphs, lists)
- Image embedding
- Video embedding
- Code snippets with syntax highlighting
- Interactive elements (quizzes, exercises)

### Content Editor

The admin interface includes a rich text editor for lessons:

- WYSIWYG editing
- HTML source editing
- Image upload and management
- Media embedding tools

## Progress Tracking

### Lesson Status

Lesson progress is tracked with three states:

- `not_started`: User has not viewed the lesson
- `in_progress`: User has viewed but not completed the lesson
- `completed`: User has marked the lesson as completed

### Course Completion

Course completion is calculated based on lesson completion:

```python
def calculate_course_completion(user_id, course_id):
    """Calculate the completion percentage for a course"""
    # Get total number of lessons in course
    # Get number of completed lessons for user
    # Calculate percentage
    # Update UserCourse.completed if all lessons are complete
    # Return percentage
```

### Progress Visualization

The user interface shows progress visually:

- Progress bars for course completion
- Status indicators for individual lessons
- Next lesson recommendations
- Completion certificates or badges

## Templates

**Directory: `templates/courses/`**

Key templates include:

- `user_dashboard.html`: Shows enrolled courses and progress
- `course_detail.html`: Displays course information and lessons
- `lesson_detail.html`: Shows lesson content with navigation
- `admin_courses.html`: Admin interface for course management
- `admin_lessons.html`: Admin interface for lesson management

## Implementation Details

### Lesson Ordering

Lessons maintain their order within courses:

```python
def reorder_lessons(course_id, lesson_ids):
    """Update the order of lessons in a course"""
    # Iterate through lesson_ids list
    # Update each lesson's order field
    # Commit changes
```

When adding or removing lessons, the order is automatically adjusted to maintain consistency.

### Content Rendering

Lesson content is rendered with security considerations:

```python
def render_lesson_content(content):
    """Safely render lesson HTML content"""
    # Sanitize HTML to prevent XSS
    # Process markdown if applicable
    # Inject any dynamic content
    # Return safe HTML
```

### Course Images

Course cover images enhance visual appeal:

- Default placeholder images for courses without custom covers
- Support for both URLs and uploaded images
- Responsive image sizing for different devices

## Integration with Other Systems

### Forum Integration

Each course has an associated forum:

- Course-specific discussion topics
- Lesson-specific questions
- Access control matching course access

### Document Analysis Integration

The document analysis feature can be used with courses:

- Upload course materials for analysis
- Generate lesson summaries
- Create questions based on lesson content

## Best Practices

### Course Design

Guidelines for effective course design:

1. **Clear structure**: Organize content logically
2. **Progressive complexity**: Start simple and build complexity
3. **Consistent format**: Maintain consistent lesson structure
4. **Engaging media**: Include images and videos
5. **Interactive elements**: Add quizzes and exercises

### Content Management

Best practices for content managers:

1. **Regular updates**: Keep course content current
2. **Quality checking**: Review content for errors
3. **Version control**: Track content changes
4. **Media optimization**: Ensure media is optimized for web
5. **Accessibility**: Make content accessible to all users