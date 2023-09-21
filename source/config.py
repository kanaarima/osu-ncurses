import json

def default_config():
    return {"username": "", "password": "", "server": "ppy.sh"}

def load_config(path):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        with open(path, "w") as f:
            json.dump(default_config(), f)
        