from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from util.file_util import get_filenames, delete_files_for_task
from enum import Enum

db = SQLAlchemy()


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(64), unique=True, nullable=False)
    _pwd = db.Column(db.String(225), nullable=False)

    def __init__(self, **kwargs):
        super(UserModel, self).__init__(**kwargs)

    def get_pwd(self):
        return self._pwd

    @classmethod
    def getUsers(cls):
        def to_json(user_object):
            return {
                "id": user_object.id,
                "email": user_object.email,
                "password": user_object.get_pwd()
            }

        return [to_json(i) for i in cls.query.all()]

    @classmethod
    def getUser(cls, user_id):
        return cls.query.filter_by(id=user_id).first()

    @classmethod
    def addUser(cls, email, password):
        try:
            user = cls(email=email, _pwd=generate_password_hash(password))
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


class RepeatType(Enum):
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'


class TasksModel(db.Model):
    __tablename__ = "task"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    deadline = db.Column(db.DateTime)
    repeat = db.Column(db.Enum(RepeatType))
    suff_time = db.Column(db.Integer)
    notes = db.Column(db.Text)
    status = db.Column(db.Boolean, nullable=False)

    def __init__(self, **kwargs):
        super(TasksModel, self).__init__(**kwargs)

    @classmethod
    def add_task(cls, user_id, **kwargs):
        try:
            task = cls(user_id=user_id, status=False, **kwargs)
            db.session.add(task)
            db.session.commit()
            return True

        except Exception as e:
            print(e)
            return False

    @classmethod
    def get_all_tasks(cls, user_id):
        def to_json(task):
            return {"title": task.title,
                    "deadline": task.deadline,
                    "repeat": task.repeat.name if task.repeat else None,
                    "suff_time": task.suff_time,
                    "notes": task.notes,
                    "status": task.status,
                    "files": get_filenames(task.id),
                    "subtasks": SubTaskModel.get_subtasks(task.id),
                    "tags": TagsModel.get_tags(task.id)}

        tasks = cls.query.filter_by(user_id=user_id)
        return {str(task.id): to_json(task) for task in tasks}

    @classmethod
    def get_last_task_id(cls):
        tasks = cls.query.all()
        max_id = 0
        for t in tasks:
            if t.id > max_id:
                max_id = t.id

        return max_id

    @classmethod
    def delete_task(cls, task_id):
        task = cls.query.filter_by(id=task_id).first()

        if not task:
            return {"error": "Not existing task_id"}

        TagsModel.delete_tags(task_id)
        SubTaskModel.delete_subtasks(task_id)
        delete_files_for_task(task_id)

        db.session.delete(task)
        db.session.commit()

        return {"success": True}

    @classmethod
    def update_task(cls, task_id, **kwargs):
        task = cls.query.filter_by(id=task_id)

        if not task.first():
            return {"error": "Not existing task", "status_code": 400}
        else:
            task.update(kwargs)
            try:
                db.session.commit()
                return {"success": True}
            except Exception as e:
                print("Failed to change task data: ", e)
                return {"error": str(e), "status_code": 500}


class SubTaskModel(db.Model):
    __tablename__ = "subtask"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, db.ForeignKey("task.id"), primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    status = db.Column(db.Boolean, nullable=False)

    def __init__(self, **kwargs):
        super(SubTaskModel, self).__init__(**kwargs)

    @classmethod
    def add_subtasks(cls, task_id, *args):
        try:
            for title in args:
                subtask = cls(task_id=task_id, title=title, status=False)
                db.session.add(subtask)
                db.session.commit()
            return True

        except Exception as e:
            print(e)
            return False

    @classmethod
    def get_subtasks(cls, task_id):
        return [{"title": subtask.title, "status": subtask.status}
                for subtask in cls.query.filter_by(task_id=task_id)]

    @classmethod
    def delete_subtasks(cls, task_id):
        for subtask in cls.query.filter_by(task_id=task_id).all():
            db.session.delete(subtask)
        db.session.commit()

    @classmethod
    def delete_subtask_by_title(cls, task_id, title):
        subtask = cls.query.filter_by(task_id=task_id, title=title).first()

        if not subtask:
            return {"error": "Not existing subtask", "status_code": 400}

        try:
            db.session.delete(subtask)
            db.session.commit()
            return {"success": True, "status_code": 200}
        except Exception as e:
            return {"error": str(e), "status_code": 500}

    @classmethod
    def update_subtask(cls, task_id, title, **kwargs):
        subtask = cls.query.filter_by(task_id=task_id, title=title)

        if not subtask.first():
            return {"error": "Not existing task", "status_code": 400}
        else:
            if "new_title" in kwargs:
                kwargs["title"] = kwargs.pop("new_title")
            subtask.update(kwargs)
            try:
                db.session.commit()
                return {"success": True}
            except Exception as e:
                print("Failed to change task data: ", e)
                return {"error": str(e), "status_code": 500}


class TagsModel(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, db.ForeignKey("task.id"), primary_key=True)
    tag_title = db.Column(db.String(50))

    def __init__(self, **kwargs):
        super(TagsModel, self).__init__(**kwargs)

    @classmethod
    def add_tag(cls, task_id, tag_title):
        try:
            tag = cls(task_id=task_id, tag_title=tag_title)
            db.session.add(tag)
            db.session.commit()
            return True

        except Exception as e:
            print(e)
            return False

    @classmethod
    def add_tags(cls, task_id, *args):
        try:
            for title in args:
                tag = cls(task_id=task_id, tag_title=title)
                db.session.add(tag)
                db.session.commit()
            return True

        except Exception as e:
            print(e)
            return False

    @classmethod
    def get_tags(cls, task_id):
        return [tag.tag_title for tag in cls.query.filter_by(task_id=task_id)]

    @classmethod
    def delete_tags(cls, task_id):
        for tag in cls.query.filter_by(task_id=task_id).all():
            db.session.delete(tag)
        db.session.commit()

    @classmethod
    def delete_tag_by_title(cls, task_id, tag_title):
        tag = cls.query.filter_by(task_id=task_id, tag_title=tag_title).first()

        if not tag:
            return {"error": "Not existing tag", "status_code": 400}

        try:
            db.session.delete(tag)
            db.session.commit()
            return {"success": True, "status_code": 200}
        except Exception as e:
            return {"error": str(e), "status_code": 500}

    @classmethod
    def update_tag(cls, task_id, tag_title, new_title):
        tag = cls.query.filter_by(task_id=task_id, tag_title=tag_title).first()

        if not tag:
            return {"error": "Not existing tag", "status_code": 400}

        tag.tag_title = new_title

        try:
            db.session.commit()
            return {"success": True, "status_code": 200}
        except Exception as e:
            return {"error": str(e), "status_code": 500}
