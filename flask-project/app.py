#!/usr/local/bin/python3

from flask import Flask, render_template, request, redirect
from flask_wtf import FlaskForm
from sqlalchemy.exc import IntegrityError
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from flask_login import current_user, login_user, login_required, logout_user
from models import db, login, UserModel

DB_USER = 'postgres'
DB_PASS = 'postgres'
DB_HOST = 'db'
DB_PORT = '5432'
DB_NAME = 'pguserregdemo'


class login_form(FlaskForm):
    username = StringField(label='Username',
                           validators=[DataRequired(),
                                       Length(min=3, max=25)])
    password = PasswordField(label='Password',
                             validators=[DataRequired(),
                                         Length(min=6, max=16)])
    submit = SubmitField(label='Login')

class registration_form(FlaskForm):
    username = StringField(label='Username',
                           validators=[DataRequired(),
                                       Length(min=3, max=25)])
    email = StringField(label='Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField(label='Password',
                             validators=[DataRequired(),
                                         Length(min=6, max=16)])
    register = SubmitField(label='Register')


app = Flask(__name__)

app.secret_key = 'a secret'
app.config['SQLALCHEMY_DATABASE_URI'] = \
     'postgresql+psycopg2://{user}:{passwd}@{host}:{port}/{db}'.format(
        user=DB_USER,
        passwd=DB_PASS,
        host=DB_HOST,
        port=DB_PORT,
        db=DB_NAME)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login.init_app(app)
login.login_view = 'login'


@app.before_first_request
def create_table():
    db.create_all()
    try:
        user = UserModel(username='some user name', email='test@nowhere.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        if e:
            pass
        return


@app.route('/')
def base_site():
    return redirect('/login')


@app.route('/authenticated')
@login_required
def authenticated():
    return render_template('authenticated.html',
                           user=current_user.username)


@app.route('/about')
def about():
    return render_template(
        'about.html',
        is_authenticated=current_user.is_authenticated
    )


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/authenticated')
    form = login_form()
    if form.validate_on_submit():
        if request.method == 'POST':
            username = request.form['username'].strip()
            password = request.form['password'].strip()
            user = UserModel.query.filter_by(username=username).first()
            if user is not None and user.check_password(password):
                login_user(user)
                print(f'this is the current user: {current_user}')
                return redirect('/authenticated')
            else:
                return render_template('login.html',
                                       has_error=True,
                                       form=form)
        else:
            return render_template('login.html', form=form)
    else:
        return render_template('login.html', form=form)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect('/authenticated')

    form = registration_form()
    if form.validate_on_submit():
        if request.method == 'POST':
            username = request.form['username'].strip()
            email = request.form['email'].strip()
            password = request.form['password'].strip()
            user = UserModel(username, email)
            try:
                user.create_user(password)
            except IntegrityError:
                return render_template('register.html',
                                       has_error=True,
                                       form=form)
            return redirect('/login')
        else:
            return render_template('register.html', form=form)
    else:
        return render_template('register.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
