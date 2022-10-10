import pytest

from flaskr.db import get_db
from sqlalchemy import text


def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('flaskr.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called


@pytest.mark.parametrize(('username', 'password', 'email'), (
    ('bob', 'password', 'test@email.com'),
    ('other', 'password', 'test@email.com')
))
def test_create_admin_command(app, runner, monkeypatch, username, password, email):
    class Recorder(object):
        called = False

    def fake_create_admin():
        Recorder.called = True

    monkeypatch.setattr('flaskr.db.create_admin', fake_create_admin())

    with app.app_context():
        result = runner.invoke(args=['create-admin', '--username', username, '--password', password, '--email', email], input='y')
        assert Recorder.called

        with get_db().connect() as conn:
            user = conn.execute(
                text('SELECT "group" FROM user WHERE username = :username;'), {'username': username}
            ).one()
            assert user['group'] == 'ADMIN'
