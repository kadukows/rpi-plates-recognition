from .db import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(120), index=True, unique=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Module(db.Model):
    __tablename__ = 'modules'

    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(32), index=True, unique=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user = db.relationship('User', backref=db.backref('modules', lazy=True))

    def __repr__(self):
        return f'<Module {self.unique_id}>'

class ActiveModule(db.Model):
    __tablename__ = 'active_modules'

    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.String(64), unique=True, nullable=False)

    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    module = db.relationship('Module', backref=db.backref('active_module', lazy=True, uselist=False))

    def __repr__(self):
        return f'<ActiveModule {self.module.unique_id}>'
