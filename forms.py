from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, DateTimeField,
                     IntegerField)
from wtforms.validators import (DataRequired, Regexp, ValidationError,
                                Length, equal_to)
from datetime import datetime

from models import User


def name_exists(form, field):
    if User.select().where(User.user_name == field.data).exists():
        raise ValidationError('User with that name already exists.')


class RegisterForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message=('Username should be one word, letters,'
                         'numbers, and underscores only.')
            ),
            name_exists
        ])
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=2),
            equal_to('password2', message='Passwords must match')
        ])
    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired()])


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class EntryForm(FlaskForm):
    title = StringField('Title:')

    date = DateTimeField("Date (format: YYYY-MM-DD):",
                         format='%Y-%m-%d')

    time_spent = StringField('Time spent studying in hours:')

    learned = StringField('What did you learn?')

    resources = StringField('What did you user as a resource?')

    tags = StringField('Enter tags (comma separated eg. tag1, tag2, tag3): ',
                       validators=[DataRequired()])
