import click
from sqlalchemy import create_engine, text

from flask import current_app, g

from flaskr.config import get_dev_db_uri, get_test_db_uri


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def init_db():
    with current_app.open_resource('schema.sql') as f:
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


def get_db():
    if 'db' not in g:
        if current_app.config['TESTING']:
            g.db = create_engine(get_test_db_uri(), echo=True, future=True)
        else:
            g.db = create_engine(get_dev_db_uri(), echo=True, future=True)

    return g.db


def close_db(e=None):
    g.pop('db', None)
