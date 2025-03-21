from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, SelectMultipleField, HiddenField, IntegerField, widgets
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Regexp
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
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
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
            
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
            
class TwoFactorForm(FlaskForm):
    token = StringField('Authentication Code', validators=[
        DataRequired(),
        Length(min=6, max=6, message='Authentication code must be 6 digits'),
        Regexp('^\d{6}$', message='Authentication code must be 6 digits')
    ])
    submit = SubmitField('Verify')

class SetupTwoFactorForm(FlaskForm):
    token = StringField('Authentication Code', validators=[
        DataRequired(),
        Length(min=6, max=6, message='Authentication code must be 6 digits'),
        Regexp('^\d{6}$', message='Authentication code must be 6 digits')
    ])
    submit = SubmitField('Enable 2FA')

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class InterestSelectionForm(FlaskForm):
    interests = MultiCheckboxField('Interests', coerce=int)
    submit = SubmitField('Save Interests')

class UserApprovalForm(FlaskForm):
    action = HiddenField(validators=[DataRequired()])
    user_id = HiddenField(validators=[DataRequired()])
    submit = SubmitField('Submit')

class CourseForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    cover_image_url = StringField('Cover Image URL', validators=[Length(max=500)])
    interests = MultiCheckboxField('Interests', coerce=int)
    submit = SubmitField('Save Course')

class LessonForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    order = IntegerField('Order', default=0)
    submit = SubmitField('Save Lesson')

class InterestForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    submit = SubmitField('Save Interest')

class UserInterestAccessForm(FlaskForm):
    user_id = HiddenField(validators=[DataRequired()])
    interest_id = HiddenField(validators=[DataRequired()])
    action = HiddenField(validators=[DataRequired()])
    submit = SubmitField('Update Access')

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=3, max=64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must start with a letter and can only contain letters, numbers, dots or underscores')
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    current_password = PasswordField('Current Password')
    new_password = PasswordField('New Password', validators=[
        Regexp('(?=.*\d)(?=.*[a-z])(?=.*[A-Z])', 0, 'Password must include at least one uppercase letter, one lowercase letter, and one number')
    ])
    new_password2 = PasswordField('Confirm New Password', validators=[
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Update Profile')
