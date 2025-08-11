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
    def __init__(self, text, start_time, end_time, font_path='static/fonts/firstFont.ttf', fontsize=24, color='white', bg_color='black'):
        self.text = text
        self.start_time = start_time
        self.end_time = end_time
        self.font_path = font_path
        self.fontsize = fontsize
        self.color = color
        self.bg_color = bg_color

    def to_textclip(self, video_size):
        """ SubtitleClip을 MoviePy의 TextClip으로 변환합니다. """
        return TextClip(
            self.text,
            font_size=self.fontsize,
            color=self.color,
            # font=self.font_path,
            bg_color=self.bg_color,
            size=(video_size[0] * 0.8, None) # 자막 너비를 비디오 너비의 80%로 제한
        ).set_position(('center', 'bottom')).set_duration(self.end_time - self.start_time).set_start(self.start_time)

class VideoEditor:
    def __init__(self, video_path, audio_path):
        self.video_clip = VideoFileClip(video_path)
        self.audio_clip = AudioFileClip(audio_path)
        self.subtitles = []

    def add_subtitles_from_timestamps(self, timestamps):
        """ 타임스탬프 정보를 바탕으로 자막들을 생성합니다. """
        for i, (word, start) in enumerate(timestamps):
            end = timestamps[i + 1][1] if i + 1 < len(timestamps) else self.audio_clip.duration
            if end > start:
                self.subtitles.append(SubtitleClip(word, start, end))

    def composite_video(self, output_path="final_video.mp4"):
        """ 비디오, 오디오, 자막을 최종 합성합니다. """
        if not self.subtitles:
            print("자막이 없습니다. 원본 영상과 오디오만 합성합니다.")
            final_clip = self.video_clip.set_audio(self.audio_clip)
        else:
            subtitle_clips = [sub.to_textclip(self.video_clip.size) for sub in self.subtitles]
            
            # 비디오 클립의 길이를 오디오 길이에 맞춥니다.
            if self.video_clip.duration > self.audio_clip.duration:
                self.video_clip = self.video_clip.subclip(0, self.audio_clip.duration)
            
            final_clip = CompositeVideoClip([self.video_clip] + subtitle_clips).set_audio(self.audio_clip)
        
        final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
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
        # 2. 테스트용 비디오 파일과 방금 생성한 오디오 파일로 VideoEditor를 초기화합니다.
        #    (테스트를 위해 'test_video.mp4'라는 이름의 영상 파일이 필요합니다.)
        try:
            # 3. 타임스탬프 정보로 자막을 추가합니다.
            editor = VideoEditor('test_video.mp4', audio_file)
            editor.add_subtitles_from_timestamps(word_timestamps)
            
            # 4. 최종 영상을 합성하고 저장합니다.
            editor.composite_video("final_output_with_subtitles.mp4")
        except Exception as e:
            print(f"영상 처리 중 오류가 발생했습니다: {e}")
            print("테스트를 위해서는 'test_video.mp4' 파일이 프로젝트 루트에 필요합니다.")
