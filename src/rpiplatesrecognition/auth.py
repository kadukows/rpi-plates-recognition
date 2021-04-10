from typing import Optional

from dataclasses import dataclass
from flask import Flask, make_response
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash

from .db import db
from .models import User

auth = HTTPBasicAuth()

class PasswordVerifier:
    def __call__(self, username: str, password: str) -> Optional[User]:
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            return user

        return None

def init_app(app: Flask):
    password_verifier = PasswordVerifier()
    auth.verify_password(password_verifier)

    @auth.error_handler
    def unauthorized():
        return make_response({'error': 'Unauthorized access'}, 401)
