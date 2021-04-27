import os

from flask import Flask
from flask_socketio import SocketIO

def create_app(test_config=None, return_socketio=False):
    """This is default factory function for creating app object"""

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.instance_path, 'rpiplatesrecognition.sqlite'),
        SQLALCHEMY_TRACK_MODIFICATIONS = False
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # assure that models are loaded before initializing db with app
    from . import models

    from . import db
    db.init_app(app)

    from . import auth
    auth.init_app(app)

    sio = SocketIO(app)
    from . import rpi_websocket_api
    rpi_websocket_api.init_app(sio)

    from . import rest_api
    rest_api.init_app_sio(app, sio)

    from . import routes
    routes.init_app(app, sio)

    from . import rpi_connection
    app.register_blueprint(rpi_connection.bp)

    from . import client_websocket_routes
    client_websocket_routes.init_app_sio(app, sio)

    from flask_bootstrap import Bootstrap
    Bootstrap(app)

    from . import manual_image
    manual_image.init_app(app)

    if return_socketio:
        return (app, sio)
    return app
