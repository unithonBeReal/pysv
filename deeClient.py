import json
import mimetypes
import os
import random
import time
from PIL import Image
import requests

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"

class DeeClient:
    def __init__(self, token, user_agent):
        self.token = token
        self.user_agent = user_agent

    def request_report(self, event_type: str):
        r = requests.post(
            "https://api.deevid.ai/event/report",
            headers={
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "Referer": "https://deevid.ai/",
                "user-agent": self.user_agent,
            },
            json={
                "eventType": "CLICK",
                "eventName": event_type,
                "eventData": {
                    "page_url": "https://deevid.ai/ko/image-to-video",
                    "host": "deevid.ai",
                    "search": "",
                    "type": "/image-to-video_image1",
                    "user_type": "free",
                },
            },
        )

        if not r.ok:
            print(f"Status Code: {r.status_code}")
            print(f"Response Text: {r.text}")
            raise Exception("request_report: not ok")

    def request_image(self, file_name: str, file_path: str, mime_type: str):
        headers_payload = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Authorization": f"Bearer {self.token}",
            "Referer": "https://deevid.ai/",
            "user-agent": self.user_agent,
        }

        data_payload = {
            "width": 1024,
            "height": 1280,
        }

        with open(file_path, "rb") as f:
            files_payload = {"file": (file_name, f, mime_type)}
            #url = "https://httpbin.org/post"
            url = "https://api.deevid.ai/file-upload/image"
            r = requests.post(
                url, headers=headers_payload, data=data_payload, files=files_payload
            )

        if not r.ok:
            print(f"Status Code: {r.status_code}")
            print(f"Response Text: {r.text}")
            raise Exception("request_image: not ok")
        return self.parse_image_response(r.text)

    def parse_image_response(self, res: str):
        resObj = json.loads(res)
        return resObj["data"]["data"]["id"]

    def request_submit(self, prompt: str, imageId: int):
        headers_payload = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Referer": "https://deevid.ai/",
            "user-agent": self.user_agent,
        }

        json_payload = {
            "userImageId": imageId,
            "prompt": prompt,
            "lengthOfSecond": 5,
            "resolution": "480p",
            "aiPromptEnhance": True,
            "addEndFrame": False,
        }

        url = "https://api.deevid.ai/image-to-video/task/submit"
        #url = "https://httpbin.org/post"
        r = requests.post(
            url,
            headers=headers_payload,
            json=json_payload
        )

        if not r.ok:
            print(f"Status Code: {r.status_code}")
            print(f"Response Text: {r.text}")
            raise Exception("request_submit: not ok")
        return self.parse_submit_response(r.text)

    def parse_submit_response(self, res: str):
        resObj = json.loads(res)
        if resObj.get("error") is not None:
            raise Exception(f"API error: {resObj['error']}")
        return resObj["data"]["data"]["id"]

    def request_tasks(self):
        headers_payload = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Referer": "https://deevid.ai/",
            "user-agent": self.user_agent,
        }

        url = "https://api.deevid.ai/video/tasks?page=1&size=20"
        #url = "https://httpbin.org/get"
        r = requests.get(url, headers=headers_payload)

        if not r.ok:
            print(f"Status Code: {r.status_code}")
            print(f"Response Text: {r.text}")
            raise Exception("request_tasks: not ok")
        return self.parse_tasks_response(r.text)

    def parse_tasks_response(self, res: str):
        resObj = json.loads(res)
        return resObj["data"]["data"]["data"]

    def print_tasks(self, tasks):
        for task in tasks:
            print(task["id"])
            print(task["taskId"])
            print(task["taskState"])
            print(task["videoUrl"])

    def parse_test(self):
        with open("image_res.json") as f:
            imageId = self.parse_image_response(f.read().strip())
        print(imageId)

        with open("submit_res.json") as f:
            taskId = self.parse_submit_response(f.read().strip())
        print(taskId)

        with open("tasks_res_processing.json") as f:
            tasks = self.parse_tasks_response(f.read().strip())
        self.print_tasks(tasks)

        with open("tasks_res_success.json") as f:
            tasks = self.parse_tasks_response(f.read().strip())
        self.print_tasks(tasks)

    def get_random_image_file_name(self, path: str):
        filename = path.split('/')[-1]
        _, ext = os.path.splitext(filename)
        random_filename = random.randint(111111, 999999)
        return f"{random_filename}{ext}"

    def get_mime_type(self, path: str):
        mime_type, encoding = mimetypes.guess_type(path)
        if mime_type is None:
            raise Exception("Unknown file type: " + path)
        return mime_type

    def get_image_size(self, path: str):
        with Image.open(path) as img:
            width, height = img.size
            return width, height

    def dee_video(self, prompt: str, image_path: str):
        self.request_report("choose_media")
        time.sleep(1)
        self.request_report("begin_upload_media")
        time.sleep(1)
        filename = self.get_random_image_file_name(image_path)
        mimetype = self.get_mime_type(image_path)
        imageId = self.request_image(filename, image_path, mimetype)
        time.sleep(1)
        id = self.request_submit(prompt, imageId)

        start_time = time.time()
        while True:
            if time.time() - start_time > 120:
                raise Exception("dee_video: timeout")

            time.sleep(6)
            tasks = self.request_tasks()
            for task in tasks:
                if task["id"] == id and task["taskState"] == "SUCCESS":
                    return task["videoUrl"]

if __name__ == "__main__":
    with open("token-20.txt", "r") as f:
        token = f.read().strip()
    with open("prompt.txt", "r") as f:
        prompt = f.read().strip()

    client = DeeClient(token=token, user_agent=DEFAULT_USER_AGENT)
    client.dee_video(prompt=prompt, image_path="1.jpg")