# Authentication System Documentation

This document explains the authentication system used in the AI Learning Platform, including user registration, login, two-factor authentication (2FA), and admin approval processes.

## Overview

The platform implements a robust multi-layer authentication system that includes:

- Email and password-based registration and login
- Mandatory two-factor authentication (2FA) for regular users
- Optional 2FA for admin users to prevent lockouts
- Admin approval workflow for new user registrations
- Password security with hashing and validation
- Profile management and password reset functionality

## Components

### 1. User Model

**File: `app/models/user.py`**

The User model is the cornerstone of the authentication system:

```python
class User(UserMixin, db.Model):
    """User model with authentication fields and methods"""
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
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Verify a password against the stored hash"""
        return check_password_hash(self.password_hash, password)
        
    def get_totp_uri(self):
        """Generate TOTP URI for QR code generation"""
        return f'otpauth://totp/AILearningPlatform:{self.email}?secret={self.otp_secret}&issuer=AILearningPlatform'
        
    def verify_totp(self, token):
        """Verify a TOTP token against the user's secret"""
        totp = pyotp.TOTP(self.otp_secret)
        return totp.verify(token)
```

Key authentication-related fields include:
- `password_hash`: Securely stored password (using Werkzeug's `generate_password_hash`)
- `is_admin`: Flag for admin privileges
- `is_approved`: Flag indicating admin approval status
- `otp_secret`: Secret key for TOTP-based 2FA
- `is_2fa_enabled`: Flag indicating whether 2FA is enabled

### 2. Authentication Forms

**File: `app/forms.py`**

Forms handle validation of user input during authentication processes:

```python
class LoginForm(FlaskForm):
    """Form for user login"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    """Form for user registration"""
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=3, max=64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must start with a letter and can only contain letters, numbers, dots or underscores')
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long'),
        Regexp('(?=.*\d)(?=.*[a-z])(?=.*[A-Z])', message='Password must include at least one uppercase letter, one lowercase letter, and one number')
    ])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class TwoFactorForm(FlaskForm):
    """Form for 2FA token verification"""
    token = StringField('Authentication Code', validators=[
        DataRequired(),
        Length(min=6, max=6, message='Authentication code must be 6 digits'),
        Regexp('^\d{6}$', message='Authentication code must be 6 digits')
    ])
    submit = SubmitField('Verify')

class SetupTwoFactorForm(FlaskForm):
    """Form for setting up 2FA"""
    token = StringField('Authentication Code', validators=[
        DataRequired(),
        Length(min=6, max=6, message='Authentication code must be 6 digits'),
        Regexp('^\d{6}$', message='Authentication code must be 6 digits')
    ])
    submit = SubmitField('Enable 2FA')
```

These forms implement robust validation:
- Email format validation
- Password complexity requirements
- Username format checking
- 2FA token validation

### 3. Authentication Routes

**File: `app/auth/routes.py`**

The authentication process is handled by several routes:

```python
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login process"""
    # Check if user is already authenticated
    # Validate login form
    # Verify password
    # Check if user is approved
    # Redirect to 2FA if enabled
    
@auth_bp.route('/two-factor', methods=['GET', 'POST'])
def two_factor_auth():
    """Handle 2FA verification"""
    # Validate 2FA form
    # Verify token
    # Complete login process
    
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    # Validate registration form
    # Create new user
    # Generate 2FA secret
    # Redirect to 2FA setup
    
@auth_bp.route('/setup-2fa', methods=['GET', 'POST'])
@login_required
def setup_2fa():
    """Setup 2FA for existing users"""
    # Generate QR code
    # Validate setup form
    # Enable 2FA for user
    
@auth_bp.route('/disable-2fa', methods=['GET', 'POST'])
@login_required
@admin_required
def disable_2fa():
    """Disable 2FA (admin only)"""
    # Validate admin status
    # Disable 2FA for specified user
```

### 4. Login Manager Configuration

**File: `app/__init__.py`**

Flask-Login is configured to manage user sessions:

```python
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))
```

## Authentication Workflows

### Registration Process

1. **User submits registration form**:
   - Username, email, and password are validated
   - Password is hashed for security
   - New user is created in the database with `is_approved = False`
   - Random OTP secret is generated for 2FA

2. **2FA Setup**:
   - QR code is generated from OTP secret
   - User scans QR code with an authenticator app
   - User verifies setup by entering a valid token
   - User account is marked with `is_2fa_enabled = True`

3. **Admin Approval**:
   - Admin logs in and views pending users
   - Admin approves or rejects the registration
   - If approved, user's `is_approved` flag is set to `True`
   - User receives notification of approval status

4. **First Login**:
   - User enters email and password
   - System verifies approval status
   - User is prompted for 2FA token
   - On successful verification, user gains access

### Login Process

1. **Email and Password Verification**:
   - User enters email and password
   - System validates credentials
   - System checks approval status

2. **2FA Verification** (for enabled users):
   - User is redirected to 2FA page
   - User enters the 6-digit token from authenticator app
   - System verifies token against secret using TOTP algorithm
   - On success, user is logged in and redirected

3. **Session Management**:
   - User session is created
   - "Remember Me" functionality maintains session across browser close
   - Session information includes login timestamp

### Password Security

Passwords are securely managed using:
- Password complexity requirements (uppercase, lowercase, digit)
- Secure password hashing (Werkzeug's `generate_password_hash`)
- No plain text storage of passwords anywhere
- Robust password verification

### 2FA Implementation

2FA is implemented using TOTP (Time-based One-Time Password) algorithm:
- Each user has a unique secret key
- Secret is used to generate a QR code for authenticator apps
- Tokens are time-based and valid for 30 seconds
- Verification includes a validation window for time drift

### Admin Tools

Special administrative tools are available for account management:
- Reset 2FA for users who lose access to their devices
- Approve or reject new user registrations
- Create admin accounts through command-line scripts
- Disable 2FA for admin accounts to prevent lockouts

## Security Considerations

### Protection Against Common Attacks

The authentication system protects against:
- Password brute force attacks (through complexity requirements)
- CSRF attacks (using Flask-WTF's protection)
- Session hijacking (secure session configuration)
- Man-in-the-middle attacks (using HTTPS in production)

### Secure Configuration

For production deployment:
- HTTPS is mandatory
- Session cookies are secure
- Sensitive routes require fresh login
- Database connection is encrypted

### Emergency Access

For emergency situations where an admin might be locked out:
- Special command-line scripts can reset admin 2FA
- Documentation includes recovery procedures
- Backup admin accounts are recommended

## Technical Implementation Details

### QR Code Generation

QR codes for 2FA setup are generated using:
```python
import qrcode
from io import BytesIO
import base64

def generate_qr_code(uri):
    """Generate a QR code as a base64 encoded image"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered)
    return base64.b64encode(buffered.getvalue()).decode()
```

### TOTP Verification

TOTP verification is implemented using the PyOTP library:
```python
import pyotp

def verify_totp(secret, token):
    """Verify a TOTP token against a secret"""
    totp = pyotp.TOTP(secret)
    return totp.verify(token)
```

### Secret Generation

Secure random secrets are generated for TOTP:
```python
def generate_totp_secret():
    """Generate a secure random TOTP secret"""
    return pyotp.random_base32()
```