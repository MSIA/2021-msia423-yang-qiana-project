from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField
from wtforms.validators import DataRequired, EqualTo


class Registration(FlaskForm):

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])

    args = {'choices': [(1, 'strongly disagree'), (2, 'disagree'), (3, 'neither disagree nor agree'),
                        (4, 'agree'), (5, 'strongly agree')],
            'coerce': int, 'validators': [DataRequired()]}
    A7 = RadioField(label='I take time out for others.', id='A7', **args)
    B11 = RadioField(label='I know that I am not a special person.', id='B11', **args)
    D5 = RadioField(label='I take control of things.', id='D5', **args)
    P9 = RadioField(label='I try to forgive and forget.', id='P9', **args)
    G10 = RadioField(label='I keep in the background.', id='G10', **args)
    N10 = RadioField(label="I can't do without the company of others.", id='N10', **args)
    I8 = RadioField(label='I trust others.', id='I8', **args)
    C5 = RadioField(label='I am not easily frustrated.', id='C5', **args)
    A5 = RadioField(label='I cheer people up.', id='A5', **args)
    G7 = RadioField(label='I often feel uncomfortable around others.', id='G7', **args)
    C1 = RadioField(label='I seldom feel blue.', id='C1', **args)
    C8 = RadioField(label='I dislike myself.', id='C8', **args)
    D1 = RadioField(label='I take charge.', id='D1', **args)
    D9 = RadioField(label='I let others make the decisions.', id='D9', **args)
    M1 = RadioField(label='I believe in the importance of art.', id='M1', **args)
    J2 = RadioField(label='I like to get lost in thought.', id='J2', **args)
    D7 = RadioField(label='I wait for others to lead the way.', id='D7', **args)
    K10 = RadioField(label='I am willing to talk about myself.', id='K10', **args)
    G6 = RadioField(label='I find it difficult to approach others.', id='G6', **args)
    N7 = RadioField(label='I enjoy my privacy.', id='N7', **args)
    J5 = RadioField(label='I swim against the current.', id='J5', **args)
    L6 = RadioField(label='I feel guilty when I say "no."', id='L6', **args)
    K2 = RadioField(label='I am hard to get to know.', id='K2', **args)
    K3 = RadioField(label="I don't talk a lot.", id='K3', **args)
    F3 = RadioField(label="I believe in one true religion.", id='F3', **args)
    P8 = RadioField(label='I am not easily annoyed.', id='P8', **args)
    L7 = RadioField(label='I feel crushed by setbacks.', id='L7', **args)
    L1 = RadioField(label='I am afraid that I will do the wrong thing.', id='L1', **args)
    E4 = RadioField(label='I enjoy being part of a loud crowd.', id='E4', **args)
    B8 = RadioField(label='I weigh the pros against the cons.', id='B8', **args)
    J7 = RadioField(label='I do unexpected things.', id='J7', **args)
    P2 = RadioField(label='I get angry easily.', id='P2', **args)
    G9 = RadioField(label='I am quiet around strangers.', id='G9', **args)
    N7 = RadioField(label="I don't mind eating alone.", id='N5', **args)
    A6 = RadioField(label='I make people feel at ease.', id='A6', **args)
    B4 = RadioField(label='I use my brain.', id='B4', **args)
    P10 = RadioField(label='I have a good word for everyone.', id='P10', **args)
    C9 = RadioField(label='I feel desperate.', id='C9', **args)
    D2 = RadioField(label='I want to be in charge.', id='D2', **args)

    submit = SubmitField('Register')


# login setup
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign in')
