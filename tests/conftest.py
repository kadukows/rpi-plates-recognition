import os, tempfile
import logging, json

import pytest
from flask import Flask
from flask_socketio import SocketIO, SocketIOTestClient

from rpiplatesrecognition import create_app
from rpiplatesrecognition.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

@pytest.fixture
def app_sio():
    db_fd, db_path = tempfile.mkstemp()

    app, sio = create_app({
        'TESTING': True,
        'DATABASE': db_path
    }, return_socketio=True)

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield (app, sio)

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def app(app_sio):
    return app_sio[0]

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class RpiTestClient(SocketIOTestClient):
    def __init__(self, app: Flask, sio_server: SocketIO):
        SocketIOTestClient.__init__(self, app, sio_server)

        self.logger = logging.getLogger('test_logger')
        # reset loggers state
        # this is done because logger handlers
        # were persisting when running all pytests
        self.logger.handlers.clear()
        self.logger.setLevel(logging.DEBUG)

        # pass this object as Client socketio connection
        handler = self.CustomLogHandler(self)
        handler.setLevel(logging.DEBUG)

        self.logger.addHandler(handler)

    class CustomLogHandler(logging.NullHandler):
        def __init__(self, sio_client):
            logging.NullHandler.__init__(self)
            self.sio = sio_client

        def handle(self, record: logging.LogRecord):
            self.sio.emit('log', json.dumps(record.__dict__))


@pytest.fixture
def app_sio_rpi_client(app_sio):
    app, sio = app_sio

    return (app, sio, RpiTestClient(app, sio))
