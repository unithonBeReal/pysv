import os
import tempfile
import ffmpeg

from task import VideoTask

def cut_videos_task(task: VideoTask, index_list: list[int]):
    for index in index_list:
        cut_video(
            task.get_video_path(index), 
            task.get_video_path(index), 
            task.options.cut_length_sec)

def merge_videos_task(task: VideoTask, index_list: list[int]):
    input_path_list = [task.get_video_path(index) for index in index_list]
    merge_videos(input_path_list, task.get_merged_video_path())

# ffmpeg -i input_path -t video_length_sec -c copy output_path -y
def cut_video(input_path: str, output_path: str, video_length_sec: int):
    stream = ffmpeg.input(input_path)
    stream = ffmpeg.output(stream, output_path, t=video_length_sec)
    ffmpeg.run(stream)

# ffmpeg -f concat -safe 0 -i filelist.txt -c copy output_path -y
def merge_videos(input_path_list: list[str], output_path: str):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        for input_path in input_path_list:
            temp_file.write(f"file '{input_path}'\n")
        stream = ffmpeg.input(temp_file.name)
        stream = ffmpeg.output(stream, output_path)
        ffmpeg.run(stream)
