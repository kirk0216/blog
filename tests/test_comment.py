from flaskr.db import get_db


def test_comment_form_requires_login(client, auth):
    response = client.get('/1/')
    assert b'action="/comment/1/create' not in response.data
    assert b'textarea id="body"' not in response.data
    assert b'input type="submit" value="Save"' not in response.data

    auth.login()
    response = client.get('/1/')
    assert b'action="/comment/1/create' in response.data
    assert b'textarea name="body"' in response.data
    assert b'input type="submit" value="Save"' in response.data


def test_comment_validation(client, auth):
    auth.login()
    response = client.post('/comment/1/create', data={'body': ''}, follow_redirects=True)
    assert b'Comment body is required.' in response.data


def test_comment(client, auth, app):
    auth.login()
    response = client.post('/comment/1/create', data={'body': 'created comment'})
    assert response.headers['Location'] == '/1/'

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM comment WHERE body="created comment";').fetchone()[0]
        assert count == 1


def test_delete_validation(client, auth, app):
    with app.app_context():
        db = get_db()
        db.execute('UPDATE comment SET author_id = 5 WHERE id = 1;')
        db.commit()

    auth.login()
    # Error message is show if comment doesn't exist
    response = client.post('/comment/1/delete/5', follow_redirects=True)
    assert b'Comment with id 5 does not exist.' in response.data

    # User doesn't see delete link for comments that aren't theirs
    assert b'form action="/comment/1/delete/1' not in client.get('/1/').data

    # Error message is shown if user does not have permission to delete the comment
    response = client.post('/comment/1/delete/1', follow_redirects=True)
    assert b'You do not have permission to delete this comment.' in response.data

    # Confirm that the comment was not deleted.
    with app.app_context():
        db = get_db()
        comment = db.execute('SELECT * FROM comment WHERE id = 1;').fetchone()
        assert comment is not None


def test_delete(client, auth, app):
    auth.login()
    response = client.post('/comment/1/delete/1')
    assert response.headers['Location'] == '/1/'

    with app.app_context():
        db = get_db()
        comment = db.execute('SELECT * FROM comment WHERE id = 2;').fetchone()
        assert comment is None
