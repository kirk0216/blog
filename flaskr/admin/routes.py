import sqlalchemy.exc
from flask import render_template, redirect, url_for, request, flash
from sqlalchemy import text

from . import bp
from flaskr.auth import login_required, csrf_protection
from flaskr.db import get_db
from flaskr import utils

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


@bp.route('/posts')
@login_required
def list_posts():
    with get_db().connect() as conn:
        posts = conn.execute(
            text(
                'SELECT p.id, p.author_id, p.created, p.title, p.body, u.username as "author" FROM post p '
                'JOIN user u ON u.id = p.author_id;'
            )
        )

        return render_template('admin/post_list.html', posts=posts)


@bp.route('/posts/edit/<int:id>', methods=('GET', 'POST'))
@login_required
@csrf_protection
def edit_post(id: int):
    with get_db().connect() as conn:
        post = conn.execute(
            text(
                'SELECT p.id, p.author_id, p.created, p.title, p.body, u.username as "author" FROM post p '
                'JOIN user u ON u.id = p.author_id '
                'WHERE p.id = :id;'
            ),
            {'id': id}
        ).one_or_none()

        if request.method == 'POST':
            title = utils.get_form_value('title')
            body = utils.get_form_value('body')
            error = None

            print('%s' % title)

            if None in [title, body]:
                error = 'Title and body cannot be empty.'
            else:
                try:
                    conn.execute(
                        text('UPDATE post SET title=:title, body=:body WHERE id=:id;'),
                        {'title': title, 'body': body, 'id': id}
                    )
                    conn.commit()
                except sqlalchemy.exc.DatabaseError:
                    error = 'There was an error saving your changes.'

            if error is not None:
                flash(error)
            else:
                return redirect(url_for('admin.list_posts'))

    return render_template('admin/post_edit.html', post=post)
