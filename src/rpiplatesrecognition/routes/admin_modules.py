from flask import Blueprint, render_template
from flask_login import current_user, login_required

from ..auth import admin_required
from ..models import Module

bp = Blueprint('admin_modules', __name__, url_prefix='/admin_modules')

@bp.route('')
@login_required
@admin_required
def index():
    return render_template('admin_modules.html', modules=Module.query.all())
