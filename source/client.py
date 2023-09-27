from osu.bancho.constants import ServerPackets
from osu.objects import Player, Channel
from datetime import datetime
from threading import Thread
from typing import Union
from osu import Game

class Client:
    
    def __init__(self, username, password, server) -> None:
        self.game = Game(username, password, server=server)
        self.messages = {}
        self.targets = {}
        self.register_events()
        self.loop()
    
    def loop(self):
        thread = Thread(target=self.game.run)
        thread.start()
    
    def register_events(self):
        @self.game.events.register(ServerPackets.SEND_MESSAGE)
        def on_message(sender: Player, message: str, target: Union[Player, Channel]):
            if target.name not in self.messages:
                self.messages[target.name] = list()
                self.targets[target.name] = target
            self.messages[target.name].append((datetime.now(), message))
        @self.game.events.register(ServerPackets.CHANNEL_JOIN_SUCCESS)
        def on_channel_join(channel: Channel):
            if channel.name not in self.messages:
                self.messages[channel.name] = list()
                self.targets[channel.name] = channel
            self.messages[channel.name].append((datetime.now(), f"Joined {channel.name}"))
            