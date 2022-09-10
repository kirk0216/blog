import secrets

import sqlalchemy.exc
from flask import (flash, g, redirect, render_template, request, session, url_for, current_app)
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import text

from flaskr.db import get_db

from . import bp
from .models import GROUPS
from .forms import AuthForm


@bp.route('/register', methods=('GET', 'POST'))
def register():
    form = AuthForm()

    if form.validate_on_submit():
        try:
            with get_db().connect() as conn:
                conn.execute(
                    text('INSERT INTO "user" (username, password) VALUES (:username, :password);'),
                    {'username': form.username.data, 'password': generate_password_hash(form.password.data)}
                )

                conn.commit()
        except sqlalchemy.exc.IntegrityError:
            flash(f'User {form.username.data} is already registered.')
        else:
            return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    form = AuthForm()

    if form.validate_on_submit():
        error = None

        with get_db().connect() as conn:
            user = conn.execute(
                text('SELECT * FROM "user" WHERE username = :username;'), {'username': form.username.data}
            ).one_or_none()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], form.password.data):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html', form=form)


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


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
