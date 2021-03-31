from flask_socketio import SocketIOTestClient

from rpiplatesrecognition.db import get_db



def test_rpi_websocket_api_will_record_login_event_in_database(app_sio):
    app, sio = app_sio
    test_client = SocketIOTestClient(app, sio)

    unique_id = 'unique_id_1'

    test_client.emit('login', {'unique_id': unique_id})

    with app.app_context():
        db = get_db()
        record = db.execute("""
            SELECT * FROM active_rpi
            INNER JOIN rpi ON active_rpi.rpi_id = rpi.id
            WHERE rpi.unique_id = ?
            """, (unique_id,)).fetchone()

    assert record is not None
    assert record['sid'] is not None

    test_client.disconnect()
    with app.app_context():
        db = get_db()
        record = db.execute("""
            SELECT * FROM active_rpi
            INNER JOIN rpi ON active_rpi.rpi_id = rpi.id
            WHERE rpi.unique_id = ?
            """, (unique_id,)).fetchone()

    assert record is None
