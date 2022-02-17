from app.models import UserModel
import pytest


def test_register(client):
    data = {"email": "email@email.com", "password": "password"}
    response = client.post('/auth/signup', json=data)
    assert response.status_code == 201
    assert response.get_json()["success"]

    assert list(filter(lambda user: user["email"] == "email" and
                                    UserModel.verify_password(user["password"], "password"), UserModel.getUsers())) \
           is not None


@pytest.mark.parametrize(
    ("email", "password"),
    (
        ("", "password"),
        ("t@t.t", "password")
    ),
)
def test_register_with_invalid_data(client, email, password):
    response = client.post('/auth/signup', json={"email": email, "password": password})
    assert response.status_code == 400
    assert "error" in response.get_json().keys()


def test_sign_in(client_with_user):
    response = client_with_user.post('/auth/signin', json={"email": "mail@mail.com", "password": "password"})
    data = response.get_json()

    assert response.status_code == 200
    assert "token" in data.keys()
    assert "refresh_token" in data.keys()

    check_token = client_with_user.get('/auth/checktoken', headers={"Authorization": f'Bearer {data["token"]}'})

    assert check_token.status_code == 200
    assert check_token.get_json()["success"]


def test_sign_in_incorrect_data(client_with_user):
    response = client_with_user.post('/auth/signin', json={"email": "all@mail.com", "password": "11111111"})

    assert response.status_code == 400
    assert "error" in response.get_json().keys()


def test_refresh_token(client_with_user):
    token = client_with_user.post('/auth/signin', json={"email": "mail@mail.com", "password": "password"}).get_json()

    new_token = client_with_user.post('/auth/tokenrefresh',
                                      headers={"Authorization": f'Bearer {token["refresh_token"]}'})

    assert new_token.status_code == 200
    assert "token" in new_token.get_json().keys()

    check_token = client_with_user.get('/auth/checktoken',
                                       headers={"Authorization": f'Bearer {new_token.get_json()["token"]}'})

    assert check_token.status_code == 200
    assert check_token.get_json()["success"]


def test_logout(client_with_user):
    token = client_with_user.post('/auth/signin', json={"email": "mail@mail.com", "password": "password"}).get_json()

    del_token = client_with_user.post('/auth/logout/access', headers={"Authorization": f'Bearer {token["token"]}'})
    assert del_token.status_code == 200
    assert del_token.get_json()["success"]
    assert client_with_user.get('/auth/checktoken',
                                headers={"Authorization": f'Bearer {token["token"]}'}).status_code == 401

    del_refresh_token = client_with_user.post('/auth/logout/refresh',
                                              headers={"Authorization": f'Bearer {token["refresh_token"]}'})
    assert del_refresh_token.status_code == 200
    assert del_refresh_token.get_json()["success"]
