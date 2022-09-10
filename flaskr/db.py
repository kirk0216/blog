import click
import sqlalchemy.exc
from sqlalchemy import create_engine, text, event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SqliteConnection

from flask import current_app, g

from flaskr.config import get_dev_db_uri, get_test_db_uri, get_production_db_uri


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin)


def init_db():
    schema_filename = 'schema.production.sql'

    if current_app.config['TESTING'] or current_app.config['DEBUG']:
        schema_filename = 'schema.development.sql'

    with current_app.open_resource(schema_filename) as f:
        if current_app.config['TESTING']:
            import sqlite3
            conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
            conn.executescript(f.read().decode('UTF-8'))
            conn.commit()
        else:
            db = get_db()

            with db.connect() as conn:
                conn.execute(text(f.read()))


@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized database.')


@click.command('create-admin')
@click.option('--username', required=True, prompt=True)
@click.password_option(required=True)
@click.option('--env', default='DEV')
def create_admin(username, password, env):
    if env == 'DEV':
        current_app.config['DEBUG'] = True

    with get_db().connect() as conn:
        from werkzeug.security import generate_password_hash

        try:
            conn.execute(text(
                'INSERT INTO user (username, password, "group") VALUES (:username, :password, "ADMIN");'
            ), {'username': username, 'password': generate_password_hash(password)})
            conn.commit()
        except sqlalchemy.exc.IntegrityError:
            if click.confirm(f'User "{username}" already exists. Would you like to make them an admin?', default=False):
                conn.execute(text(
                    'UPDATE user SET "group" = "ADMIN" WHERE username = :username;'
                ), {'username': username})
                conn.commit()


def get_db():
    if 'db' not in g:
        if current_app.config['TESTING']:
            g.db = create_engine(get_test_db_uri(), echo=True, future=True)
        else:
            if current_app.config['DEBUG']:
                g.db = create_engine(get_dev_db_uri(), echo=True, future=True)
            else:
                g.db = create_engine(get_production_db_uri(), echo=False, future=True)

    return g.db


def close_db(e=None):
    g.pop('db', None)


# https://stackoverflow.com/questions/2614984/sqlite-sqlalchemy-how-to-enforce-foreign-keys
@event.listens_for(Engine, 'connect')
def enable_sqlite_fk(connection, connection_record):
    if isinstance(connection, SqliteConnection):
        cursor = connection.cursor()
        cursor.execute('PRAGMA foreign_keys=on;')
        cursor.close()
