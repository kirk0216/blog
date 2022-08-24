import secrets

import sqlalchemy.exc
from flask import (flash, g, redirect, render_template, request, session, url_for, abort)
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import text

from flaskr.db import get_db

from . import bp
from .models import GROUPS


def get_user_details_from_form():
    return request.form['username'], request.form['password']


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username, password = get_user_details_from_form()
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                with db.connect() as conn:
                    conn.execute(
                        text('INSERT INTO "user" (username, password) VALUES (:username, :password);'),
                        {'username': username, 'password': generate_password_hash(password)}
                    )

                    conn.commit()
            except sqlalchemy.exc.IntegrityError:
                error = f'User {username} is already registered.'
            else:
                return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username, password = get_user_details_from_form()
        db = get_db()
        error = None

        with db.connect() as conn:
            user = conn.execute(
                text('SELECT * FROM "user" WHERE username = :username;'), {'username': username}
            ).one_or_none()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            csrf_token = session['csrf_token']

            session.clear()
            session['csrf_token'] = csrf_token
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@bp.before_app_request
def check_csrf_token():
    csrf_token = session.get('csrf_token')

    if csrf_token is None:
        session.clear()

        token = secrets.token_hex(32)

        session['csrf_token'] = token
    else:
        g.csrf_token = session['csrf_token']


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
        g.user_group = GROUPS['DEFAULT']
    else:
        db = get_db()

        with db.connect() as conn:
            g.user = conn.execute(text('SELECT * FROM "user" WHERE id = :id;'), {'id': user_id}).one()
            g.user_group = GROUPS[g.user['group']]
