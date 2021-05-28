from flask import Flask, render_template, redirect, flash, url_for, request

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from werkzeug.urls import url_parse

from src.create_db import UserData, SurveyManager


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign in')


# default template_folder path is 'templates' in root directory; recommended to specify a custom path
app = Flask(__name__, template_folder='app/templates')
app.config.from_pyfile('config/flaskconfig.py')
sm = SurveyManager(app)

# login setup
login = LoginManager(app)
login.login_view = 'login'


# what's with id???
@login.user_loader
def user_loader(id):
    return sm.session.query(UserData).get(int(id))


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Qiana'}
    posts = [0, 0, 0]
    return render_template('index.html', user=user, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        # edge case not implemented: non-unique usernames
        user = sm.session.query(UserData).filter_by(name=form.username.data,
                                                    password=form.password.data).first()
        if user is None:
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
            return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))









