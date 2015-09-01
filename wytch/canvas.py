# The MIT License (MIT)
# 
# Copyright (c) 2015 Josef Gajdusek
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import shutil
import sys
import tty
from functools import reduce
from wytch import colors
from wytch.misc import typed

def ansi_escape(code, *args):
    return "\x1b[" + reduce(lambda i, v: i + str(v) + ";", args[:-1], "") + str(args[-1]) + code

class Canvas:

    def clear(self):
        for x in range(self.width):
            for y in range(self.height):
                self.set(x, y, " ")

    def set(self, x, y, c):
        pass

    def square(self, x, y, width, height, bordercolor = colors.WHITE):
        for xi in range(x, x + width + 1):
            for yi in range(y, y + height + 1):
                self.set(xi, yi, " ", fg = bordercolor, bg = bordercolor)

class ConsoleCanvas(Canvas):

    def __init__(self):
        self.width, self.height = shutil.get_terminal_size((80, 20))
        self.cursor_x = None
        self.cursor_y = None
        self._fg_color = None
        self._bg_color = None
        tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        self._send_ansi("l", "?25")
        self._set_cursor(0, 0)
        self.clear()

    def _send_ansi(self, code, *args):
        sys.stdout.write(ansi_escape(code, *args))

    def _set_cursor(self, x, y):
        if self.cursor_x == x and self.cursor_y == y:
            return
        self.cursor_x = x
        self.cursor_y = y
        self._send_ansi("H", y, x)

    @typed(None, colors.Color)
    def _set_fg_color(self, color):
        if self._fg_color == color:
            return
        self._fg_color = color
        self._send_ansi("m", 38, 5, color.to_256())

    @typed(None, colors.Color)
    def _set_bg_color(self, color):
        if self._bg_color == color:
            return
        self._bg_color = color
        self._send_ansi("m", 48, 5, color.to_256())

    def clear(self):
        self._send_ansi("J", 2)

    def set(self, x, y, c, fg = colors.WHITE, bg = colors.BLACK):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            raise ValueError("Coordinates x: %d, y: %d out of bounds" % (x, y))
        self._set_cursor(x + 1, y + 1) # Terminal rows/columns are indexed from 0
        self._set_fg_color(fg)
        self._set_bg_color(bg)
        sys.stdout.write(c)
        sys.stdout.flush()
        self.cursor_x += 1
        self.cursor_y += int(self.cursor_x / self.width)
        self.cursor_x %= self.width

    def destroy(self):
        self._send_ansi("h", "?25")
