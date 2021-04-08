from dataclasses import dataclass
from flask import Flask, make_response
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash

from .db import get_db

auth = HTTPBasicAuth()

@dataclass
class User:
    """This is a hack for ORM-oriented flask_httpauth package"""

    id: int
    username: str

class PasswordVerifier:
    def __init__(self, app: Flask):
        self.app = app

    def __call__(self, username: str, password: str):
        with self.app.app_context():
            db = get_db()
            record = db.execute('SELECT * FROM user_accounts WHERE username = ?', (username, )).fetchone()

            if record and check_password_hash(record['password_hash'], password):
                return User(record['id'], record['username'])

        return None

def init_app(app: Flask):
    password_verifier = PasswordVerifier(app)
    auth.verify_password(password_verifier)

    @auth.error_handler
    def unauthorized():
        return make_response({'error': 'Unauthorized access'}, 401)
