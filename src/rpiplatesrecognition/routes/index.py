from flask import Blueprint, render_template
from flask_login import current_user

bp = Blueprint('index', __name__)

#
# Home page View
#

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html')
