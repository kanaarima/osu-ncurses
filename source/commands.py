from client import Client


def handle_input(command, client: Client):
    split = command.split()
    if split[0] == "exit":
        exit(1)
    elif split[0] == "open":
        player = client.game.bancho.players.by_name(" ".join(split[1:]))
        if not player:
            return
        client.targets[player.name] = player
        client.messages[player.name] = []