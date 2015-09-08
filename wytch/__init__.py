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

import tty
import termios
import sys
from wytch import view
from wytch import canvas
from wytch import input

def wrapmain(fn):
    rootcanvas = canvas.ConsoleCanvas()
    try:
        root = view.ContainerView()
        root.canvas = rootcanvas
        ret = fn(root)
        root.focused = True
        root.render()
        # Input loop
        while True:
            c = sys.stdin.read(1)
            if ord(c) == 3:
                raise KeyboardInterrupt
            elif c == "\x1b": # TODO: handle ESC key press
                # TODO: Figure out how much is this broken on terminals other than xfce4-terminal...
                c += sys.stdin.read(1)
                if c[-1] in ["[", "O"]: # CSI and SS3
                    c += sys.stdin.read(1)
                    while ord(c[-1]) in range(ord("0"), ord("9") + 1):
                        c += sys.stdin.read(1)
                    if c[-1] == ";":
                        c += sys.stdin.read(1)
                        while ord(c[-1]) in range(ord("0"), ord("9") + 1):
                            c += sys.stdin.read(1)
            kc = input.KeyEvent(c)
            root.onevent(kc)
    finally:
        rootcanvas.destroy()
        print() # Newline

    return ret
