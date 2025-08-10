from dataclasses import dataclass
import os
import random

DATA_PATH = os.environ.get("DATA_PATH", "")
if not DATA_PATH:
    raise ValueError("DATA_PATH is not set")
    
@dataclass
class VideoOptions:
    business_name: str
    cut_length_sec: int

class VideoTask:
    def create_new(options: VideoOptions):
        work_dir = os.path.join(DATA_PATH, str(random.randint(10000, 99999)))
        os.makedirs(work_dir, exist_ok=True)
        os.makedirs(os.path.join(work_dir, "input"), exist_ok=True)
        os.makedirs(os.path.join(work_dir, "video"), exist_ok=True)
        return VideoTask(work_dir, options)
    
    def __init__(self, work_dir: str, options: VideoOptions):
        self.work_dir = work_dir
        self.options = options

    def get_image_path(self, index: int):
        return os.path.join(self.work_dir, "input", str(index) + ".jpg")

    def get_video_path(self, index: int):
        return os.path.join(self.work_dir, "video", str(index) + ".mp4")

    def get_merged_video_path(self):
        return os.path.join(self.work_dir, "merged.mp4")