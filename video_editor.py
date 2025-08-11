import os
import tempfile
import ffmpeg
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

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

class SubtitleClip:
    def __init__(self, text, start_time, duration, font_path='static/fonts/firstFont.ttf', fontsize=36, color='black', bg_color='black'):
        self.text = text
        self.start_time = start_time
        self.duration = duration
        self.font_path = font_path
        self.fontsize = fontsize
        self.color = color
        self.bg_color = bg_color

    def to_textclip(self, video_size):
        """ SubtitleClip을 MoviePy의 TextClip으로 변환합니다. """
        clip = TextClip(
            text=self.text,
            font_size=int(self.fontsize),
            color=self.color,
            font=self.font_path,
            bg_color="white",
            method="label",
            margin=(20, 10))

        pos_x = (video_size[0] - clip.size[0]) / 2
        return (clip.with_position((int(pos_x), 300), False)
                .with_duration(self.duration)
                .with_start(self.start_time))

class VideoEditor:
    def __init__(self, video_path, audio_path):
        self.video_clip = VideoFileClip(video_path)
        self.audio_clip = AudioFileClip(audio_path)
        self.subtitles = []

    def add_subtitles_from_timestamps(self, timestamps):
        """ 타임스탬프 정보를 바탕으로 자막들을 생성합니다. timestamps는 각 아이템의 끝 시간을 나타냅니다. """
        for i, (word, end_time) in enumerate(timestamps):
            # 이전 자막의 끝 시간을 시작 시간으로 사용
            if i > 0:
                start_time = timestamps[i - 1][1]  # 이전 자막의 끝 시간
            else:
                # 첫 번째 자막인 경우 0초부터 시작
                start_time = 0.0
            
            duration = end_time - start_time
            if duration > 0:
                self.subtitles.append(SubtitleClip(word, start_time, duration))

    def composite_video(self, output_path="final_video.mp4"):
        subtitle_clips = [sub.to_textclip(self.video_clip.size) for sub in self.subtitles]
        # 비디오 클립의 길이를 오디오 길이에 맞춥니다.
        if self.video_clip.duration > self.audio_clip.duration:
            self.video_clip = (self.video_clip
                .subclipped(0)
                .with_duration(self.audio_clip.duration))

        self.video_clip = CompositeVideoClip([self.video_clip] + subtitle_clips)
        self.video_clip = self.video_clip.with_audio(self.audio_clip)
        self.video_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
        print(f"최종 영상이 '{output_path}'에 저장되었습니다.")

# 예제 사용법
if __name__ == '__main__':
    # 1. GoogleTTS를 사용하여 음성 파일과 타임스탬프를 생성합니다.
    from google_tts import GoogleTTS
    tts = GoogleTTS()
    text_to_speak = "안녕하세요, 이것은 영상 편집과 자막 생성 테스트입니다. 각 단어마다 자막이 표시됩니다."
    audio_file = "test_audio.mp3"
    success, word_timestamps = tts.synthesize_speech(text_to_speak, audio_file)

    if success:
        editor = VideoEditor('test_video.mp4', audio_file)
        editor.add_subtitles_from_timestamps(word_timestamps)

        # 4. 최종 영상을 합성하고 저장합니다.
        editor.composite_video("final_output_with_subtitles.mp4")
