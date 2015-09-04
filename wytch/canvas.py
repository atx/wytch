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
import termios
import tty
from functools import reduce
from wytch import colors
from wytch.misc import typed

BOLD = 1 << 0
FAINT = 1 << 1
ITALIC = 1 << 2
UNDERLINE = 1 << 3
BLINK = 1 << 4
BLINK_FAST = 1 << 5
NEGATIVE = 1 << 6

SGR_CODES = {
    BOLD: 1,
    FAINT: 2,
    ITALIC: 3,
    UNDERLINE: 4,
    BLINK: 5,
    BLINK_FAST: 6,
    NEGATIVE: 7,
}

def ansi_escape(code, *args):
    return "\x1b[" + reduce(lambda i, v: i + str(v) + ";", args[:-1], "") + str(args[-1]) + code

class Canvas:

    def clear(self):
        for x in range(self.width):
            for y in range(self.height):
                self.set(x, y, " ")

    def set(self, x, y, c, fg = colors.WHITE, bg = colors.BLACK, flags = 0):
        pass

    def square(self, x, y, width, height, bordercolor = colors.WHITE):
        for xi in range(x, x + width + 1):
            for yi in range(y, y + height + 1):
                self.set(xi, yi, " ", fg = bordercolor, bg = bordercolor)

    def hline(self, x, y, length, fg = colors.WHITE, bg = colors.BLACK,
            char = "─"):
        for xi in range(x, x + length):
            self.set(xi, y, char, fg = fg, bg = bg)

    def vline(self, x, y, length, fg = colors.WHITE, bg = colors.BLACK,
            char = "│"):
        for yi in range(y, y + length):
            self.set(x, yi, char, fg = fg, bg = bg)

    def box(self, x, y, width, height, fg = colors.WHITE, bg = colors.BLACK):
        self.hline(x + 1, y, width - 1, fg = fg, bg = bg)
        self.vline(x, y + 1, height - 1, fg = fg, bg = bg)
        self.hline(x + 1, y + height, width -1, fg = fg, bg = bg)
        self.vline(x + width, y + 1, height - 1, fg = fg, bg = bg)
        self.set(x, y, "┌", fg = fg, bg = bg)
        self.set(x + width, y, "┐", fg = fg, bg = bg)
        self.set(x, y + height, "└", fg = fg, bg = bg)
        self.set(x + width, y + height, "┘", fg = fg, bg = bg)

    def text(self, x, y, text, fg = colors.WHITE, bg = colors.BLACK, flags = 0):
        for i, s in enumerate(text):
            self.set(x + i, y, s, fg = fg, bg = bg, flags = flags)


class ConsoleCanvas(Canvas):

    def __init__(self):
        self.width, self.height = shutil.get_terminal_size((80, 20))
        self.cursor_x = None
        self.cursor_y = None
        self._fg_color = None
        self._bg_color = None
        self._flags = None
        self._oldattrs = termios.tcgetattr(sys.stdin.fileno())
        tty.setraw(sys.stdin.fileno())
        #tty.setcbreak(sys.stdin.fileno())
        self._send_ansi("l", "?25")
        self._set_cursor(0, 0)
        self.clear()

    def _send_ansi(self, code, *args):
        sys.stdout.write(ansi_escape(code, *args))

    def _send_sgr(self, code, *args):
        self._send_ansi("m", code, *args)

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
        self._send_sgr(38, 5, color.to_256())

    @typed(None, colors.Color)
    def _set_bg_color(self, color):
        if self._bg_color == color:
            return
        self._bg_color = color
        self._send_sgr(48, 5, color.to_256())

    def _set_flags(self, flags):
        if self._flags == flags:
            return
        self._send_sgr(0) # Reset all parameters
        self._flags = flags
        if flags & BOLD:
            self._send_sgr(SGR_CODES[BOLD])
        if flags & FAINT:
            self._send_sgr(SGR_CODES[FAINT])
        if flags & ITALIC:
            self._send_sgr(SGR_CODES[ITALIC])
        if flags & UNDERLINE:
            self._send_sgr(SGR_CODES[UNDERLINE])
        if flags & BLINK:
            self._send_sgr(SGR_CODES[BLINK])
        if flags & BLINK_FAST:
            self._send_sgr(SGR_CODES[BLINK_FAST])
        if flags & NEGATIVE:
            self._send_sgr(SGR_CODES[NEGATIVE])

    def clear(self):
        self._send_ansi("J", 2)

    def set(self, x, y, c, fg = colors.WHITE, bg = colors.BLACK, flags = 0):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            raise ValueError("Coordinates x: %d, y: %d out of bounds" % (x, y))
        self._set_cursor(x + 1, y + 1) # Terminal rows/columns are indexed from 0
        self._set_flags(flags)
        self._set_fg_color(fg)
        self._set_bg_color(bg)
        sys.stdout.write(c)
        sys.stdout.flush()
        self.cursor_x += 1
        self.cursor_y += int(self.cursor_x / self.width)
        self.cursor_x %= self.width

    def destroy(self):
        self._set_flags(0)
        self._set_fg_color(colors.WHITE)
        self._set_bg_color(colors.BLACK)
        self.clear()
        self._set_cursor(0, 0)
        self._send_ansi("h", "?25")
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self._oldattrs)


class SubCanvas(Canvas):

    def __init__(self, parent, x, y, width, height):
        self.parent = parent
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def set(self, x, y, c, fg = colors.WHITE, bg = colors.BLACK, flags = 0):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            raise ValueError("Coordinates x: %d, y: %d out of bounds" % (x, y))
        self.parent.set(self.x + x, self.y + y, c,
              fg = fg, bg = bg, flags = flags)
