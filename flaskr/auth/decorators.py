import functools

from flask import redirect, url_for, abort, session


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        user = session.get('user')

        if user is None:
            return redirect(url_for('auth.login'))

        return view(*args, **kwargs)

    return wrapped_view


def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        user = session.get('user')

        if user is not None:
            if user.permissions.ADMIN:
                return view(*args, **kwargs)

        abort(403)

    return wrapped_view


def can_post_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        user = session.get('user')

        if user is not None:
            if session['user'].permissions.CAN_POST:
                return view(*args, **kwargs)

        abort(403)

    return wrapped_view


def can_comment_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        user = session.get('user')

        if user is not None:
            if session['user'].permissions.CAN_COMMENT:
                return view(*args, **kwargs)

        abort(403)

    return wrapped_view
