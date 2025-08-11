import os
import json

config_file_path = os.getenv("CONFIG_FILE_PATH")
if not config_file_path:
    raise ValueError("CONFIG_FILE_PATH environment variable must be set")

is_config_loaded = False
config = {}

def get_config_all():
    if not is_config_loaded:
        load_config()
    return config

def get_config(key: str):
    if not is_config_loaded:
        load_config()
    return config[key]

def set_config(key: str, value: str):
    config[key] = value

def load_config():
    global config
    global is_config_loaded
    with open(config_file_path, 'r', encoding="utf-8") as f:
        config = json.load(f)
    is_config_loaded = True

def save_config():
    global config
    os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
        
    with open(config_file_path, 'w') as f:
        json.dump(config, f, indent=2)

