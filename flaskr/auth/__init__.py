import functools
from flask import Blueprint, redirect, url_for, abort, g

bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates')

from . import routes, models


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(*args, **kwargs)

    return wrapped_view


def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is not None:
            group: models.UserGroup = models.GROUPS[g.user['group']]

            if group.ADMIN:
                return view(*args, **kwargs)

        abort(403)

    return wrapped_view


def can_post_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is not None:
            group: models.UserGroup = models.GROUPS[g.user['group']]

            if group.CAN_POST:
                return view(*args, **kwargs)

        abort(403)

    return wrapped_view


def can_comment_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is not None:
            group: models.UserGroup = models.GROUPS[g.user['group']]

            if group.CAN_COMMENT:
                return view(*args, **kwargs)

        abort(403)

    return wrapped_view
