from typing import List, Dict
from datetime import datetime
from client import Client
import curses
import time

class View():
    
    def __init__(self) -> None:
        self.name = "TestView"
    
    def render(self, stdscr):
        stdscr.addstr(0,0,"hello world")
        stdscr.refresh()

class ChatView(View):
    
    def __init__(self, client: Client, message_key) -> None:
        self.name = message_key
        self.client = client
        self.message_key = message_key

    def render(self, stdscr):
        y = 0
        for time, message in self.client.messages[self.message_key]:
            stdscr.addstr(y, 0, f"{time}: {message}")
            y+=1
        stdscr.refresh()

messages_views: Dict[str, View] = {}
active_views: List[View] = []

def draw_status_bar(client: Client, stdscr):
    friends = list()
    for player in client.game.bancho.players:
        if player.id in client.game.bancho.friends:
            friends.append(player)
    active_view_name = active_views[0].name if active_views else "..."
    stdscr.addstr(0,0,f">{client.game.username}@{client.game.server} {datetime.now()} (Users: {len(client.game.bancho.players)}, Friends: {len(friends)}) Current: {active_view_name}")

def draw_tabs(client: Client, stdscr):
    str = ""
    y, x = stdscr.getmaxyx()
    for active_view in active_views:
        str += active_view.name + " "
    stdscr.addstr(y-1,0, str)


def loop(client: Client, config: dict):
    stdscr = curses.initscr()
    stdscr.clear()
    curses.noecho()
    curses.cbreak()
    #active_views.append(View())
    old_y, old_x = stdscr.getmaxyx()
    render_window = curses.newwin(old_y-1, old_x, 1, 0)
    while True:
        for messages in client.messages:
            if messages not in messages_views:
                view = ChatView(client=client, message_key=messages)
                active_views.append(view)
                messages_views[messages] = view
        # TODO handle resize
        stdscr.clear()
        draw_status_bar(client, stdscr)
        draw_tabs(client, stdscr)
        stdscr.refresh()
        if active_views:
            active_views[0].render(render_window)
        time.sleep(1)