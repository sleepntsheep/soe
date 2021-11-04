import curses
import os
from posixpath import join
import re
import sys

class Editor:
    def __init__(self, stdscr, file_name):
        self.screen_x = 0
        self.screen_y = 0
        self.offscreen_x = 0
        self.offscreen_y = 0 
        self.total_x = self.screen_x + self.offscreen_x
        self.total_y = self.screen_y + self.offscreen_y
        self.RUN = True
        self.win = stdscr
        self.height, self.width = self.win.getmaxyx()
        self.status_win = stdscr.subwin(1, self.width - 1, self.height - 1, 0)
        self.status = ''
        self.file_name = file_name
        self.load_file()

        curses.noecho()
        
    def load_file(self):
        if os.path.exists(self.file_name):
            with open(self.file_name, 'r') as file:
                self.text = file.read().splitlines()
        else:
            with open(self.file_name, 'w') as file:
                self.text = ''

    def main(self):
        while self.RUN:
            self.win.clear()

            self.total_x = self.screen_x + self.offscreen_x
            self.total_y = self.screen_y + self.offscreen_y
            
            for index, line in enumerate(self.text[self.offscreen_y:]):
                if index >= self.height:
                    break
                self.win.insstr(index, 0, line[self.offscreen_x:self.width-1])

            self.win.move(self.screen_y, self.screen_x)

            status = f"{self.total_x}, {self.total_y}"
            
            self.status_win.clear()
            self.status_win.addstr(0, 0, status + '  ' + self.status, curses.A_REVERSE)

            self.status_win.refresh()
            self.win.refresh()

            key = self.win.getch()

            if key == 17: # ctrl q
                self.RUN = False
            elif key == curses.KEY_LEFT:
                self.left()
            elif key == curses.KEY_RIGHT:
                self.right()
            elif key == curses.KEY_UP:
                self.up()
            elif key == curses.KEY_DOWN:
                self.down()
            elif key == curses.KEY_BACKSPACE or key == 127:  
                self.delch()
            elif key == 6:
                self.search()
            elif key == 19:
                self.save_file()
            elif key == 26:
                self.undo()
            elif key == curses.KEY_ENTER or key == 10:
                self.new_line()
            else:
                self.addch(chr(key))

    def new_line(self):
        try:
            self.text.insert(self.total_y + 1, self.text[self.total_y][self.total_x:])
            self.text[self.total_y] = self.text[self.total_y][:self.total_x]
            self.down()
        except Exception as e:
            print(e)

    def search(self):
        ...

    def undo(self):
        ...

    def addch(self, ch):
        if len(self.text[self.total_y]) < 1:
            self.text[self.total_y] = ch
        self.text[self.total_y] = self.text[self.total_y][:self.total_x] + ch + self.text[self.total_y][self.total_x:]
        self.right()

    def delch(self):
        if self.total_x == 0:
            self.text[self.total_y - 1] += self.text[self.total_y]
            self.text.pop(self.total_y)
        else:
            self.text[self.total_y] = self.text[self.total_y][:self.total_x - 1] + self.text[self.total_y][self.total_x:]
        self.left()


    def left(self):
        if self.screen_x == 0:
            if self.total_y == 0:
                return
            self.screen_y -= 1
            self.screen_x = len(self.text[self.total_y - 1]) - 1
        else:
            self.screen_x -= 1

    def right(self):
        # if cursor is at end of line
        if self.screen_x > len(self.text[self.total_y]) - 1:
            if self.total_y == len(self.text) - 1: # if at the last line
                return
            self.screen_x = 0
            self.screen_y += 1
            return
        elif self.screen_x >= self.width - 1:
            self.offscreen_x += 1
        elif self.screen_x < self.width - 1:
            self.screen_x += 1
    
    def up(self):
        if self.total_y == 0:
            return
        if self.screen_y > 0:
            if self.screen_x >= len(self.text[self.total_y - 1]):
                self.screen_x = len(self.text[self.total_y - 1])
            self.screen_y -= 1
        else:
            self.offscreen_y -= 1
    
    def down(self):
        if self.total_y == len(self.text) - 1:
            return
        if self.screen_y < self.height - 1:
            if self.screen_x >= len(self.text[self.total_y + 1]):
                self.screen_x = len(self.text[self.total_y + 1])
            self.screen_y += 1
        else:
            self.offscreen_y += 1

    def save_file(self):
        if sys.platform == 'win32':
            newline = '\r\n'
        elif sys.platform == 'linux':
            newline = '\n'
        else:
            newline = '\n'
        with open(self.file_name, 'w') as f:
            for line in self.text:
                f.write(line + newline)
            self.status = f'Saved as {self.file_name}'

def c_main(win: curses.window):
    file_name = sys.argv[1] if len(sys.argv) > 1 else None
    editor = Editor(win, file_name)
    editor.main()

    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else: 
        file_name = 'output'
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            text = file.readlines()
    else:
        with open(file_name, 'w') as file:
            text = ''

def main():
    curses.wrapper(c_main)

if __name__ == '__main__':
    exit(main())
