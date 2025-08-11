import os

from google import genai

class GeminiClient:
    def __init__(self):
        """
        GeminiClient를 초기화하고 API 키를 설정합니다.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY가 설정 파일에 없습니다.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_script(self, prompt: str) -> str:
        """
        주어진 프롬프트를 기반으로 릴스 대본을 생성합니다.

        :param prompt: 대본 생성을 위한 프롬프트
        :return: 생성된 대본 텍스트
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error during script generation: {e}")
            return ""

if __name__ == '__main__':

    gemini_client = GeminiClient()
    
    test_prompt = "피트니스 센터를 홍보하는 30초짜리 릴스 대본을 작성해줘. 활기찬 분위기로!"
    script = gemini_client.generate_script(test_prompt)
    
    if script:
        print("생성된 릴스 대본:")
        print(script)
