import json, base64
from os import name
from flask import Flask, session, flash, url_for
from flask_socketio import SocketIO, join_room
from flask_login import login_required, current_user
from werkzeug.utils import redirect

from rpiplatesrecognition.auth import admin_required

from .models import AccessAttempt, Module, User, Dirs
from .db import db

def init_app_sio(app: Flask, sio: SocketIO):

    @sio.event(namespace='/rpi')
    @login_required
    @admin_required
    def connect():
        pass



    @sio.on('join_rpi_room_from_client', namespace='/rpi')
    def join_rpi_room(data):
        if 'unique_id' in data:
            # check if current user own module that it wants to connect to

            module = Module.query.filter_by(unique_id=data['unique_id']).first()

            if module is not None:
                session['sio_module_id'] = module.id
                join_room(module.unique_id)
                sio.emit(
                    'message_from_server_to_client',
                    f'Connected to room: {module.unique_id}',
                    namespace='/rpi',
                    to=module.unique_id)



    @sio.on('message_from_client', namespace='/rpi')
    def from_client(data):
        if 'command' in data and 'sio_module_id' in session:
            module = Module.query.get(session['sio_module_id'])
            sio.emit('message_from_server_to_rpi',
                data['command'],
                namespace='/rpi',
                to=module.unique_id)


    @sio.on('rerun_access_attempt_from_client', namespace='/rpi')
    def rerun_access_attempt(data):
        if 'access_attempt_id' in data:
            access_attempt = AccessAttempt.query.get(data['access_attempt_id'])
            access_attempt: AccessAttempt
            if access_attempt:
                path = access_attempt.get_src_image_filepath(Dirs.Absolute)
                with open(path, 'rb') as file:
                    img_bytes = base64.encodebytes(file.read())
                    with db.session.no_autoflush:
                        new_access_attempt = AccessAttempt(access_attempt.module, img_bytes)
                        db.session.add(new_access_attempt)

                    db.session.commit()

                    sio.emit(
                        'new_access_attempt_from_server_to_client',
                        data=json.dumps(new_access_attempt.to_dict()),
                        namespace='/rpi',
                        to=new_access_attempt.module.unique_id)
