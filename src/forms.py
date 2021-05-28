from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField
from wtforms.validators import DataRequired, EqualTo, ValidationError

from src.create_db import UserData, SurveyManager
from app import app

sm = SurveyManager(app=app)


class RegistrationForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])

    args = {'choices': [(1, 'strongly disagree'), (2, 'disagree'), (3, 'neither disagree nor agree'),
                        (4, 'agree'), (5, 'strongly agree')],
            'coerce': int, 'validators': [DataRequired()]}
    A7 = RadioField(label='I know that I am not a special person.', id='A7', **args)

    submit = SubmitField('Register')

    def validate_username(self, username):
        user = sm.session.query(UserData).filter_by(name=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
        if len(username.data) > 50:
            raise ValidationError('Username cannot be longer than 50 characters.')

    def validate_password(self, password):
        if len(password.data) > 32:
            raise ValidationError('Password cannot be longer than 32 characters.')


# login setup
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign in')
