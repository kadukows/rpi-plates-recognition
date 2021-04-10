from flask import session, request
from flask_socketio import SocketIO

from .db import db
from . import models

def init_app(sio: SocketIO):
    @sio.on('login')
    def login(data):
        print('login call')
        if 'unique_id' in data:
            '''
            db = get_db()
            record = db.execute(
                'SELECT * FROM rpi WHERE unique_id = ?',
                (data['unique_id'],)
            ).fetchone()
            '''
            module = models.Module.query.filter_by(unique_id=data['unique_id']).first()
            session.clear()

            if module is not None:
                session['module_id'] = module.id
                module.active_module = models.ActiveModule(sid=request.sid)
                db.session.commit()


    @sio.event
    def disconnect():
        if 'module_id' in session:
            # beacuse every socketio 'message' has different app_context, you can't store user object in 'session' dict
            module = models.Module.query.filter_by(id=session['module_id']).one()
            db.session.delete(module.active_module)
            db.session.commit()

            # insert logs dump
            # TODO

            session.clear()

    @sio.on('log')
    def log(data):
        if 'id' in session:
            if 'logs' not in session:
                session['logs'] = []
            session['logs'].append(data)
            sio.emit('log', data=data, to=request.sid, namespace='/api')
