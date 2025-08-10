from dataclasses import dataclass
import os
import random

DATA_PATH = os.environ.get("DATA_PATH", "")
if not DATA_PATH:
    raise ValueError("DATA_PATH is not set")
    
@dataclass
class VideoOptions:
    business_name: str

class VideoTask:
    def create_new(options: VideoOptions):
        work_dir = os.path.join(DATA_PATH, str(random.randint(10000, 99999)))
        os.makedirs(work_dir, exist_ok=True)
        return VideoTask(work_dir, options)
    
    def __init__(self, work_dir: str, options: VideoOptions):
        self.work_dir = work_dir
        self.options = options

    def get_wd_image_path(self, index: int):
        return os.path.join(self.work_dir, "input", index)

    def get_wd_video_path(self, index: int):
        return os.path.join(self.work_dir, "video", index)