import pytest
from sqlalchemy import text

from flaskr.db import get_db


def test_index(client, auth):
    response = client.get('/')
    assert b'Login' in response.data
    assert b'Register' in response.data

    auth.login()
    response = client.get('/')
    assert b'Logout' in response.data
    assert b'href="/1/"' in response.data
    assert b'Test Title' in response.data
    assert b'by test on 2022-01-01' in response.data
    assert b'test body' in response.data


@pytest.mark.parametrize('path', ('/create', '/1/update', '/1/delete'))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers['Location'] == '/auth/login'


def test_author_required(app, client, auth):
    # Change the post author to another user
    with app.app_context():
        db = get_db()

        with db.connect() as conn:
            conn.execute(text('UPDATE post SET author_id = 2 WHERE author_id = 1;'))
            conn.commit()

    auth.login()
    # Current user cannot modify another user's post
    assert client.post('/1/update').status_code == 403
    # Current user cannot delete another user's post
    assert client.post('/1/delete').status_code == 403
    # Current user does not see edit link
    assert b'href="/1/update"' not in client.get('/').data


@pytest.mark.parametrize('path', ('/2/update', '/2/delete'))
def test_update_delete_require_post_to_exist(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_view_requires_post_to_exist(client):
    assert client.get('/2/').status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get('/create').status_code == 200

    client.post('/create', data={'title': 'created', 'body': ''})

    with app.app_context():
        db = get_db()

        with db.connect() as conn:
            count = conn.execute(text('SELECT COUNT(id) FROM post;')).scalar_one()
            assert count == 2


def test_view(client, auth, app):
    response = client.get('/1/')
    assert b'Test Title' in response.data
    assert b'by test on 2022-01-01' in response.data
    assert b'test body' in response.data

    auth.login()
    response = client.get('/1/')
    assert b'Test Title' in response.data
    assert b'by test on 2022-01-01' in response.data
    assert b'test body' in response.data
    assert b'href="/1/update"' in response.data


def test_update(client, auth, app):
    auth.login()
    assert client.get('/1/update').status_code == 200

    client.post('/1/update', data={'title': 'updated', 'body': ''})

    with app.app_context():
        db = get_db()

        with db.connect() as conn:
            post = conn.execute(text('SELECT * FROM post WHERE id = 1;')).one()
            assert post['title'] == 'updated'


@pytest.mark.parametrize('path', ('/create', '/1/update'))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data


def test_delete(client, auth, app):
    auth.login()
    response = client.post('/1/delete')
    assert response.headers['Location'] == '/'

    with app.app_context():
        db = get_db()

        with db.connect() as conn:
            post = conn.execute(text('SELECT * FROM post WHERE id = 1;')).one_or_none()

        assert post is None
