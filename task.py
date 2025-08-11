from dataclasses import dataclass
import os
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

from genClients import gen_video
from video_editor import cut_video, merge_videos

DATA_PATH = os.environ.get("DATA_PATH", "")
if not DATA_PATH:
    raise ValueError("DATA_PATH is not set")

PROMPT_TEMPLATE = """
zoom in to the image and <business_name>
"""
    
@dataclass
class VideoOptions:
    business_name: str
    cut_length_sec: int

class VideoTask:
    def create_new(options: VideoOptions):
        task_id = str(random.randint(10000, 99999))
        task = VideoTask(task_id, options)
        task.initialize_dir()
        return task
    
    def resume_from(task_id: str, options: VideoOptions):
        task = VideoTask(task_id, options)
        task.initialize_dir()
        return task

    def __init__(self, task_id: str, options: VideoOptions):
        self.task_id = task_id
        self.options = options
        self.ext_list = []

    def initialize_dir(self):
        os.makedirs(self.get_work_dir(), exist_ok=True)
        os.makedirs(os.path.join(self.get_work_dir(), "input"), exist_ok=True)
        os.makedirs(os.path.join(self.get_work_dir(), "video"), exist_ok=True)

    def get_work_dir(self):
        return os.path.join(DATA_PATH, self.task_id)

    def get_image_count(self):
        return len(self.ext_list)

    def get_image_path(self, index: int):
        return os.path.join(self.get_work_dir(), "input", str(index) + self.ext_list[index])

    def get_generated_video_path(self, index: int):
        return os.path.join(self.get_work_dir(), "video", str(index) + ".mp4")

    def get_cutted_video_path(self, index: int):
        return os.path.join(self.get_work_dir(), "cut", str(index) + ".mp4")

    def get_merged_video_path(self):
        return os.path.join(self.get_work_dir(), "merged.mp4")

    def add_image(self, ext: str) -> str:
        path = os.path.join(self.get_work_dir(), "input", str(self.get_image_count()) + ext)
        self.ext_list.append(ext)
        return path

    def generate_prompt(self):
        return PROMPT_TEMPLATE.replace("<business_name>", self.options.business_name)

    def generate_videos(self):
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_to_index = {
                executor.submit(self.generate_video, index): index 
                for index in range(self.get_image_count())
            }

            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    future.result()
                    print(f"Completed video generation for index: {index}")
                except Exception as e:
                    print(f"Error generating video for index {index}: {e}")

    def generate_video(self, index: int):
        prompt = self.generate_prompt()
        image_path = self.get_image_path(index)
        output_video_path = self.get_generated_video_path(index)
        gen_video(image_path, prompt, output_video_path)

    def cut_videos(self):
        for index in range(self.get_image_count()):
            cut_video(
                self.get_generated_video_path(index), 
                self.get_cutted_video_path(index), 
                self.options.cut_length_sec)

    def merge_videos(self):
        input_path_list = [self.get_cutted_video_path(index) for index in range(self.get_image_count())]
        merge_videos(input_path_list, self.get_merged_video_path())

    def run(self):
        self.generate_videos()
        self.cut_videos()
        self.merge_videos()