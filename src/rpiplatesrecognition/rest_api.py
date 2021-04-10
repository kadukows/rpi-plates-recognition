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
        '''
        active_rpis = get_db().execute(
            'SELECT (unique_id) FROM rpi WHERE user_id = ?', (user.id, )
        ).fetchall()
        '''
        return {'unique_ids': [module.unique_id for module in user.modules]}

    @app.route('/api/get_active/', methods=['GET'])
    @auth.login_required
    def is_active():
        """Route returning status of rpi with unique_id"""

        user = auth.current_user()
        '''
        db = get_db()
        records = db.execute("""
            SELECT *
            FROM rpi
                INNER JOIN
                active_rpi
                ON rpi.id = active_rpi.rpi_id
            WHERE rpi.user_id = ?
        """, (user.id, )).fetchall()
        '''
        active_modules = (db.session.query(Module.unique_id)
                            .join(ActiveModule, Module.id == ActiveModule.module_id)
                            .filter(Module.user_id == user.id)).all()

        assert isinstance(active_modules, list)

        return {'active_rpis': [obj[0] for obj in active_modules]}

    # This is not really rest API, as this is using WebSockets to pass through
    # logs from rpi to users web app
    # TODO: move to other file
    @sio.event(namespace='/api')
    @auth.login_required
    def connect():
        session['user'] = auth.current_user()

    @sio.on('join_rpi_room', namespace='/api')
    def join_rpi_room(data):
        """Route adding user to specific rpi's room for log subscribing"""

        if 'unique_id' in data:
            '''
            db = get_db()
            record = db.execute("""
                SELECT *
                FROM active_rpi
                    INNER JOIN rpi ON active_rpi.rpi_id = rpi.id
                    INNER JOIN user_accounts ON rpi.user_id = user_accounts.id
                WHERE rpi.unique_id = ?
            """, (data['unique_id'], )).fetchone()
            '''
            # unique_id is users and there is active_module record
            sid = (db.session.query(ActiveModule.sid)
                    .join(Module, ActiveModule.module_id == Module.id)
                    .join(User, Module.user_id == User.id)
                    .filter(Module.unique_id == data['unique_id'])
                    .filter(User.id == session['user'].id)).first()

            if sid is not None:
                session['sid'] = sid
                join_room(sid)

    @sio.on('leave_rpi_room', namespace='/api')
    def leave_rpi_room(data):
        """Route to leave specific rpi room"""
        '''
        if 'unique_id' in data:

            db = get_db()
            record = db.execute("""
                SELECT *
                FROM active_rpi
                    INNER JOIN rpi ON active_rpi.rpi_id = rpi.id
                    INNER JOIN user_accounts ON rpi.user_id = user_accounts.id
                WHERE rpi.unique_id = ? AND user_accounts.username = ?
            """, (data['unique_id'], session['user'].username)).fetchone()

            if record is not None:
                leave_room(record['sid'])
            '''
        if 'sid' in session:
            leave_room(session['sid'])
