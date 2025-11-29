"""Authentication forms"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User


class RegistrationForm(FlaskForm):
    """User registration form"""
    name = StringField('Name', validators=[
        DataRequired(),
        Length(min=1, max=100)
    ])
    email = EmailField('Email', validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=5, message='Password must be at least 8 characters')
    ])
    password_confirm = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')

    def validate_email(self, field):
        """Check if email is already registered"""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered. Please use a different email or login.')


class LoginForm(FlaskForm):
    """User login form"""
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')
