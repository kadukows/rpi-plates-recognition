from typing import Tuple
from flask import Flask
from flask_socketio import SocketIO, SocketIOTestClient

from rpiplatesrecognition.models import Module

from .tests_libs.rpi_test_client import RpiTestClient
