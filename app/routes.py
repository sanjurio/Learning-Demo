from flask import render_template, flash, redirect, url_for, request, abort, session, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
import os
import io
from . import db
from .models import (User, Course, Lesson, Interest, UserInterest,
                    CourseInterest, UserCourse, ForumTopic, ForumReply,
                    UserLessonProgress)
from .forms import (LoginForm, RegistrationForm, TwoFactorForm,
                   SetupTwoFactorForm, InterestSelectionForm, UserApprovalForm,
                   CourseForm, LessonForm, InterestForm,
                   UserInterestAccessForm, ProfileForm, ForumTopicForm,
                   ForumReplyForm)
from .utils.auth_helpers import generate_otp_secret, verify_totp, generate_qr_code
from .utils.course_helpers import get_user_accessible_courses, get_recommended_courses, user_can_access_course, get_user_interests_status
from .utils.admin_helpers import get_pending_users, approve_user, reject_user, grant_interest_access, revoke_interest_access, set_user_video_access
from .document_analysis import analyze_document
from datetime import datetime


def register_routes(app):
    """Register all routes with the Flask app"""
    
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_dashboard'))

        return render_template('index.html', title='Welcome to Erlang Systems LMS')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))

        if request.args.get('registration_complete'):
            flash('Registration successful! Your account is pending approval from an administrator.', 'success')
            session.pop('user_created', None)

        form = LoginForm()

        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()

            if user is None or not user.check_password(form.password.data):
                flash('Invalid email or password', 'danger')
                return render_template('auth/login.html', title='Sign In', form=form)

            if not user.is_approved:
                flash('Your account is pending approval from an administrator.', 'warning')
                return render_template('auth/login.html', title='Sign In', form=form)

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
                flash('Your account is missing 2FA configuration. Please contact an administrator.', 'danger')
                return render_template('auth/login.html', title='Sign In', form=form)

            # Store user info in session for 2FA verification
            session['user_id'] = user.id
            session['remember_me'] = form.remember_me.data
            return redirect(url_for('two_factor_auth'))

        return render_template('auth/login.html', title='Sign In', form=form)

    @app.route('/admin/users/pending')
    @login_required
    def admin_pending_users():
        if not current_user.is_admin:
            flash('You do not have permission to access the admin area.', 'danger')
            return redirect(url_for('index'))

        pending_users = get_pending_users()
        form = UserApprovalForm()

        return render_template('admin/approve_users.html',
                               title='Pending Users',
                               pending_users=pending_users,
                               form=form)

    @app.route('/admin/users/approve', methods=['POST'])
    @login_required
    def admin_approve_user():
        if not current_user.is_admin:
            abort(403)

        user_id = request.form.get('user_id')
        action = request.form.get('action')
        video_access = request.form.get('video_access')

        if user_id and action:
            try:
                user_id = int(user_id)
                if action == 'approve':
                    if approve_user(user_id, current_user.id):
                        # Set video access if specified
                        if video_access is not None:
                            set_user_video_access(user_id, video_access == 'on')
                        flash('User has been approved successfully.', 'success')
                    else:
                        flash('Error approving user. User may not exist.', 'danger')
                elif action == 'reject':
                    if reject_user(user_id):
                        flash('User has been rejected and removed.', 'success')
                    else:
                        flash('Error rejecting user. User may not exist.', 'danger')
                else:
                    flash('Invalid action specified.', 'danger')
            except ValueError:
                flash('Invalid user ID format.', 'danger')
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

    @app.route('/admin/dashboard')
    @login_required
    def admin_dashboard():
        if not current_user.is_admin:
            flash('You do not have permission to access the admin area.', 'danger')
            return redirect(url_for('index'))

        stats = {
            'total_users': User.query.count(),
            'pending_users': User.query.filter_by(is_approved=False, is_admin=False).count(),
            'total_courses': Course.query.count(),
            'total_lessons': Lesson.query.count(),
            'thbs_users': User.query.filter_by(email_domain='thbs.com').count(),
            'bt_users': User.query.filter_by(email_domain='bt.com').count()
        }

        return render_template('admin/dashboard.html', title='Admin Dashboard', stats=stats)

    @app.route('/user/dashboard')
    @login_required
    def user_dashboard():
        if not current_user.is_approved:
            flash('Your account is pending approval.', 'warning')
            return redirect(url_for('logout'))

        courses = get_user_accessible_courses(current_user)
        recommended = get_recommended_courses(current_user)

        return render_template('user/dashboard.html',
                               title='Dashboard',
                               courses=courses,
                               recommended=recommended)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))

    @app.route('/admin/users')
    @login_required
    def admin_users():
        if not current_user.is_admin:
            flash('You do not have permission to access the admin area.', 'danger')
            return redirect(url_for('index'))

        users = User.query.filter_by(is_admin=False).all()
        return render_template('admin/users.html',
                               title='Manage Users',
                               users=users)

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

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))

        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            user.set_access_based_on_domain()
            db.session.add(user)
            db.session.commit()
            
            # Set up 2FA
            user.otp_secret = generate_otp_secret()
            db.session.commit()
            
            flash('Registration successful! Your account is pending admin approval.', 'success')
            return redirect(url_for('login', registration_complete=1))

        return render_template('auth/register.html', title='Register', form=form)

    @app.route('/forum')
    def forum_index():
        topics = ForumTopic.query.filter_by(course_id=None).order_by(ForumTopic.created_at.desc()).all()
        return render_template('forum/index.html', title='General Forum', topics=topics)

    @app.route('/two-factor', methods=['GET', 'POST'])
    def two_factor_auth():
        if current_user.is_authenticated:
            return redirect(url_for('index'))

        user_id = session.get('user_id')
        if not user_id:
            flash('Session expired. Please log in again.', 'warning')
            return redirect(url_for('login'))

        user = User.query.get(user_id)
        if not user or not user.otp_secret:
            flash('Invalid session. Please log in again.', 'danger')
            return redirect(url_for('login'))

        form = TwoFactorForm()
        if form.validate_on_submit():
            if verify_totp(user.otp_secret, form.token.data):
                login_user(user, remember=session.get('remember_me', False))
                session.pop('user_id', None)
                session.pop('remember_me', None)
                flash('Login successful!', 'success')
                
                next_page = request.args.get('next')
                if not next_page or urlparse(next_page).netloc != '':
                    next_page = url_for('index')
                return redirect(next_page)
            else:
                flash('Invalid authentication code. Please try again.', 'danger')

        return render_template('auth/two_factor.html', title='Two-Factor Authentication', form=form)

    @app.route('/document-analysis', methods=['GET', 'POST'])
    @login_required
    def document_analysis():
        if request.method == 'POST':
            # Handle file upload
            if 'file' not in request.files:
                return jsonify({'error': 'No file uploaded'})
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'})
            
            try:
                result = analyze_document(file, file.filename)
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)})
        
        return render_template('document_analysis.html', title='Document Analysis')

    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        form = ProfileForm()
        if form.validate_on_submit():
            current_user.username = form.username.data
            current_user.email = form.email.data
            
            if form.new_password.data:
                if form.current_password.data and current_user.check_password(form.current_password.data):
                    current_user.set_password(form.new_password.data)
                    flash('Password updated successfully!', 'success')
                else:
                    flash('Current password is incorrect.', 'danger')
                    return render_template('user/profile.html', title='Profile', form=form)
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))
        
        # Pre-populate form with current user data
        form.username.data = current_user.username
        form.email.data = current_user.email
        
        return render_template('user/profile.html', title='Profile', form=form)

    @app.route('/user/interests')
    @login_required
    def user_interests():
        if not current_user.is_approved:
            flash('Your account is pending approval.', 'warning')
            return redirect(url_for('logout'))

        all_interests = Interest.query.all()
        user_interests_status = get_user_interests_status(current_user.id)
        
        return render_template('user/interests.html',
                               title='My Interests',
                               interests=all_interests,
                               user_interests=user_interests_status)

    @app.route('/courses/<int:course_id>')
    @login_required
    def view_course(course_id):
        course = Course.query.get_or_404(course_id)
        
        if not user_can_access_course(current_user, course):
            flash('You do not have access to this course.', 'danger')
            return redirect(url_for('user_dashboard'))
        
        lessons = Lesson.query.filter_by(course_id=course.id).order_by(Lesson.order).all()
        
        return render_template('user/course.html',
                               title=course.title,
                               course=course,
                               lessons=lessons)

    @app.route('/lessons/<int:lesson_id>')
    @login_required
    def view_lesson(lesson_id):
        lesson = Lesson.query.get_or_404(lesson_id)
        
        if not user_can_access_course(current_user, lesson.course):
            flash('You do not have access to this lesson.', 'danger')
            return redirect(url_for('user_dashboard'))
        
        return render_template('user/lesson.html',
                               title=lesson.title,
                               lesson=lesson)