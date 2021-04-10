from flask import Flask, render_template, session, flash, url_for, redirect
from flask.globals import request
from flask_login import current_user, login_user
from flask_login.utils import login_required, logout_user
from werkzeug.urls import url_parse

from .db import db
from .forms import LoginForm, RegistrationForm
from .models import User

def init_app(app: Flask):
    @app.route('/')
    @app.route('/index')
    def index():
        if 'user' in session:
            return render_template('index.html', user=session['user'])
        else:
            return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))

        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password')
                return redirect(url_for('login'))

            login_user(user)

            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')

            return redirect(url_for('index'))

        return render_template('login.html', form=form)

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
            user = User(username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash(f'You, {user.username}, are now registered!')
            return redirect(url_for('login'))

        return render_template('register.html', form=form)
