from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from werkzeug.exceptions import HTTPException
import json
from genClients import generate_video_list
from task import VideoOptions, VideoTask

FLASK_HOST = os.environ.get("FLASK_HOST", "")
if not FLASK_HOST:
    raise ValueError("FLASK_HOST is not set")
FLASK_PORT = int(os.environ.get("FLASK_PORT", "!"))
if not FLASK_PORT:
    raise ValueError("FLASK_PORT is not set")

app = Flask(__name__)
CORS(app)

def save_uploaded_images(task: VideoTask) -> list[int]:
    if "images" not in request.files:
        raise HTTPException(status_code=400, detail="No images provided")

    files = request.files.getlist("images")
    if not files or files[0].filename == "":
        raise HTTPException(status_code=400, detail="No images selected")

    saved_file_index_list = []

    file_index = 1
    for file in files:
        file_path = task.get_wd_image_path(file_index)
        file.save(file_path)

        saved_file_index_list.append(file_index)
        file_index += 1

    return saved_file_index_list

@app.route("/api/create", methods=["POST"])
def create():
    if "options" not in request.files:
        raise HTTPException(status_code=400, detail="No options provided")
    video_options = VideoOptions(**json.loads(request.files["options"].read()))

    video_task = VideoTask.create_new(video_options)
    print(f"work dir: {video_task.work_dir}")
    print(f"options: {video_task.options}")

    saved_file_index_list = save_uploaded_images(video_task)
    print(f"total saved files: {len(saved_file_index_list)}")

    generate_video_list(video_task, saved_file_index_list)

    return jsonify({"message": "Hello, World!", "status": "success"})


if __name__ == "__main__":
    app.run(debug=True, host=FLASK_HOST, port=FLASK_PORT)
