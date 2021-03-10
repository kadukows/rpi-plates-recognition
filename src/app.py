from flask import Flask, json, render_template, request, jsonify, url_for
from flask_socketio import SocketIO
from random import Random
import time

app = Flask(__name__)
socketio = SocketIO(app)
random = Random()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/latest_photos', methods=['GET'])
def latest_photos():
    # TODO
    # connect to db
    data = request.args.to_dict()
    response = {'photo-plates': []}

    print(data)

    if 'start' in data and 'count' in data:
        start = int(data['start'])
        for i in range(int(data['count'])):
            if random.randint(0, 1) != 0:
                response['photo-plates'].append(
                    {'photo_id': i + start,
                     'timestamp': time.time(),
                     'plates': str(random.randint(100000, 200000))})
            else:
                response['photo-plates'].append(
                    {'photo_id': i + start,
                     'timestamp': time.time()})
        response['success'] = True

    elif 'from' in data:
        pass

    else:
        pass

    if 'success' not in response:
        response['success'] = False

    return jsonify(response)

@app.route('/get_photo', methods=['GET'])
def get_photo():
    data = request.args.to_dict()

    print(f'hello get_photo ${data["photo_id"]}')

    if 'photo_id' in data and int(data['photo_id']) == 1:
        return jsonify({
            'success': True,
            'photo_url': url_for('static', filename='photos/elmo.png')})
    else:
        return jsonify({
            'success': False
        })
