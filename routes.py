from flask import render_template, flash, redirect, url_for, request, abort, session, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
import os
import io
from app import app, db
from models import (User, Course, Lesson, Interest, UserInterest,
                    CourseInterest, UserCourse, ForumTopic, ForumReply,
                    UserLessonProgress)
from forms import (LoginForm, RegistrationForm, TwoFactorForm,
                   SetupTwoFactorForm, InterestSelectionForm, UserApprovalForm,
                   CourseForm, LessonForm, InterestForm,
                   UserInterestAccessForm, ProfileForm, ForumTopicForm,
                   ForumReplyForm)
from utils import (generate_otp_secret, verify_totp, generate_qr_code,
                   get_user_accessible_courses, get_pending_users,
                   approve_user, reject_user, grant_interest_access,
                   revoke_interest_access, get_user_interests_status,
                   user_can_access_course, setup_initial_data,
                   get_recommended_courses)
from document_analysis import analyze_document
from datetime import datetime


# Initialize the database with some data when needed
def initialize_db():
    # This will be called from route functions, not at import time
    setup_initial_data()


@app.route('/')
def index():
    # Initialize the database with initial data if needed
    initialize_db()

    # If user is logged in, redirect to dashboard
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('user_dashboard'))

    return render_template('index.html',
                           title='Welcome to AI Learning Platform')


# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # Check if user just completed registration and show a message
    if request.args.get('registration_complete'):
        flash(
            'Registration successful! Your account is pending approval from an administrator.',
            'success')
        # Clear the user_created flag to allow new registrations
        session.pop('user_created', None)

    form = LoginForm()

    app.logger.info(f"Login attempt - Method: {request.method}")
    if request.method == 'POST':
        app.logger.info(f"Form data: {request.form}")
        app.logger.info(f"Form validation: {form.validate()}")
        if not form.validate():
            app.logger.info(f"Form errors: {form.errors}")

    if form.validate_on_submit():
        app.logger.info(f"Attempting login with email: {form.email.data}")
        user = User.query.filter_by(email=form.email.data).first()

        if user is None:
            app.logger.info(f"No user found with email: {form.email.data}")
            flash('Invalid email or password', 'danger')
            return render_template('auth/login.html',
                                   title='Sign In',
                                   form=form)

        app.logger.info(f"User found: {user.username}, checking password...")
        password_check = user.check_password(form.password.data)
        app.logger.info(f"Password check result: {password_check}")

        if not password_check:
            flash('Invalid email or password', 'danger')
            return render_template('auth/login.html',
                                   title='Sign In',
                                   form=form)

        if not user.is_approved:
            flash('Your account is pending approval from an administrator.',
                  'warning')
            return render_template('auth/login.html',
                                   title='Sign In',
                                   form=form)

        # Special case for admin: bypass 2FA
        if user.is_admin:
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('index')

            flash('Welcome, Administrator!', 'success')
            return redirect(next_page)

        # Check if user has 2FA configured
        if not user.otp_secret:
            flash(
                'Your account is missing 2FA configuration. Please contact an administrator.',
                'danger')
            return render_template('auth/login.html',
                                   title='Sign In',
                                   form=form)

        # Store user ID in session for the 2FA step (2FA is mandatory for non-admin users)
        session['user_id_for_2fa'] = user.id
        session['remember_me'] = form.remember_me.data
        return redirect(url_for('two_factor_auth'))

    return render_template('auth/login.html', title='Sign In', form=form)


@app.route('/two-factor', methods=['GET', 'POST'])
def two_factor_auth():
    app.logger.info("2FA authentication route accessed")

    if current_user.is_authenticated:
        app.logger.info("User already authenticated, redirecting")
        return redirect(url_for('index'))

    if 'user_id_for_2fa' not in session:
        app.logger.warning("2FA access without user_id_for_2fa in session")
        flash('Authentication error. Please log in again.', 'danger')
        return redirect(url_for('login'))

    user_id = session.get('user_id_for_2fa')
    app.logger.info(f"Processing 2FA for user_id: {user_id}")

    form = TwoFactorForm()

    if form.validate_on_submit():
        app.logger.info(f"2FA form submitted for user_id: {user_id}")
        user = User.query.get(user_id)

        if not user:
            app.logger.error(f"User not found for 2FA, user_id: {user_id}")
            session.pop('user_id_for_2fa', None)
            session.pop('remember_me', None)
            flash('Authentication error. User not found.', 'danger')
            return redirect(url_for('login'))

        token = form.token.data
        # Enhanced validation
        if not token or not token.isdigit() or len(token) != 6:
            app.logger.warning(f"Invalid token format: {token}")
            flash('Authentication code must be 6 digits.', 'danger')
            return render_template('auth/two_factor.html',
                                   title='Two-Factor Authentication',
                                   form=form)

        if verify_totp(user.otp_secret, token):
            app.logger.info(
                f"Successful 2FA verification for user: {user.username}")
            login_user(user, remember=session.get('remember_me', False))

            # Clear session data
            session.pop('user_id_for_2fa', None)
            session.pop('remember_me', None)

            # Redirect to appropriate page
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('user_dashboard')

            flash('Login successful!', 'success')
            return redirect(next_page)
        else:
            app.logger.warning(
                f"Invalid 2FA token provided for user: {user.username}")
            flash('Invalid authentication code. Please try again.', 'danger')

    return render_template('auth/two_factor.html',
                           title='Two-Factor Authentication',
                           form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    app.logger.info("Registration route accessed")
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # Clear all registration-related session data when starting a new registration
    if request.method == 'GET':
        app.logger.info(
            "Registration GET: Clearing all registration session data")
        for key in [
                'user_created', 'registration_data', 'registration_step',
                'otp_secret'
        ]:
            session.pop(key, None)

    # Handle initial user registration form
    form = RegistrationForm()

    # Step 1: Show registration form for initial GET request
    if request.method == 'GET':
        app.logger.info("Registration GET: Showing registration form")
        return render_template('auth/register.html',
                               title='Register',
                               form=form)

    # Step 2: Process form submission
    if request.method == 'POST' and 'registration_step' not in session:
        app.logger.info(
            "Registration POST: Processing initial form submission")

        # Log form data for debugging
        app.logger.info(f"Form data: {request.form}")
        app.logger.info(f"Form validation status: {form.validate_on_submit()}")

        if not form.validate_on_submit():
            app.logger.warning(
                f"Registration form validation failed: {form.errors}")
            return render_template('auth/register.html',
                                   title='Register',
                                   form=form)

        # Form is valid, proceed to 2FA setup
        otp_secret = generate_otp_secret()

        # Store registration data in session
        registration_data = {
            'username': form.username.data,
            'email': form.email.data,
            'password': form.password.data,
            'otp_secret': otp_secret
        }
        session['registration_data'] = registration_data
        session['registration_step'] = 'setup_2fa'

        app.logger.info(
            f"Registration: 2FA setup for {registration_data['username']}, redirecting"
        )

        # Redirect to 2FA setup page to avoid form resubmission issues
        return redirect(url_for('setup_2fa_register'))

    # If we reach here, it means there was a POST request but the registration_step is already in session
    # or another condition wasn't met correctly. Let's handle this case more gracefully.
    if request.method == 'POST':
        app.logger.info(
            "Registration POST: Form processing outside of normal flow")
        app.logger.info(f"Session keys: {list(session.keys())}")

        # If there's registration data and setup is in progress, redirect to 2FA setup
        if 'registration_data' in session and session.get(
                'registration_step') == 'setup_2fa':
            app.logger.info(
                "Registration in progress, redirecting to 2FA setup")
            return redirect(url_for('setup_2fa_register'))

        # Otherwise, clear any partial registration data and restart
        for key in ['registration_data', 'registration_step', 'user_created']:
            session.pop(key, None)

        flash('There was an issue with your registration. Please try again.',
              'warning')
        return render_template('auth/register.html',
                               title='Register',
                               form=form)


@app.route('/register/setup-2fa', methods=['GET', 'POST'])
def setup_2fa_register():
    """Dedicated route for 2FA setup during registration"""
    app.logger.info("2FA Registration setup route accessed")

    # Check if we already completed registration (prevent going back)
    if request.args.get('registration_complete'):
        flash(
            'Registration successful! Your account is pending approval from an administrator.',
            'success')
        return redirect(url_for('login'))

    # Check if this is direct access without proper registration flow
    if 'registration_step' not in session or session[
            'registration_step'] != 'setup_2fa':
        # Just redirect silently without warning message
        app.logger.info(
            "Redirecting to registration page - direct 2FA setup access")
        return redirect(url_for('register'))

    # Get registration data from session
    registration_data = session.get('registration_data', {})
    if not registration_data:
        app.logger.info(
            "No registration data in session, redirecting to registration page"
        )
        return redirect(url_for('register'))

    setup_form = SetupTwoFactorForm()

    # For GET requests, check username/email availability first, then show the QR code
    if request.method == 'GET':
        # Check if username or email already exists before proceeding
        username = registration_data.get('username')
        email = registration_data.get('email')

        existing_user = User.query.filter((User.username == username)
                                          | (User.email == email)).first()

        if existing_user:
            # Username or email already exists, clear session and redirect back to registration
            if existing_user.username == username:
                app.logger.warning(
                    f"Username {username} already exists during 2FA setup")
                flash(
                    'This username is already taken. Please try a different one.',
                    'danger')
            elif existing_user.email == email:
                app.logger.warning(
                    f"Email {email} already exists during 2FA setup")
                flash(
                    'This email is already registered. Please use a different email or try logging in.',
                    'danger')

            # Clear session data to let the user start fresh
            session.pop('registration_data', None)
            session.pop('registration_step', None)

            # Redirect back to the registration page to start again
            return redirect(url_for('register'))

        # If we get here, username and email are available, proceed with QR code
        qr_code = generate_qr_code(username,
                                   registration_data.get('otp_secret', ''))
        app.logger.info(f"Showing 2FA setup QR code for {username}")

        return render_template('auth/two_factor.html',
                               title='Setup Two-Factor Authentication',
                               form=setup_form,
                               qr_code=qr_code,
                               setup=True,
                               registration=True)

    # For POST requests, verify the token
    if request.method == 'POST':
        app.logger.info(f"2FA setup verification attempt: {request.form}")
        token = request.form.get('token')

        # Create QR code - needed in case we have to redisplay the form
        qr_code = generate_qr_code(registration_data.get('username', 'user'),
                                   registration_data.get('otp_secret', ''))

        if not token or len(token) != 6:
            app.logger.warning(f"Invalid token format: {token}")
            flash('Please enter a valid 6-digit authentication code.',
                  'danger')
        else:
            # Verify token
            otp_secret = registration_data.get('otp_secret')
            if verify_totp(otp_secret, token):
                app.logger.info("2FA verification successful - creating user")

                # Create the new user, but first check if it already exists
                try:
                    username = registration_data.get('username')
                    email = registration_data.get('email')

                    # Check if user already exists before creating
                    existing_user = User.query.filter(
                        (User.username == username)
                        | (User.email == email)).first()

                    if existing_user:
                        if existing_user.username == username:
                            app.logger.warning(
                                f"Username {username} already exists")
                            flash(
                                'This username is already taken. Please try a different one.',
                                'danger')
                        elif existing_user.email == email:
                            app.logger.warning(f"Email {email} already exists")
                            flash(
                                'This email is already registered. Please use a different email or try logging in.',
                                'danger')

                        # Clear session data to let the user start fresh with a new username
                        session.pop('registration_data', None)
                        session.pop('registration_step', None)

                        # Redirect back to the registration page to start again
                        return redirect(url_for('register'))

                    # User doesn't exist, proceed with creation
                    # But first, mark the session with a flag to prevent duplicate submissions
                    if session.get('user_created'):
                        app.logger.info(
                            "User creation already completed - redirecting to login"
                        )
                        return redirect(
                            url_for('login', registration_complete=1))

                    # Create new user
                    user = User(
                        username=username,
                        email=email,
                        is_approved=False,  # Will be set by domain check
                        otp_secret=otp_secret,
                        is_2fa_enabled=True  # 2FA is mandatory
                    )
                    user.set_password(registration_data.get('password'))
                    
                    # Set access level and approval based on email domain
                    user.set_access_based_on_domain()

                    # Save to database
                    db.session.add(user)
                    db.session.commit()
                    app.logger.info(
                        f"New user created: {user.username}, ID: {user.id}")

                    # Mark user as created in session to prevent duplicate submissions
                    session['user_created'] = True

                    # Use PRG pattern (Post-Redirect-Get) to avoid resubmission
                    flash(
                        'Registration successful! Your 2FA setup is complete. Your account is pending approval from an administrator.',
                        'success')

                    # Clear registration data but keep user_created flag
                    session.pop('registration_data', None)
                    session.pop('registration_step', None)

                    # Redirect to login page with a special parameter to avoid hitting the 2FA setup again
                    return redirect(url_for('login', registration_complete=1))

                except Exception as e:
                    app.logger.error(f"Error creating user: {str(e)}")
                    db.session.rollback()

                    # Clear session data on critical error to force restart
                    session.pop('registration_data', None)
                    session.pop('registration_step', None)

                    flash(
                        'An error occurred during account creation. Please try again with different information.',
                        'danger')
                    return redirect(url_for('register'))
            else:
                app.logger.warning("2FA token verification failed")
                flash('Invalid authentication code. Please try again.',
                      'danger')

        # If we get here, there was an error - regenerate QR code and show form again
        qr_code = generate_qr_code(registration_data.get('username', 'user'),
                                   registration_data.get('otp_secret', ''))
        return render_template('auth/two_factor.html',
                               title='Setup Two-Factor Authentication',
                               form=setup_form,
                               qr_code=qr_code,
                               setup=True,
                               registration=True)

    # Fallback - make sure to create a form object to avoid template errors
    form = RegistrationForm()
    return render_template('auth/register.html', title='Register', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/setup-2fa', methods=['GET', 'POST'])
@login_required
def setup_2fa():
    if current_user.is_2fa_enabled:
        flash('Two-factor authentication is already enabled for your account.',
              'info')
        return redirect(url_for('profile'))

    # Generate a new secret key
    if 'otp_secret' not in session:
        session['otp_secret'] = generate_otp_secret()

    form = SetupTwoFactorForm()
    qr_code = generate_qr_code(current_user.username, session['otp_secret'])

    if form.validate_on_submit():
        if verify_totp(session['otp_secret'], form.token.data):
            # Save the secret and enable 2FA
            current_user.otp_secret = session['otp_secret']
            current_user.is_2fa_enabled = True
            db.session.commit()

            # Clear the session
            session.pop('otp_secret', None)

            flash(
                'Two-factor authentication has been enabled for your account.',
                'success')
            return redirect(url_for('profile'))
        else:
            flash('Invalid authentication code. Please try again.', 'danger')

    return render_template('auth/two_factor.html',
                           title='Setup Two-Factor Authentication',
                           form=form,
                           qr_code=qr_code,
                           setup=True)


@app.route('/disable-2fa', methods=['POST'])
@login_required
def disable_2fa():
    # 2FA is mandatory - disabling is not allowed
    flash('Two-factor authentication is mandatory and cannot be disabled.',
          'warning')
    return redirect(url_for('profile'))


# User routes
@app.route('/dashboard')
@login_required
def user_dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))

    if not current_user.is_approved:
        flash('Your account is pending approval from an administrator.',
              'warning')
        return redirect(url_for('index'))

    # Get user's accessible courses
    courses = get_user_accessible_courses(current_user)

    # Get personalized course recommendations based on user interests
    recommended_courses = get_recommended_courses(current_user)
    
    # Create access level information for template
    access_info = {
        'level': current_user.access_level,
        'can_view_videos': current_user.can_view_videos(),
        'can_view_text': current_user.can_view_text(),
        'domain': current_user.email_domain
    }

    return render_template('user/dashboard.html',
                           title='Dashboard',
                           courses=courses,
                           recommended_courses=recommended_courses,
                           access_info=access_info)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()

    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    if form.validate_on_submit():
        # Check if the current password is provided and correct
        if form.current_password.data:
            if not current_user.check_password(form.current_password.data):
                flash('Current password is incorrect.', 'danger')
                return render_template('user/profile.html',
                                       title='Profile',
                                       form=form)

            # Update password if new password is provided
            if form.new_password.data:
                current_user.set_password(form.new_password.data)
                flash('Your password has been updated.', 'success')

        # Update username if it changed and is not already taken
        if form.username.data != current_user.username:
            if User.query.filter_by(username=form.username.data).first():
                flash('Username already exists.', 'danger')
                return render_template('user/profile.html',
                                       title='Profile',
                                       form=form)

            current_user.username = form.username.data

        # Update email if it changed and is not already taken
        if form.email.data != current_user.email:
            if User.query.filter_by(email=form.email.data).first():
                flash('Email already exists.', 'danger')
                return render_template('user/profile.html',
                                       title='Profile',
                                       form=form)

            current_user.email = form.email.data

        db.session.commit()
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('profile'))

    return render_template('user/profile.html', title='Profile', form=form)


@app.route('/course/<int:course_id>')
@login_required
def view_course(course_id):
    course = Course.query.get_or_404(course_id)

    # Check if user has access to this course
    if not user_can_access_course(current_user, course):
        flash("You don't have access to this course.", 'danger')
        return redirect(url_for('user_dashboard'))

    lessons = Lesson.query.filter_by(course_id=course.id).order_by(
        Lesson.order).all()
    return render_template('user/course.html',
                           title=course.title,
                           course=course,
                           lessons=lessons)


@app.route('/lesson/<int:lesson_id>')
@login_required
def view_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    course = Course.query.get(lesson.course_id)

    # Check if user has access to this course
    if not user_can_access_course(current_user, course):
        flash("You don't have access to this lesson.", 'danger')
        return redirect(url_for('user_dashboard'))

    # Check what content the user can view based on their access level
    content_access = lesson.can_view_content(current_user)
    
    # Get next and previous lessons
    next_lesson = Lesson.query.filter(Lesson.course_id == course.id,
                                      Lesson.order > lesson.order).order_by(
                                          Lesson.order).first()

    prev_lesson = Lesson.query.filter(Lesson.course_id == course.id,
                                      Lesson.order < lesson.order).order_by(
                                          Lesson.order.desc()).first()

    # Create access level information for template
    access_info = {
        'level': current_user.access_level,
        'can_view_videos': current_user.can_view_videos(),
        'can_view_text': current_user.can_view_text(),
        'domain': current_user.email_domain
    }

    return render_template('user/lesson.html',
                           title=lesson.title,
                           lesson=lesson,
                           course=course,
                           next_lesson=next_lesson,
                           prev_lesson=prev_lesson,
                           content_access=content_access,
                           access_info=access_info)


@app.route('/interests', methods=['GET', 'POST'])
@login_required
def user_interests():
    form = InterestSelectionForm()

    # Get all available interests for the form
    interests = Interest.query.all()
    form.interests.choices = [(i.id, i.name) for i in interests]

    # Get current user interests
    user_interests = UserInterest.query.filter_by(
        user_id=current_user.id).all()
    selected_interests = [ui.interest_id for ui in user_interests]

    if request.method == 'GET':
        form.interests.data = selected_interests

    if form.validate_on_submit():
        # Remove interests that were unselected
        for ui in user_interests:
            if ui.interest_id not in form.interests.data:
                db.session.delete(ui)

        # Add new interests
        for interest_id in form.interests.data:
            if interest_id not in selected_interests:
                user_interest = UserInterest(
                    user_id=current_user.id,
                    interest_id=interest_id,
                    access_granted=False  # New interests require admin approval
                )
                db.session.add(user_interest)

        db.session.commit()
        flash('Your interests have been updated.', 'success')
        return redirect(url_for('user_interests'))

    # Get interest status including access granted
    interest_status = get_user_interests_status(current_user.id)

    return render_template('user/interests.html',
                           title='My Interests',
                           form=form,
                           interest_status=interest_status)


# Admin routes
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('You do not have permission to access the admin area.', 'danger')
        return redirect(url_for('index'))

    pending_users_count = User.query.filter_by(is_approved=False).count()
    courses_count = Course.query.count()
    users_count = User.query.filter_by(is_approved=True).count()
    interests_count = Interest.query.count()

    return render_template('admin/dashboard.html',
                           title='Admin Dashboard',
                           pending_users_count=pending_users_count,
                           courses_count=courses_count,
                           users_count=users_count,
                           interests_count=interests_count)


@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('You do not have permission to access the admin area.', 'danger')
        return redirect(url_for('index'))

    users = User.query.filter_by(is_approved=True).all()
    return render_template('admin/users.html',
                           title='Manage Users',
                           users=users)


@app.route('/admin/users/pending')
@login_required
def admin_pending_users():
    if not current_user.is_admin:
        flash('You do not have permission to access the admin area.', 'danger')
        return redirect(url_for('index'))

    pending_users = get_pending_users()
    # Since we're using direct form inputs, we don't need to pass a form object
    # But we'll keep it to maintain compatibility with the template
    form = UserApprovalForm()

    app.logger.info(
        f"Pending users: {len(pending_users) if pending_users else 0}")

    return render_template('admin/approve_users.html',
                           title='Pending Users',
                           pending_users=pending_users,
                           form=form)


@app.route('/admin/users/approve', methods=['POST'])
@login_required
def admin_approve_user():
    if not current_user.is_admin:
        abort(403)

    app.logger.info(f"Admin approve user form data: {request.form}")

    # Get data directly from form submission
    user_id = request.form.get('user_id')
    action = request.form.get('action')

    app.logger.info(f"Processing user_id: {user_id}, action: {action}")

    if user_id and action:
        try:
            user_id = int(user_id)
            if action == 'approve':
                if approve_user(user_id, current_user.id):
                    flash('User has been approved successfully.', 'success')
                else:
                    flash('Error approving user. User may not exist.',
                          'danger')
            elif action == 'reject':
                if reject_user(user_id):
                    flash('User has been rejected and removed.', 'success')
                else:
                    flash('Error rejecting user. User may not exist.',
                          'danger')
            else:
                flash('Invalid action specified.', 'danger')
        except ValueError:
            flash('Invalid user ID format.', 'danger')
            app.logger.error(f"Invalid user ID format: {user_id}")
    else:
        flash('Missing required form data. Please try again.', 'danger')

    return redirect(url_for('admin_pending_users'))


@app.route('/admin/courses')
@login_required
def admin_courses():
    if not current_user.is_admin:
        flash('You do not have permission to access the admin area.', 'danger')
        return redirect(url_for('index'))

    courses = Course.query.all()
    return render_template('admin/content.html',
                           title='Manage Courses',
                           courses=courses)


@app.route('/admin/courses/add', methods=['GET', 'POST'])
@login_required
def admin_add_course():
    if not current_user.is_admin:
        abort(403)

    form = CourseForm()

    # Get all available interests for the form
    interests = Interest.query.all()
    form.interests.choices = [(i.id, i.name) for i in interests]

    if form.validate_on_submit():
        course = Course(title=form.title.data,
                        description=form.description.data,
                        cover_image_url=form.cover_image_url.data,
                        created_by=current_user.id)
        db.session.add(course)
        db.session.flush()  # Get the course ID

        # Add course-interest relationships
        for interest_id in form.interests.data:
            course_interest = CourseInterest(course_id=course.id,
                                             interest_id=interest_id,
                                             created_by=current_user.id)
            db.session.add(course_interest)

        db.session.commit()
        flash('Course has been added.', 'success')
        return redirect(url_for('admin_courses'))

    return render_template('admin/edit_course.html',
                           title='Add Course',
                           form=form,
                           course=None)


@app.route('/admin/courses/edit/<int:course_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_course(course_id):
    if not current_user.is_admin:
        abort(403)

    course = Course.query.get_or_404(course_id)
    form = CourseForm()

    # Get all available interests for the form
    interests = Interest.query.all()
    form.interests.choices = [(i.id, i.name) for i in interests]

    # Get current course interests
    course_interests = CourseInterest.query.filter_by(
        course_id=course.id).all()
    selected_interests = [ci.interest_id for ci in course_interests]

    if request.method == 'GET':
        form.title.data = course.title
        form.description.data = course.description
        form.cover_image_url.data = course.cover_image_url
        form.interests.data = selected_interests

    if form.validate_on_submit():
        course.title = form.title.data
        course.description = form.description.data
        course.cover_image_url = form.cover_image_url.data
        course.updated_at = datetime.utcnow()

        # Update course interests
        # Remove interests that were unselected
        for ci in course_interests:
            if ci.interest_id not in form.interests.data:
                db.session.delete(ci)

        # Add new interests
        for interest_id in form.interests.data:
            if interest_id not in selected_interests:
                course_interest = CourseInterest(course_id=course.id,
                                                 interest_id=interest_id,
                                                 created_by=current_user.id)
                db.session.add(course_interest)

        db.session.commit()
        flash('Course has been updated.', 'success')
        return redirect(url_for('admin_courses'))

    return render_template('admin/edit_course.html',
                           title='Edit Course',
                           form=form,
                           course=course)


@app.route('/admin/courses/delete/<int:course_id>', methods=['POST'])
@login_required
def admin_delete_course(course_id):
    if not current_user.is_admin:
        abort(403)

    course = Course.query.get_or_404(course_id)

    # Delete all lessons, course interests, and user courses
    Lesson.query.filter_by(course_id=course.id).delete()
    CourseInterest.query.filter_by(course_id=course.id).delete()
    UserCourse.query.filter_by(course_id=course.id).delete()

    db.session.delete(course)
    db.session.commit()

    flash('Course has been deleted.', 'success')
    return redirect(url_for('admin_courses'))


@app.route('/admin/lessons/<int:course_id>')
@login_required
def admin_lessons(course_id):
    if not current_user.is_admin:
        abort(403)

    course = Course.query.get_or_404(course_id)
    lessons = Lesson.query.filter_by(course_id=course.id).order_by(
        Lesson.order).all()

    return render_template('admin/lessons.html',
                           title='Manage Lessons',
                           course=course,
                           lessons=lessons)


@app.route('/admin/lessons/add/<int:course_id>', methods=['GET', 'POST'])
@login_required
def admin_add_lesson(course_id):
    if not current_user.is_admin:
        abort(403)

    course = Course.query.get_or_404(course_id)
    form = LessonForm()

    if form.validate_on_submit():
        lesson = Lesson(title=form.title.data,
                        content=form.content.data,
                        course_id=course.id,
                        order=form.order.data)
        db.session.add(lesson)
        db.session.commit()

        flash('Lesson has been added.', 'success')
        return redirect(url_for('admin_lessons', course_id=course.id))

    return render_template('admin/edit_lesson.html',
                           title='Add Lesson',
                           form=form,
                           course=course,
                           lesson=None)


@app.route('/admin/lessons/edit/<int:lesson_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_lesson(lesson_id):
    if not current_user.is_admin:
        abort(403)

    lesson = Lesson.query.get_or_404(lesson_id)
    course = Course.query.get_or_404(lesson.course_id)
    form = LessonForm()

    if request.method == 'GET':
        form.title.data = lesson.title
        form.content.data = lesson.content
        form.order.data = lesson.order

    if form.validate_on_submit():
        lesson.title = form.title.data
        lesson.content = form.content.data
        lesson.order = form.order.data
        lesson.updated_at = datetime.utcnow()

        db.session.commit()
        flash('Lesson has been updated.', 'success')
        return redirect(url_for('admin_lessons', course_id=course.id))

    return render_template('admin/edit_lesson.html',
                           title='Edit Lesson',
                           form=form,
                           course=course,
                           lesson=lesson)


@app.route('/admin/lessons/delete/<int:lesson_id>', methods=['POST'])
@login_required
def admin_delete_lesson(lesson_id):
    if not current_user.is_admin:
        abort(403)

    lesson = Lesson.query.get_or_404(lesson_id)
    course_id = lesson.course_id

    db.session.delete(lesson)
    db.session.commit()

    flash('Lesson has been deleted.', 'success')
    return redirect(url_for('admin_lessons', course_id=course_id))


@app.route('/admin/interests')
@login_required
def admin_interests():
    if not current_user.is_admin:
        flash('You do not have permission to access the admin area.', 'danger')
        return redirect(url_for('index'))

    interests = Interest.query.all()
    return render_template('admin/interests.html',
                           title='Manage Interests',
                           interests=interests)


@app.route('/admin/interests/add', methods=['GET', 'POST'])
@login_required
def admin_add_interest():
    if not current_user.is_admin:
        abort(403)

    form = InterestForm()

    if form.validate_on_submit():
        interest = Interest(name=form.name.data,
                            description=form.description.data,
                            created_by=current_user.id)
        db.session.add(interest)
        db.session.commit()

        flash('Interest has been added.', 'success')
        return redirect(url_for('admin_interests'))

    return render_template('admin/edit_interest.html',
                           title='Add Interest',
                           form=form,
                           interest=None)


@app.route('/admin/interests/edit/<int:interest_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_interest(interest_id):
    if not current_user.is_admin:
        abort(403)

    interest = Interest.query.get_or_404(interest_id)
    form = InterestForm()

    if request.method == 'GET':
        form.name.data = interest.name
        form.description.data = interest.description

    if form.validate_on_submit():
        interest.name = form.name.data
        interest.description = form.description.data

        db.session.commit()
        flash('Interest has been updated.', 'success')
        return redirect(url_for('admin_interests'))

    return render_template('admin/edit_interest.html',
                           title='Edit Interest',
                           form=form,
                           interest=interest)


@app.route('/admin/interests/delete/<int:interest_id>', methods=['POST'])
@login_required
def admin_delete_interest(interest_id):
    if not current_user.is_admin:
        abort(403)

    interest = Interest.query.get_or_404(interest_id)

    # Delete all user interests and course interests
    UserInterest.query.filter_by(interest_id=interest.id).delete()
    CourseInterest.query.filter_by(interest_id=interest.id).delete()

    db.session.delete(interest)
    db.session.commit()

    flash('Interest has been deleted.', 'success')
    return redirect(url_for('admin_interests'))


@app.route('/admin/user-interests/<int:user_id>')
@login_required
def admin_user_interests(user_id):
    if not current_user.is_admin:
        abort(403)

    user = User.query.get_or_404(user_id)
    interest_status = get_user_interests_status(user.id)
    form = UserInterestAccessForm()

    return render_template('admin/user_interests.html',
                           title=f'Manage Access for {user.username}',
                           user=user,
                           interest_status=interest_status,
                           form=form)


@app.route('/admin/user-interests/update', methods=['POST'])
@login_required
def admin_update_user_interest():
    if not current_user.is_admin:
        abort(403)

    form = UserInterestAccessForm()

    if form.validate_on_submit():
        user_id = int(form.user_id.data)
        interest_id = int(form.interest_id.data)
        action = form.action.data

        if action == 'grant':
            if grant_interest_access(user_id, interest_id, current_user.id):
                flash('Access has been granted.', 'success')
            else:
                flash('Error granting access.', 'danger')
        elif action == 'revoke':
            if revoke_interest_access(user_id, interest_id):
                flash('Access has been revoked.', 'success')
            else:
                flash('Error revoking access.', 'danger')

    return redirect(url_for('admin_user_interests', user_id=form.user_id.data))


# Forum routes
@app.route('/forum')
@login_required
def forum_index():
    if not current_user.is_approved:
        flash('Your account is pending approval from an administrator.',
              'warning')
        return redirect(url_for('index'))

    # Get all general forum topics (where course_id is None)
    topics = ForumTopic.query.filter_by(course_id=None).order_by(
        ForumTopic.pinned.desc(), ForumTopic.updated_at.desc()).all()

    form = ForumTopicForm()
    return render_template('forum/index.html',
                           title='General Forum',
                           topics=topics,
                           form=form,
                           is_general=True)


@app.route('/forum/topic/<int:topic_id>', methods=['GET', 'POST'])
@login_required
def forum_topic(topic_id):
    if not current_user.is_approved:
        flash('Your account is pending approval from an administrator.',
              'warning')
        return redirect(url_for('index'))

    topic = ForumTopic.query.get_or_404(topic_id)

    # If course-specific topic, check if user has access to the course
    if topic.course_id and not (current_user.is_admin
                                or user_can_access_course(
                                    current_user, topic.course)):
        flash('You do not have access to this forum topic.', 'danger')
        return redirect(url_for('forum_index'))

    replies = ForumReply.query.filter_by(topic_id=topic_id).order_by(
        ForumReply.created_at.asc()).all()

    # Handle actions like pin/unpin/delete
    if request.method == 'POST' and request.form.get('action'):
        action = request.form.get('action')

        # Handle topic actions
        if 'topic_id' in request.form:
            # Toggle pin status (admin only)
            if action == 'toggle_pin' and current_user.is_admin:
                topic.pinned = not topic.pinned
                db.session.commit()
                flash(
                    'Topic has been ' +
                    ('pinned' if topic.pinned else 'unpinned'), 'success')
                return redirect(url_for('forum_topic', topic_id=topic_id))

            # Delete topic (owner or admin only)
            elif action == 'delete' and (current_user.id == topic.user_id
                                         or current_user.is_admin):
                # Redirect appropriately based on whether it's a course topic or general topic
                redirect_url = url_for('forum_index')
                if topic.course_id:
                    redirect_url = url_for('course_forum',
                                           course_id=topic.course_id)

                db.session.delete(topic)
                db.session.commit()
                flash('Topic has been deleted', 'success')
                return redirect(redirect_url)

        # Handle reply actions
        elif 'reply_id' in request.form:
            reply_id = request.form.get('reply_id')
            reply = ForumReply.query.get_or_404(reply_id)

            # Delete reply (owner or admin only)
            if action == 'delete_reply' and (current_user.id == reply.user_id
                                             or current_user.is_admin):
                db.session.delete(reply)
                db.session.commit()
                flash('Reply has been deleted', 'success')
                return redirect(url_for('forum_topic', topic_id=topic_id))

    # Handle new reply submission
    form = ForumReplyForm()
    if form.validate_on_submit():
        reply = ForumReply(content=form.content.data,
                           user_id=current_user.id,
                           topic_id=topic_id)
        db.session.add(reply)
        # Update the topic's updated_at timestamp
        topic.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Your reply has been posted.', 'success')
        return redirect(url_for('forum_topic', topic_id=topic_id))

    return render_template('forum/topic.html',
                           title=topic.title,
                           topic=topic,
                           replies=replies,
                           form=form)


@app.route('/forum/new', methods=['GET', 'POST'])
@login_required
def forum_new_topic():
    if not current_user.is_approved:
        flash('Your account is pending approval from an administrator.',
              'warning')
        return redirect(url_for('index'))

    form = ForumTopicForm()

    # If coming from a course page, pre-fill the course ID
    course_id = request.args.get('course_id', None)
    if course_id:
        course = Course.query.get_or_404(int(course_id))
        if not (current_user.is_admin
                or user_can_access_course(current_user, course)):
            flash(
                'You do not have access to create topics in this course forum.',
                'danger')
            return redirect(url_for('forum_index'))

    if form.validate_on_submit():
        topic = ForumTopic(title=form.title.data,
                           content=form.content.data,
                           user_id=current_user.id)

        if form.course_id.data:
            # Ensure the user has access to the course
            course_id = int(form.course_id.data)
            course = Course.query.get(course_id)
            if course and (current_user.is_admin
                           or user_can_access_course(current_user, course)):
                topic.course_id = course_id
            else:
                flash(
                    'You do not have access to create topics in this course forum.',
                    'danger')
                return redirect(url_for('forum_index'))

        db.session.add(topic)
        db.session.commit()
        flash('Your topic has been created.', 'success')

        if topic.course_id:
            return redirect(url_for('course_forum', course_id=topic.course_id))
        else:
            return redirect(url_for('forum_index'))

    return render_template('forum/new_topic.html',
                           title='New Forum Topic',
                           form=form,
                           course_id=course_id)


@app.route('/course/<int:course_id>/forum')
@login_required
def course_forum(course_id):
    if not current_user.is_approved:
        flash('Your account is pending approval from an administrator.',
              'warning')
        return redirect(url_for('index'))

    course = Course.query.get_or_404(course_id)

    # Check if the user has access to this course
    if not (current_user.is_admin
            or user_can_access_course(current_user, course)):
        flash('You do not have access to this course forum.', 'danger')
        return redirect(url_for('forum_index'))

    topics = ForumTopic.query.filter_by(course_id=course_id).order_by(
        ForumTopic.pinned.desc(), ForumTopic.updated_at.desc()).all()

    form = ForumTopicForm()
    form.course_id.data = course_id

    return render_template('forum/course_forum.html',
                           title=f'{course.title} - Forum',
                           course=course,
                           topics=topics,
                           form=form)


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html', title='Not Found'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html', title='Server Error'), 500


# Document Analysis Chatbot routes
@app.route('/document-analysis', methods=['GET'])
@login_required
def document_analysis():
    """Render the document analysis page"""
    app.logger.info("Loading document analysis page")
    return render_template('document_analysis.html',
                         title='Document Analysis')


# Add a simple API endpoint to check if OpenAI API key is configured


# Add a diagnostic route for testing OpenAI API connectivity
# Document analysis routes



@app.route('/api/analyze-document', methods=['POST'])
@login_required
def api_analyze_document():
    """API endpoint to analyze an uploaded document"""
    try:
        app.logger.info("Document analysis API called")

        if 'file' not in request.files:
            app.logger.warning("No file uploaded in request")
            return jsonify({
                'success': False,
                'message': 'No file uploaded'
            }), 400

        file = request.files['file']

        if file.filename == '':
            app.logger.warning("Empty filename in uploaded file")
            return jsonify({
                'success': False,
                'message': 'No file selected'
            }), 400

        # Check if the file is one of the allowed types
        allowed_extensions = {'pdf', 'docx', 'txt'}
        if not ('.' in file.filename and file.filename.rsplit(
                '.', 1)[1].lower() in allowed_extensions):
            app.logger.warning(f"Invalid file format: {file.filename}")
            return jsonify({
                'success':
                False,
                'message':
                'Invalid file format. Please upload a PDF, DOCX, or TXT file.'
            }), 400

        # Read file into memory
        file_bytes = io.BytesIO(file.read())
        app.logger.info(f"Analyzing document: {file.filename}")

        # Analyze the document
        result = analyze_document(file_bytes, file.filename)
        app.logger.info(
            f"Analysis result success: {result.get('success', False)}")
        app.logger.debug(f"Full analysis result: {result}")

        return jsonify(result)
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        app.logger.error(f"Error in document analysis endpoint: {str(e)}")
        app.logger.error(f"Traceback: {error_traceback}")
        return jsonify({
            'success':
            False,
            'message':
            f'An error occurred during document analysis: {str(e)}'
        }), 500
