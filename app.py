from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify, request
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


@app.route("/api/create", methods=["POST"])
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
            file_path = video_task.add_image(file.filename)
            file.save(file_path)

        video_task.run()
        return jsonify({"message": "success", "status": "success"})

    except Exception as e:
        print(f"error: {e}")
        return jsonify({"message": "error", "status": "error", "error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host=FLASK_HOST, port=FLASK_PORT)
