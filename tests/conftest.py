import os, tempfile
import logging, json

import pytest
from flask import Flask
from flask_socketio import SocketIO, SocketIOTestClient

from rpiplatesrecognition import create_app
from rpiplatesrecognition.db import get_db, init_db

from .tests_libs.rpi_test_client import RpiTestClient

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

@pytest.fixture
def app_sio_rpi_client(app_sio):
    app, sio = app_sio

    return (app, sio, RpiTestClient(app, sio))
