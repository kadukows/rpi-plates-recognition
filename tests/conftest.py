import os, tempfile
import logging, json

import pytest
from flask import Flask
from flask_socketio import SocketIO, SocketIOTestClient
from werkzeug.security import generate_password_hash

from rpiplatesrecognition import create_app
from rpiplatesrecognition.db import init_db, db, init_db_command
from rpiplatesrecognition.models import User, Module, Whitelist, Plate

from .tests_libs.rpi_test_client import RpiTestClient

@pytest.fixture
def app_sio():
    db_fd, db_path = tempfile.mkstemp()

    app, sio = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + db_path,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False,
        'LOGIN_DISABLED': True
    }, return_socketio=True)

    with app.app_context():
        # this ensures clean database
        init_db()

        # populate database with basic values
        # add more if neccessary
        user = User(username='user1', password_hash=generate_password_hash('user1'))
        module_1 = Module('unique_id_1')
        user.modules.append(module_1)
        user.modules.append(Module(unique_id='unique_id_3'))
        db.session.add(user)

        module2 = Module(unique_id='unique_id_2')
        db.session.add(module2)

        whitelist = Whitelist(name='debug_whitelist_1')
        module_1.whitelists.append(whitelist)

        for plate_text in ('DEBUG1', 'DEBUG2'):
            whitelist.append(Plate(text=plate_text))


        db.session.commit()

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
