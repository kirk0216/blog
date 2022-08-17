from flask import (Blueprint, render_template, request, flash, g, redirect, url_for, g)

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


def get_comment(comment_id: int):
    comment = get_db().execute(
        'SELECT c.id, c.post_id, c.author_id, c.body, c.created, u.username '
        'FROM comment c '
        'JOIN user u ON u.id == c.author_id '
        'WHERE c.id == ?;',
        (comment_id,)
    ).fetchone()

    return comment


@bp.route('/<int:post_id>/create', methods=('POST',))
@login_required
def create(post_id: int):
    body = request.form['body']
    error = None

    if not body:
        error = 'Comment body is required.'

    if error is None:
        db = get_db()

        result = db.execute(
            'INSERT INTO comment (post_id, author_id, body) VALUES (?, ?, ?);',
            (post_id, g.user['id'], body)
        )
        db.commit()

        return {
            'success': True,
            'html': render_template('comment/comment.html', comment=get_comment(result.lastrowid))
        }

    return {'success': False, 'error': error}


@bp.route('/delete/<int:comment_id>', methods=('POST',))
@login_required
def delete(comment_id: int):
    comment = get_comment(comment_id)
    error = None

    if comment is None:
        error = 'Comment with id %s does not exist.' % str(comment_id)
    elif comment['author_id'] != g.user['id']:
        error = 'You do not have permission to delete this comment.'

    if error is None:
        db = get_db()
        db.execute('DELETE FROM comment WHERE id = ?;', (comment_id,))
        db.commit()

        return {'success': True}
    else:
        return {'success': False, 'error': error}
