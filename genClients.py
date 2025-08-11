import time
import genai
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.genai.types import Image
from google import genai
from task import VideoTask

#VIDEO_MODEL_NAME = "veo-3.0-fast-generate-preview"
VIDEO_MODEL_NAME = "veo-2.0-generate-001"
RETRY_COUNT = 3

# Load API keys from environment variable
api_keys_str = os.getenv('GENAI_API_KEY', '')
api_keys = [key.strip() for key in api_keys_str.split(',') if key.strip()]

# Initialize genai clients
genai_clients = [genai.Client(api_key=api_key) for api_key in api_keys]
current_client_index = 0
client_lock = threading.Lock()  # Lock for thread-safe client rotation

def get_current_genai_client():
    """Returns the current genai client based on current_client_index"""
    if not genai_clients:
        raise ValueError("No genai clients available")
    with client_lock:
        return genai_clients[current_client_index]

def rotate_genai_client():
    """Rotates to the next genai client, wrapping around to the beginning if needed"""
    global current_client_index
    if not genai_clients:
        raise ValueError("No genai clients available")
    with client_lock:
        current_client_index = (current_client_index + 1) % len(genai_clients)
        return genai_clients[current_client_index]

def gen_video(input_image_path: str, prompt: str, output_video_path: str):
    for i in range(RETRY_COUNT):
        try:
            inner_gen_video(input_image_path, prompt, output_video_path)
            return
        except Exception as e:
            print(e)
            rotate_genai_client()
            last_error = e
    raise last_error

def inner_gen_video(input_image_path: str, prompt: str, output_video_path: str):
    client = get_current_genai_client()
    image = Image.from_file(location=input_image_path)
    operation = client.models.generate_videos(
        model=VIDEO_MODEL_NAME,
        prompt=prompt,
        image=image)
        
    elapsed_time = 0
    while not operation.done:
        print(f"generate_video: {output_video_path} elapsed time: {elapsed_time}s")
        time.sleep(10)
        elapsed_time += 10
        operation = client.operations.get(operation)

    video = operation.response.generated_videos[0]
    client.files.download(file=video.video)
    video.video.save(output_video_path)
    print(f"saved video: {output_video_path}")