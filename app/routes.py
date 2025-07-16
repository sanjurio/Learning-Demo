from flask import render_template, flash, redirect, url_for, request, abort, session, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
import os
import io
from . import db
from .models import (User, Course, Lesson, Interest, UserInterest,
                    CourseInterest, UserCourse, ForumTopic, ForumReply,
                    UserLessonProgress, UserNote, UserBookmark, UserActivity)
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

        # Get stats for dashboard cards
        stats = {
            'pending_users_count': User.query.filter_by(is_approved=False, is_admin=False).count(),
            'users_count': User.query.filter_by(is_admin=False).count(),
            'courses_count': Course.query.count(),
            'interests_count': Interest.query.count()
        }

        return render_template('admin/approve_users.html',
                               title='Pending Users',
                               pending_users=pending_users,
                               form=form,
                               **stats)

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

        # Get stats for dashboard cards
        stats = {
            'pending_users_count': User.query.filter_by(is_approved=False, is_admin=False).count(),
            'users_count': User.query.filter_by(is_admin=False).count(),
            'courses_count': Course.query.count(),
            'interests_count': Interest.query.count()
        }

        return render_template('admin/content.html',
                               title='Manage Courses',
                               courses=courses,
                               **stats)

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

        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))

        # Get user's interests and available courses
        user_interests = get_user_interests_status(current_user.id)

        # Get courses based on user's approved interests
        approved_interest_ids = [ui['interest'].id for ui in user_interests if ui['access_granted']]

        available_courses = []
        if approved_interest_ids:
            # Get Fun interest ID
            fun_interest = Interest.query.filter_by(name='Fun').first()

            # Filter out Fun courses for BT users only
            if current_user.email_domain == 'bt.com' and fun_interest:
                approved_interest_ids = [id for id in approved_interest_ids if id != fun_interest.id]
            # THBS users can access Fun courses - no filtering needed

            if approved_interest_ids:
                available_courses = db.session.query(Course)\
                    .join(CourseInterest, Course.id == CourseInterest.course_id)\
                    .filter(CourseInterest.interest_id.in_(approved_interest_ids))\
                    .distinct()\
                    .all()

        # Get user's progress statistics
        progress_stats = current_user.get_progress_stats()

        # Get user's recent activities
        recent_activities = current_user.get_recent_activity()

        # Get user's bookmarked lessons
        bookmarked_lessons = current_user.get_bookmarked_lessons()

        # Get current lesson (in progress)
        current_lesson = current_user.get_current_lesson()

        # Get recommended courses
        recommended_courses = get_recommended_courses(current_user)

        return render_template('user/dashboard.html',
                               title='Dashboard',
                               courses=available_courses,
                               user_interests=user_interests,
                               progress_stats=progress_stats,
                               recent_activities=recent_activities,
                               bookmarked_lessons=bookmarked_lessons,
                               current_lesson=current_lesson,
                               recommended_courses=recommended_courses)

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

        # Get stats for dashboard cards
        stats = {
            'pending_users_count': User.query.filter_by(is_approved=False, is_admin=False).count(),
            'users_count': User.query.filter_by(is_admin=False).count(),
            'courses_count': Course.query.count(),
            'interests_count': Interest.query.count()
        }

        return render_template('admin/users.html',
                               title='Manage Users',
                               users=users,
                               **stats)

    @app.route('/admin/interests')
    @login_required
    def admin_interests():
        if not current_user.is_admin:
            flash('You do not have permission to access the admin area.', 'danger')
            return redirect(url_for('index'))

        interests = Interest.query.all()

        # Get stats for dashboard cards
        stats = {
            'pending_users_count': User.query.filter_by(is_approved=False, is_admin=False).count(),
            'users_count': User.query.filter_by(is_admin=False).count(),
            'courses_count': Course.query.count(),
            'interests_count': Interest.query.count()
        }

        return render_template('admin/interests.html',
                               title='Manage Interests',
                               interests=interests,
                               **stats)

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

    @app.route('/user/interests', methods=['GET', 'POST'])
    @login_required
    def user_interests():
        if not current_user.is_approved:
            flash('Your account is pending approval.', 'warning')
            return redirect(url_for('logout'))

        form = InterestSelectionForm()
        all_interests = Interest.query.all()

        # Filter out Fun interest for BT users only, THBS users can see it
        if current_user.email_domain == 'bt.com':
            all_interests = [i for i in all_interests if i.name != 'Fun']

        form.interests.choices = [(i.id, i.name) for i in all_interests]

        if form.validate_on_submit():
            # Handle form submission - create pending interest requests
            selected_interest_ids = form.interests.data

            # Remove any existing interest requests for this user
            UserInterest.query.filter_by(user_id=current_user.id).delete()

            # Create new interest requests
            for interest_id in selected_interest_ids:
                user_interest = UserInterest(
                    user_id=current_user.id,
                    interest_id=interest_id,
                    access_granted=False
                )
                db.session.add(user_interest)

            db.session.commit()
            flash('Your interest selections have been updated and are pending admin approval.', 'success')
            return redirect(url_for('user_interests'))

        # Pre-populate form with current selections
        user_interests_status = get_user_interests_status(current_user.id)
        current_selections = [ui['interest'].id for ui in user_interests_status if ui.get('selected', False)]
        form.interests.data = current_selections

        return render_template('user/interests.html',
                               title='My Interests',
                               form=form,
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

        # Get previous and next lessons for navigation
        prev_lesson = Lesson.query.filter(
            Lesson.course_id == lesson.course_id,
            Lesson.order < lesson.order
        ).order_by(Lesson.order.desc()).first()

        next_lesson = Lesson.query.filter(
            Lesson.course_id == lesson.course_id,
            Lesson.order > lesson.order
        ).order_by(Lesson.order.asc()).first()

        # Check if user can view content based on access level
        can_view_content = lesson.can_view_content(current_user)
        
        # Get user's lesson progress
        lesson_progress = UserLessonProgress.query.filter_by(
            user_id=current_user.id,
            lesson_id=lesson.id
        ).first()
        
        # Get user's notes for this lesson
        user_notes = UserNote.query.filter_by(
            user_id=current_user.id,
            lesson_id=lesson.id
        ).order_by(UserNote.created_at.desc()).all()

        return render_template('user/lesson.html',
                               title=lesson.title,
                               lesson=lesson,
                               course=lesson.course,
                               prev_lesson=prev_lesson,
                               next_lesson=next_lesson,
                               can_view_content=can_view_content,
                               lesson_progress=lesson_progress,
                               user_notes=user_notes)

    # Admin routes for managing interests
    @app.route('/admin/interests/add', methods=['GET', 'POST'])
    @login_required
    def admin_add_interest():
        if not current_user.is_admin:
            abort(403)

        form = InterestForm()
        if form.validate_on_submit():
            interest = Interest(
                name=form.name.data,
                description=form.description.data,
                created_by=current_user.id
            )
            db.session.add(interest)
            db.session.commit()
            flash('Interest created successfully!', 'success')
            return redirect(url_for('admin_interests'))

        return render_template('admin/edit_interest.html', title='Add Interest', form=form)

    @app.route('/admin/interests/<int:interest_id>/edit', methods=['GET', 'POST'])
    @login_required
    def admin_edit_interest(interest_id):
        if not current_user.is_admin:
            abort(403)

        interest = Interest.query.get_or_404(interest_id)
        form = InterestForm()

        if form.validate_on_submit():
            interest.name = form.name.data
            interest.description = form.description.data
            db.session.commit()
            flash('Interest updated successfully!', 'success')
            return redirect(url_for('admin_interests'))

        form.name.data = interest.name
        form.description.data = interest.description
        return render_template('admin/edit_interest.html', title='Edit Interest', form=form, interest=interest)

    @app.route('/admin/interests/<int:interest_id>/delete', methods=['POST'])
    @login_required
    def admin_delete_interest(interest_id):
        if not current_user.is_admin:
            abort(403)

        interest = Interest.query.get_or_404(interest_id)
        db.session.delete(interest)
        db.session.commit()
        flash('Interest deleted successfully!', 'success')
        return redirect(url_for('admin_interests'))

    @app.route('/admin/users/<int:user_id>/interests')
    @login_required
    def admin_user_interests(user_id):
        if not current_user.is_admin:
            abort(403)

        user = User.query.get_or_404(user_id)
        interests = Interest.query.all()
        user_interests_status = get_user_interests_status(user_id)

        return render_template('admin/user_interests.html',
                               title=f'Manage Interests for {user.username}',
                               user=user,
                               interests=interests,
                               user_interests=user_interests_status)

    @app.route('/admin/user-interest/update', methods=['POST'])
    @login_required
    def admin_update_user_interest():
        if not current_user.is_admin:
            abort(403)

        user_id = request.form.get('user_id')
        interest_id = request.form.get('interest_id')
        action = request.form.get('action')

        if user_id and interest_id and action:
            try:
                user_id = int(user_id)
                interest_id = int(interest_id)

                if action == 'grant':
                    if grant_interest_access(user_id, interest_id):
                        flash('Interest access granted successfully.', 'success')
                    else:
                        flash('Error granting interest access.', 'danger')
                elif action == 'revoke':
                    if revoke_interest_access(user_id, interest_id):
                        flash('Interest access revoked successfully.', 'success')
                    else:
                        flash('Error revoking interest access.', 'danger')
                else:
                    flash('Invalid action specified.', 'danger')
            except ValueError:
                flash('Invalid user or interest ID.', 'danger')
        else:
            flash('Missing required form data.', 'danger')

        return redirect(url_for('admin_user_interests', user_id=user_id))

    # Admin course management routes
    @app.route('/admin/courses/add', methods=['GET', 'POST'])
    @login_required
    def admin_add_course():
        if not current_user.is_admin:
            abort(403)

        form = CourseForm()
        interests = Interest.query.all()
        form.interests.choices = [(i.id, i.name) for i in interests]

        if form.validate_on_submit():
            course = Course(
                title=form.title.data,
                description=form.description.data,
                cover_image_url=form.cover_image_url.data,
                created_by=current_user.id
            )
            db.session.add(course)
            db.session.flush()  # Get the course ID

            # Add course-interest relationships
            for interest_id in form.interests.data:
                course_interest = CourseInterest(
                    course_id=course.id,
                    interest_id=interest_id,
                    created_by=current_user.id
                )
                db.session.add(course_interest)

            db.session.commit()
            flash('Course created successfully!', 'success')
            return redirect(url_for('admin_courses'))

        return render_template('admin/edit_course.html', title='Add Course', form=form)

    @app.route('/admin/courses/<int:course_id>/edit', methods=['GET', 'POST'])
    @login_required
    def admin_edit_course(course_id):
        if not current_user.is_admin:
            abort(403)

        course = Course.query.get_or_404(course_id)
        form = CourseForm()
        interests = Interest.query.all()
        form.interests.choices = [(i.id, i.name) for i in interests]

        if form.validate_on_submit():
            course.title = form.title.data
            course.description = form.description.data
            course.cover_image_url = form.cover_image_url.data

            # Update course-interest relationships
            CourseInterest.query.filter_by(course_id=course.id).delete()
            for interest_id in form.interests.data:
                course_interest = CourseInterest(
                    course_id=course.id,
                    interest_id=interest_id,
                    created_by=current_user.id
                )
                db.session.add(course_interest)

            db.session.commit()
            flash('Course updated successfully!', 'success')
            return redirect(url_for('admin_courses'))

        # Pre-populate form
        form.title.data = course.title
        form.description.data = course.description
        form.cover_image_url.data = course.cover_image_url

        # Set selected interests
        current_interests = [ci.interest_id for ci in CourseInterest.query.filter_by(course_id=course.id).all()]
        form.interests.data = current_interests

        return render_template('admin/edit_course.html', title='Edit Course', form=form, course=course)

    @app.route('/admin/courses/<int:course_id>/delete', methods=['POST'])
    @login_required
    def admin_delete_course(course_id):
        if not current_user.is_admin:
            abort(403)

        course = Course.query.get_or_404(course_id)
        db.session.delete(course)
        db.session.commit()
        flash('Course deleted successfully!', 'success')
        return redirect(url_for('admin_courses'))

    # Admin lesson management routes
    @app.route('/admin/courses/<int:course_id>/lessons')
    @login_required
    def admin_lessons(course_id):
        if not current_user.is_admin:
            abort(403)

        course = Course.query.get_or_404(course_id)
        lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order).all()

        return render_template('admin/lessons.html',
                               title=f'Manage Lessons for {course.title}',
                               course=course,
                               lessons=lessons)

    @app.route('/admin/courses/<int:course_id>/lessons/add', methods=['GET', 'POST'])
    @login_required
    def admin_add_lesson(course_id):
        if not current_user.is_admin:
            abort(403)

        course = Course.query.get_or_404(course_id)
        form = LessonForm()

        if form.validate_on_submit():
            lesson = Lesson(
                title=form.title.data,
                content=form.content.data,
                content_type=form.content_type.data,
                video_url=form.video_url.data,
                order=form.order.data,
                course_id=course_id,
                created_by=current_user.id
            )
            db.session.add(lesson)
            db.session.commit()
            flash('Lesson created successfully!', 'success')
            return redirect(url_for('admin_lessons', course_id=course_id))

        return render_template('admin/edit_lesson.html', title='Add Lesson', form=form, course=course)

    @app.route('/admin/lessons/<int:lesson_id>/edit', methods=['GET', 'POST'])
    @login_required
    def admin_edit_lesson(lesson_id):
        if not current_user.is_admin:
            abort(403)

        lesson = Lesson.query.get_or_404(lesson_id)
        form = LessonForm()

        if form.validate_on_submit():
            lesson.title = form.title.data
            lesson.content = form.content.data
            lesson.content_type = form.content_type.data
            lesson.video_url = form.video_url.data
            lesson.order = form.order.data
            db.session.commit()
            flash('Lesson updated successfully!', 'success')
            return redirect(url_for('admin_lessons', course_id=lesson.course_id))

        # Pre-populate form
        form.title.data = lesson.title
        form.content.data = lesson.content
        form.content_type.data = lesson.content_type
        form.video_url.data = lesson.video_url
        form.order.data = lesson.order

        return render_template('admin/edit_lesson.html', title='Edit Lesson', form=form, lesson=lesson, course=lesson.course)

    @app.route('/admin/lessons/<int:lesson_id>/delete', methods=['POST'])
    @login_required
    def admin_delete_lesson(lesson_id):
        if not current_user.is_admin:
            abort(403)

        lesson = Lesson.query.get_or_404(lesson_id)
        course_id = lesson.course_id
        db.session.delete(lesson)
        db.session.commit()
        flash('Lesson deleted successfully!', 'success')
        return redirect(url_for('admin_lessons', course_id=course_id))

    # Forum routes
    @app.route('/forum/new', methods=['GET', 'POST'])
    @login_required
    def forum_new_topic():
        form = ForumTopicForm()

        if form.validate_on_submit():
            topic = ForumTopic(
                title=form.title.data,
                content=form.content.data,
                course_id=form.course_id.data if form.course_id.data else None,
                user_id=current_user.id
            )
            db.session.add(topic)
            db.session.commit()
            flash('Topic created successfully!', 'success')

            if topic.course_id:
                return redirect(url_for('course_forum', course_id=topic.course_id))
            else:
                return redirect(url_for('forum_index'))

        return render_template('forum/new_topic.html', title='New Topic', form=form)

    @app.route('/forum/topic/<int:topic_id>')
    @login_required
    def forum_topic(topic_id):
        topic = ForumTopic.query.get_or_404(topic_id)
        replies = ForumReply.query.filter_by(topic_id=topic_id).order_by(ForumReply.created_at).all()
        form = ForumReplyForm()

        return render_template('forum/topic.html',
                               title=topic.title,
                               topic=topic,
                               replies=replies,
                               form=form)

    @app.route('/forum/topic/<int:topic_id>/reply', methods=['POST'])
    @login_required
    def forum_reply(topic_id):
        topic = ForumTopic.query.get_or_404(topic_id)
        form = ForumReplyForm()

        if form.validate_on_submit():
            reply = ForumReply(
                content=form.content.data,
                topic_id=topic_id,
                user_id=current_user.id
            )
            db.session.add(reply)
            db.session.commit()
            flash('Reply posted successfully!', 'success')

        return redirect(url_for('forum_topic', topic_id=topic_id))

    @app.route('/courses/<int:course_id>/forum')
    @login_required
    def course_forum(course_id):
        course = Course.query.get_or_404(course_id)

        if not user_can_access_course(current_user, course):
            flash('You do not have access to this course forum.', 'danger')
            return redirect(url_for('user_dashboard'))

        topics = ForumTopic.query.filter_by(course_id=course_id).order_by(ForumTopic.created_at.desc()).all()

        return render_template('forum/course_forum.html',
                               title=f'{course.title} Forum',
                               course=course,
                               topics=topics)

    # Admin interest requests management
    @app.route('/admin/interest-requests')
    @login_required
    def admin_user_interest_requests():
        if not current_user.is_admin:
            abort(403)

        # Get all user interests that are not yet granted access
        pending_requests = db.session.query(UserInterest, User, Interest).join(
            User, UserInterest.user_id == User.id
        ).join(
            Interest, UserInterest.interest_id == Interest.id
        ).filter(UserInterest.access_granted == False).all()

        # Convert to a list of objects with user and interest attributes
        pending_list = []
        for ui, user, interest in pending_requests:
            pending_list.append({
                'user': user,
                'interest': interest,
                'user_interest': ui
            })

        # Get stats for dashboard cards
        stats = {
            'pending_users_count': User.query.filter_by(is_approved=False, is_admin=False).count(),
            'users_count': User.query.filter_by(is_admin=False).count(),
            'courses_count': Course.query.count(),
            'interests_count': Interest.query.count()
        }

        return render_template('admin/user_interest_requests.html',
                               title='User Interest Requests',
                               pending_requests=pending_list,
                               **stats)

    @app.route('/admin/approve-interest-request', methods=['POST'])
    @login_required
    def admin_approve_interest_request():
        if not current_user.is_admin:
            abort(403)

        user_id = request.form.get('user_id')
        interest_id = request.form.get('interest_id')
        action = request.form.get('action')

        if user_id and interest_id and action:
            try:
                user_id = int(user_id)
                interest_id = int(interest_id)

                user_interest = UserInterest.query.filter_by(
                    user_id=user_id,
                    interest_id=interest_id
                ).first()

                if action == 'approve':
                    if user_interest:
                        user_interest.access_granted = True
                        user_interest.granted_at = datetime.utcnow()
                        user_interest.granted_by = current_user.id
                        db.session.commit()
                        flash('Interest access approved successfully.', 'success')
                    else:
                        flash('Interest request not found.', 'danger')
                elif action == 'reject':
                    if user_interest:
                        db.session.delete(user_interest)
                        db.session.commit()
                        flash('Interest request rejected and removed.', 'success')
                    else:
                        flash('Interest request not found.', 'danger')
                else:
                    flash('Invalid action specified.', 'danger')
            except ValueError:
                flash('Invalid user or interest ID.', 'danger')
        else:
            flash('Missing required form data.', 'danger')

        return redirect(url_for('admin_user_interest_requests'))

    @app.route('/admin/bulk-interest-requests', methods=['POST'])
    @login_required
    def admin_bulk_interest_requests():
        if not current_user.is_admin:
            abort(403)

        selected_requests = request.form.getlist('selected_requests')
        bulk_action = request.form.get('bulk_action')

        if selected_requests and bulk_action:
            success_count = 0
            error_count = 0

            for request_id in selected_requests:
                try:
                    # Handle individual interest request (format: user_id_interest_id)
                    parts = request_id.split('_')
                    if len(parts) == 2:
                        user_id, interest_id = int(parts[0]), int(parts[1])
                        user_interest = UserInterest.query.filter_by(
                            user_id=user_id,
                            interest_id=interest_id,
                            access_granted=False
                        ).first()

                        if user_interest:
                            if bulk_action == 'approve':
                                user_interest.access_granted = True
                                user_interest.granted_at = datetime.utcnow()
                                user_interest.granted_by = current_user.id
                                success_count += 1
                            elif bulk_action == 'reject':
                                db.session.delete(user_interest)
                                success_count += 1
                        else:
                            error_count += 1
                    else:
                        error_count += 1

                except (ValueError, AttributeError):
                    error_count += 1

            db.session.commit()

            if success_count > 0:
                action_word = 'approved' if bulk_action == 'approve' else 'rejected'
                flash(f'Successfully {action_word} {success_count} interest request(s).', 'success')
            if error_count > 0:
                flash(f'Failed to process {error_count} request(s).', 'warning')
        else:
            flash('No requests selected or invalid action.', 'warning')

        return redirect(url_for('admin_user_interest_requests'))
    
    # API endpoints for interactive learning features
    @app.route('/api/toggle_bookmark/<int:lesson_id>', methods=['POST'])
    @login_required
    def api_toggle_bookmark(lesson_id):
        lesson = Lesson.query.get_or_404(lesson_id)
        
        # Check if user has access to this lesson
        if not user_can_access_course(current_user, lesson.course):
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if bookmark exists
        bookmark = UserBookmark.query.filter_by(
            user_id=current_user.id,
            lesson_id=lesson_id
        ).first()
        
        if bookmark:
            # Remove bookmark
            db.session.delete(bookmark)
            is_bookmarked = False
            
            # Log activity
            activity = UserActivity(
                user_id=current_user.id,
                activity_type='bookmark_removed',
                lesson_id=lesson_id,
                course_id=lesson.course_id,
                activity_data='{"lesson_title": "' + lesson.title + '"}'
            )
            db.session.add(activity)
        else:
            # Add bookmark
            bookmark = UserBookmark(
                user_id=current_user.id,
                lesson_id=lesson_id
            )
            db.session.add(bookmark)
            is_bookmarked = True
            
            # Log activity
            activity = UserActivity(
                user_id=current_user.id,
                activity_type='bookmark_added',
                lesson_id=lesson_id,
                course_id=lesson.course_id,
                activity_data='{"lesson_title": "' + lesson.title + '"}'
            )
            db.session.add(activity)
        
        db.session.commit()
        return jsonify({'success': True, 'is_bookmarked': is_bookmarked})
    
    @app.route('/api/check_bookmark/<int:lesson_id>')
    @login_required
    def api_check_bookmark(lesson_id):
        lesson = Lesson.query.get_or_404(lesson_id)
        
        # Check if user has access to this lesson
        if not user_can_access_course(current_user, lesson.course):
            return jsonify({'error': 'Access denied'}), 403
        
        bookmark = UserBookmark.query.filter_by(
            user_id=current_user.id,
            lesson_id=lesson_id
        ).first()
        
        return jsonify({'is_bookmarked': bookmark is not None})
    
    @app.route('/api/mark_lesson_complete/<int:lesson_id>', methods=['POST'])
    @login_required
    def api_mark_lesson_complete(lesson_id):
        lesson = Lesson.query.get_or_404(lesson_id)
        
        # Check if user has access to this lesson
        if not user_can_access_course(current_user, lesson.course):
            return jsonify({'error': 'Access denied'}), 403
        
        # Get or create progress record
        progress = UserLessonProgress.query.filter_by(
            user_id=current_user.id,
            lesson_id=lesson_id
        ).first()
        
        if not progress:
            progress = UserLessonProgress(
                user_id=current_user.id,
                lesson_id=lesson_id,
                status='completed',
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow()
            )
            db.session.add(progress)
        else:
            progress.status = 'completed'
            progress.completed_at = datetime.utcnow()
        
        # Log activity
        activity = UserActivity(
            user_id=current_user.id,
            activity_type='lesson_completed',
            lesson_id=lesson_id,
            course_id=lesson.course_id,
            activity_data='{"lesson_title": "' + lesson.title + '"}'
        )
        db.session.add(activity)
        
        db.session.commit()
        return jsonify({'success': True, 'status': 'completed'})
    
    @app.route('/api/mark_lesson_progress/<int:lesson_id>', methods=['POST'])
    @login_required
    def api_mark_lesson_progress(lesson_id):
        lesson = Lesson.query.get_or_404(lesson_id)
        
        # Check if user has access to this lesson
        if not user_can_access_course(current_user, lesson.course):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        status = data.get('status', 'in_progress')
        
        # Get or create progress record
        progress = UserLessonProgress.query.filter_by(
            user_id=current_user.id,
            lesson_id=lesson_id
        ).first()
        
        if not progress:
            progress = UserLessonProgress(
                user_id=current_user.id,
                lesson_id=lesson_id,
                status=status,
                started_at=datetime.utcnow() if status == 'in_progress' else None,
                last_interaction=datetime.utcnow()
            )
            db.session.add(progress)
            
            # Log activity for first time starting
            if status == 'in_progress':
                activity = UserActivity(
                    user_id=current_user.id,
                    activity_type='lesson_started',
                    lesson_id=lesson_id,
                    course_id=lesson.course_id,
                    activity_data='{"lesson_title": "' + lesson.title + '"}'
                )
                db.session.add(activity)
        else:
            # Only update if not already completed
            if progress.status != 'completed':
                progress.status = status
                progress.last_interaction = datetime.utcnow()
                if status == 'in_progress' and not progress.started_at:
                    progress.started_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'success': True, 'status': progress.status})
    
    @app.route('/api/save_note/<int:lesson_id>', methods=['POST'])
    @login_required
    def api_save_note(lesson_id):
        lesson = Lesson.query.get_or_404(lesson_id)
        
        # Check if user has access to this lesson
        if not user_can_access_course(current_user, lesson.course):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        note_text = data.get('note_text', '').strip()
        
        if not note_text:
            return jsonify({'error': 'Note text cannot be empty'}), 400
        
        # Create note
        note = UserNote(
            user_id=current_user.id,
            lesson_id=lesson_id,
            note_text=note_text
        )
        db.session.add(note)
        
        # Log activity
        activity = UserActivity(
            user_id=current_user.id,
            activity_type='note_added',
            lesson_id=lesson_id,
            course_id=lesson.course_id,
            activity_data='{"lesson_title": "' + lesson.title + '"}'
        )
        db.session.add(activity)
        
        db.session.commit()
        return jsonify({'success': True, 'note_id': note.id})
    
    @app.route('/api/delete_note/<int:note_id>', methods=['DELETE'])
    @login_required
    def api_delete_note(note_id):
        note = UserNote.query.get_or_404(note_id)
        
        # Check if user owns this note
        if note.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        db.session.delete(note)
        db.session.commit()
        return jsonify({'success': True})