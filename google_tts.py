import os
from google.cloud import texttospeech_v1beta1 as texttospeech
import re

class GoogleTTS:
    def __init__(self, credentials_path="google-service-key.json"):
        """
        GoogleTTS 클래스를 초기화합니다.
        GOOGLE_APPLICATION_CREDENTIALS 환경 변수를 설정합니다.

        :param credentials_path: Google Cloud 서비스 계정 키 파일 경로
        """
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        self.client = texttospeech.TextToSpeechClient()

    def synthesize_speech(self, text, output_filename="output.mp3", language_code="ko-KR", voice_name="ko-KR-WaveNet-A", speaking_rate=1.0):
        """
        주어진 텍스트를 음성으로 변환하고, 단어별 타임스탬프를 반환합니다.

        :param text: 음성으로 변환할 텍스트
        :param output_filename: 저장할 오디오 파일 이름
        :param language_code: 사용할 언어 코드
        :param voice_name: 사용할 목소리 이름
        :param speaking_rate: 말하기 속도
        :return: (성공 여부, 단어별 타임스탬프 리스트)
        """
        words = re.findall(r"[\w']+", text)
        ssml_text = "<speak>"
        for i, word in enumerate(words):
            ssml_text += f'{word} <mark name="{i}"/>'
        ssml_text += "</speak>"

        synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=speaking_rate
        )

        try:
            request = texttospeech.SynthesizeSpeechRequest(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config,
                enable_time_pointing=[texttospeech.SynthesizeSpeechRequest.TimepointType.SSML_MARK]
            )
            response = self.client.synthesize_speech(request=request)

            with open(output_filename, "wb") as out:
                out.write(response.audio_content)
                print(f'Audio content written to file "{output_filename}"')

            timepoints = []
            for i, timepoint in enumerate(response.timepoints):
                if i < len(words):
                    timepoints.append((words[i], timepoint.time_seconds))
            
            return True, timepoints
        except Exception as e:
            print(f"Error during speech synthesis: {e}")
            return False, []

# 예제 사용법
if __name__ == '__main__':
    tts_client = GoogleTTS()
 
    success, timestamps = tts_client.synthesize_speech(
        "노릇노릇 익은 삼겹살이 불판 위에서 지글지글, 쫀득한 육즙이 입안 가득 퍼지는 황홀함. 상추쌈과 함께 즐기는 조합, 지금 바로 청운 삼겹살에서 한 끼의 행복을 경험해보세요.",
        "output.mp3",
        language_code="ko-KR",
        voice_name="ko-KR-WaveNet-A"
    )

    if success:
        print("한국어 타임스탬프가 성공적으로 추출되었습니다")
        for word, time in timestamps:
            print(f"- 단어: '{word}', 시간: {time:.2f}초")
