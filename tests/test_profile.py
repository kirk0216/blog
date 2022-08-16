def test_view_requires_login(client):
    response = client.get('/user/1/')
    assert response.headers['Location'] == '/auth/login'


def test_view_requires_user_to_exist(client, auth):
    auth.login()
    assert client.get('/user/3/').status_code == 404


def test_view(client, auth):
    auth.login()
    response = client.get('/user/1/')
    assert b'test\'s Profile' in response.data
    assert b'Test Title' in response.data
    assert b'2022-01-01 00:00:00' in response.data
    assert b'test body' in response.data

    assert b'test comment' in response.data
    assert b'2022-02-01 00:00:00' in response.data
