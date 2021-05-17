from flask import Blueprint, flash, redirect, url_for, render_template, request, current_app, jsonify
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from sqlalchemy.orm import Query
from wtforms import StringField, SelectField, SubmitField, ValidationError, HiddenField
from wtforms.validators import DataRequired, Length, Regexp

from ..db import db
from ..db.helpers import get_whitelists_for_user_query, get_modules_for_user_query, get_plates_for_whitelist_query
from ..models import Whitelist, Plate, Module
from ..helpers import AjaxForm, process_bootstrap_table_request

bp = Blueprint('whitelists', __name__, url_prefix='/whitelists')

#
# Whitelists View
#

class AddWhitelistForm(FlaskForm):
    whitelist_name = StringField('Whitelist name', validators=[DataRequired(), Length(2)])
    modules_assign = SelectField('Module to assign', validators=[DataRequired()])

    UNNASIGNED_STR = 'Unassigned'

    def validate_whitelist_name(self, whitelist_name):
        possible_users_whitelist = get_whitelists_for_user_query(current_user).filter(Whitelist.name == whitelist_name.data).first()

        if possible_users_whitelist is not None:
            raise ValidationError('This name is already taken')

    def validate_modules_assign(self, modules_assign):
        if modules_assign.data != self.UNNASIGNED_STR:
            module = get_modules_for_user_query(current_user).filter(Module.unique_id == modules_assign.data).first()

            if module is None:
                raise ValidationError('Wrong modules unique_id')

    def get_modules_assign_module(self):
        return get_modules_for_user_query(current_user).filter(Module.unique_id == self.modules_assign.data).first()


@bp.route('')
@login_required
def index():
    form = AddWhitelistForm()
    form.modules_assign.choices = [module.unique_id for module in current_user.modules] + [AddWhitelistForm.UNNASIGNED_STR]

    return render_template('whitelists.html', whitelists=current_user.whitelists, form=form)


@bp.route('/add', methods=['POST'])
@login_required
def add_ajax():
    form = AddWhitelistForm()
    form.modules_assign.choices = [module.unique_id for module in current_user.modules] + [AddWhitelistForm.UNNASIGNED_STR]

    if not form.validate_on_submit():
        result = {'errors': {}}
        for field in form:
            if field.errors:
                result['errors'][field.name] = [error for error in field.errors]

        return result, 409
    else:
        whitelist = Whitelist(name=form.whitelist_name.data)
        current_user.whitelists.append(whitelist)

        possible_module = form.get_modules_assign_module()
        if possible_module is not None:
            possible_module.whitelists.append(whitelist)

        db.session.commit()

        flash(f'Added a whitelist: {whitelist.name}')
        return '', 201


@bp.route('/get')
@login_required
def get():
    total, totalNotFiltered, whitelists = process_bootstrap_table_request(
        get_whitelists_for_user_query(current_user),
        Whitelist.name,
        Whitelist.name
    )

    return {
        'total': total,
        'totalNotFiltered': totalNotFiltered,
        'rows': [{
            'id': whitelist.id,
            'name': whitelist.name
        } for whitelist in whitelists.all()]
    }

class AddPlateForm(AjaxForm):
    plate = StringField('Plate', validators=[DataRequired()], render_kw={'placeholder': 'Plate...'})
    whitelist_id = HiddenField('whitelist_id', validators=[DataRequired()])

    def validate_whitelist_id(self, whitelist_id):
        whitelist = get_whitelists_for_user_query(current_user).filter(Whitelist.id == whitelist_id.data).first()

        if whitelist is None:
            raise ValidationError('Wrong whitelist id')

    def validate_plate(self, plate):
        if not Plate.is_valid_plate(plate.data):
            raise ValidationError('Plate does not comply to policy')

        possible_plate = (Whitelist.query
            .join(Plate, Whitelist.id == Plate.whitelist_id)
            .filter(Whitelist.id == self.whitelist_id.data)
            .filter(Plate.text == plate.data)).first()

        if possible_plate is not None:
            raise ValidationError('Plate already in a whitelist')

class RemovePlateForm(AjaxForm):
    plate_ids = HiddenField('plate_ids', validators=[DataRequired()])
    whitelist_id = HiddenField('whitelist_id', validators=[DataRequired(), Regexp(r'\d+(,\d+)*')])

    def validate_whitelist_id(self, whitelist_id):
        whitelist = get_whitelists_for_user_query(current_user).filter(Whitelist.id == whitelist_id.data).first()

        if whitelist is None:
            raise ValidationError('Wrong whitelist id')

    def validate_plate_ids(self, plate_ids):
        plate_ints = self.get_plate_id_int_list()

        whitelist = get_whitelists_for_user_query(current_user).filter(Whitelist.id == self.whitelist_id.data).first()
        if whitelist is None:
            raise ValidationError('Invalid whitelist id')

        query = get_plates_for_whitelist_query(whitelist) \
            .filter(Plate.id.in_(plate_ints))

        if len(plate_ints) != query.count():
            raise ValidationError('Some ids are wrong')

    def get_plate_id_int_list(self):
        return [int(plate_id) for plate_id in self.plate_ids.data.split(',')]

    def get_plates_query(self) -> Query:
        plate_ints = self.get_plate_id_int_list()
        query = get_plates_for_whitelist_query(Whitelist.query.get(self.whitelist_id.data)) \
            .filter(Plate.id.in_(plate_ints))
        return query


@bp.route('/edit/<int:whitelist_id>')
@login_required
def edit(whitelist_id):
    whitelist = get_whitelists_for_user_query(current_user) \
        .filter(Whitelist.id == whitelist_id).first()

    if whitelist is None:
        flash('Unknown whitelist id')
        return redirect(url_for('index.index'))

    add_plate_form = AddPlateForm(whitelist_id=whitelist_id)
    remove_plate_form = RemovePlateForm(whitelist_id=whitelist_id)

    return render_template('edit_whitelist.html', whitelist=whitelist, add_plate_form=add_plate_form, remove_plate_form=remove_plate_form)


@bp.route('/edit/<int:whitelist_id>/get')
@login_required
def edit_get_plates(whitelist_id):
    whitelist = get_whitelists_for_user_query(current_user).filter(Whitelist.id == whitelist_id).first()

    if whitelist is None:
        return {}

    total, totalNotFiltered, query = process_bootstrap_table_request(
        get_plates_for_whitelist_query(whitelist),
        Plate.text,
        Plate.text
    )

    return {
        'total': total,
        'totalNotFiltered': totalNotFiltered,
        'rows': [{
            'id': plate.id,
            'text': plate.text
        } for plate in query.all()]
    }


@bp.route('/edit/<int:whitelist_id>/add_plate', methods=['POST'])
@login_required
def edit_add_plate(whitelist_id):
    form = AddPlateForm(whitelist_id=whitelist_id)

    if not form.validate_on_submit():
        return form.generate_failed_response_dict(), 409
    else:
        plate = Plate(text=form.plate.data)
        whitelist = Whitelist.query.get(form.whitelist_id.data)
        whitelist.plates.append(plate)
        db.session.commit()
        flash(f'Added plate: {plate.text}')
        return {'plate': plate.text}, 201


@bp.route('/edit/<int:whitelist_id>/remove_plates', methods=['POST'])
@login_required
def edit_remove_plates(whitelist_id):
    form = RemovePlateForm(whitelist_id=whitelist_id)

    if not form.validate_on_submit():
        return form.generate_failed_response_dict(), 409
    else:
        query = form.get_plates_query()
        removed_string = ', '.join(plate.text for plate in query.all())
        flash(f'Sucessfully removed plates: {removed_string}')
        query.delete()
        db.session.commit()
        return '', 201


@bp.route('/remove', methods=['POST'])
@login_required
def remove():
    whitelist_ids = request.args.getlist('id', None)
    if whitelist_ids is None:
        flash('Not correct whitelist id')
        return redirect(url_for('whitelists.index'))

    whitelists = get_whitelists_for_user_query(current_user) \
        .filter(Whitelist.id.in_(whitelist_ids))

    whitelists_string = ', '.join(whitelist.name for whitelist in whitelists.all())

    flash(f'Deleted {whitelists_string} whitelists')
    whitelists.delete()
    db.session.commit()
    return redirect(url_for('whitelists.index'))
