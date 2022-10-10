from flask import Blueprint

bp = Blueprint('blog', __name__, template_folder='templates')

from . import blog, comment, profile
