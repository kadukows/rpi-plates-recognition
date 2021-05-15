from typing import Optional
from functools import wraps

from dataclasses import dataclass
from flask import Flask, make_response, flash, url_for
from flask_login import LoginManager, current_user
from werkzeug.security import check_password_hash
from werkzeug.utils import redirect

from .db import db
from .models import User


login_manager = LoginManager()  # auth for cookie-based webapp


def init_app(app: Flask):
    # login manager configuration
    login_manager.init_app(app)

    @login_manager.user_loader
    def laod_user(id):
        return User.query.get(int(id))

    # endpoint to 'Login' page, same value that is passed to 'url_for' function
    login_manager.login_view = 'auth.login'


def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.is_admin():
            return f(*args, **kwargs)
        else:
            flash("you need to be an admin to view this page")
            return redirect(url_for('index.index'))

    return wrap
