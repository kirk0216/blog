from flask import (Blueprint, flash, g, redirect, render_template, request, url_for)
from werkzeug.exceptions import abort
from sqlalchemy import text

from flaskr.auth import login_required, csrf_protection
from flaskr.db import get_db
from flaskr.comment import get_comments

from flaskr.utils import get_form_value

bp = Blueprint('blog', __name__)


def get_post(post_id: int, check_author: bool = True):
    db = get_db()

    with db.connect() as conn:
        post = conn.execute(
            text('SELECT p.id, title, body, created, author_id, username '
                 'FROM post p '
                 'JOIN "user" u ON p.author_id = u.id WHERE p.id = :id;'),
            {'id': post_id}
        ).one_or_none()

    if post is None:
        abort(404, f'Post id {post_id} does not exist.')

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


def get_post_details_from_form():
    return get_form_value('title'), get_form_value('body'), get_form_value('csrf_token')


@bp.route('/')
def index():
    db = get_db()

    with db.connect() as conn:
        posts = conn.execute(
            text('SELECT p.id, title, body, created, author_id, username '
                 'FROM post p JOIN "user" u ON p.author_id = u.id ORDER BY created DESC;')
        ).all()

    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
@csrf_protection
def create():
    if request.method == 'POST':
        title, body, csrf_token = get_post_details_from_form()
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()

            with db.connect() as conn:
                conn.execute(
                    text('INSERT INTO post (title, body, author_id) VALUES (:title, :body, :author_id);'),
                    {'title': title, 'body': body, 'author_id': g.user['id']}
                )
                conn.commit()

            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


@bp.route('/<int:id>/', methods=('GET',))
def view(id: int):
    post = get_post(id, False)
    comments = get_comments(id)

    return render_template('blog/view.html', post=post, comments=comments)


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
@csrf_protection
def update(id: int):
    post = get_post(id)

    if request.method == 'POST':
        title, body, csrf_token = get_post_details_from_form()
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()

            with db.connect() as conn:
                conn.execute(
                    text('UPDATE post SET title = :title, body = :body WHERE id = :post_id;'),
                    {'title': title, 'body': body, 'post_id': id}
                )
                conn.commit()

            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
@csrf_protection
def delete(id: int):
    get_post(id)

    db = get_db()

    with db.connect() as conn:
        conn.execute(text('DELETE FROM post WHERE id = :post_id;'), {'post_id': id})
        conn.commit()

    return redirect(url_for('blog.index'))
