import curses
import os
import re
import sys

class Editor:
    def __init__(self, stdscr, file_name):
        curses.noecho()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        stdscr.keypad(True)
        stdscr.nodelay(False)

        self.screen_x = 0
        self.screen_y = 0
        self.offscreen_x = 0
        self.offscreen_y = 0 
        self.total_x = self.screen_x + self.offscreen_x
        self.total_y = self.screen_y + self.offscreen_y
        self.RUN = True
        self.stdscr = stdscr
        self.std_height, self.std_width = stdscr.getmaxyx()
        self.win = stdscr.subwin(self.std_height - 1, self.std_width - 1, 0, 0)
        self.height, self.width = self.win.getmaxyx()
        self.status_win = stdscr.subwin(1, self.std_width - 1, self.std_height - 1, 0)
        self.status = ''
        self.file_name = file_name
        self.load_file()

    def get_input(self):
        ...
        
    def load_file(self):
        if os.path.exists(self.file_name):
            with open(self.file_name, 'r') as file:
                self.text = file.read().splitlines()
        else:
            self.text = []

    def main(self):
        while self.RUN:
            self.win.clear()
            self.status_win.clear()
            self.status_win.bkgd(' ', curses.color_pair(1))
            
            self.std_height, self.std_width = self.stdscr.getmaxyx()

            self.total_x = self.screen_x + self.offscreen_x
            self.total_y = self.screen_y + self.offscreen_y
            
            for index, line in enumerate(self.text[self.offscreen_y:]):
                if index >= self.height:
                    break
                self.win.insstr(index, 0, line[self.offscreen_x:self.width-1])

            self.win.move(self.screen_y, self.screen_x)

            status = f"{self.total_x}, {self.total_y}"
            
            self.status_win.addstr(0, 0, status + '  ' + self.status)

            self.status_win.refresh()
            self.win.refresh()

            key = self.stdscr.getch()
            self.status = str(key)

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
            elif key == 545: #ctrl left
                for i in range(0, 8):
                    self.left()
            elif key == 560: #ctrl right
                for i in range(0, 8):
                    self.right()
            elif key == 566: #ctrl up
                for i in range(0, 8):
                    self.up()
            elif key == 525: #ctrl down
                for i in range(0, 8):
                    self.down()
            elif key == 330:
                self.delete()
            elif key == curses.KEY_BACKSPACE or key == 127:  
                self.back()
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

    def delete(self):
        if self.total_x == len(self.text[self.total_y]):
            if self.total_y == len(self.text) - 1:
                return
            self.text[self.total_y] += self.text[self.total_y + 1]
            self.text.pop(self.total_y + 1)
        else:
            self.text[self.total_y] = self.text[self.total_y][:self.total_x] + self.text[self.total_y][self.total_x + 1:]

    def addch(self, ch):
        if len(self.text) == 0:
            self.text.append(ch)
#        elif len(self.text[self.total_y]) < 1:
#           self.text[self.total_y] = ch
        self.text[self.total_y] = self.text[self.total_y][:self.total_x] + ch + self.text[self.total_y][self.total_x:]
        self.right()

    def back(self):
        if self.total_x == 0:
            if self.total_y == 0:
                return
            self.text[self.total_y - 1] += self.text[self.total_y]
            self.text.pop(self.total_y)
        else:
            self.text[self.total_y] = self.text[self.total_y][:self.total_x - 1] + self.text[self.total_y][self.total_x:]
        self.left()

    def left(self):
        if self.screen_x == 0:
            if self.total_y == 0:
                return
            self.up()
            self.screen_x = len(self.text[self.total_y - 1])
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
        if self.total_y == max(len(self.text) - 1, 0):
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
    file_name = sys.argv[1] if len(sys.argv) > 1 else 'output'
    editor = Editor(win, file_name)
    editor.main()

def main():
    exit(curses.wrapper(c_main))

if __name__ == '__main__':
    main()
