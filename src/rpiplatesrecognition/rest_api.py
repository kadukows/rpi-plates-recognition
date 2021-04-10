import base64

from flask import Flask, request, session
from flask import json
from flask.json import jsonify
from flask_socketio import SocketIO, join_room, leave_room, disconnect
from werkzeug.datastructures import Authorization

from .auth import auth, PasswordVerifier
from .db import db
from .models import User, Module, ActiveModule

def init_app_sio(app: Flask, sio: SocketIO):
    @app.route('/api/rpis', methods=['GET'])
    @auth.login_required
    def rpis():
        """Route returning list of rpis for user"""

        user = auth.current_user()
        return {'unique_ids': [module.unique_id for module in user.modules]}

    @app.route('/api/get_active/', methods=['GET'])
    @auth.login_required
    def is_active():
        """Route returning status of rpi with unique_id"""

        user = auth.current_user()
        active_modules = (Module.query
                            .join(ActiveModule, Module.id == ActiveModule.module_id)
                            .filter(Module.user_id == user.id)).all()

        return {'active_rpis': [active_module.unique_id for active_module in active_modules]}


    # This is not really REST API, as this is using WebSockets to pass through
    # logs from rpi to users web app
    # TODO: move to other file
    @sio.event(namespace='/api')
    @auth.login_required
    def connect():
        # every socketio message is different app_context, can't store Model objects
        # between different messages
        session['user_id'] = auth.current_user().id

    @sio.on('join_rpi_room', namespace='/api')
    def join_rpi_room(data):
        """Route adding user to specific rpi's room for log subscribing"""

        if 'unique_id' in data:
            # unique_id is users and there is active_module record
            sid = (db.session.query(ActiveModule.sid)
                    .join(Module, ActiveModule.module_id == Module.id)
                    .join(User, Module.user_id == User.id)
                    .filter(Module.unique_id == data['unique_id'])
                    .filter(User.id == session['user_id'])).first()

            if sid is not None:
                session['sid'] = sid
                join_room(sid)

    @sio.on('leave_rpi_room', namespace='/api')
    def leave_rpi_room(data):
        """Route to leave specific rpi room"""

        if 'sid' in session:
            leave_room(session['sid'])
