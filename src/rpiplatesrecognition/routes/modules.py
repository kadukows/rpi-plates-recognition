from flask import Blueprint, flash, render_template
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError, SelectMultipleField
from wtforms.validators import DataRequired

from ..models import Module, Whitelist, User
from ..db import db


bp = Blueprint('modules', __name__, url_prefix='/modules')

#
#  User's modules View
#

@bp.route('')
@login_required
def index():
    form = AddModuleFormAjax()

    whitelists_dict = {}

    for module in current_user.modules:
        whitelists_dict[module.unique_id] = { (whitelist.id, whitelist.name): False for whitelist in current_user.whitelists }
        for selected_whitelist in module.whitelists:
            whitelists_dict[module.unique_id][(selected_whitelist.id, selected_whitelist.name)] = True

    edit_whitelist_form = BindWhitelistToModuleDynamicCtor(current_user)

    return render_template(
        'modules.html',
        modules=current_user.modules,
        form=form,
        whitelists_dict=whitelists_dict,
        edit_whitelist_form=edit_whitelist_form)

@bp.route('/add_module_ajax', methods=['POST'])
@login_required
def add_module_ajax():
    form = AddModuleFormAjax()

    if not form.validate_on_submit():
        result = {'errors': {}}
        for field in form:
            if field.errors:
                result['errors'][field.name] = [error for error in field.errors]

        return result, 409
    else:
        module = Module.query.filter_by(unique_id=form.unique_id.data).first()
        module: Module

        module.user = current_user
        db.session.commit()

        return '', 201

@bp.route('/get_whitelists_with_bound_modules_ajax')
@login_required
def get_whitelists_with_bound_modules_ajax():
    result = {
        whitelist.id: {
            'name': whitelist.name,
            'bound_modules': [module.unique_id for module in whitelist.modules]
        } for whitelist in current_user.whitelists
    }

    return result, 200

@bp.route('/bind_modules_to_whitelists_ajax', methods=['POST'])
@login_required
def bind_modules_to_whitelists_ajax():
    form = BindWhitelistToModuleDynamicCtor(current_user)

    edited_modules_names = []

    if not form.validate_on_submit():
        result = {'errors': {}}
        for field in form:
            if field.errors:
                result['errors'][field.name] = [error for error in field.errors]

        return result, 409
    else:
        for field in form:
            if field.data != field.default:
                if field.name.endswith('_whitelists'):
                    unique_id = field.name.replace('_whitelists', '')
                    module = Module.query.filter_by(unique_id=unique_id).first()
                    module: Module

                    edited_modules_names.append(module.unique_id)

                    module.whitelists.clear()
                    for whitelist_id in field.data:
                        module.whitelists.append(Whitelist.query.get(whitelist_id))

        db.session.commit()
        if len(edited_modules_names) > 0:
            flash('Successfully edited modules: ' + ', '.join(edited_modules_names))

        return '', 201

class AddModuleForm(FlaskForm):
    unique_id = StringField('Unique id', validators=[DataRequired()])
    submit = SubmitField('Add')

    def validate_unique_id(self, unique_id):
        module = Module.query.filter_by(unique_id=unique_id.data).first()

        if module is None:
            raise ValidationError('Unknown unique id')

        if module.user is not None:
            raise ValidationError('Module is already registed to a user')


class AddModuleFormAjax(AddModuleForm):
    submit = None

def BindWhitelistToModuleDynamicCtor(user: User):
    class Form(FlaskForm):
        pass

    for module in user.modules:
        form_name = f'{module.unique_id}_whitelists'

        users_whitelists = [(whitelist.id, whitelist.name) for whitelist in user.whitelists]

        setattr(Form, form_name, SelectMultipleField(
            'Select whitelists',
            choices=users_whitelists,
            default=[whitelist.id for whitelist in module.whitelists],
            coerce=int,
            render_kw={"class": "selectpicker"}))

        def validate(self, field):
            if not all(whitelist is not None for whitelist in field.data):
                raise ValidationError('Wrong whitelists')

        setattr(Form, 'validate_' + form_name, validate)

    return Form()
