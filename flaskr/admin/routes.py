import sqlalchemy.exc
from flask import render_template, redirect, url_for, request, flash
from sqlalchemy import text

from . import bp
from flaskr.auth.decorators import login_required, required_permissions
from flaskr.auth.forms import AuthForm
from flaskr.blog.forms import BlogForm, CommentForm
from flaskr.db import get_db

sections = ['users', 'posts', 'comments']


@bp.route('/')
@login_required
@required_permissions(['ADMIN'])
def index():
    return render_template('admin/index.html', sections=sections)


@bp.route('/users')
@login_required
@required_permissions(['ADMIN'])
def list_users():
    with get_db().connect() as conn:
        users = conn.execute(
            text('SELECT u.id, u.username FROM "user" u;')
        ).all()

    return render_template('admin/user_list.html', users=users)


@bp.route('/users/edit/<int:id>', methods=('GET', 'POST'))
@login_required
@required_permissions(['ADMIN'])
def edit_user(id: int):
    with get_db().connect() as conn:
        user = conn.execute(
            text('SELECT u.id, u.username FROM "user" u WHERE u.id = :id;'),
            {'id': id}
        ).one_or_none()

        form = AuthForm(obj=user)
        del form.password

        if form.validate_on_submit():
            try:
                conn.execute(
                    text('UPDATE "user" SET username=:username WHERE id = :id;'),
                    {'username': form.username.data, 'id': id}
                )
                conn.commit()
            except sqlalchemy.exc.IntegrityError:
                flash('Username is already in use.')

            return redirect(url_for('admin.list_users'))

    return render_template('admin/user_edit.html', form=form, user_id=id)


@bp.route('/posts')
@login_required
@required_permissions(['ADMIN'])
def list_posts():
    with get_db().connect() as conn:
        posts = conn.execute(
            text(
                'SELECT p.id, p.author_id, p.created, p.title, p.body, u.username as "author" FROM post p '
                'JOIN "user" u ON u.id = p.author_id;'
            )
        ).all()

        return render_template('admin/post_list.html', posts=posts)


@bp.route('/posts/edit/<int:id>', methods=('GET', 'POST'))
@login_required
@required_permissions(['ADMIN'])
def edit_post(id: int):
    with get_db().connect() as conn:
        post = conn.execute(
            text(
                'SELECT p.id, p.author_id, p.created, p.title, p.body, u.username as "author" FROM post p '
                'JOIN "user" u ON u.id = p.author_id '
                'WHERE p.id = :id;'
            ),
            {'id': id}
        ).one_or_none()

        form = BlogForm(obj=post)

        if form.validate_on_submit():
            try:
                conn.execute(
                    text('UPDATE post SET title=:title, body=:body WHERE id=:id;'),
                    {'title': form.title.data, 'body': form.body.data, 'id': id}
                )
                conn.commit()
            except sqlalchemy.exc.DatabaseError:
                flash('There was an error saving your changes.')

            return redirect(url_for('admin.list_posts'))

    return render_template('admin/post_edit.html', form=form, post_id=id)


@bp.route('/comments')
@login_required
@required_permissions(['ADMIN'])
def list_comments():
    with get_db().connect() as conn:
        comments = conn.execute(
            text(
                'SELECT c.id, c.post_id, c.author_id, c.created, '
                'u.username AS "author", p.title AS "post_title" FROM comment c '
                'JOIN post p ON p.id = c.post_id '
                'JOIN "user" u ON u.id = c.author_id;'
            )
        ).all()

        return render_template('admin/comment_list.html', comments=comments)


@bp.route('/comments/edit/<int:id>', methods=('GET', 'POST'))
@login_required
@required_permissions(['ADMIN'])
def edit_comment(id: int):
    with get_db().connect() as conn:
        comment = conn.execute(
            text(
                'SELECT c.id, c.post_id, c.author_id, c.body FROM comment c '
                'WHERE c.id=:id;'
            ),
            {'id': id}
        ).one_or_none()

        form = CommentForm(obj=comment)

        if form.validate_on_submit():
            try:
                conn.execute(
                    text('UPDATE comment SET body=:body WHERE id=:id;'),
                    {'body': form.body.data, 'id': id}
                )
                conn.commit()
            except sqlalchemy.exc.DatabaseError:
                flash('A database error occurred.')

            return redirect(url_for('admin.list_comments'))

    return render_template('admin/comment_edit.html', form=form, comment_id=id)
