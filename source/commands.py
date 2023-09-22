from client import Client


def handle_input(command, client: Client):
    split = command.split()
    if split[0] == "exit":
        exit(1)