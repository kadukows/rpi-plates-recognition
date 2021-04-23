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
    
    @app.route('/api/get_modules', methods=['GET'])
    @rest_auth.login_required
    def get_modules():
        """Route returning modules asigned to user"""

        user = rest_auth.current_user()
        modules = Module.query.filter_by(user_id=user.id).all()

        return {'modules': [module.unique_id for module in modules]}
    
    @app.route('/api/add_module', methods=['POST'])
    @rest_auth.login_required
    def post_module():
        user = rest_auth.current_user()
        data = request.get_json() or {}
        if "unique_id" not in data:
            return "error"
        
        module = Module(unique_id=data['unique_id'],is_active=0,user_id=user.user_id)
        db.session.add(module)
        db.session.commit()
    
        return {'OK'}


    @app.route('/api/remove_module?id=<UNIQUE_ID>', methods=['DELETE'])
    @rest_auth.login_required
    def remove_module():
        pass

    
    

