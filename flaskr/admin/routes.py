import sqlalchemy.exc
from flask import render_template, redirect, url_for, request, flash
from sqlalchemy import text

from . import bp
from flaskr.auth import login_required, csrf_protection
from flaskr.db import get_db

sections = ['users', 'posts', 'comments']


@bp.route('/')
@login_required
def index():
    return render_template('admin/index.html', sections=sections)


@bp.route('/users')
@login_required
def list_users():
    with get_db().connect() as conn:
        users = conn.execute(
            text('SELECT u.id, u.username FROM user u;')
        ).all()

    return render_template('admin/user_list.html', users=users)


@bp.route('/users/edit/<int:id>', methods=('GET', 'POST'))
@login_required
@csrf_protection
def edit_user(id: int):
    with get_db().connect() as conn:
        user = conn.execute(
            text('SELECT u.id, u.username FROM user u WHERE u.id = :id;'),
            {'id': id}
        ).one_or_none()

    if request.method == 'POST':
        username = request.form['username']
        error = None

        if username is None or len(username) == 0:
            error = 'Username cannot be blank.'

        with get_db().connect() as conn:
            try:
                conn.execute(
                    text('UPDATE user SET username=:username WHERE id = :id;'),
                    {'username': username, 'id': id}
                )
                conn.commit()
            except sqlalchemy.exc.IntegrityError:
                error = 'Username is already in use.'

        if error is not None:
            flash(error)
        else:
            return redirect(url_for('admin.list_users'))

    return render_template('admin/user_edit.html', user=user)
