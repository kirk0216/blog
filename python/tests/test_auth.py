import pytest
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy import text
from werkzeug.security import check_password_hash

from flask import request, session

from flaskr.db import get_db


def test_register(client, app):
    assert client.get('/auth/register').status_code == 200

    response = client.post(
        '/auth/register',
        data={'username': 'a', 'email': 'a@test.com', 'password': 'a', 'confirm': 'a'}
    )

    assert response.headers['Location'] == '/auth/login'

    with app.app_context():
        with get_db().connect() as conn:
            user = conn.execute(
                text("SELECT * FROM user WHERE username = 'a';")
            ).one_or_none()

            assert user is not None
            assert user['group'] == 'READER'


@pytest.mark.parametrize(('username', 'password', 'confirm', 'email', 'message'), (
        ('', '', '', '', b'Username: This field is required.'),
        ('a', '', '', '', b'Password: This field is required.'),
        ('test', 'test', 'test', 'test@test.com', b'is already registered.'),
        ('a', 'password', 'nomatch', 'test@test.com', b'Passwords must match')
))
def test_register_validate_input(client, username, password, confirm, email, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'email': email, 'password': password, 'confirm': confirm}
    )
    assert message in response.data


def test_login(client, auth):
    with client:
        assert client.get('/auth/login').status_code == 200

        response = auth.login()
        assert response.request.path == '/'

        client.get('/')

        user = session.get('user')
        assert user is not None
        assert user.id == 1
        assert user.username == 'test'
        assert 'ADMIN' in user.permissions
        assert 'CAN_POST' in user.permissions
        assert 'CAN_COMMENT' in user.permissions


@pytest.mark.parametrize(('username', 'password', 'message'), (
        ('a', 'test', b'Incorrect username.'),
        ('test', 'a', b'Incorrect password.')
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_login_redirects(auth, app, client):
    with client:
        response = client.get('/user/1', follow_redirects=True)
        assert request.path == '/auth/login'
        assert b'id="redirect" name="redirect" type="hidden" value="/user/1/"' in response.data

        response = auth.login(redirect='/user/1')
        assert request.path == '/user/1/'
        assert b'test\'s Profile' in response.data


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


def test_forgot_password(client, app, monkeypatch):
    class EmailReceiver:
        email = None
        reset_link = None

    def mock_send_email(email, reset_link):
        EmailReceiver.email = email
        EmailReceiver.reset_link = reset_link

    monkeypatch.setattr('flaskr.auth.routes.send_reset_password_email', mock_send_email)

    assert client.get('/auth/forgot-password').status_code == 200

    client.post('/auth/forgot-password', data={'username': 'test'})

    assert EmailReceiver.email == 'test@email.com'
    assert EmailReceiver.reset_link is not None

    with app.app_context():
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'], salt='auth.password_reset')
        data = s.loads(EmailReceiver.reset_link)

        assert data['username'] == 'test'


def test_reset_password(client, app):
    with app.app_context():
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'], salt='auth.password_reset')
        token = s.dumps({'username': 'test'})

        assert client.get(f'/auth/reset-password/{token}').status_code == 200

        client.post(f'/auth/reset-password/{token}', data={'password': 'updated', 'confirm': 'updated'})

        with get_db().connect() as conn:
            user = conn.execute(
                text('SELECT u.password FROM user u WHERE u.username = :username;'), {'username': 'test'}).one()

            assert check_password_hash(user['password'], 'updated')


def test_reset_password_validate(client, app):
    with app.app_context():
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'], salt='auth.password_reset')
        token = s.dumps({'username': 'test'})

        app.config['RESETPASSWORD_LINK_LIFETIME'] = -1

        response = client.post(
            f'/auth/reset-password/{token}',
            data={'password': 'updated', 'confirm': 'updated'},
            follow_redirects=True
        )

        assert b'Password reset link is invalid. Please submit a new request.' in response.data

        with get_db().connect() as conn:
            user = conn.execute(
                text('SELECT u.password FROM user u WHERE u.username = "test";')
            ).one()

            assert check_password_hash(user['password'], 'test')


def test_edit_profile(client, auth, app):
    with client:
        auth.login()

        assert client.get('/auth/edit-profile').status_code == 200

        response = client.post(
            '/auth/edit-profile',
            data={'email': 'changed@test.com', 'password': 'changed_password', 'confirm_password': 'changed_password'},
            follow_redirects=True)

        assert response.status_code == 200

        with app.app_context():
            with get_db().connect() as conn:
                user = conn.execute(
                    text('SELECT u.username, u.email, u.password FROM user u WHERE id = :id;'),
                    {'id': session['user'].id}).one()

                assert user['email'] == 'changed@test.com'
                assert check_password_hash(user['password'], 'changed_password')
