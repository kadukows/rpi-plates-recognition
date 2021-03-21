from flask import Blueprint, json, jsonify

from rpiplatesrecognition.db import get_db
from rpiplatesrecognition.libs.gate import gate

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/take_photo', methods=('GET',))
def take_photo():
    """API route for initializing photo -> acquisition -> access decision routine.

    Upon receiving GET request /api/take_photo will initialize photo ->
    acquisition -> acces decision routine. It will call every module
    separately, pass appropriate arguments to each, and handle error codes.
    Additionally, if photo was taken sucessfully, it will record acces attempt
    to acces_attempt table in database. Finally, this route will return
    appropriate JSON object.
    """

    # methods for that routines are under construction, so lets assume that
    # photo was taken, and plates were recognized
    recognized_plates = 'WW1234L'
    db = get_db()

    plates_record = db.execute(
        'SELECT * FROM plates WHERE plate = ?',
        (recognized_plates,)
    ).fetchone()

    if plates_record is not None:
        # lets assume that gate is never busy and always ready to be opened
        gate.open()
        return jsonify({'success': True})
