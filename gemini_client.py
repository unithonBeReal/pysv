import os
from dotenv import load_dotenv
from google import genai

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()


class GeminiClient:

    def __init__(self):
        """
        GeminiClient를 초기화하고 API 키 설정 및 모델을 준비합니다.
        """
        # 1. 환경 변수에서 API 키를 읽어옵니다.
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")

        # 2. google-genai 라이브러리에 API 키를 설정합니다.
        self.model = genai.Client(api_key=api_key)

    def generate_script(self, prompt: str = "이 집은 진짜.... 와 같이 초반에는 후킹 할 수 있는 멘트로 구성하고 음식점 홍보하는 릴스 대본 100글자로 딱 한글만 줘 상황 설명하는 괄호는 빼줘") -> str:
        """
        주어진 프롬프트를 기반으로 릴스 대본을 생성합니다.

        :param prompt: 대본 생성을 위한 프롬프트
        :return: 생성된 대본 텍스트
        """
        try:
            # 4. generate_content 메서드로 API에 요청을 보냅니다.
            response = self.model.models.generate_content(
                model='gemini-2.5-flash', contents=[prompt])
            return response.text
        except Exception as e:
            print(f"스크립트 생성 중 오류 발생: {e}")
            return ""


if __name__ == '__main__':
    # 💡 테스트 전, .env 파일을 생성하고 아래 형식으로 키를 저장하거나
    #    셸 환경에서 `export GEMINI_API_KEY="your_api_key_here"`를 실행해야 합니다.
    #    GEMINI_API_KEY="여러분의실제API키"

    try:
        gemini_client = GeminiClient()

        test_prompt = "이 집은 진짜.... 와 같이 초반에는 후킹 할 수 있는 멘트로 구성하고 음식점 홍보하는 릴스 대본 100글자로 딱 한글만 줘 상황 설명하는 괄호는 빼줘"
        script = gemini_client.generate_script(test_prompt)

        if script:
            print("🤖 생성된 릴스 대본:")
            print("--------------------")
            print(script)

    except ValueError as e:
        print(e)