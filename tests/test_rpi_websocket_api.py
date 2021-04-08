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
    assert 'sid' in record.keys()

    test_client.disconnect()
    with app.app_context():
        db = get_db()
        record = db.execute("""
            SELECT * FROM active_rpi
                INNER JOIN rpi ON active_rpi.rpi_id = rpi.id
            WHERE rpi.unique_id = ?
            """, (unique_id,)).fetchone()

    assert record is None



def test_rpitest_rpi_websocket_api_will_pass_through_log_event(app_sio):
    app, sio = app_sio
    test_client_rpi = SocketIOTestClient(app, sio)
    test_client_web = SocketIOTestClient(app, sio, namespace='/api', )

    unique_id = 'unique_id_1'

    test_client_rpi.emit('login', {'unique_id': unique_id})
