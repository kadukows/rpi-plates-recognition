from logging import Formatter, LogRecord
from types import SimpleNamespace
import json

from flask import session, request, jsonify
from flask_socketio import SocketIO, join_room

from .db import db
from .models import Module, AccessAttempt, Plate, Whitelist, whitelist_to_module_assignment
from .libs.plate_acquisition.config_file import ExtractionConfigParameters
import dataclasses

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
    def log_from_rpi(data):
        if 'module_id' in session:
            module = Module.query.get(session['module_id'])
            sio.emit(
                'message_from_server_to_client',
                data,
                namespace='/rpi',
                to=module.unique_id)

    @sio.on('image_from_rpi', namespace='/rpi')
    def image_from_rpi(data):
        if 'module_id' in session:
            module = Module.query.get(session['module_id'])
            if module and module.user:
                access_attempt = AccessAttempt(module, data)
                db.session.add(access_attempt)

                sio.emit(
                    'new_access_attempt_from_server_to_client',
                    data=json.dumps(access_attempt.to_dict()),
                    namespace='/rpi',
                    to=module.unique_id)

                if access_attempt.processed_plate_string:
                    whitelist_with_plate = (Whitelist.query
                        .join(whitelist_to_module_assignment)
                        .filter(whitelist_to_module_assignment.c.module_id == module.id)
                        .filter(whitelist_to_module_assignment.c.whitelist_id == Whitelist.id)
                        .join(Plate, Plate.whitelist_id == Whitelist.id)
                        .filter(Plate.text == access_attempt.processed_plate_string)
                    ).first()

                    if whitelist_with_plate:
                        access_attempt.got_access = True
                        sio.emit(
                            'message_from_server_to_rpi',
                            data={'command': 'open_gate'},
                            namespace='/rpi',
                            to=module.unique_id)

                db.session.commit()



    @sio.on('update_config', namespace='/rpi')
    def update_config(data):
        if 'module_id' in session:
            module = Module.query.get(session['module_id'])
            if module and module.user:
                return json.dumps(dataclasses.asdict(module.extraction_params))
