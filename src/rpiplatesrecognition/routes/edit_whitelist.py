from flask import Blueprint, flash, redirect, url_for, render_template
from flask_login import current_user, login_required

from ..db.helpers import get_whitelists_for_user_query
from ..forms import AddPlateForm
from ..models import Whitelist, Plate

bp = Blueprint('edit_whitelist', __name__, url_prefix='edit_whitelist')

@bp.route('/<int:whitelist_id>')
@login_required
def index(whitelist_id):
        whitelist = get_whitelists_for_user_query(current_user) \
            .filter(Whitelist.id == whitelist_id).first()

        if whitelist is None:
            flash('Unknown whitelist id')
            return redirect(url_for('index'))

        form = AddPlateForm(whitelist_id = whitelist.id)

        return render_template('edit_whitelist.html', whitelist=whitelist, form=form)


@app.route('/edit_whitelist/add_plate', methods=['POST'])
@login_required
def edit_whitelist_add_plate():
    form = AddPlateForm()

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
