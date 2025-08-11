import requests

TOKEN_PATH = "token-0.txt"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"

def read_token():
    with open(TOKEN_PATH, "r") as f:
        token = f.read().strip()
    return token

def request_report(token: str):
    r = requests.post("https://api.deevid.ai/event/report", headers={
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Referer": "https://deevid.ai/",
        "user-agent": ""
    })

def request_image():
    pass

def request_submit():
    pass

def request_tasks():
    pass

def dee_video(input_image_path: str, prompt: str, output_video_path: str):
    pass

def main():
    token = read_token()
    print(token)
    result = request_report()
    print(result)

if __name__ == "__main__":
    main()