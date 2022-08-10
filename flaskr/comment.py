from flask import (Blueprint, request, flash, g, redirect, url_for)

from flaskr.db import get_db
from flaskr.auth import login_required

bp = Blueprint('comment', __name__, url_prefix='/comment')


def get_comments(post_id: int):
    comments = get_db().execute(
        'SELECT c.id, c.author_id, c.body, c.created, u.username '
        'FROM comment c '
        'JOIN user u on c.author_id = u.id '
        'WHERE c.post_id = ?;',
        (post_id,)
    ).fetchall()

    return comments


@bp.route('/<int:post_id>/create', methods=('POST',))
@login_required
def create(post_id: int):
    body = request.form['body']
    error = None

    if not body:
        error = 'Comment body is required.'

    if error is not None:
        flash(error)
    else:
        db = get_db()

        db.execute('INSERT INTO comment (post_id, author_id, body) VALUES (?, ?, ?);', (post_id, g.user['id'], body))
        db.commit()

    return redirect(url_for('blog.view', id=post_id))


@bp.route('/<int:post_id>/delete/<int:comment_id>')
@login_required
def delete(post_id: int, comment_id: int):
    db = get_db()
    db.execute('DELETE FROM comment WHERE id = ?;', (comment_id,))
    db.commit()

    return redirect(url_for('blog.view', id=post_id))
