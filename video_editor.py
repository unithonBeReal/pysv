import os
import tempfile
import ffmpeg
from mutagen.mp3 import MP3
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

AUDIO_PRE_CUT_SEC = 0.5

# ffmpeg -i input_path -t video_length_sec -c copy output_path -y
def cut_video(input_path: str, output_path: str, video_length_sec: int):
    stream = ffmpeg.input(input_path)
    stream = ffmpeg.output(stream, output_path, t=video_length_sec)
    ffmpeg.run(stream)

# ffmpeg -f concat -safe 0 -i filelist.txt -c copy output_path -y
def merge_audios(input_path_list: list[str], output_path: str):
    import subprocess
    import os
    
    # filelist.txt 파일에 입력 파일 목록 작성
    with open('filelist.txt', 'w', encoding='utf-8') as temp_file:
        for input_path in input_path_list:
            temp_file.write(f"file '{input_path}'\n")
            temp_file.write(f"inpoint {AUDIO_PRE_CUT_SEC}\n")
    
    # ffmpeg 명령어 실행
    cmd = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', 'filelist.txt',
        '-c', 'copy',
        output_path,
        '-y'  # 기존 파일 덮어쓰기
    ]
    
    # subprocess로 ffmpeg 실행하고 완료될 때까지 대기
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # filelist.txt 파일 삭제
    if os.path.exists('filelist.txt'):
        os.unlink('filelist.txt')
    
    if result.returncode != 0:
        print(f"FFmpeg 오류: {result.stderr}")
        return False
    else:
        print(f"음성 파일이 성공적으로 합쳐져서 '{output_path}'에 저장되었습니다.")
        return True

def cut_prompt_by_word_boundary(text: str, min_length: int = 6, max_length: int = 30) -> list[str]:
    """
    텍스트를 20-30글자 사이로 자르되, 공백으로만 잘라서 단어가 짤리지 않도록 합니다.
    끝까지 다 잘라서 문자열 배열을 반환합니다.
    
    Args:
        text (str): 자를 텍스트
        min_length (int): 최소 글자수 (기본값: 20)
        max_length (int): 최대 글자수 (기본값: 30)
    
    Returns:
        list[str]: 잘린 텍스트들의 배열
    """
    if len(text) <= max_length:
        return [text]
    
    # 공백으로 단어를 분리
    words = text.split()
    result_parts = []
    current_part = ""
    
    for word in words:
        # 현재 단어를 추가했을 때의 길이 계산
        test_text = current_part + (" " + word if current_part else word)
        
        # 최대 길이를 초과하면 현재 부분을 결과에 추가하고 새 부분 시작
        if len(test_text) > max_length:
            if current_part:  # 현재 부분이 있으면 결과에 추가
                result_parts.append(current_part)
                current_part = word
            else:  # 현재 부분이 없으면 첫 번째 단어라도 포함
                current_part = word
        else:
            current_part = test_text
    
    # 마지막 부분이 남아있으면 추가
    if current_part:
        # 최소 길이 조건 확인
        if len(current_part) >= min_length:
            result_parts.append(current_part)
        elif result_parts:  # 최소 길이보다 짧지만 이전 부분이 있으면 마지막 부분에 추가
            result_parts[-1] = result_parts[-1] + " " + current_part
        else:  # 첫 번째 부분이고 최소 길이보다 짧으면 그냥 추가
            result_parts.append(current_part)
    
    return result_parts

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

def synthesize_speech(text: str, duration_sec: float):
    #return [(text, duration)]
    sec_per_ch = duration_sec / len(text)

    # 2. 공백 기준으로 문장을 나누어 단어를 추출
    words = text.split(' ')
    
    # 3. 각 단어의 글자수 * MS_PER_CH를 곱해 단어의 길이를 계산
    timestamps = []
    current_time = 0
    
    for word in words:
        if word.strip():  # 빈 문자열이 아닌 경우만 처리
            word_duration = len(word) * sec_per_ch
            current_time += word_duration
            timestamps.append((word, current_time))
    
    return timestamps

# 예제 사용법
if __name__ == '__main__':
    # import os
    # audio_files = [os.path.abspath(f"{i + 1}.mp3") for i in range(10)]
    # merge_videos(audio_files, "final_audio.mp3")

    # 1. GoogleTTS를 사용하여 음성 파일과 타임스탬프를 생성합니다.
    from google_tts import GoogleTTS
    tts = GoogleTTS()
    prompt = """
이 집은 진짜...
와, 이건 미쳤다!
인생 맛집 등극!
메뉴 하나하나가
전부 다 예술이야.
특히 시그니처는
꼭 먹어야 할 맛!
분위기도 최고다.
지금 당장 가야 해.
후회는 없을 거야!
"""
    
    # 프롬프트를 20-30글자로 자르기
    #cut_prompts = cut_prompt_by_word_boundary(prompt)
    cut_prompts = [line.strip() for line in prompt.split('\n') if line.strip()]
    print(f"원본 프롬프트 길이: {len(prompt)}글자")
    print(f"잘린 프롬프트 개수: {len(cut_prompts)}개")
    for i, cut_prompt in enumerate(cut_prompts):
        print(f"  {i+1}번째: {cut_prompt} ({len(cut_prompt)}글자)")
    
    # 각 잘린 프롬프트마다 TTS 생성 및 타임스탬프 계산
    all_timestamps = []
    current_time = 0.0
    
    for i, cut_prompt in enumerate(cut_prompts):
        audio_file = f"{i+1}.mp3"
        
        # TTS 생성
        success = tts.synthesize_speech(
            cut_prompt,
            audio_file,
            #language_code="ko-KR",
            #voice_name="ko-KR-WaveNet-A"
            language_code="en-US",
            voice_name="en-US-Chirp3-HD-Achernar"
        )
        
        if success:
            # 각 음성 파일의 duration 구하기
            duration = MP3(audio_file).info.length - AUDIO_PRE_CUT_SEC
            print(f"{i+1}번째 음성 파일 길이: {duration:.2f}초")
            
            # 현재 프롬프트의 타임스탬프 계산 (이전 시간을 더해서)
            timestamps = synthesize_speech(cut_prompt, duration)
            
            # 타임스탬프에 이전 시간을 더해서 조정
            adjusted_timestamps = []
            for word, end_time in timestamps:
                adjusted_end_time = current_time + end_time
                adjusted_timestamps.append((word, adjusted_end_time))
            
            all_timestamps.extend(adjusted_timestamps)
            
            # 다음 프롬프트의 시작 시간을 현재 시간 + 현재 duration으로 설정
            current_time += duration
        else:
            print(f"TTS 생성 실패: {cut_prompts[i]}")
    
    # 모든 타임스탬프 출력
    print(f"\n전체 타임스탬프:")
    for i, (word, end_time) in enumerate(all_timestamps):
        print(f"  {i+1}: {word} (끝: {end_time:.2f}초)")
    
    # 음성 파일들을 하나로 합치기
    final_audio_file = "final.mp3"
    if len(cut_prompts) > 1:
        import os
        audio_files = [os.path.abspath(f"{i+1}.mp3") for i in range(len(cut_prompts))]
        merge_videos(audio_files, "final_audio.mp3")
        final_audio_file = "final_audio.mp3"
    else:
        final_audio_file = "1.mp3"
    
    # 비디오 에디터 초기화 및 자막 추가
    if all_timestamps:
        editor = VideoEditor('test_video.mp4', final_audio_file)
        editor.add_subtitles_from_timestamps(all_timestamps)

        # 4. 최종 영상을 합성하고 저장합니다.
        editor.composite_video("final_output_with_subtitles.mp4")
