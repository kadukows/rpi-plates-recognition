from logging import Formatter, LogRecord
from types import SimpleNamespace

from flask import session, request, jsonify
from flask_socketio import SocketIO, join_room

from .db import db
from .models import Module, AccessAttempt

def init_app(sio: SocketIO):
    @sio.on('login_from_rpi', namespace='/rpi')
    def login(data):
        if 'unique_id' in data:
            module = Module.query.filter_by(unique_id=data['unique_id']).first()
            session.clear()

            if module is not None:
                session['module_id'] = module.id
                module.is_active = True
                db.session.commit()

                join_room(module.unique_id)

                return {'success': True}

        return {'success': False}


    @sio.event(namespace='/rpi')
    def disconnect():
        if 'module_id' in session:
            # beacuse every socketio 'message' has different app_context, you can't store user object in 'session' dict
            module = Module.query.get(session['module_id'])
            module.is_active = False
            db.session.commit()

            session.clear()

    @sio.on('log_from_rpi', namespace='/rpi')
    def log(data):
        if 'module_id' in session:
            module = Module.query.get(session['module_id'])
            sio.emit(
                'message_from_server_to_client',
                data,
                namespace='/rpi',
                to=module.unique_id)

    @sio.on('image_from_rpi', namespace='/rpi')
    def image(data):
        if 'module_id' in session:
            module = Module.query.get(session['module_id'])
            if module and module.user:
                pass
                # uncomment when done
                #access_attempt = AccessAttempt(module=module)
                #db.session.commit()  # inits access_attempt.id
                # access_attempt.init_files(data)
