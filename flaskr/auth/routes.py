import os

import itsdangerous.exc
import sqlalchemy.exc

from flask import (flash, redirect, render_template, session, url_for, current_app)
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import text
from itsdangerous import URLSafeTimedSerializer
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from flaskr.db import get_db

from . import bp
from .decorators import login_required
from .models import User
from .forms import EditProfileForm, ForgotPasswordForm, LoginForm, RegisterForm, ResetPasswordForm


@bp.route('/register', methods=('GET', 'POST'))
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        try:
            with get_db().connect() as conn:
                conn.execute(
                    text('INSERT INTO "user" (username, email, password) VALUES (:username, :email, :password);'),
                    {'username': form.username.data, 'email': form.email.data, 'password': generate_password_hash(form.password.data)}
                )

                conn.commit()
        except sqlalchemy.exc.IntegrityError:
            flash(f'User {form.username.data} is already registered.')
        else:
            return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()

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
            session['user'] = User(user)

            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html', form=form)


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@bp.route('/forgot-password', methods=('GET', 'POST'))
def forgot_password():
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        with get_db().connect() as conn:
            user = conn.execute(
                text('SELECT u.username, u.email FROM user u WHERE username = :username;'),
                {'username': form.username.data}
            ).one_or_none()

            if user is not None:
                s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt='auth.password_reset')
                token = s.dumps({'username': user['username']})

                send_reset_password_email(user['email'], token)

    return render_template('auth/forgotpassword.html', form=form)


def send_reset_password_email(email, token):
    reset_link = url_for('auth.reset_password', token=token, _external=True)

    content = f'<p>Please use the following link to reset your password.</p>' \
              f'<a href="{reset_link}">{reset_link}</a>'

    message = Mail(
        from_email='no-reply@patrickkirk.ca',
        to_emails=email,
        subject='Password Reset',
        html_content=content
    )

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        sg.send(message)
    except Exception as e:
        print(e.message)


@bp.route('/reset-password/<string:token>', methods=('GET', 'POST'))
def reset_password(token):
    form = ResetPasswordForm()
    form.token.data = token

    if form.validate_on_submit():
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt='auth.password_reset')

        try:
            result = s.loads(token, max_age=current_app.config['RESETPASSWORD_LINK_LIFETIME'])
        except itsdangerous.exc.SignatureExpired:
            flash(f'Password reset link is invalid. Please submit a new request.')
            return redirect(url_for('auth.forgot_password'))

        with get_db().connect() as conn:
            conn.execute(text('UPDATE user SET password = :password WHERE username = :username;'),
                         {'password': generate_password_hash(form.password.data), 'username': result['username']})
            conn.commit()

        return redirect(url_for('auth.login'))

    return render_template('auth/resetpassword.html', form=form)


@bp.route('/edit-profile', methods=('GET', 'POST'))
@login_required
def edit_profile():
    form = EditProfileForm()

    if form.validate_on_submit():
        with get_db().connect() as conn:
            conn.execute(
                text('UPDATE user SET email = :email, password = :password WHERE id = :id;'),
                {'email': form.email.data, 'password': generate_password_hash(form.password.data), 'id': session['user'].id})
            conn.commit()

        flash('Profile updated!', 'alert-success')
        return redirect(url_for('index'))

    return render_template('auth/editprofile.html', form=form)
