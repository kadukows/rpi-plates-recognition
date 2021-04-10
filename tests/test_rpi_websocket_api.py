from typing import Tuple
from flask import Flask
from flask_socketio import SocketIO, SocketIOTestClient

from rpiplatesrecognition.models import ActiveModule, Module

from .tests_libs.rpi_test_client import RpiTestClient



def test_rpi_websocket_api_will_record_login_event_in_database(app_sio_rpi_client: Tuple[Flask, SocketIO, RpiTestClient]):
    app, sio, rpi_client = app_sio_rpi_client
    unique_id = 'unique_id_1'

    rpi_client.emit('login', {'unique_id': unique_id})

    with app.app_context():
        query = (ActiveModule.query
            .join(Module, ActiveModule.module_id == Module.id)
            .filter(Module.unique_id == unique_id))

        active_modules = query.all()

    assert len(active_modules) == 1
    assert active_modules[0] is not None

    rpi_client.disconnect()

    with app.app_context():
        active_modules = query.all()

    assert len(active_modules) == 0
