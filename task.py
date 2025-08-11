import logging
import shutil
from dataclasses import dataclass, asdict
import json
import os
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from config import get_config
from deeClient import DeeClient
from gemini_client import GeminiClient
from video_editor import cut_video, VideoEditor, ffmpeg_merge_videos, synthesize_speech, ffmpeg_merge_audios, \
    AUDIO_PRE_CUT_SEC
from google_tts import GoogleTTS
from mutagen.mp3 import MP3

VIDEO_PROMPT = """
줌인, 탑뷰 카메라 무빙, 45도 각도 카메라 무빙, 궤도 샷 (Arc Shot / Orbit Shot): 음식의 측면에서 시작하여 45도 각도까지 부드럽게 원을 그리며 돈다, 1인칭 시점으로 먹는 것처럼 보여준다, 젓가락으로 음식 들기
위 기법 중 네가 랜덤으로 2개 선택해서 화면 전화해줘
"""

WORK_GENERATE_VIDEO = "generate_video"
WORK_CUT_VIDEO = "cut_video"
WORK_MERGE_VIDEO = "merge_video"
WORK_GENERATE_SCRIPT = "generate_script"
WORK_GENERATE_TTS = "generate_tts"
WORK_EDIT_VIDEO = "edit_video"
WORK_FINISH = "finish"

DATA_PATH = os.environ.get("DATA_PATH", "")
if not DATA_PATH:
    raise ValueError("DATA_PATH is not set")

@dataclass
class VideoCreationOptions:
    business_name: str
    description: str
    mode: str
    cut_length_sec: int

class VideoTask:
    @staticmethod
    def create_new(options: VideoCreationOptions):
        task_id = str(random.randint(100000, 999999))
        task = VideoTask(task_id)
        task.options = options
        task.initialize_dir()
        return task

    @staticmethod
    def resume_from(task_id: str):
        task = VideoTask(task_id)
        task.initialize_dir()
        task.load_info()
        return task

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.ext_list = []
        self.script_list = []
        self.completed_work_list = []
        self.options = VideoCreationOptions("", "", "", 5)

    def serialize(self):
        info_data = {
            'task_id': self.task_id,
            'ext_list': self.ext_list,
            'script_list': self.script_list,
            'completed_work_list': self.completed_work_list,
            'options': asdict(self.options)
        }
        return json.dumps(info_data, ensure_ascii=False, indent=2)

    def load_info(self):
        path = self.get_info_file_path()
        with open(path, 'r', encoding='utf-8') as f:
            obj = json.load(f)
            self.task_id = obj["task_id"]
            self.ext_list = obj["ext_list"]
            self.script_list = obj["script_list"]
            self.completed_work_list = obj["completed_work_list"]
            self.options = VideoCreationOptions(**obj["options"])

    def save_info(self):
        path = self.get_info_file_path()
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.serialize())

    def get_work_dir(self):
        return os.path.join(DATA_PATH, self.task_id)

    def initialize_dir(self):
        os.makedirs(self.get_work_dir(), exist_ok=True)
        os.makedirs(os.path.join(self.get_work_dir(), "input"), exist_ok=True)
        os.makedirs(os.path.join(self.get_work_dir(), "video"), exist_ok=True)
        os.makedirs(os.path.join(self.get_work_dir(), "cut"), exist_ok=True)
        os.makedirs(os.path.join(self.get_work_dir(), "tts"), exist_ok=True)

    def get_info_file_path(self):
        return os.path.abspath(os.path.join(self.get_work_dir(), "info.json"))

    def get_image_path(self, index: int):
        return os.path.abspath(os.path.join(self.get_work_dir(), "input", str(index) + self.ext_list[index]))

    def get_generated_video_path(self, index: int):
        return os.path.abspath(os.path.join(self.get_work_dir(), "video", str(index) + ".mp4"))

    def get_cutted_video_path(self, index: int):
        return os.path.abspath(os.path.join(self.get_work_dir(), "cut", str(index) + ".mp4"))

    def get_merged_video_path(self):
        return os.path.abspath(os.path.join(self.get_work_dir(), "merged.mp4"))

    def get_tts_path(self, index: int):
        return os.path.abspath(os.path.join(self.get_work_dir(), "tts", str(index) + ".mp3"))

    def get_merged_tts_path(self):
        return os.path.abspath(os.path.join(self.get_work_dir(), "merged.mp3"))

    def get_final_video_path(self):
        return os.path.abspath(os.path.join(self.get_work_dir(), "final.mp4"))

    def get_image_count(self):
        return len(self.ext_list)

    def add_image(self, ext: str) -> str:
        path = os.path.join(self.get_work_dir(), "input", str(self.get_image_count()) + ext)
        self.ext_list.append(ext)
        return path

    def has_work_done(self, work_name: str):
        return work_name in self.completed_work_list

    def add_work_done(self, work_name: str):
        self.completed_work_list.append(work_name)

    def generate_videos(self):
        with ThreadPoolExecutor(max_workers=1) as executor:
            future_to_index = {
                executor.submit(self.generate_video, index): index 
                for index in range(self.get_image_count())
            }

            for future in as_completed(future_to_index):
                future.result()

    def generate_video(self, index: int):
        image_path = self.get_image_path(index)
        output_video_path = self.get_generated_video_path(index)
        
        client = DeeClient(
            token=get_config("dee_token"), 
            user_agent=get_config("dee_user_agent"))
        video_url = client.dee_video(VIDEO_PROMPT, image_path)

        if not video_url:
            raise Exception("no video url")

        # download video_url into output_video_path
        response = requests.get(video_url, stream=True)
        if response.status_code == 200:
            with open(output_video_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        else:
            raise Exception(f"Failed to download video from {video_url}, status code: {response.status_code}")

    def cut_videos(self):
        for index in range(self.get_image_count()):
            if self.options.cut_length_sec <= 0:
                shutil.copy2(
                    self.get_generated_video_path(index),
                    self.get_cutted_video_path(index))
            else:
                cut_video(
                    self.get_generated_video_path(index),
                    self.get_cutted_video_path(index),
                    self.options.cut_length_sec)

    def merge_videos(self):
        input_path_list = [self.get_cutted_video_path(index) for index in range(self.get_image_count())]
        ffmpeg_merge_videos(input_path_list, self.get_merged_video_path())

    def generate_script(self):
        gemini_client = GeminiClient()
        script = gemini_client.generate_script(self.options.business_name, self.options.description, self.options.mode)
        self.script_list = []
        for line in script.split('\n'):
            if line.strip():
                self.script_list.append(line.strip())
        
    def generate_tts(self):
        tts = GoogleTTS()
        for index, prompt in enumerate(self.script_list):
            tts_path = self.get_tts_path(index)
            tts.synthesize_speech(
                prompt,
                tts_path,
                language_code="en-US",
                voice_name="en-US-Chirp3-HD-Achernar"
            )

    def edit_video(self):
        all_timestamps = []
        current_time = 0.0
        for index, prompt in enumerate(self.script_list):
            tts_path = self.get_tts_path(index)
            tts_duration = MP3(tts_path).info.length
            timestamps = synthesize_speech(prompt, tts_duration)

            adjusted_timestamps = []
            for word, end_time in timestamps:
                adjusted_end_time = current_time + end_time
                adjusted_timestamps.append((word, adjusted_end_time))

            all_timestamps.extend(adjusted_timestamps)
            current_time += (tts_duration - AUDIO_PRE_CUT_SEC)

        tts_files = [self.get_tts_path(index) for index in range(len(self.script_list))]
        ffmpeg_merge_audios(tts_files, self.get_merged_tts_path())

        editor = VideoEditor(
            self.get_merged_video_path(), 
            self.get_merged_tts_path())

        editor.add_subtitles_from_timestamps(all_timestamps)
        editor.composite_video(self.get_final_video_path())

    def run_work(self, work_name: str, func):
        try:
            if not self.has_work_done(work_name):
                func()
                self.add_work_done(work_name)
        except Exception as e:
            raise e
        finally:
            self.save_info()

    def run(self):
        try:
            self.run_work(WORK_GENERATE_VIDEO, lambda: self.generate_videos())
            self.run_work(WORK_CUT_VIDEO, lambda: self.cut_videos())
            self.run_work(WORK_MERGE_VIDEO, lambda: self.merge_videos())
            self.run_work(WORK_GENERATE_SCRIPT, lambda: self.generate_script())
            self.run_work(WORK_GENERATE_TTS, lambda: self.generate_tts())
            self.run_work(WORK_EDIT_VIDEO, lambda: self.edit_video())
            self.run_work(WORK_FINISH, lambda: None)
        except Exception as e:
            logging.error(f"Error in run: {e}")
            raise e