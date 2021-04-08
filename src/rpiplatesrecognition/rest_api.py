import base64

from flask import Flask, request
from flask import json
from flask.globals import g
from flask.json import jsonify
from flask_socketio import SocketIO, join_room, leave_room, disconnect
from werkzeug.datastructures import Authorization

from .auth import auth, PasswordVerifier
from .db import get_db

def init_app_sio(app: Flask, sio: SocketIO):
    @app.route('/api/rpis', methods=['GET'])
    @auth.login_required
    def rpis():
        """Route returning list of rpis for user"""

        user = auth.current_user()
        active_rpis = get_db().execute(
            'SELECT (unique_id) FROM rpi WHERE user_id = ?', (user.id, )
        ).fetchall()

        if active_rpis:
            return {'unique_ids': [row['unique_id'] for row in active_rpis]}
        else:
            return {}

    @app.route('/api/get_active/', methods=['GET'])
    @auth.login_required
    def is_active():
        """Route returning status of rpi with unique_id"""

        user = auth.current_user()
        db = get_db()
        records = db.execute("""
            SELECT *
            FROM rpi
                INNER JOIN
                active_rpi
                ON rpi.id = active_rpi.rpi_id
            WHERE rpi.user_id = ?
        """, (user.id, )).fetchall()

        if records:
            return {'active_rpis': [record['unique_id'] for record in records]}
        else:
            return {'active_rpis': []}


    @sio.event(namespace='/api')
    @auth.login_required
    def connect():
        g.user = auth.current_user

    @sio.on('join_rpi_room', namespace='/api')
    def join_rpi_room(data):
        """Route adding user to specific rpi's room for log subscribing"""

        if 'unique_id' in data:
            db = get_db()
            record = db.execute("""
                SELECT *
                FROM active_rpi
                    INNER JOIN rpi ON active_rpi.rpi_id = rpi.id
                    INNER JOIN user_accounts ON rpi.user_id = user_accounts.id
                WHERE rpi.unique_id = ?
            """, (data['unique_id'], )).fetchone()

            if record is not None:
                join_room(record['sid'])

    @sio.on('leave_rpi_room', namespace='/api')
    def leave_rpi_room(data):
        """Route to leave specific rpi room"""

        if 'unique_id' in data:
            db = get_db()
            record = db.execute("""
                SELECT *
                FROM active_rpi
                    INNER JOIN rpi ON active_rpi.rpi_id = rpi.id
                    INNER JOIN user_accounts ON rpi.user_id = user_accounts.id
                WHERE rpi.unique_id = ? AND user_accounts.username = ?
            """, (data['unique_id'], g.user.username)).fetchone()

            if record is not None:
                leave_room(record['sid'])
