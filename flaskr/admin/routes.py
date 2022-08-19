from flask import render_template

from . import bp
from flaskr.auth import login_required


@bp.route('/')
@login_required
def index():
    return render_template('admin/index.html')
