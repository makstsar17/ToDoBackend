import json

from flask import request, jsonify, Blueprint, send_from_directory
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity
from util.file_util import allowed_file, UPLOAD_FOLDER_TEMPORARY, create_dir_for_user, create_dir_for_task
from instance.config import UPLOAD_FOLDER
import os

file_manager = Blueprint('files', __name__, url_prefix='/file')


@file_manager.route('/upload', methods=['POST'])  # +++++++++++++
@jwt_required()
def upload_file():
    current_user = get_jwt_identity()

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    files = request.files.getlist("file")
    for file in files:
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if file and allowed_file(file.filename):
            create_dir_for_user(current_user)
            file.save(os.path.join(UPLOAD_FOLDER_TEMPORARY, str(current_user), secure_filename(file.filename)))

    return jsonify({"success": True})


@file_manager.route('/cancel_upload_all', methods=["POST"])  # ++++++++++++++
@jwt_required()
def cancel():
    current_user = get_jwt_identity()
    path = os.path.join(UPLOAD_FOLDER_TEMPORARY, str(current_user))

    for file in os.listdir(path):
        os.remove(os.path.join(path, file))

    return jsonify({"success": True}), 200


@file_manager.route('/cancel_upload_file', methods=["POST"])  # +++++++++++++
@jwt_required()
def cancel_file():
    current_user = get_jwt_identity()
    path = os.path.join(UPLOAD_FOLDER_TEMPORARY, str(current_user))

    if "file" not in request.json:
        return jsonify({"error": "No file part"}), 400

    os.remove(os.path.join(path, request.json["file"]))

    return jsonify({"success": True}), 200


@file_manager.route('/delete_file', methods=["POST"])  # +++++++++++++++
@jwt_required()
def delete():
    if "file" not in request.json or "task_id" not in request.json:
        return jsonify({"error": "Invalid form"}), 400

    try:
        os.remove(os.path.join(UPLOAD_FOLDER, str(request.json["task_id"]), request.json["file"]))
    except Exception as e:
        print("Failed to delete file ", e)
        return jsonify({"error": "Failed to delete file"}), 500

    return jsonify({"success": True})


@file_manager.route('/download', methods=["POST"])  # +++++++++++++++++++
@jwt_required()
def download_file():
    if "file" not in request.json and "task_id" not in request.json:
        return jsonify({"error": "Invalid form"}), 400

    try:
        return send_from_directory(os.path.join("..", UPLOAD_FOLDER, str(request.json["task_id"])),
                                   request.json["file"], as_attachment=True), 200

    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404


@file_manager.route('/add_file_to_task', methods=["POST"])
@jwt_required()
def add_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    request_json = json.loads(request.form.get("data"))
    if "task_id" not in request_json:
        return jsonify({"error": "Invalid form"}), 400

    files = request.files.getlist("file")
    for file in files:
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if file and allowed_file(file.filename):
            create_dir_for_task(request_json["task_id"])
            file.save(os.path.join(UPLOAD_FOLDER, str(request_json["task_id"]), secure_filename(file.filename)))

    return jsonify({"success": True})
