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

import sys

class KeyEvent:

    _CSI_CURSOR = {
        "A": "<up>",
        "B": "<down>",
        "C": "<right>",
        "D": "<left>",
        "H": "<home>",
        "F": "<end>",
        "P": "<f1>",
        "Q": "<f2>",
        "R": "<f3>",
        "S": "<f4>",
    }

    _CSINUM = {
        2: "<insert>",
        3: "<delete>",
        5: "<pageup>",
        6: "<pagedown>",
        15: "<f5>",
        17: "<f6>",
        18: "<f7>",
        19: "<f8>",
        20: "<f9>",
        21: "<f10>",
        23: "<f11>",
        24: "<f12>",
    }

    def __init__(self, s):
        self.raw = s
        self.shift = False
        self.alt = False
        self.ctrl = False
        self.isescape = False
        if s[0] == "\x1b": # Escape sequence
            if s[1] in ["[", "O"]:
                csinum = 1
                if ";" in s: # Some modifiers were pressed
                    spl = s[2:-1].split(";")
                    csinum = int(spl[0])
                    mod = int(spl[1]) - 1
                    if mod & 0x1:
                        self.shift = True
                    if mod & 0x2:
                        self.alt = True
                    if mod & 0x4:
                        self.ctrl = True
                elif s[-1] == "~":
                    csinum = int(s[2:-1])
                if csinum != 1 and csinum in KeyEvent._CSINUM.keys():
                    self.val = KeyEvent._CSINUM[csinum]
                elif s[-1] in KeyEvent._CSI_CURSOR.keys():
                    self.val = KeyEvent._CSI_CURSOR[s[-1]]
                elif s[-1] == "Z":
                    self.val = "\t"
                    self.shift = True
                else:
                    raise ValueError("Invalid CSI value")
            else:
                self.val = s[1]
                self.alt = True
        else:
            self.val = s

        if len(self.val) == 1 and ord(self.val) in range(0x01, 0x1a) \
                and self.val not in "\r\t\n":
            self.val = chr(ord(self.val) + 0x60)
            self.ctrl = True

        if self.shift:
            self.val = self.val.upper()
        if self.alt:
            self.val = "!" + self.val
        if self.ctrl:
            self.val = "^" + self.val

    def __str__(self):
        return "<input.KeyEvent shift = %r alt = %r ctrl = %r val = %r>" % \
                (self.shift, self.alt, self.ctrl, self.val)
