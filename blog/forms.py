#!/usr/bin/python3
""" A module to create forms that accept User input and validate
then notify the user if input is valid or invalid.

"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from blog.models import User

class RegistrationForm(FlaskForm):
    # A class which inherited from FlaskForm for registration form
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email Address',
                        validators=[DataRequired(), Email()])
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    accept = BooleanField('I accept the Terms of Service and Privacy Notice', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    # Set Restriction => unique email, username
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose another')

    def validate_email(self, email):
            email = User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError('That email is taken. Please choose another')


class LoginForm(FlaskForm):
    # A class which inherited from FlaskForm for login form
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ResetForm(FlaskForm):
    # A class which inherited from FlaskForm for Reset form
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Reset')


class ForgotForm(FlaskForm):
    # A class which inherited from FlaskForm for Forget form
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

    def validate_email(self, email):
            email = User.query.filter_by(email=email.data).first()
            if email is None:
                raise ValidationError('There is no account with that email. You must register first.')


class UpdateAccountForm(FlaskForm):
    # A class which inherited from FlaskForm for registration form
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email Address',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update profile picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    # Set Restriction => unique email, username
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose another')

    def validate_email(self, email):
            if email.data != current_user.email:
                email = User.query.filter_by(email=email.data).first()
                if email:
                    raise ValidationError('That email is taken. Please choose another')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    categories = SelectField("Categories", choices=[('category', 'Select categories'),
                                                    ('Languages', 'Languages and Frameworks'),
                                                            ('Mobile', 'Mobile App Development'),
                                                            ('Web', 'Web Development'),
                                                            ('Database', 'Database'),
                                                            ('Algorithms', 'Algorithms and Data Structures'),
                                                            ('DevOps', 'DevOps and Tools'),
                                                            ('ML', 'Machine Learning and AI'),
                                                            ('SWE', 'Software Engineering'),
                                                            ('CNS', 'Cybersecurity'),
                                                            ('OS', 'Operating Systems')],
                                                            validators=[DataRequired()])
    
    read_time = StringField('Reading time', validators=[DataRequired()])
    picture = FileField('Insert an image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    submit = SubmitField('Post')


class SearchForm(FlaskForm):
    # A class which inherited from FlaskForm for search form
    search = StringField('Search',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')