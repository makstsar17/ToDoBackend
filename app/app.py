from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import redis

app = Flask(__name__)
app.config.from_pyfile("../instance/config.py")
db = SQLAlchemy(app)
CORS(app)
jwt = JWTManager(app)


jwt_redis_blocklist = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)

import utils.jwt_util
