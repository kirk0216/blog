import pytest


@pytest.mark.parametrize('page', (
    '/admin/',
    '/admin/users',
    '/admin/posts',
    '/admin/comments'
))
def test_admin_authorization_required(client, auth, page):
    # Non-admin user
    auth.login('other', 'other')
    assert client.get(page).status_code == 403


@pytest.mark.parametrize(('page', 'expected'), (
        ('/admin/users', b''),
        ('/admin/posts', b''),
        ('/admin/comments', b'')
))
def test_lists(client, auth, page, expected):
    pass


def test_edit_user(client, auth):
    pass


def test_edit_post(client, auth):
    pass


def test_edit_comment(client, auth):
    pass
