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
            stdscr.addstr(y, 0, f"{time.strftime(msg_format)}: {message}")
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
            self.client.messages[self.message_key].append((datetime.now(), self.client.game.username + ": " + self.textbox))
            self.textbox = ""
        else:
            self.textbox += chr(key)


class CommandPromptView(View):
    
    def __init__(self) -> None:
        self.textbox = ""
        self.done = False
    
    def render(self, stdscr):
        y, x = stdscr.getmaxyx()
        stdscr.addstr(y-2, 0, "cmd>"+self.textbox.ljust(x-1, " "))
    
    def handle_key(self, key: int):
        if key == keys.KEY_DELETE:
            self.textbox = self.textbox[:-2]
        elif key == keys.KEY_RETURN:
            self.done = True
        else:
            self.textbox += chr(key)

class HelpView(View):
    
    def __init__(self) -> None:
        self.name = "Help"
    
    def render(self, stdscr):
        stdscr.addstr(1,0,"Help\nPress tab to switch tabs\nPress ctrl+D to close a tab.\nPress control+e to open command prompt.\nCommands available: \nopen (username) | Initialise a chat with someone", curses.COLOR_WHITE)
        stdscr.refresh()

messages_views: Dict[str, View] = {}
active_views: List[View] = []
current_view = 0
dialog = None
commandprompt = None
date_format = "%a %d %b %Y %H:%M"
msg_format = "%H:%M"

def draw_status_bar(client: Client, stdscr):
    friends = list()
    for player in client.game.bancho.players:
        if player.id in client.game.bancho.friends:
            friends.append(player)
    y, x = stdscr.getmaxyx()
    active_view_name =  "..."
    if len(active_views):
        active_view_name = active_views[current_view].name
    stdscr.addstr(0,0,f">{client.game.username}@{client.game.server} {datetime.now().strftime(date_format)} (Users: {len(client.game.bancho.players)}, Friends: {len(friends)}) Current: {active_view_name}".ljust(x, " "), curses.color_pair(1))

def draw_tabs(client: Client, stdscr):
    str = ""
    y, limitx = stdscr.getmaxyx()
    x = 0
    for active_view in active_views:
        str = active_view.name +" "
        stdscr.addstr(y-1, x, str, curses.color_pair(2) if active_view == active_views[current_view] else curses.color_pair(3))
        x+=len(str)
    stdscr.addstr(y-1, x, " "*int(limitx-x-1), curses.color_pair(1))

def loop(client: Client, config: dict):
    global current_view, commandprompt
    stdscr = curses.initscr()
    stdscr.clear()
    curses.noecho()
    curses.cbreak()
    kbhit = KBHit()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)

    active_views.append(HelpView())
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
        if char == keys.KEY_TAB:
            current_view += 1
            if current_view == len(active_views):
                current_view = 0
            stdscr.clear()
            char = None
        elif char == keys.KEY_CONTROL_E:
            if commandprompt:
                commandprompt = None
            else:
                commandprompt = CommandPromptView()
            stdscr.clear()
            char = None
        elif char == keys.KEY_CONTROL_D:
            del active_views[current_view]
            current_view=-1
            if current_view < 0:
                current_view = 0
            char = None
            stdscr.clear()
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
                if active_views:
                    active_views[current_view].handle_key(char)
        if commandprompt:
            commandprompt.render(stdscr)    
        if active_views:
            active_views[current_view].render(render_window)
        stdscr.refresh()
        time.sleep(60/1000)