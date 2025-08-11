import os
from dotenv import load_dotenv
from google import genai

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

PROMPT = """
음식점 홍보용 인스타그램 릴스 대본을 아래 조건에 맞춰 생성해 줘.

[조건]
- 첫 문장은 '이 집은 진짜...'처럼 호기심을 유발하는 문구로 시작
- 전체 분량은 공백 포함 100자 내외로 구성
- 각 문장은 20자 미만으로, 한 줄씩 줄바꿈으로 구분
- 음식 맛, 가게 분위기, 방문 추천 내용을 포함
- 최종 결과물은 한글 대본만, 괄호나 부가 설명 없이 출력
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

    def generate_script(self) -> str:
        response = self.model.models.generate_content(
            model='gemini-2.5-flash', contents=[PROMPT])
        return response.text


if __name__ == '__main__':
    # 💡 테스트 전, .env 파일을 생성하고 아래 형식으로 키를 저장하거나
    #    셸 환경에서 `export GEMINI_API_KEY="your_api_key_here"`를 실행해야 합니다.
    #    GEMINI_API_KEY="여러분의실제API키"

    try:
        gemini_client = GeminiClient()
        script = gemini_client.generate_script()

        if script:
            print("🤖 생성된 릴스 대본:")
            print("--------------------")
            print(script)

    except ValueError as e:
        print(e)