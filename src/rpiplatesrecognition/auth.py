from dataclasses import dataclass
from flask import Flask, make_response
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash

from .db import db
from . import models

auth = HTTPBasicAuth()

'''
@dataclass
class User:
    """This is a hack for ORM-oriented flask_httpauth package"""

    id: int
    username: str
'''

class PasswordVerifier:
    def __init__(self, app: Flask):
        self.app = app

    def __call__(self, username: str, password: str) -> models.User:
        #with self.app.app_context():
            #record = db.execute('SELECT * FROM user_accounts WHERE username = ?', (username, )).fetchone()

        user = models.User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            return user

        return None

def init_app(app: Flask):
    password_verifier = PasswordVerifier(app)
    auth.verify_password(password_verifier)

    @auth.error_handler
    def unauthorized():
        return make_response({'error': 'Unauthorized access'}, 401)
