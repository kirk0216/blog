from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, HiddenField
from wtforms.validators import DataRequired, EqualTo


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    redirect = HiddenField('Redirect')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField(
        'Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')]
    )


class ForgotPasswordForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Confirm Password',
                            validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    token = HiddenField('token', validators=[DataRequired()])


class EditProfileForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
