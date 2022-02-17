import os
import shutil
from instance.config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER

UPLOAD_FOLDER_TEMPORARY = os.path.join(UPLOAD_FOLDER, "temporary_files")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def relocate_new_files(user_id, task_id):
    if str(task_id) not in os.listdir(os.path.join(UPLOAD_FOLDER)):
        try:
            os.mkdir(os.path.join(UPLOAD_FOLDER, str(task_id)))
        except Exception as e:
            print("Creation of directory is failed: ", e)
            return

    path = os.path.join(UPLOAD_FOLDER_TEMPORARY, str(user_id))
    for file in os.listdir(path):
        shutil.move(os.path.join(path, file),
                    os.path.join(os.path.join(UPLOAD_FOLDER, str(task_id)), file))


def get_filenames(task_id):
    if str(task_id) in os.listdir(UPLOAD_FOLDER):
        return [filename for filename in os.listdir(os.path.join(UPLOAD_FOLDER, str(task_id)))]


def create_dir_for_user(user_id):
    if str(user_id) in os.listdir(UPLOAD_FOLDER_TEMPORARY):
        return
    try:
        os.mkdir(os.path.join(UPLOAD_FOLDER_TEMPORARY, str(user_id)))
    except Exception as e:
        print("Creation of directory is failed: ", e)


def delete_files_for_task(task_id):
    if str(task_id) in os.listdir(UPLOAD_FOLDER):
        try:
            for file in os.listdir(os.path.join(UPLOAD_FOLDER, str(task_id))):
                os.remove(os.path.join(UPLOAD_FOLDER, str(task_id), file))
        except Exception as e:
            print("Failed to delete file ", e)


def create_dir_for_task(task_id):
    if str(task_id) not in os.listdir(UPLOAD_FOLDER):
        try:
            os.mkdir(os.path.join(UPLOAD_FOLDER, str(task_id)))
        except Exception as e:
            print("Failed to create dir: ", e)
