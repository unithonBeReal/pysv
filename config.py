import os
import json

config_file_path = os.getenv("CONFIG_FILE_PATH")
if not config_file_path:
    raise ValueError("CONFIG_FILE_PATH environment variable must be set")

config = {}

def get_config_all():
    return config

def get_config(key: str):
    return config[key]

def set_config(key: str, value: str):
    config[key] = value

def load_config():
    global config
    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as f:
            config = json.load(f)
    else:
        print(f"Config file not found: {config_file_path}")

def save_config():
    global config
    os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
        
    with open(config_file_path, 'w') as f:
        json.dump(config, f, indent=2)

