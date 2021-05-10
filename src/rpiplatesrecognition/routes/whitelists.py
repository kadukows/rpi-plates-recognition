from flask import Blueprint, flash, redirect, url_for, render_template, request
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, ValidationError, HiddenField
from wtforms.validators import DataRequired, Length

from ..db import db
from ..db.helpers import get_whitelists_for_user_query, get_modules_for_user_query
from ..models import Whitelist, Plate, Module

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


@bp.route('/edit/<int:whitelist_id>')
@login_required
def edit(whitelist_id):
        whitelist = get_whitelists_for_user_query(current_user) \
            .filter(Whitelist.id == whitelist_id).first()

        if whitelist is None:
            flash('Unknown whitelist id')
            return redirect(url_for('index.index'))

        form = AddPlateForm(whitelist_id=whitelist_id)

        return render_template('edit_whitelist.html', whitelist=whitelist, form=form)


@bp.route('/edit/<int:whitelist_id>/add_plate', methods=['POST'])
@login_required
def edit_add_plate(whitelist_id):
    form = AddPlateForm(whitelist_id=whitelist_id)

    if not form.validate_on_submit():
        result = {'errors': {}}
        for field in form:
            if field.errors:
                result['errors'][field.name] = [error for error in field.errors]

        return result, 409
    else:
        plate = Plate(text=form.plate.data)
        whitelist = Whitelist.query.get(form.whitelist_id.data)
        whitelist.plates.append(plate)
        db.session.commit()
        flash(f'Added plate: {plate.text}')
        return {'plate': plate.text}, 201


@bp.route('/edit/<int:whitelist_id>/remove_plate', methods=['POST'])
@login_required
def edit_remove_plate(whitelist_id):
    whitelist = (Whitelist.query
        .filter(Whitelist.user_id == current_user.id)
        .filter(Whitelist.id == whitelist_id)).first()

    if whitelist is None:
        flash('Wrong whitelist')
        return redirect(url_for('index.index'))

    plate_id = request.args.get('plate_id', None)

    if plate_id is None:
        flash("Wrong plate")
        return redirect(url_for('whitelists.edit', whitelist_id=whitelist_id))

    plate_query = (Plate.query
        .filter(Plate.whitelist_id == whitelist_id)
        .filter(Plate.id == plate_id))

    if plate_query.count() == 0:
        flash('Wrong plate')
        return redirect(url_for('whitelists.edit', whitelist_id=whitelist_id))

    plate = plate_query.first()
    plate_query.delete()
    flash(f'Sucessfully removed plate: {plate.text}')
    db.session.commit()
    return redirect(url_for('whitelists.edit', whitelist_id=whitelist_id))


@bp.route('/remove', methods=['POST'])
@login_required
def remove():
    whitelist_id = request.args.get('whitelist_id', None)
    if whitelist_id is None:
        flash('Not correct whitelist id')
        return redirect(url_for('whitelists.index'))

    whitelist = Whitelist.query.filter_by(id=whitelist_id).first()

    if whitelist is None:
        flash('Wrong whitelist id')
    else:
        flash(f'Deleted {whitelist.name} whitelist')
        db.session.delete(whitelist)
        db.session.commit()
    return redirect(url_for('whitelists.index'))


class AddPlateForm(FlaskForm):
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
