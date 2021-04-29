import base64

from flask import Flask, request, session
from flask import json
from flask.json import jsonify
from flask_socketio import SocketIO, join_room, leave_room, disconnect
from werkzeug.datastructures import Authorization

from .auth import rest_auth, PasswordVerifier
from .db import db
from .models import User, Module, Whitelist, whitelist_assignment

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

        #http -a user1:user1 GET http://127.0.0.1:5000/api/get_modules

        user = rest_auth.current_user()
        modules = Module.query.filter_by(user_id=user.id).all()

        if modules is None:
            return 'No module on list', 500

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
        if module.user is not None:
            return "Module already assigned", 500

        with db.session():
            module.user = user
            db.session.commit()

        return "Created resource",201


    @app.route('/api/remove_module', methods=['DELETE'])
    @rest_auth.login_required
    def remove_module():
        #http -a user1:user1 DELETE http://127.0.0.1:5000/api/remove_module unique_id=unique_id_5

        user = rest_auth.current_user()
        data = request.get_json() or {}
        if "unique_id" not in data or user is None:
            return "Wrong json", 401

        module = Module.query.filter_by(unique_id = data['unique_id']).first()

        if module is None:
            return 'No resource', 404

        if module.user is not user:
            return 'Module with such ID is bound to another user or is not bound to anyone', 412

        with db.session():
            module.user = None
            db.session.commit()

        return "Succesfuly removed from user", 201


    @app.route('/api/create_whitelist', methods=['POST'])
    @rest_auth.login_required
    def create_whitelist():
        #http -a user1:user1 POST http://127.0.0.1:5000/api/create_whitelist whitelist_name=test

        user = rest_auth.current_user()
        data = request.get_json() or {}
        if "whitelist_name" not in data or user is None:
            return "Wrong json", 401

        if Whitelist.query.filter_by(name=data['whitelist_name']).first() is not None:
            return 'Whitelist with such name already exists',418

        with db.session():
            whitelist = Whitelist(name=data['whitelist_name'])
            whitelist.user = user

            db.session.add(whitelist)
            db.session.commit()

        return "Created whitelist", 201


    @app.route('/api/get_all_whitelists', methods=['GET'])
    @rest_auth.login_required
    def get_all_whitelist():
        # http -a user1:user1 GET http://127.0.0.1:5000/api/get_all_whitelists

        user = rest_auth.current_user()
        whitelists = Whitelist.query.filter_by(user_id=user.id).all()

        if whitelists is None:
            return 'No whitelists', 500

        return {'whitelists': [whitelist.name for whitelist in whitelists]}

    @app.route('/api/get_whitelisted_plates', methods=['GET'])
    @rest_auth.login_required
    def get_whitelisted_plates():
        #http -a user1:user1 GET http://127.0.0.1:5000/api/get_whitelisted_plates?id=id1
        #http -a user1:user1 GET http://127.0.0.1:5000/api/get_whitelisted_plates?id='example whitelist name'

        user = rest_auth.current_user()
        data = request.args
        if "id" not in data or user is None:
            return "Lack of args", 401

        whitelist = Whitelist.query.filter_by(name=data['id']).first()

        if whitelist is None:
            return "Whitelist with such id does not exists", 404


        # not done yet
        return {'plates':'a'}
