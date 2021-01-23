from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, DateField,
                     IntegerField, TextAreaField)
from wtforms.validators import (DataRequired, Regexp, ValidationError,
                                Length, equal_to)


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

    tags = TextAreaField('Tags (comma separated, like this: tag1, tag2, tag3',
                         validators=[DataRequired()])

