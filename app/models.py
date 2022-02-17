from .app import db
from werkzeug.security import generate_password_hash, check_password_hash


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    _pwd = db.Column(db.String(225), nullable=False)

    def __init__(self, username, email, pwd):
        self.username = username
        self.email = email
        self._pwd = pwd

    @classmethod
    def getUsers(cls):
        def to_json(user_object):
            return {
                "id": user_object.id,
                "username": user_object.username,
                "email": user_object.email,
                "password": user_object._pwd
            }
        return [to_json(i) for i in cls.query.all()]

    @classmethod
    def getUser(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def addUser(cls, username, email, password):
        try:
            user = cls(username, email, generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            return False

    @classmethod
    def removeUser(cls, user_id):
        try:
            user = cls.query.get(user_id)
            db.session.delete(user)
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def verify_password(password_hash, password):
        return check_password_hash(password_hash, password)
