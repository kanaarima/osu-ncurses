from osu.bancho.constants import ServerPackets
from osu.objects import Player
from osu import Game

class Client:

    def __init__(self, username, password, server) -> None:
        self.game = Game(username, password, server=server)
    