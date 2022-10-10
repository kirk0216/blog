import functools

from flask import abort, redirect, request, session, url_for

from flaskr.auth.models import User


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        user = session.get('user')

        if user is None:
            session['login_redirect'] = request.path
            return redirect(url_for('auth.login'))

        return view(*args, **kwargs)

    return wrapped_view


def required_permissions(permissions: list[str]):
    def decorated_function(view):
        @functools.wraps(view)
        def wrapped_view(*args, **kwargs):
            user: User = session.get('user')

            if user is not None:
                for permission in permissions:
                    if permission not in user.permissions:
                        abort(403)

            return view(*args, **kwargs)

        return wrapped_view

    return decorated_function
