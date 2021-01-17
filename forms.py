from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import (DataRequired, Regexp, ValidationError,
                                Length, equal_to)
from peewee import *

from models import User


def name_exists(form, field):
    if User.select().where(User.user_name == field.data).exists():
        raise ValidationError('User with that name already exists.')


class RegisterForm(Form):
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


class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class EntryForm(Form):
    title = StringField('Title:',
                        validators=[DataRequired()])

    date = DateTimeField("Date (format: YYYY-MM-DD):")

    time_spent = TextField('Time spent studying in hours:')

    learned = TextField('What did you learn?'
                        )
    resources = TextField('What did you user as a resource?')

    tags = StringField('Enter tags (comma separated eg. tag1, tag2, tag3): ',
                       validators=[DataRequired(),
                                   Regexp('^[a-z]+(,[a-z]+)*$',
                                          message='Like this: tag1, tag2, tag3')
                                   ])
