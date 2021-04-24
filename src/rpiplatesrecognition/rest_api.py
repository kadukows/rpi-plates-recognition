import base64

from flask import Flask, request, session
from flask import json
from flask.json import jsonify
from flask_socketio import SocketIO, join_room, leave_room, disconnect
from werkzeug.datastructures import Authorization

from .auth import rest_auth, PasswordVerifier
from .db import db
from .models import User, Module, Whitelist

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
        # http -a user1:user1 POST http://127.0.0.1:5000/api/add_module unique_id=unique_id_5
        user = rest_auth.current_user()
        data = request.get_json() or {}
        if "unique_id" not in data or user is None:
            return "Wrong json", 401

        module = Module.query.filter_by(unique_id = data['unique_id']).first()
        with db.session():
            module.user = user
            db.session.commit()

        return "Created resource",201


    @app.route('/api/remove_module', methods=['DELETE'])
    @rest_auth.login_required
    def remove_module():
        
        user = rest_auth.current_user()
        data = request.get_json() or {}
        if "unique_id" not in data or user is None:
            return "Wrong json", 401

        module = Module.query.filter_by(unique_id = data['unique_id']).first()
        with db.session():
            module.user = None
            db.session.commit()

        return "Succesfuly removed from user",204
    
    @app.route('/api/create_whitelist', methods=['POST'])
    @rest_auth.login_required
    def create_whitelist():
        #http -a user1:user1 POST http://127.0.0.1:5000/api/create_whitelist whitelist_name=test
       
        user = rest_auth.current_user()
        data = request.get_json() or {}
        if "whitelist_name" not in data or user is None:
            return "Wrong json", 401

        with db.session():
            whitelist = Whitelist(name=data['whitelist_name'])
            whitelist.user = user

            db.session.add(whitelist)
            db.session.commit()

        return "Created whitelist",201
    
    @app.route('/api/get_all_whitelists', methods=['GET'])
    @rest_auth.login_required
    def get_all_whitelist():

        #user = rest_auth.current_user()
        #modules = Module.query.filter_by(user_id=user.id).all()

        r#eturn {'modules': [module.unique_id for module in modules]}
    
    

    
    

