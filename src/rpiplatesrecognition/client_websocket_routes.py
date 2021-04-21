from flask import Flask, session, flash, url_for
from flask_socketio import SocketIO, join_room
from flask_login import login_required, current_user
from werkzeug.utils import redirect

from rpiplatesrecognition.auth import admin_required

from .models import Module, User
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

            '''
            module = (Module.query
                    .join(User, Module.user_id == User.id)
                    .filter(Module.unique_id == data['unique_id'])
                    .filter(User.id == session['sio_user_id'])).first()
            '''

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
