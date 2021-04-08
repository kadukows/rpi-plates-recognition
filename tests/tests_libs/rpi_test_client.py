import logging, json

from flask import Flask
from flask_socketio import SocketIO, SocketIOTestClient

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
