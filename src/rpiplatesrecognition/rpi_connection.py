import base64, os, json
from dataclasses import asdict
from flask import Blueprint, render_template, jsonify, flash, url_for, send_from_directory, current_app
from flask_login.utils import login_required
from werkzeug.utils import redirect

from .auth import admin_required
from .models import Module, AccessAttempt
from .forms import UploadImageForm
from .db import db
from .helpers import Dirs

bp = Blueprint('rpi_connection', __name__, url_prefix='/rpi_connection')

@bp.route('/<string:unique_id>')
@login_required
@admin_required
def index(unique_id):
    module = Module.query.filter_by(unique_id=unique_id).first()
    if module is None:
        flash("wrong unique_id!")
        return redirect(url_for('index'))

    return render_template('rpi_connection.html', module=module)

@bp.route('/get_images_for_access_attempt/<int:access_attempt_id>')
@login_required
@admin_required
def get_images_for_access_attempt(access_attempt_id: int):
    access_attempt = AccessAttempt.query.get(access_attempt_id)
    access_attempt: AccessAttempt

    if access_attempt is None:
        return {}

    return {
        'img_src': url_for('rpi_connection.access_attempt_src_image', access_attempt_id=access_attempt_id),
        'edge_proj': [
            url_for('rpi_connection.access_attempt_edge_proj_image', access_attempt_id=access_attempt_id, edge_proj_id=edge_proj_id) for edge_proj_id in range(access_attempt.plate_region_num)
        ],
        'segments': [
            url_for('rpi_connection.access_attempt_seg_image', access_attempt_id=access_attempt_id, seg_id=seg_idx) for seg_idx in range(access_attempt.segments_num)
        ],
        'extraction_params': asdict(access_attempt.extraction_params)
    }

@bp.route('/get_access_attempts/<string:unique_id>')
@login_required
@admin_required
def get_access_attempts(unique_id: str):
    module = Module.query.filter_by(unique_id=unique_id).first()
    module: Module

    if module is None:
        return {}

    return jsonify(
        [access_attempt.to_dict() for access_attempt in module.access_attempts]
    )

@bp.route('/get_module_params/<string:unique_id>')
@login_required
@admin_required
def get_module_params(unique_id: str):
    module = Module.query.filter_by(unique_id=unique_id).first()
    module: Module

    if module is None:
        return {}

    return asdict(module.extraction_params)

@bp.route('/upload_access_attempt/<string:unique_id>/', methods=['GET', 'POST'])
@login_required
@admin_required
def upload_access_attempt(unique_id):
    module = Module.query.filter_by(unique_id=unique_id).first()

    if module is None:
        flash('Wrong unique_id')
        return redirect(url_for('index'))

    if module.user is None:
        flash('Cant upload an access attempt to not bound module!')
        return redirect(url_for('rpi_connection.index', unique_id=unique_id))

    form = UploadImageForm()
    if form.validate_on_submit():
        img_data = form.file.data.stream.read()

        access_attempt = AccessAttempt(module, base64.encodebytes(img_data))
        db.session.add(access_attempt)
        db.session.commit()

        return redirect(url_for('rpi_connection.index', unique_id=unique_id))

    return render_template('rpi_connection_file_upload.html', form=form, module=module)


@bp.route('/access_attempt/src_image/<int:access_attempt_id>')
@login_required
@admin_required
def access_attempt_src_image(access_attempt_id: int):
    access_attempt = AccessAttempt.query.get(access_attempt_id)
    access_attempt: AccessAttempt

    if access_attempt is None:
        return b'Not found', 404

    dirname, filename = os.path.split(access_attempt.get_src_image_filepath(Dirs.Absolute))
    return send_from_directory(dirname, filename)


@bp.route('/access_attempt/seg_result_image/<int:access_attempt_id>/<int:seg_id>')
@login_required
@admin_required
def access_attempt_seg_image(access_attempt_id: int, seg_id: int):
    access_attempt = AccessAttempt.query.get(access_attempt_id)
    access_attempt: AccessAttempt

    if access_attempt is None:
        return b'Not found', 404

    return send_from_directory(access_attempt.get_segments_dirpath(Dirs.Absolute), str(seg_id) + '.png')

@bp.route('/access_attempt/edge_proj_image/<int:access_attempt_id>/<int:edge_proj_id>')
@login_required
@admin_required
def access_attempt_edge_proj_image(access_attempt_id: int, edge_proj_id: int):
    access_attempt = AccessAttempt.query.get(access_attempt_id)
    access_attempt: AccessAttempt

    if access_attempt is None:
        return b'Not found', 404

    return send_from_directory(access_attempt.get_edge_proj_dirpath(Dirs.Absolute), str(edge_proj_id) +'.png')
