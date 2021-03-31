from flask import session, request
import socketio

from .db import get_db

def init_app(sio):
    @sio.on('login')
    def login(data):
        if 'unique_id' in data:
            db = get_db()
            record = db.execute(
                'SELECT * FROM rpi WHERE unique_id = ?',
                (data['unique_id'],)
            ).fetchone()

            session.clear()

            if record is not None:
                session['id'] = record['id']
                session['unique_id'] = record['unique_id']

                if db.execute('SELECT * FROM active_rpi WHERE rpi_id = ?', (session['id'], )).fetchone() is None:
                    db.execute(
                        'INSERT INTO active_rpi (rpi_id, sid) VALUES (?, ?)',
                        (session['id'], request.sid)
                    )
                    db.commit()

    @sio.event
    def disconnect():
        if 'id' in session:
            db = get_db()

            # delete rpi from active rpis
            db.execute('DELETE FROM active_rpi WHERE rpi_id = ?', (session['id'], ))

            # insert logs dump
            # TODO

            db.commit()
            session.clear()

    @sio.on('log')
    def log(data):
        if 'id' in session:
            if 'logs' not in session:
                session['logs'] = []
            session['logs'].append(data)
            sio.emit('log', to=request.sid)
