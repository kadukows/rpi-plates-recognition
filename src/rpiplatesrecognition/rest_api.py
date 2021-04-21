import base64

from flask import Flask, request, session
from flask import json
from flask.json import jsonify
from flask_socketio import SocketIO, join_room, leave_room, disconnect
from werkzeug.datastructures import Authorization

from .auth import rest_auth, PasswordVerifier
from .db import db
from .models import User, Module

def init_app_sio(app: Flask, sio: SocketIO):
    @app.route('/api/rpis', methods=['GET'])
    @rest_auth.login_required
    def rpis():
        """Route returning list of rpis for user"""

        user = rest_auth.current_user()
        return {'unique_ids': [module.unique_id for module in user.modules]}

    @app.route('/api/get_active/', methods=['GET'])
    @rest_auth.login_required
    def is_active():
        """Route returning status of rpi with unique_id"""

        user = rest_auth.current_user()
        active_modules = Module.query.filter_by(user_id=user.id, is_active=True).all()

        return {'active_rpis': [active_module.unique_id for active_module in active_modules]}
