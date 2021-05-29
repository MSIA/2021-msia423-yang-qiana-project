from flask import Flask, render_template, redirect, flash, url_for, request
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from werkzeug.urls import url_parse

from src.create_db import UserData, SurveyManager
from src.forms import Registration as Registration
from src.forms import LoginForm as LoginForm
from wtforms.validators import ValidationError

from pandas import pd


# default template_folder path is 'templates' in root directory; recommended to specify a custom path
app = Flask(__name__, template_folder='app/templates')
app.config.from_pyfile('config/flaskconfig.py')
sm = SurveyManager(app=app)
login = LoginManager(app)
login.login_view = 'login'


class RegistrationForm(Registration):

    def validate_username(self, username):
        user = sm.session.query(UserData).filter_by(name=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
        if len(username.data) > 50:
            raise ValidationError('Username cannot be longer than 50 characters.')

    def validate_password(self, password):
        if len(password.data) > 32:
            raise ValidationError('Password cannot be longer than 32 characters.')

# what's with id???
@login.user_loader
def user_loader(id):
    return sm.session.query(UserData).get(int(id))


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Qiana'}
    return render_template('index.html', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
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


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # organize survey data into np.array
        # put all file paths in config
        raw_data = {key: values for key, values in form.__dict__.items() if key.startswith(r'[A-Z]')}
        raw_df = pd.DataFrame(raw_data, orient='columns')
        # NEED TO CHANGE!!!
        sm.add_user_record(fa_path=None, ca_path=None, username=form.username.data,
                           password=form.password.data, survey=raw_df, age=None, gender=None, country=None)
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)









