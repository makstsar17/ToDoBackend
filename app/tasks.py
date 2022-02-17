import os

from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import TasksModel, SubTaskModel, TagsModel
from util.file_util import UPLOAD_FOLDER_TEMPORARY, relocate_new_files

tasks_manager = Blueprint('tasks', __name__, url_prefix='/tasks')


@tasks_manager.route('/get_all_tasks', methods=["GET"])
@jwt_required()
def get_all_tasks():
    current_user = get_jwt_identity()
    tasks = TasksModel.get_all_tasks(current_user)
    tasks["success"] = True

    return jsonify(tasks), 200


@tasks_manager.route('/add_task', methods=["POST"])
@jwt_required()
def add_task():
    current_user = get_jwt_identity()

    request_json = request.get_json()
    subtasks = None
    tags = None

    if "title" not in request_json:
        return jsonify({"error": "Invalid form"}), 400
    if "subtasks" in request_json:
        subtasks = request_json.pop("subtasks")
    if "tags" in request_json:
        tags = request_json.pop("tags")

    add_task_res = TasksModel.add_task(current_user, **request_json)
    if not add_task_res:
        return jsonify({"error": "Can't add tasks to database"}), 500

    task_id = TasksModel.get_last_task_id()
    if subtasks:
        if isinstance(subtasks, list):
            add_subtask_res = SubTaskModel.add_subtasks(task_id, *subtasks)
        else:
            add_subtask_res = SubTaskModel.add_subtasks(task_id, subtasks)

        if not add_subtask_res:
            return jsonify({"error": "Can't add subtasks to database"}), 500

    if tags:
        if isinstance(tags, list):
            add_tag_res = TagsModel.add_tags(task_id, *tags)
        else:
            add_tag_res = TagsModel.add_tags(task_id, tags)

        if not add_tag_res:
            return jsonify({"error": "Can't add tags to database"}), 500

    if str(current_user) in os.listdir(UPLOAD_FOLDER_TEMPORARY) and \
            os.listdir(os.path.join(UPLOAD_FOLDER_TEMPORARY, str(current_user))):
        relocate_new_files(current_user, task_id)

    return jsonify({"success": True}), 200


@tasks_manager.route('/delete_task', methods=["POST"])
@jwt_required()
def delete_task():
    if "task_id" not in request.json:
        return jsonify({"error": "Invalid form"}), 400
    result = TasksModel.delete_task(request.json["task_id"])

    if "success" in result:
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@tasks_manager.route('/update_task', methods=["POST"])
@jwt_required()
def update_task():
    request_json = request.get_json()

    if "task_id" not in request_json:
        return jsonify({"error": "Invalid form"}), 400

    task_id = request_json.pop("task_id")
    result = TasksModel.update_task(task_id, **request_json)

    if "error" in result:
        return jsonify({"error": result["error"]}), result["status_code"]
    else:
        return jsonify({"success": result["success"]}), 200


@tasks_manager.route('/add_tags', methods=["POST"])
@jwt_required()
def add_tags():
    if "task_id" not in request.json or "tags" not in request.json:
        return jsonify({"error": "Invalid form"}), 400

    result = TagsModel.add_tags(request.json["task_id"], *request.json["tags"])

    if result:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"error": "Failed to add tags"}), 500


@tasks_manager.route('/update_tag', methods=["POST"])
@jwt_required()
def update_tag():
    if "task_id" not in request.json or "tag_title" not in request.json or "new_title" not in request.json:
        return jsonify({"error": "Invalid form"}), 400

    result = TagsModel.update_tag(request.json["task_id"], request.json["tag_title"], request.json["new_title"])

    if "success" in result:
        return jsonify({"success": result["success"]}), result["status_code"]
    else:
        return jsonify({"error": result["error"]}), result["status_code"]


@tasks_manager.route('/delete_tag', methods=["POST"])
@jwt_required()
def delete_tag():
    if "task_id" not in request.json or "tag_title" not in request.json:
        return jsonify({"error": "Invalid form"}), 400

    result = TagsModel.delete_tag_by_title(request.json["task_id"], request.json["tag_title"])

    if "success" in result:
        return jsonify({"success": result["success"]}), result["status_code"]
    else:
        return jsonify({"error": result["error"]}), result["status_code"]


@tasks_manager.route('/add_subtasks', methods=["POST"])
@jwt_required()
def add_subtasks():
    if "task_id" not in request.json or "subtasks" not in request.json:
        return jsonify({"error": "Invalid form"}), 400

    result = SubTaskModel.add_subtasks(request.json["task_id"], *request.json["subtasks"])

    if result:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"error": "Failed to add subtasks"}), 500


@tasks_manager.route('/update_subtask', methods=["POST"])
@jwt_required()
def update_subtask():
    request_json = request.get_json()

    if "task_id" not in request_json or "title" not in request_json:
        return jsonify({"error": "Invalid form"}), 400

    task_id = request_json.pop("task_id")
    title = request_json.pop("title")
    result = SubTaskModel.update_subtask(task_id, title, **request_json)

    if "error" in result:
        return jsonify({"error": result["error"]}), result["status_code"]
    else:
        return jsonify({"success": result["success"]}), 200


@tasks_manager.route('/delete_subtask', methods=["POST"])
@jwt_required()
def delete_subtask():
    if "task_id" not in request.json or "title" not in request.json:
        return jsonify({"error": "Invalid form"}), 400

    result = SubTaskModel.delete_subtask_by_title(request.json["task_id"], request.json["title"])

    if "success" in result:
        return jsonify({"success": result["success"]}), result["status_code"]
    else:
        return jsonify({"error": result["error"]}), result["status_code"]
