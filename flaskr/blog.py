from flask import (Blueprint, flash, g, redirect, render_template, request, url_for)
from werkzeug.exceptions import abort

from flaskr.auth import login_required, csrf_protection
from flaskr.db import get_db
from flaskr.comment import get_comments

from flaskr.utils import get_form_value

bp = Blueprint('blog', __name__)


def get_post(post_id: int, check_author: bool = True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username '
        'FROM post p '
        'JOIN user u ON p.author_id = u.id WHERE p.id = ?;',
        (post_id,)
    ).fetchone()

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

    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username '
        'FROM post p JOIN user u ON p.author_id = u.id ORDER BY created DESC;'
    ).fetchall()

    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@csrf_protection
@login_required
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

            db.execute('INSERT INTO post (title, body, author_id) VALUES (?, ?, ?);', (title, body, g.user['id']))
            db.commit()

            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


@bp.route('/<int:id>/', methods=('GET',))
def view(id: int):
    post = get_post(id, False)
    comments = get_comments(id)

    return render_template('blog/view.html', post=post, comments=comments)


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@csrf_protection
@login_required
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
            db.execute('UPDATE post SET title = ?, body = ? WHERE id = ?;', (title, body, id))
            db.commit()

            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@csrf_protection
@login_required
def delete(id: int):
    get_post(id)

    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?;', (id,))
    db.commit()

    return redirect(url_for('blog.index'))
