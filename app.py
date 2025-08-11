import logging

from dotenv import load_dotenv
load_dotenv()

from config import get_config_all, load_config, save_config, set_config
from flask import Flask, Response, jsonify, request, send_file
from flask_cors import CORS
import os
from werkzeug.exceptions import HTTPException
import json
from task import VideoOptions, VideoTask

FLASK_HOST = os.environ.get("FLASK_HOST", "")
if not FLASK_HOST:
    raise ValueError("FLASK_HOST is not set")
FLASK_PORT = int(os.environ.get("FLASK_PORT", "!"))
if not FLASK_PORT:
    raise ValueError("FLASK_PORT is not set")

app = Flask(__name__)
CORS(app)


@app.route("/api/tasks", methods=["POST"])
def create():
    try:
        if "options" not in request.form:
            raise HTTPException(status_code=400, detail="No options provided")
        if "images" not in request.files:
            raise HTTPException(status_code=400, detail="No images provided")

        files = request.files.getlist("images")
        if not files or files[0].filename == "":
            raise HTTPException(status_code=400, detail="No images selected")

        video_options = VideoOptions(**json.loads(request.form.get("options")))
        video_task = VideoTask.create_new(video_options)
        for file in files:
            file_ext = os.path.splitext(file.filename)[1]
            file_path = video_task.add_image(file_ext)
            file.save(file_path)

        video_task.run()
        return jsonify({"status": "success", "id": video_task.task_id})

    except Exception as e:
        logging.exception("/api/create")
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route("/api/tasks/<task_id>/result", methods=["GET"])
def get_result(task_id):
    try:
        video_task = VideoTask.resume_from(task_id, {})
        video_path = video_task.get_merged_video_path()
        return send_file(video_path)        
    except Exception as e:
        logging.exception("/api/tasks/<task_id>/result")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/api/config", methods=["GET"])
def get_config():
    return jsonify(get_config_all())


@app.route("/api/config/reload", methods=["GET"])
def get_reload_config():
    load_config()
    return jsonify(get_config_all())


@app.route("/api/config", methods=["POST"])
def post_set_config():
    set_config(request.form["key"], request.form["value"])
    save_config()
    return Response(status=204)


if __name__ == "__main__":
    load_config()
    app.run(debug=False, use_reloader=False, host=FLASK_HOST, port=FLASK_PORT)
