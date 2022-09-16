from flask_wtf import FlaskForm
from wtforms import StringField, EmailField
from wtforms.validators import DataRequired


class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
