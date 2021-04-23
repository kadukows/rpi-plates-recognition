from enum import unique
import click
from flask import current_app
from flask.cli import with_appcontext
from flask_login import UserMixin
from sqlalchemy.orm import subqueryload
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


whitelist_to_module_assignment = db.Table("whitelist_to_module_assignment",
    db.Column('whitelist_id', db.Integer, db.ForeignKey('whitelists.id'), primary_key=True),
    db.Column('module_id', db.Integer, db.ForeignKey('modules.id'), primary_key=True)
)


class Module(db.Model):
    __tablename__ = 'modules'

    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(32), index=True, unique=True)
    is_active = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user = db.relationship('User', backref=db.backref('modules', lazy=True))

    whitelists = db.relationship('Whitelist', secondary=whitelist_to_module_assignment, lazy='subquery',
        backref=db.backref('modules', lazy=True))

    def __repr__(self):
        return f'<Module {self.unique_id}>'


whitelist_assignment = db.Table('whitelist_assignments',
    db.Column('whitelist_id', db.Integer, db.ForeignKey('whitelists.id'), primary_key=True),
    db.Column('plate_id', db.Integer, db.ForeignKey('plates.id'), primary_key=True)
)

class Whitelist(db.Model):
    __tablename__ = 'whitelists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('whitelists', lazy=True))

    plates = db.relationship('Plate', secondary=whitelist_assignment, lazy='subquery',
        backref=db.backref('whitelists', lazy=True))


class Plate(db.Model):
    __tablename__ = 'plates'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(10), unique=True, index=True, nullable=False)
