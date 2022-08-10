from flask import Blueprint, abort, render_template

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('user', __name__, url_prefix='/user')


def get_user_profile(user_id: int):
    db = get_db()

    user = db.execute(
        'SELECT u.id, u.username, u.password FROM user u WHERE id = ?;',
        (user_id,)
    ).fetchone()

    if user is None:
        abort(404, f'Post id {user_id} does not exist.')

    posts = db.execute(
        'SELECT p.id, p.created, p.title, p.body FROM post p WHERE p.author_id = ?;',
        (user_id,)
    ).fetchall()

    comments = db.execute(
        'SELECT c.id, c.post_id, c.created, c.body, p.title FROM comment c '
        'LEFT JOIN post p ON p.author_id = c.author_id '
        'WHERE c.author_id = ?;',
        (user_id,)
    ).fetchall()

    return user, posts, comments


@bp.route('/<int:user_id>/')
@login_required
def view(user_id: int):
    user, posts, comments = get_user_profile(user_id)

    return render_template('profile/view.html', user=user, posts=posts, comments=comments)
