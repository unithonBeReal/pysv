import os
from dotenv import load_dotenv
from google import genai

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

PROMPT = """
이 집은 진짜.... 와 같이 초반에는 후킹 할 수 있는 멘트로 구성하고 음식점 홍보하는 릴스 대본 100글자로 딱 한글만 줘 상황 설명하는 괄호는 빼줘. 한 줄에 한 문장씩 쓸 수 있도록 자연스럽게 만들어주고, 한 줄은 최대 20글자 정도로
가게 이름: <business_name>
가게 설명: <description>
가게 분위기: <mode>
"""

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

    def generate_script(self, business_name: str, description: str, mode: str) -> str:
        prompt = PROMPT.replace("<business_name>", business_name)
        prompt = prompt.replace("<description>", description)
        prompt = prompt.replace("<mode>", mode)
        response = self.model.models.generate_content(
            model='gemini-2.5-flash', contents=[prompt])
        return response.text


if __name__ == '__main__':
    # 💡 테스트 전, .env 파일을 생성하고 아래 형식으로 키를 저장하거나
    #    셸 환경에서 `export GEMINI_API_KEY="your_api_key_here"`를 실행해야 합니다.
    #    GEMINI_API_KEY="여러분의실제API키"

    try:
        gemini_client = GeminiClient()

        # 예시 데이터
        business_name = "매콤돈까스"
        description = "새롭게 오픈한 돈까스 맛집, 특별한 매콤 소스가 일품입니다."
        mode = "활기찬"

        script = gemini_client.generate_script(
            business_name=business_name,
            description=description,
            mode=mode
        )

        if script:
            print("🤖 생성된 릴스 대본:")
            print("--------------------")
            print(script)

    except ValueError as e:
        print(e)