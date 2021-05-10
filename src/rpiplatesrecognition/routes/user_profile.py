from flask import Blueprint, flash, redirect, url_for, render_template
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo

from ..db import db


bp = Blueprint('user_profile', __name__, url_prefix='/user_profile')

#
# USers profile view
#

@bp.route('')
@login_required
def index():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash(f'Password change was successful!')
        return redirect(url_for('index.index'))

    return render_template('user_profile.html', form=form)

class ChangePasswordForm(FlaskForm):
    new_password = PasswordField('Password', validators=[DataRequired()])
    new_password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change password')
