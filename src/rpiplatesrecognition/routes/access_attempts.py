import os
from flask import Blueprint, flash
from flask.globals import request
from flask.helpers import send_from_directory, url_for
from flask.templating import render_template
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError

from ..db import db
from ..db.helpers import get_modules_for_user_query, get_access_attempts_for_module_user_query, get_access_attempts_for_user_query, get_whitelists_for_user_query
from ..models import Module, AccessAttempt, Dirs, Whitelist
from ..helpers import process_bootstrap_table_request

bp = Blueprint('access_attempts', __name__, url_prefix='/access_attempts')


class BindwhitelistToModule(FlaskForm):
    whitelists = SelectMultipleField('Bound whitelists', render_kw={'class': 'selectpicker', 'autocomplete': 'off', 'data-live-search': 'true'}, coerce=int)
    submit = SubmitField('Submit')

    def validate_whitelists(self, whitelists):
        users_whitelists_query = get_whitelists_for_user_query(current_user).filter(Whitelist.id.in_(whitelists.data))

        if users_whitelists_query.count() != len(whitelists.data):
            raise ValidationError('wrong whitelist name')


@bp.route('/<string:unique_id>', methods=['GET', 'POST'])
@login_required
def index(unique_id):
    module = get_modules_for_user_query(current_user).filter(Module.unique_id == unique_id).first()

    if module is None:
        flash('Module not found')
        return redirect(url_for('index'))

    form = BindwhitelistToModule()
    form.whitelists.choices = [(whitelist.id, whitelist.name) for whitelist in current_user.whitelists]

    if form.validate_on_submit():
        module.whitelists = [Whitelist.query.get(whitelist_id) for whitelist_id in form.whitelists.data]
        db.session.commit()
        return redirect(url_for('access_attempts.index', unique_id=unique_id))

    form.whitelists.data = [whitelist.id for whitelist in module.whitelists]

    return render_template('access_attempts.html', module=module, form=form)


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
