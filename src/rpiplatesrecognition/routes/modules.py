from flask import Blueprint, flash, render_template
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError, SelectMultipleField, HiddenField
from wtforms.validators import DataRequired

from ..models import Module, Whitelist, User
from ..db import db
from ..db.helpers import get_modules_for_user_query
from ..helpers import process_bootstrap_table_request, AjaxForm


bp = Blueprint('modules', __name__, url_prefix='/modules')

#
#  User's modules View
#

class AddModuleForm(AjaxForm):
    unique_id = StringField('Unique id', validators=[DataRequired()])

    def validate_unique_id(self, unique_id):
        module = Module.query.filter_by(unique_id=unique_id.data).first()

        if module is None:
            raise ValidationError('Unknown unique id')

        if module.user is not None:
            raise ValidationError('Module is already registed to a user')


class RemoveModuleForm(AjaxForm):
    unique_ids = HiddenField('unique_ids', validators=[DataRequired()])

    def validate_unique_ids(self, unique_ids):
        unique_ids_splitted = unique_ids.data.split(',')
        query = get_modules_for_user_query(current_user).filter(Module.unique_id.in_(unique_ids_splitted))
        if query.count() != len(unique_ids_splitted):
            raise ValidationError('Wrong module unique id')

    def get_modules_query(self):
        unique_ids_splitted = self.unique_ids.data.split(',')
        return get_modules_for_user_query(current_user).filter(Module.unique_id.in_(unique_ids_splitted))


@bp.route('')
@login_required
def index():
    return render_template('modules.html', add_form=AddModuleForm(), remove_form=RemoveModuleForm())

@bp.route('/get')
@login_required
def get():
    total, totalNotFiltered, modules_query = process_bootstrap_table_request(
        get_modules_for_user_query(current_user),
        Module.unique_id,
        Module.unique_id
    )

    return {
        'total': total,
        'totalNotFiltered': totalNotFiltered,
        'rows': [
            {
                'unique_id': module.unique_id,
                'is_active': module.is_active
            } for module in modules_query.all()
        ]
    }

@bp.route('/add', methods=['POST'])
@login_required
def add():
    form = AddModuleForm()

    if not form.validate_on_submit():
        return form.generate_failed_response_dict(), 409
    else:
        module = Module.query.filter_by(unique_id=form.unique_id.data).first()
        module.user = current_user
        flash(f"Bound new module: {module.unique_id}")
        db.session.commit()
        return '', 201


@bp.route('/remove', methods=['POST'])
@login_required
def remove():
    form = RemoveModuleForm()

    if not form.validate_on_submit():
        return form.generate_failed_response_dict(), 409
    else:
        query = form.get_modules_query()
        query_string = ", ".join(module.unique_id for module in query.all())
        flash(f"Unbound modules: {query_string}")
        query.delete()
        db.session.commit()
        return '', 201
