import re
from .app import app, jwt_redis_blocklist
from models import UserModel
from flask import request, jsonify
from flask_jwt_extended import (create_access_token, jwt_required, create_refresh_token,
                                get_jwt_identity, get_jwt)
from instance.config import JWT_ACCESS_TOKEN_EXPIRES, JWT_REFRESH_TOKEN_EXPIRES


@app.route('/api/signup', methods=["POST"])
def signup():
    try:
        email = request.json["email"]
        email = email.lower()
        password = request.json["password"]
        username = request.json["username"]

        if not password or not email or not username:
            return jsonify({"error": "Invalid form"}), 401

        user = list(filter(lambda user: user["email"] == email, UserModel.getUsers()))
        if len(user) != 0:
            return jsonify({"error": "Account with such email has already existed"}), 400

        if not re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email):
            return jsonify({"error": "Invalid form of email"}), 400
        # TODO make checking email for existing
        UserModel.addUser(username, email, password)
        return jsonify({"success": True}), 201

    except Exception as e:
        return jsonify({"error": e}), 500


@app.route('/api/signin', methods=["POST"])
def signin():
    try:
        email = request.json["email"]
        password = request.json["password"]

        if not password or not email:
            return jsonify({"error": "Invalid form"}), 401

        user = list(filter(lambda user: user["email"] == email and
                                        UserModel.verify_password(user["password"], password), UserModel.getUsers()))
        if len(user) == 1:
            token = create_access_token(identity=user[0]["id"])
            refresh_token = create_refresh_token(identity=user[0]["id"])
            response = jsonify({"token": token, "refresh_token": refresh_token})
            return response, 200

        else:
            return jsonify({"error": "Incorrect email or password"}), 400

    except Exception as e:
        return jsonify({"error": e}), 500


@app.route('/api/checktoken', methods=["GET"])
@jwt_required()
def checktoken():
    return jsonify({"success": True}), 200


@app.route('/api/tokenrefresh', methods=["POST"])
@jwt_required(refresh=True)
def tokenrefresh():
    current_user = get_jwt_identity()
    token = create_access_token(identity=current_user)

    response = jsonify({"token": token})
    return response, 200


@app.route('/api/logout/access', methods=["POST"])
@jwt_required()
def access_logout():
    jti = get_jwt()["jti"]
    try:
        jwt_redis_blocklist.set(jti, "", ex=JWT_ACCESS_TOKEN_EXPIRES)
        return jsonify({}), 200

    except Exception as e:
        return jsonify({"error": e}), 500


@app.route('/api/logout/refresh', methods=["POST"])
@jwt_required(refresh=True)
def refresh_logout():
    jti = get_jwt()["jti"]
    try:
        jwt_redis_blocklist.set(jti, "", ex=JWT_REFRESH_TOKEN_EXPIRES)
        return jsonify({}), 200

    except Exception as e:
        return jsonify({"error": e}), 500
