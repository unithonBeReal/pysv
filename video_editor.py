import os
import tempfile
import ffmpeg

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
