from client import Client
from views import loop
import config


if __name__ == "__main__":
    cfg = config.load_config("config.json")
    if not cfg:
        print("Please edit config.json!")
        exit(-1)
    print("Logging in...")
    client = Client(cfg['username'], cfg['password'], cfg['server'])
    print("Starting loop...")
    loop(client, cfg)