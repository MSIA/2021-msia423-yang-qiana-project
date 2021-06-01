from flask import Flask, render_template, redirect, flash, url_for, request
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from werkzeug.urls import url_parse
from wtforms.validators import ValidationError

from src.create_db import UserData, SurveyManager
from src.forms import Registration as Registration
from src.forms import LoginForm as LoginForm
from config.flaskconfig import MAX_ROWS_SHOW

import pandas as pd
import re
from sqlalchemy.sql import text
from base64 import b64encode

# default template_folder path is 'templates' in root directory if no template folder is specified
app = Flask(__name__, template_folder='app/templates', static_folder="app/static")
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


@login.user_loader
def user_loader(id):
    return sm.session.query(UserData).get(int(id))


@app.route('/')
@app.route('/index')
@login_required
def index():
    norm = current_user.factor1 ** 2 + \
           current_user.factor2 ** 2 + \
           current_user.factor3 ** 2 + \
           current_user.factor4 ** 2 + \
           current_user.factor5 ** 2 + \
           current_user.factor6 ** 2 + \
           current_user.factor7 ** 2 + \
           current_user.factor8 ** 2 + \
           current_user.factor9 ** 2 + \
           current_user.factor10 ** 2 + \
           current_user.factor11 ** 2 + \
           current_user.factor12 ** 2
    match = text(f'SELECT (factor1 * {current_user.factor1} + '
                 f'factor2 * {current_user.factor2} + '
                 f'factor3 * {current_user.factor3} + '
                 f'factor4 * {current_user.factor4} + '
                 f'factor5 * {current_user.factor5} + '
                 f'factor6 * {current_user.factor6} + '
                 f'factor7 * {current_user.factor7} + '
                 f'factor8 * {current_user.factor8} + '
                 f'factor9 * {current_user.factor9} + '
                 f'factor10 * {current_user.factor10} + '
                 f'factor11 * {current_user.factor11} + '
                 f'factor12 * {current_user.factor12}) /'
                 f'(SQRT(factor1 * factor1 + factor2 * factor2 + factor3 * factor3 + '
                 f'factor4 * factor4 + factor5 * factor5 + factor6 * factor6 + '
                 f'factor7 * factor7 + factor8 * factor8 + factor9 * factor9 + '
                 f'factor10 * factor10 + factor11 * factor11 + factor12 * factor12)'
                 f' * SQRT({norm})) AS cosine, name, age, image, '
                 f'CASE WHEN gender = 1 THEN "Male" WHEN gender = 2 THEN "Female" WHEN gender = 3 THEN "Non-binary" '
                 f'ELSE NULL END AS sex '
                 f'FROM user_data '
                 f'WHERE cluster = {current_user.cluster} AND id <> {current_user.id} '
                 f'ORDER BY cosine DESC '
                 f'LIMIT {MAX_ROWS_SHOW};')
    top_10 = sm.session.execute(match)
    photo = current_user.image
    return render_template('index.html', filestring=photo, top_10=top_10, title='Homepage')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        user = sm.session.query(UserData).filter_by(name=username,
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
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    file_string = None
    if form.validate_on_submit():
        # upload picture
        file = form.photo.data
        if file:
            file_string = b64encode(file.read()).decode('utf-8')
            app.logger.debug(f'file type: {type(file_string)}, file length: {len(file_string)}')
        # organize survey data into np.array
        raw_data = {field.label.field_id: [field.data] for field in form if re.match('^[A-Z]', field.label.field_id)}
        raw_data = {key: value if value != [None] else [0] for key, value in raw_data.items()}
        raw_df = pd.DataFrame.from_dict(raw_data, orient='columns')
        app.logger.debug(f'Raw_df created from user input: {raw_df}')
        # add new user record
        sm.add_user_record(username=form.username.data,
                           password=form.password.data,
                           survey=raw_df,
                           age=form.age.data,
                           gender=form.gender.data,
                           image=file_string)
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
