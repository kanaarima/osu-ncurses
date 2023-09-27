from typing import List, Dict
from datetime import datetime
from client import Client
from kbhit import KBHit
import commands
import curses
import time
import keys

class View():
    
    def __init__(self) -> None:
        self.name = "TestView"
    
    def render(self, stdscr):
        stdscr.addstr(0,0,"hello world")
        stdscr.refresh()

    def handle_key(self, key: int):
        pass

class ChatView(View):
    
    def __init__(self, client: Client, message_key) -> None:
        self.name = message_key
        self.client = client
        self.message_key = message_key
        self.textbox = ""

    def render(self, stdscr):
        y = 0
        for time, message in self.client.messages[self.message_key]:
            stdscr.addstr(y, 0, f"{time}: {message}")
            y+=1
        y, x = stdscr.getmaxyx()
        stdscr.addstr(y-2, 0, ">"+self.textbox.ljust(x-1, " "))
        stdscr.refresh()

    def handle_key(self, key: int):
        if key == keys.KEY_DELETE:
            self.textbox = self.textbox[:-2]
        elif key == keys.KEY_RETURN:
            if not len(self.textbox):
                return
            self.client.targets[self.message_key].send_message(self.textbox)
            self.client.messages[self.message_key].append((datetime.now(), self.textbox))
            self.textbox = ""
        else:
            self.textbox += chr(key)


class CommandPromptView(View):
    
    def __init__(self) -> None:
        self.textbox = ""
        self.done = False
    
    def render(self, stdscr):
        y, x = stdscr.getmaxyx()
        stdscr.addstr(y-2, 0, ">"+self.textbox.ljust(x-1, " "))
    
    def handle_key(self, key: int):
        if key == keys.KEY_DELETE:
            self.textbox = self.textbox[:-2]
        elif key == keys.KEY_RETURN:
            self.done = True
        else:
            self.textbox += chr(key)

messages_views: Dict[str, View] = {}
active_views: List[View] = []
current_view = 0
commandprompt = None

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
    global current_view, commandprompt
    stdscr = curses.initscr()
    stdscr.clear()
    curses.noecho()
    curses.cbreak()
    kbhit = KBHit()
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i, i, -1);

    #active_views.append(View())
    old_y, old_x = stdscr.getmaxyx()
    render_window = curses.newwin(old_y-1, old_x, 1, 0)
    last_char = None
    while True:
        for messages in client.messages:
            if messages not in messages_views:
                view = ChatView(client=client, message_key=messages)
                active_views.append(view)
                messages_views[messages] = view
        # TODO handle resize
        draw_status_bar(client, stdscr)
        draw_tabs(client, stdscr)
        char = None
        if kbhit.kbhit():
            char = stdscr.getch()
        if char == keys.KEY_RIGHT:
            current_view += 1
            if current_view == len(active_views):
                current_view = 0
            stdscr.clear()
            char = None
        elif char == keys.KEY_LEFT:
            current_view -= 1
            if current_view == -1:
                current_view = max(0,len(active_views)-1)
            stdscr.clear()
            char = None
        elif char == keys.KEY_CONTROL_E:
            if commandprompt:
                commandprompt = None
            else:
                commandprompt = CommandPromptView()
            stdscr.clear()
            char = None
        if char == last_char: # for some reason some keys repeats twice
            char = None
        last_char = char
        if char:
            if commandprompt:
                commandprompt.handle_key(char)
                if commandprompt.done:
                    commands.handle_input(commandprompt.textbox, client=client)
                    commandprompt = None
                    stdscr.clear()
            else:
                active_views[current_view].handle_key(char)
        if commandprompt:
            commandprompt.render(stdscr)    
        if active_views:
            active_views[current_view].render(render_window)
        stdscr.refresh()
        time.sleep(60/1000)