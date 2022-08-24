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
        ).all()

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


@bp.route('/comments')
@login_required
def list_comments():
    with get_db().connect() as conn:
        comments = conn.execute(
            text(
                'SELECT c.id, c.post_id, c.author_id, c.created, '
                'u.username AS "author", p.title AS "post_title" FROM comment c '
                'JOIN post p ON p.id = c.post_id '
                'JOIN user u ON u.id = c.author_id;'
            )
        ).all()

        return render_template('admin/comment_list.html', comments=comments)


@bp.route('/comments/edit/<int:id>', methods=('GET', 'POST'))
@login_required
@csrf_protection
def edit_comment(id: int):
    with get_db().connect() as conn:
        comment = conn.execute(
            text(
                'SELECT c.id, c.post_id, c.author_id, c.body FROM comment c '
                'WHERE c.id=:id;'
            ),
            {'id': id}
        ).one_or_none()

        if request.method == 'POST':
            body = utils.get_form_value('body')
            error = None

            if body is None:
                error = 'Comment body cannot be empty.'
            else:
                try:
                    conn.execute(
                        text('UPDATE comment SET body=:body WHERE id=:id;'),
                        {'body': body, 'id': id}
                    )
                    conn.commit()
                except sqlalchemy.exc.DatabaseError:
                    error = 'A database error occurred.'

            if error is not None:
                flash(error)
            else:
                return redirect(url_for('admin.list_comments'))

    return render_template('admin/comment_edit.html', comment=comment)
