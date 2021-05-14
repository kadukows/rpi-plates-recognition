import os
from flask import Blueprint, flash
from flask.globals import request
from flask.helpers import send_from_directory, url_for
from flask.templating import render_template
from flask_login import login_required, current_user
from werkzeug.utils import redirect

from ..db.helpers import get_modules_for_user_query, get_access_attempts_for_module_user_query, get_access_attempts_for_user_query
from ..models import Module, AccessAttempt, Dirs
from ..helpers import process_bootstrap_table_request

bp = Blueprint('access_attempts', __name__, url_prefix='/access_attempts')

@bp.route('/<string:unique_id>')
@login_required
def index(unique_id):
    module = get_modules_for_user_query(current_user).filter(Module.unique_id == unique_id).first()

    if module is None:
        flash('Module not found')
        return redirect(url_for('index'))

    return render_template('access_attempts.html', module=module)


@bp.route('/<string:unique_id>/get')
@login_required
def get(unique_id):
    module = get_modules_for_user_query(current_user).filter(Module.unique_id == unique_id).first()

    if module is None:
        return {}

    total, totalNotFiltered, access_attempts = process_bootstrap_table_request(
        get_access_attempts_for_module_user_query(module, current_user),
        AccessAttempt.processed_plate_string,
        AccessAttempt.date
    )

    return {
        'total': total,
        'totalNotFiltered': totalNotFiltered,
        'rows': [
            {**access_attempt.to_dict(),
             **{'image_url': url_for('access_attempts.get_image', access_attempt_id=access_attempt.id)} }
            for access_attempt in access_attempts.all()]
    }


@bp.route('/get_image')
@login_required
def get_image():
    access_attempt_id = request.args.get('access_attempt_id', None, type=int)
    if access_attempt_id is None:
        return '', 404

    access_attempt = get_access_attempts_for_user_query(current_user) \
        .filter(AccessAttempt.id == access_attempt_id).first()

    if access_attempt is None:
        return '', 404

    dirname, filename = os.path.split(access_attempt.get_src_image_filepath(Dirs.Absolute))
    return send_from_directory(dirname, filename)
