from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, DateField,
                     IntegerField, TextAreaField)
from wtforms.validators import (DataRequired, Regexp, ValidationError,
                                Length, equal_to)

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


class EntryForm(FlaskForm):
    title = StringField('Title:',
                        validators=[DataRequired()])

    date = DateField("Date (format: YYYY-MM-DD):",
                     format='%Y-%m-%d')

    time_spent = IntegerField('Time spent studying in hours:',
                              validators=[DataRequired()])

    learned = TextAreaField('What did you learn?',
                            validators=[DataRequired()])

    resources = TextAreaField('What did you user as a resource?',
                              validators=[DataRequired()])

    tags = TextAreaField('Tags (letters and numbers only, space separated, like this: tag1 tag2 tag3)',
                         validators=[DataRequired(),
                                     Regexp("^[a-zA-Z0-9_ ]+$",
                                     message="letters and numbers only, space separated!")]
                         )


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
