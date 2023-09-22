import curses

scr =curses.initscr()
while True:
    ch = scr.getch()
    scr.addstr(f"  {ch}  ")
    scr.refresh()