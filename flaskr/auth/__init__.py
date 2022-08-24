import functools
from flask import Blueprint, current_app, request, redirect, url_for, flash, session, abort, g

bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates')

from . import routes
from flaskr import utils


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


def csrf_protection(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not current_app.config.get('TESTING') and request.method == 'POST':
            token = utils.get_form_value('csrf_token')
            error = validate_csrf_token(token)

            validate_origin_and_referer()
            validate_fetch_site()

            if error is not None:
                flash(error)
                return redirect(url_for('index'))

        return view(**kwargs)

    return wrapped_view


def validate_csrf_token(token) -> str:
    # Validate CSRF token
    if token is None or token != session['csrf_token']:
        return 'CSRF token is invalid. ' \
                'Please try again. ' \
                'If this error continues, please contact an administrator.'

    return None


def validate_origin_and_referer():
    config_origin = current_app.config.get('ORIGIN')
    origin = request.headers['Origin'] if 'Origin' in request.headers else None
    referer = request.headers['Referer'] if 'Referer' in request.headers else None

    # Allow the request if both Origin and Referer are None, or if the ORIGIN config value is not set.
    if not (config_origin is None or (origin is None and referer is None)):
        # Check that one of Origin or Referer is set and matches our configured Origin
        if (origin is not None and origin != config_origin) and \
                (referer is not None and referer != config_origin):
            abort(403)


def validate_fetch_site():
    # A request with the following Sec-Fetch-Site values will be allowed.
    # https://web.dev/fetch-metadata/
    allowed_fetch_sites = ['same-origin', 'same-site', 'none']

    if 'Sec-Fetch-Site' in request.headers and not request.headers['Sec-Fetch-Site'] in allowed_fetch_sites:
        abort(403)
