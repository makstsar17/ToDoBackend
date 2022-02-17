import pytest
from datetime import timedelta
from app import create_app
from app.models import db, UserModel


@pytest.fixture(scope='module')
def app_for_testing():
    config = {'TESTING': True,
              'SQLALCHEMY_DATABASE_URI': 'postgresql://postgres:postgres@localhost:5432/test',
              'SECRET_KEY': 'e1adcf4c523b2a24400f47a5ef4d5691f8ce609d30760312c1f3fb9e51a35233',
              'SQLALCHEMY_TRACK_MODIFICATIONS': False,
              'JWT_SECRET_KEY': '137380f22888e8b8ae2528aee6481716bd3f3872dcbb92a58fc1d1d5ae143613',
              'JWT_ACCESS_TOKEN_EXPIRES': timedelta(hours=1),
              'JWT_REFRESH_TOKEN_EXPIRES': timedelta(days=10)}
    app = create_app(config)
    with app.app_context():
        db.create_all()

    yield app

    db.drop_all(app=app)


@pytest.fixture()
def client(app_for_testing):
    with app_for_testing.test_client() as client:
        with app_for_testing.app_context():
            yield client
            db.session.query(UserModel).delete()
            db.session.commit()


@pytest.fixture()
def client_with_user(app_for_testing):
    with app_for_testing.test_client() as client:
        with app_for_testing.app_context():
            UserModel.addUser("username", "mail@mail.com", "password")
            yield client
            db.session.query(UserModel).delete()
            db.session.commit()
