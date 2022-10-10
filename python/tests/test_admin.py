import pytest

from sqlalchemy import text

from flaskr.db import get_db


@pytest.mark.parametrize('page', (
    '/admin/',
    '/admin/users',
    '/admin/posts',
    '/admin/comments'
))
def test_admin_authorization_required(client, auth, page):
    # Non-admin user
    auth.login('other', 'other')
    assert client.get(page).status_code == 403


@pytest.mark.parametrize(('page', 'expected'), (
        ('/admin/users', [b'<a href="/admin/users/edit/1">test</a>']),
        ('/admin/posts', [b'<a href="/admin/posts/edit/1">test title</a>', b'<td>test</td>', b'2022-01-01 00:00:00']),
        ('/admin/comments', [b'<a href="/admin/comments/edit/1">test title</a>', b'test', b'2022-02-01 00:00:00'])
))
def test_lists(client, auth, page, expected):
    auth.login()
    response = client.get(page)

    assert response.status_code == 200

    for part in expected:
        assert part in response.data


def test_edit_user(client, auth, app):
    auth.login()
    assert client.get('/admin/users/edit/1').status_code == 200

    client.post('/admin/users/edit/1', data={'username': 'updated'})

    with app.app_context():
        with get_db().connect() as conn:
            user = conn.execute(text('SELECT * FROM user WHERE id = 1;')).one()
            assert user['username'] == 'updated'


@pytest.mark.parametrize(('username', 'expected'), (
    ('', b'Username: This field is required.'),
    ('other', b'Username is already in use.')
))
def test_edit_user_validate(client, auth, username, expected):
    auth.login()

    response = client.post('/admin/users/edit/1', data={'username': username}, follow_redirects=True)
    assert expected in response.data


def test_edit_post(client, auth, app):
    auth.login()
    assert client.get('/admin/posts/edit/1').status_code == 200

    client.post('/admin/posts/edit/1', data={'title': 'updated title', 'body': 'updated body'})

    with app.app_context():
        with get_db().connect() as conn:
            post = conn.execute(text('SELECT * FROM post WHERE id = 1;')).one()
            assert post['title'] == 'updated title'
            assert post['body'] == 'updated body'


@pytest.mark.parametrize(('title', 'body', 'expected'), (
    ('', '', b'Title: This field is required.'),
    ('', 'body', b'Title: This field is required.'),
    ('title', '', b'Body: This field is required.')
))
def test_edit_post_validate(client, auth, title, body, expected):
    auth.login()

    response = client.post('/admin/posts/edit/1', data={'title': title, 'body': body})
    assert expected in response.data


def test_edit_comment(client, auth, app):
    auth.login()
    assert client.get('/admin/comments/edit/1').status_code == 200

    client.post('/admin/comments/edit/1', data={'body': 'updated body'})

    with app.app_context():
        with get_db().connect() as conn:
            comment = conn.execute(text('SELECT * FROM comment WHERE id = 1;')).one()
            assert comment['body'] == 'updated body'


@pytest.mark.parametrize(('body', 'expected'), (
    ('', b'Body: This field is required.'),
))
def test_edit_comment_validate(client, auth, body, expected):
    auth.login()

    response = client.post('/admin/comments/edit/1', data={'body': body})
    assert expected in response.data
