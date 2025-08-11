import os
import shutil

from dotenv import load_dotenv
load_dotenv()

from task import VideoCreationOptions, VideoTask

def create_new():
    video_options = VideoCreationOptions(business_name="889와규 숭실대점", cut_length_sec=0)
    video_task = VideoTask.create_new(video_options)
    files = ["1.jpg", "2.jpg", "3.jpg"]
    print(video_task.task_id)
    for file_src in files:
        file_ext = os.path.splitext(file_src)[1]
        file_dst = video_task.add_image(file_ext)
        shutil.copy2(file_src, file_dst)
    video_task.run()

def resume_from():
    video_task = VideoTask.resume_from("568591")
    print(video_task.task_id)
    video_task.run()

if __name__ == "__main__":
    #create_new()
    resume_from()