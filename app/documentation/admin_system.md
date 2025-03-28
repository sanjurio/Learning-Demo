# Admin System Documentation

This document details the admin features available in the AI Learning Platform, including user management, content administration, and system configuration.

## Overview

The admin system provides privileged users with tools to:

- Manage user accounts and approvals
- Create and organize educational content
- Configure system settings and API keys
- Monitor and moderate forum discussions
- Control access to interest-based content

## Admin User Creation

Admin users can be created through several methods:

### 1. Direct Database Script

**File: `create_admin_direct.py`**

This script creates an admin user directly in the database:

```python
def create_admin_user():
    """Create admin user directly in the database"""
    # Connect to database
    # Check if admin exists
    # Create admin user with specified credentials
    # Set admin flag to True
    # Enable admin account without 2FA requirement
```

### 2. Application-Based Creation

**File: `create_admin.py`**

This script creates an admin user through the application's models:

```python
def create_new_admin():
    """Create a new admin user through application models"""
    # Initialize application context
    # Create admin user with app models
    # Set admin flags and permissions
    # Commit changes to database
```

### 3. Reset Admin 2FA

**File: `reset_admin_2fa.py`**

This script resets 2FA for admin users in case of lockout:

```python
def reset_admin_2fa():
    """Reset 2FA for admin users"""
    # Find admin user
    # Disable 2FA
    # Reset OTP secret
    # Save changes
```

## Admin Dashboard

**Routes: `app/admin/routes.py`**

The admin dashboard provides an overview of the platform:

```python
@admin_bp.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    """Render the admin dashboard"""
    # Get key statistics:
    # - User counts
    # - Course counts
    # - Recent activity
    # - Pending approvals
```

The dashboard includes:
- Summary statistics
- Quick links to common tasks
- Recent system activity
- Pending approval notifications

## User Management

### User Listing and Search

```python
@admin_bp.route('/users')
@login_required
@admin_required
def admin_users():
    """List all users with search capability"""
    # Get all users
    # Apply search filters
    # Paginate results
```

This interface allows admins to:
- View all user accounts
- Search by username or email
- Filter by admin status or approval status
- Access individual user management

### Pending User Approvals

```python
@admin_bp.route('/users/pending')
@login_required
@admin_required
def admin_pending_users():
    """List users awaiting approval"""
    # Get users with is_approved=False
    # Display approval interface
```

This page shows:
- New user registrations awaiting approval
- Registration date and user details
- Approval/rejection buttons

### User Approval Process

```python
@admin_bp.route('/users/approve', methods=['POST'])
@login_required
@admin_required
def admin_approve_user():
    """Approve or reject a user registration"""
    # Validate form
    # Approve or reject based on action
    # Update user record
    # Notify user
```

When approving users, admins can:
- Review user information
- Grant or deny access to the platform
- Add notes for internal reference

### User Interest Management

```python
@admin_bp.route('/users/<int:user_id>/interests')
@login_required
@admin_required
def admin_user_interests(user_id):
    """Manage interests for a specific user"""
    # Get user by ID
    # Get all interests
    # Show current access status
```

This interface lets admins:
- See which interests a user has access to
- Grant or revoke access to specific interests
- Control content visibility for each user

## Content Management

### Interest Management

```python
@admin_bp.route('/interests')
@login_required
@admin_required
def admin_interests():
    """Manage interest categories"""
    # List all interests
    # Show related courses
    # Provide CRUD links
```

Admins can:
- Create new interest categories
- Edit existing interest details
- Delete interests (if not associated with courses)
- View courses in each interest

### Course Management

```python
@admin_bp.route('/courses')
@login_required
@admin_required
def admin_courses():
    """Manage courses"""
    # List all courses
    # Show course details
    # Provide CRUD links
```

Course management includes:
- Creating new courses
- Assigning courses to interests
- Editing course details and content
- Deleting courses

### Lesson Management

```python
@admin_bp.route('/courses/<int:course_id>/lessons')
@login_required
@admin_required
def admin_lessons(course_id):
    """Manage lessons for a specific course"""
    # Get course by ID
    # List all lessons
    # Show lesson order
```

Lesson management allows:
- Creating new lessons
- Editing lesson content
- Changing lesson order
- Deleting lessons

## Forum Moderation

Admins have special privileges in the forum system:

```python
# Special admin actions in forum routes
def forum_topic(topic_id):
    """View a forum topic with admin controls"""
    # Show topic and replies
    # For admins, include:
    # - Pin/unpin option
    # - Delete controls
    # - Moderation tools
```

Admin forum capabilities include:
- Pinning important topics
- Deleting inappropriate topics or replies
- Viewing all forums, including course-specific ones
- Moderating discussions

## API Key Management

```python
@admin_bp.route('/api-keys', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_api_keys():
    """Manage API keys for external services"""
    # List existing API keys
    # Show update form
    # Handle form submission
    # Test API connectivity
```

This interface allows admins to:
- Add or update API keys for services like OpenAI
- Test API connections
- View API usage statistics
- Securely manage sensitive credentials

## Administrative Forms

**File: `app/forms.py`**

Several forms support admin functionality:

```python
class UserApprovalForm(FlaskForm):
    """Form for approving/rejecting user registrations"""
    action = HiddenField(validators=[DataRequired()])
    user_id = HiddenField(validators=[DataRequired()])
    submit = SubmitField('Submit')

class InterestForm(FlaskForm):
    """Form for creating/editing interests"""
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    submit = SubmitField('Save Interest')

class CourseForm(FlaskForm):
    """Form for creating/editing courses"""
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    cover_image_url = StringField('Cover Image URL', validators=[Length(max=500)])
    interests = MultiCheckboxField('Interests', coerce=int)
    submit = SubmitField('Save Course')

class LessonForm(FlaskForm):
    """Form for creating/editing lessons"""
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    order = IntegerField('Order', default=0)
    submit = SubmitField('Save Lesson')

class UserInterestAccessForm(FlaskForm):
    """Form for managing user access to interests"""
    user_id = HiddenField(validators=[DataRequired()])
    interest_id = HiddenField(validators=[DataRequired()])
    action = HiddenField(validators=[DataRequired()])
    submit = SubmitField('Update Access')

class ApiKeyForm(FlaskForm):
    """Form for managing API keys"""
    openai_api_key = PasswordField('OpenAI API Key', validators=[
        DataRequired(),
        Length(min=20, message='API key should be at least 20 characters long')
    ])
    submit = SubmitField('Save API Key')
```

## Admin Authorization

**File: `app/utils/auth_helpers.py`**

Admin access is controlled through decorators:

```python
def admin_required(f):
    """Decorator to restrict access to admin users only"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Administrator access required.', 'danger')
            return redirect(url_for('core.index'))
        return f(*args, **kwargs)
    return decorated_function
```

This decorator is applied to all admin routes to ensure only authorized users can access them.

## Database Initialization and Setup

**File: `setup_db.py`**

Admins can initialize the database with sample data:

```python
def create_interests(admin_id):
    """Create basic interest categories if they don't exist"""
    # Check existing interests
    # Create default interests if none exist
    
def create_sample_courses():
    """Create sample courses with lessons"""
    # Create courses in various interests
    # Populate with sample lessons
```

## Admin Templates

**Directory: `templates/admin/`**

The admin interface uses a set of templates including:

- `admin_layout.html`: Base template for admin pages
- `dashboard.html`: Admin dashboard
- `users.html`: User management
- `pending_users.html`: Approval interface
- `courses.html`: Course management
- `interests.html`: Interest management
- `lessons.html`: Lesson management
- `api_keys.html`: API key configuration

These templates include:
- Consistent navigation
- Admin-specific controls
- Form validation
- Data tables with sorting and filtering

## Security Considerations

### Route Protection

All admin routes are protected by:
- Login requirement
- Admin status verification
- CSRF protection

### Form Validation

Admin forms include:
- Data validation
- CSRF tokens
- Confirmation for destructive actions

### Audit Logging

Actions taken by admins are logged:
- User approvals and rejections
- Content creation and deletion
- System configuration changes
- API key updates

## Best Practices for Administrators

1. **Regular User Review**:
   - Periodically review pending user registrations
   - Check for suspicious activity

2. **Content Management**:
   - Organize courses within logical interest categories
   - Maintain consistent course structure
   - Regularly update course material

3. **API Key Security**:
   - Rotate API keys periodically
   - Use restrictive permissions for API keys
   - Monitor API key usage

4. **System Monitoring**:
   - Check system logs for errors
   - Monitor user activity
   - Address user reported issues promptly

5. **2FA Management**:
   - Maintain backup admin accounts
   - Document 2FA reset procedures
   - Consider emergency access protocols