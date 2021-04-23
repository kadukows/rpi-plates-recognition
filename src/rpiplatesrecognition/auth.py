from typing import Optional
from functools import wraps

from dataclasses import dataclass
from flask import Flask, make_response, flash, url_for
from flask_httpauth import HTTPBasicAuth
from flask_login import LoginManager, current_user
from werkzeug.security import check_password_hash
from werkzeug.utils import redirect

from .db import db
from .models import User

rest_auth = HTTPBasicAuth()  # auth for rest api
login_manager = LoginManager()  # auth for cookie-based webapp

class PasswordVerifier:
    def __call__(self, username: str, password: str) -> Optional[User]:
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            return user

        return None

def init_app(app: Flask):
    # rest auth configuration
    password_verifier = PasswordVerifier()
    rest_auth.verify_password(password_verifier)

    @rest_auth.error_handler
    def unauthorized():
        return make_response({'error': 'Unauthorized access'}, 401)


    # login manager configuration
    login_manager.init_app(app)

    @login_manager.user_loader
    def laod_user(id):
        return User.query.get(int(id))

    # endpoint to 'Login' page, same value that is passed to 'url_for' function
    login_manager.login_view = 'login'

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.role == 'Admin':
            return f(*args, **kwargs)
        else:
            flash("you need to be an admin to view this page")
            return redirect(url_for('index'))

    return wrap
