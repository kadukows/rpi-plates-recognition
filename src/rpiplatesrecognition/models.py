from enum import unique
import click
from flask import current_app
from flask.cli import with_appcontext
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .db import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(120), index=True, unique=True)
    # workaround, right now possible Values: 'Admin' and 'User'
    role = db.Column(db.String(12), index=False, unique=False, default='User')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Module(db.Model):
    __tablename__ = 'modules'

    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(32), index=True, unique=True)
    is_active = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user = db.relationship('User', backref=db.backref('modules', lazy=True))

    def __repr__(self):
        return f'<Module {self.unique_id}>'
