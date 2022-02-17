from app.models import UserModel


def test_new_user():
    username = "username"
    email = "email@email.com"
    pwd = "password"
    user = UserModel(username, email, pwd)

    assert user.username == username
    assert user.email == email
    assert user._pwd == pwd


def test_add_user(client):

    UserModel.addUser("test1", "test1@mail.com", "test1")
    UserModel.addUser("test2", "test2@mail.com", "test2")
    UserModel.addUser("test3", "test3@mail.com", "test3")

    user = UserModel.getUser(2)
    assert user.id == 2
    assert user.username == "test2"
    assert user.email == "test2@mail.com"
    assert UserModel.verify_password(user._pwd, "test2")

    assert len(UserModel.getUsers()) == 3


def test_remove_user(client):
    UserModel.addUser("test1", "test1@mail.com", "test1")
    UserModel.addUser("test2", "test2@mail.com", "test2")

    UserModel.removeUser(UserModel.query.filter_by(username="test2").first().id)

    assert len(UserModel.getUsers()) == 1
    assert UserModel.getUsers()[0]["username"] == "test1"
