import base64
from os import name
from typing import Tuple, Any
import json

from .tests_libs.rpi_test_client import RpiTestClient

from flask import Flask
from flask.testing import FlaskClient
from flask_socketio import SocketIO, SocketIOTestClient, test_client

from rpiplatesrecognition.db import db
from rpiplatesrecognition.models import User, Module


def make_auth_header(username: str, password: str):
    return {'Authorization': 'Basic ' + base64.b64encode((f'{username}:{password}'.encode('utf8'))).decode('utf8')}


def test_rest_api_will_return_401_for_unknown_user(client: FlaskClient):
    response = client.get('/api/rpis', headers=make_auth_header('unknown_user', 'password'))

    assert response.status_code == 401

def test_rest_api_will_return_list_of_rpis_for_user(client: FlaskClient):
    response = client.get('/api/rpis', headers=make_auth_header('user1', 'user1'))

    assert response.status_code == 200
    assert 'unique_id_1' in response.json['unique_ids']

def test_rest_api_will_return_list_of_connected_rpis(app_sio_rpi_client: Tuple[Flask, SocketIO, RpiTestClient]):
    app, sio, rpi_client = app_sio_rpi_client
    test_client_flask = app.test_client()
    unique_id = 'unique_id_1'

    # login with rpi
    rpi_client.emit('login_from_rpi', {'unique_id': unique_id}, namespace='/rpi')

    # make request as rest api user
    response = test_client_flask.get('/api/get_active/', headers=make_auth_header('user1', 'user1'))

    assert response.status_code == 200
    assert 'active_rpis' in response.json
    assert [unique_id] == response.json['active_rpis']

    # disconnect as rpi
    rpi_client.disconnect(namespace='/rpi')

    response = test_client_flask.get('/api/get_active/', headers=make_auth_header('user1', 'user1'))

    assert response.status_code == 200
    assert 'active_rpis' in response.json
    assert response.json['active_rpis'] == []


def test_rest_api_will_reroute_logs_from_rpi(app_sio_rpi_client: Tuple[Flask, SocketIO, RpiTestClient]):
    app, sio, rpi_client = app_sio_rpi_client
    test_client_client_sio = sio.test_client(app, namespace='/api', headers=make_auth_header('user1', 'user1'))

    unique_id = 'unique_id_1'

    # login with rpi
    rpi_client.emit('login', {'unique_id': unique_id})

    # register for logs as a web app user
    test_client_client_sio.emit('join_rpi_room', {'unique_id': unique_id}, namespace='/api')

    # emit logs as rpi
    log1 = 'log message one'
    log2 = 'log message two'
    rpi_client.logger.debug(log1)
    rpi_client.logger.debug(log2)

    received = test_client_client_sio.get_received(namespace='/api')
    received_json = [json.loads(obj['args'][0]) for obj in received if obj['name'] == 'log']

    assert log1, log2 in (obj['msg'] for obj in received_json)


    # leave room as to not receive any more logs
    test_client_client_sio.emit('leave_rpi_room', {'unique_id': unique_id}, namespace='/api')

    log3 = 'log message three'
    rpi_client.logger.debug(log3)

    received = test_client_client_sio.get_received(namespace='/api')
    received_json = [json.loads(obj['args'][0]) for obj in received if obj['name'] == 'log']

    assert log3 not in (obj['msg'] for obj in received_json)


def test_rest_api_get_username_should_return_username(client):
    response = client.get('/get_username', headers=make_auth_header('user1', 'user1'))
    print(response.json)

def test_returning_all_modules_assigned_to_user(client):
    response = client.get('/api/get_modules', headers=make_auth_header('user1', 'user1'))
    assert response.status_code == 200
    assert 'modules' in response.json

    assert response.json['modules'] == ['unique_id_1','unique_id_3']


#  tu jest cos nie tak z testem, problemem jest przeslanie zarowno headera z authentykacja jak i jsona w poscie
def test_adding_module(app):
    client = app.test_client()
    data = { "unique_id": "unique_id_2", }
    response = client.post('/api/add_module', headers={'Authorization': 'Basic ' + base64.b64encode(('user1:user1'.encode('utf8'))).decode('utf8'),"Content-Type": "application/json"}
    , data = json.dumps(data))
    
    assert response.status_code == 201
    
    with app.app_context():
        user = User.query.filter_by(username="user1").first()
        assert user is not None
        assert any([module.unique_id=="unique_id_2" for module in user.modules])
        




    
