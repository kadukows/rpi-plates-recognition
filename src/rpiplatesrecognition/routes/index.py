from flask import Blueprint, render_template
from flask_login import current_user

bp = Blueprint('index', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html')
