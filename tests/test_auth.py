import pytest
from sqlalchemy import text

from flask import g, session

import flaskr.auth.models
from flaskr.db import get_db


def test_register(client, app):
    assert client.get('/auth/register').status_code == 200

    response = client.post(
        '/auth/register',
        data={'username': 'a', 'password': 'a'}
    )
    assert response.headers['Location'] == '/auth/login'

    with app.app_context():
        db = get_db()

        with db.connect() as conn:
            user = conn.execute(
                text("SELECT * FROM user WHERE username = 'a';")
            ).one_or_none()

            assert user is not None
            assert user['group'] == 'READER'


@pytest.mark.parametrize(('username', 'password', 'message'), (
        ('', '', b'Username: This field is required.'),
        ('a', '', b'Password: This field is required.'),
        ('test', 'test', b'is already registered.')
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data


def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200

    response = auth.login()
    assert response.headers['Location'] == '/'

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'
        assert g.user_group == flaskr.auth.models.Admin


@pytest.mark.parametrize(('username', 'password', 'message'), (
        ('a', 'test', b'Incorrect username.'),
        ('test', 'a', b'Incorrect password.')
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session


@pytest.mark.parametrize(('group', 'expected_status_code'), (
        ('DEFAULT', 403),
        ('READER', 403),
        ('AUTHOR', 403),
        ('ADMIN', 200)
))
def test_admin_required(client, auth, app, group, expected_status_code):
    with app.app_context():
        with get_db().connect() as conn:
            conn.execute(
                text('UPDATE user SET `group`=:group WHERE id=1;'),
                {'group': group}
            )
            conn.commit()

        auth.login()
        assert client.get('/admin/').status_code == expected_status_code


@pytest.mark.parametrize(('group', 'expected_status_code'), (
        ('DEFAULT', 403),
        ('READER', 403),
        ('AUTHOR', 200),
        ('ADMIN', 200)
 ))
def test_can_post_required(client, auth, app, group, expected_status_code):
    with app.app_context():
        with get_db().connect() as conn:
            conn.execute(
                text('UPDATE user SET `group`=:group WHERE id=1;'),
                {'group': group}
            )
            conn.commit()

        auth.login()
        assert client.get('/1/update').status_code == expected_status_code
        assert client.post('/1/update', data={'title': 'update', 'body': 'updated'}, follow_redirects=True).status_code == expected_status_code


@pytest.mark.parametrize(('group', 'expected_status_code'), (
        ('DEFAULT', 403),
        ('READER', 200),
        ('AUTHOR', 200),
        ('ADMIN', 200)
))
def test_can_comment_required(client, auth, app, group, expected_status_code):
    with app.app_context():
        with get_db().connect() as conn:
            conn.execute(
                text('UPDATE user SET `group`=:group WHERE id=1;'),
                {'group': group}
            )
            conn.commit()

        auth.login()
        assert client.post('/comment/1/create', data={'body': 'comment'}).status_code == expected_status_code
