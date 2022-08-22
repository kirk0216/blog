import os
import tempfile
import pytest

from flaskr import create_app
from flaskr.db import get_db, init_db
from flaskr.config import TestConfig

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app(TestConfig)
    app.config['DATABASE_PATH'] = db_path

    with app.app_context():
        init_db()

        import sqlite3
        conn = sqlite3.connect(app.config['DATABASE_PATH'])
        conn.executescript(_data_sql)
        conn.commit()
        conn.close()

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
