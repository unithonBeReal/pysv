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

PROMPT_TEMPLATE = """
zoom in to the image and <business_name>
"""

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

def generate_prompt(task: VideoTask):
    return PROMPT_TEMPLATE.replace("<business_name>", task.options.business_name)

def generate_video_list(task: VideoTask, index_list: list[int]):
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Submit all video generation tasks
        future_to_index = {
            executor.submit(generate_video, task, index): index 
            for index in index_list
        }
        
        # Wait for all tasks to complete
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            try:
                future.result()  # This will raise any exception that occurred
                print(f"Completed video generation for index: {index}")
            except Exception as e:
                print(f"Error generating video for index {index}: {e}")

def generate_video(task: VideoTask, index: int):
    for i in range(RETRY_COUNT):
        try:
            inner_generate_video(task, index)
            break
        except Exception as e:
            last_error = e
            print(e)
            rotate_genai_client()
    raise last_error

def inner_generate_video(task: VideoTask, index: int):
    client = get_current_genai_client()
    prompt = generate_prompt(task)
    image_path = task.get_image_path(index)
    image = Image.from_file(location=image_path)
    operation = client.models.generate_videos(
        model=VIDEO_MODEL_NAME,
        prompt=prompt,
        image=image)
        
    elapsed_time = 0
    while not operation.done:
        print(f"generate_video: {task.work_dir} {index} elapsed time: {elapsed_time}s")
        time.sleep(10)
        elapsed_time += 10
        operation = client.operations.get(operation)

    video = operation.response.generated_videos[0]
    client.files.download(file=video.video)
    video.video.save(task.get_video_path(index))
    print(f"saved video: {task.work_dir} {index}")