import os
from google.cloud import texttospeech

class GoogleTTS:
    def __init__(self, credentials_path="google-service-key.json"):
        """
        GoogleTTS 클래스를 초기화합니다.
        GOOGLE_APPLICATION_CREDENTIALS 환경 변수를 설정합니다.

        :param credentials_path: Google Cloud 서비스 계정 키 파일 경로
        """
        # TODO: "YOUR_SERVICE_ACCOUNT_KEY.json"을 실제 서비스 계정 키 파일 경로로 바꾸세요.
        # 이 파일은 Google Cloud Console에서 다운로드할 수 있습니다.
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        self.client = texttospeech.TextToSpeechClient()

    def synthesize_speech(self, text, output_filename="output.mp3", language_code="en-US", voice_name="en-US-Chirp3-HD-Achernar", speaking_rate=1.0):
        """
        주어진 텍스트를 음성으로 변환하고 파일로 저장합니다.

        :param text: 음성으로 변환할 텍스트
        :param output_filename: 저장할 오디오 파일 이름 (기본값: "output.mp3")
        :param language_code: 사용할 언어 코드 (기본값: "ko-KR")
        :param voice_name: 사용할 목소리 이름 (기본값: "ko-KR-Neural2-A")
        :param speaking_rate: 말하기 속도 (0.25 ~ 4.0, 기본값: 1.0)
        :return: 성공 시 True, 실패 시 False
        """
        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=speaking_rate
        )

        try:
            response = self.client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

            with open(output_filename, "wb") as out:
                out.write(response.audio_content)
                print(f'Audio content written to file "{output_filename}"')
            
            return True
        except Exception as e:
            print(f"Error during speech synthesis: {e}")
            return False

# 예제 사용법
if __name__ == '__main__':

    tts_client = GoogleTTS()

    # 공백 제거 10글자에 2초 걸립니다!
    tts_client.synthesize_speech("1배속 테스트는 몇 초 걸릴까요? 이것 좀 보세요", "output_english.mp3", language_code="en-US", voice_name="en-US-Chirp3-HD-Achernar")
    tts_client.synthesize_speech("2배속 테스트는 여덞구", "output_english2.mp3", language_code="en-US", voice_name="en-US-Chirp3-HD-Achernar")
    tts_client.synthesize_speech("새벽 3시까지 영업? 명동 한복판에 이런 숨겨진 아지트가 있었어? 초 복잡한 세상 완벽한 나만의 시간... 하이볼에 정성 가득 안주는 기본 혼술러 눈치 보일 틈 1도 없어", "output_english3.mp3", language_code="en-US", voice_name="en-US-Chirp3-HD-Achernar")
