import os
import sqlite3
import click
import psycopg2
from flask import current_app, g


class Database:
    connection = None
    IntegrityError = sqlite3.IntegrityError

    def get_connection(self):
        raise NotImplementedError()

    def execute(self, sql, parameters=()):
        if self.get_connection() is not None:
            return self.get_connection().execute(sql, parameters)

    def executescript(self, script):
        if self.get_connection() is not None:
            return self.get_connection().executescript(script)

    def commit(self):
        if self.get_connection() is not None:
            self.get_connection().commit()

    def close(self):
        if self.get_connection() is not None:
            self.get_connection().close()


class DevelopmentDatabase(Database):
    def get_connection(self):
        if self.connection is None:
            connection_string = os.path.join(current_app.instance_path, current_app.config['DATABASE_URI'])

            self.connection = sqlite3.connect(connection_string, detect_types=sqlite3.PARSE_DECLTYPES)
            self.connection.row_factory = sqlite3.Row

        return self.connection


class ProductionDatabase(Database):
    cursor = None

    def get_connection(self):
        if self.connection is None:
            config = current_app.config

            self.connection = psycopg2.connect(
                host=config['DB_HOST'],
                database=config['DB_NAME'],
                user=config['DB_USER'],
                password=config['DB_PASS']
            )

        return self.connection

    def execute(self, sql, parameters=()):
        if self.get_connection() is not None:
            if self.cursor is None:
                self.cursor = self.get_connection().cursor()

            self.cursor.execute(sql.replace('?', '%s'), parameters)

            return self.cursor

    def commit(self):
        if self.get_connection() is not None:
            self.get_connection().commit()
            self.cursor.close()
            self.cursor = None

    def close(self):
        if self.get_connection() is not None:
            if self.cursor is not None:
                self.cursor.close()

            self.get_connection().close()


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized database.')


def get_db():
    if 'db' not in g:
        g.db = current_app.config['DATABASE']

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
