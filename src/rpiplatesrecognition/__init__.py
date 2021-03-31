import os

from flask import Flask
from flask_socketio import SocketIO

def create_app(test_config=None, return_socketio=False):
    """This is default factory function for creating app object"""

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'rpiplatesrecognition.sqlite')
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    sio = SocketIO(app)
    from . import rpi_websocket_api
    rpi_websocket_api.init_app(sio)

    if return_socketio:
        return (app, sio)
    return app
