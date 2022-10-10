from sqlalchemy import text

from flaskr.db import get_db


def test_comment_form_requires_login(client, auth):
    required_elements = [
        b'div id="comment-form"',
        b'textarea id="body"',
        b'button id="submit-comment"'
    ]

    response = client.get('/1/')
    for element in required_elements:
        assert element not in response.data

    auth.login()
    response = client.get('/1/')
    for element in required_elements:
        assert element in response.data


def test_comment_validation(client, auth):
    auth.login()
    response = client.post('/comment/1/create', data={'body': ''}, follow_redirects=True)
    assert b'Comment body is required.' in response.data


def test_comment(client, auth, app):
    auth.login()
    response = client.post('/comment/1/create', data={'body': 'created comment'})
    assert response.is_json
    assert 'success' in response.json
    assert response.json['success']
    assert 'html' in response.json
    assert 'created comment' in response.json['html']

    with app.app_context():
        db = get_db()

        with db.connect() as conn:
            count = conn.execute(text('SELECT COUNT(id) FROM comment WHERE body="created comment";')).scalar_one()

        assert count == 1


def test_delete_validation(client, auth, app):
    with app.app_context():
        db = get_db()

        with db.connect() as conn:
            conn.execute(text('UPDATE comment SET author_id = 2 WHERE id = 1;'))
            conn.commit()

    auth.login()
    # Error message is show if comment doesn't exist
    response = client.post('/comment/delete/5', follow_redirects=True)
    assert 'Comment with id 5 does not exist.' in response.json['error']

    # User doesn't see delete link for comments that aren't theirs
    assert b'onclick="deleteComment(1);"' not in client.get('/1/').data

    # Error message is shown if user does not have permission to delete the comment
    response = client.post('/comment/delete/1')
    assert 'You do not have permission to delete this comment.' in response.json['error']

    # Confirm that the comment was not deleted.
    with app.app_context():
        db = get_db()

        with db.connect() as conn:
            comment = conn.execute(text('SELECT * FROM comment WHERE id = 1;')).one_or_none()

        assert comment is not None


def test_delete(client, auth, app):
    auth.login()
    response = client.post('/comment/delete/1')
    assert response.is_json
    assert 'success' in response.json
    assert response.json['success']

    with app.app_context():
        db = get_db()

        with db.connect() as conn:
            comment = conn.execute(text('SELECT * FROM comment WHERE id = 2;')).one_or_none()

        assert comment is None
