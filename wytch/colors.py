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

import collections
from math import sqrt

from wytch.misc import typed

class Color:

    def __init__(self, a):
        if isinstance(a, str):
            if a.startswith("#"):
                self.r = int(a[1:3], 16)
                self.g = int(a[3:5], 16)
                self.b = int(a[5:7], 16)
        elif isinstance(a, collections.Iterable):
            self.r = a[0]
            self.g = a[1]
            self.b = a[2]
        else:
            raise ValueError("Invalid argument %s" % type(a))
        self.n256 = None

    def distance(self, c):
        return sqrt((self.r - c.r) ** 2 + (self.g - c.g) ** 2 + (self.b - c.b) ** 2)

    def to_256(self):
        if self.n256 is not None:
            return self.n256
        # Technically this is incorrect, TODO
        self.n256, _ = min(enumerate(c256), key = lambda x: self.distance(x[1]))
        return self.n256

    def invert(self):
        return Color((255 - self.r, 255 - self.g, 255 - self.b))

    def __eq__(self, other):
        try:
            return self.r == other.r and self.g == other.g and self.b == other.b
        except AttributeError:
            return False

    def __hash__(self):
        return hash((self.r, self.g, self.b))

    def __str__(self):
        return "<%s.%s r = %02x g = %02x b = %02x>" % \
                (self.__class__.__module__, self.__class__.__name__,
                        self.r, self.g, self.b)


c256 = [
    Color("#000000"), Color("#800000"), Color("#008000"), Color("#808000"),
    Color("#000080"), Color("#800080"), Color("#008080"), Color("#c0c0c0"),
    Color("#808080"), Color("#ff0000"), Color("#00ff00"), Color("#ffff00"),
    Color("#0000ff"), Color("#ff00ff"), Color("#00ffff"), Color("#ffffff"),
    Color("#000000"), Color("#00005f"), Color("#000087"), Color("#0000af"),
    Color("#0000d7"), Color("#0000ff"), Color("#005f00"), Color("#005f5f"),
    Color("#005f87"), Color("#005faf"), Color("#005fd7"), Color("#005fff"),
    Color("#008700"), Color("#00875f"), Color("#008787"), Color("#0087af"),
    Color("#0087d7"), Color("#0087ff"), Color("#00af00"), Color("#00af5f"),
    Color("#00af87"), Color("#00afaf"), Color("#00afd7"), Color("#00afff"),
    Color("#00d700"), Color("#00d75f"), Color("#00d787"), Color("#00d7af"),
    Color("#00d7d7"), Color("#00d7ff"), Color("#00ff00"), Color("#00ff5f"),
    Color("#00ff87"), Color("#00ffaf"), Color("#00ffd7"), Color("#00ffff"),
    Color("#5f0000"), Color("#5f005f"), Color("#5f0087"), Color("#5f00af"),
    Color("#5f00d7"), Color("#5f00ff"), Color("#5f5f00"), Color("#5f5f5f"),
    Color("#5f5f87"), Color("#5f5faf"), Color("#5f5fd7"), Color("#5f5fff"),
    Color("#5f8700"), Color("#5f875f"), Color("#5f8787"), Color("#5f87af"),
    Color("#5f87d7"), Color("#5f87ff"), Color("#5faf00"), Color("#5faf5f"),
    Color("#5faf87"), Color("#5fafaf"), Color("#5fafd7"), Color("#5fafff"),
    Color("#5fd700"), Color("#5fd75f"), Color("#5fd787"), Color("#5fd7af"),
    Color("#5fd7d7"), Color("#5fd7ff"), Color("#5fff00"), Color("#5fff5f"),
    Color("#5fff87"), Color("#5fffaf"), Color("#5fffd7"), Color("#5fffff"),
    Color("#870000"), Color("#87005f"), Color("#870087"), Color("#8700af"),
    Color("#8700d7"), Color("#8700ff"), Color("#875f00"), Color("#875f5f"),
    Color("#875f87"), Color("#875faf"), Color("#875fd7"), Color("#875fff"),
    Color("#878700"), Color("#87875f"), Color("#878787"), Color("#8787af"),
    Color("#8787d7"), Color("#8787ff"), Color("#87af00"), Color("#87af5f"),
    Color("#87af87"), Color("#87afaf"), Color("#87afd7"), Color("#87afff"),
    Color("#87d700"), Color("#87d75f"), Color("#87d787"), Color("#87d7af"),
    Color("#87d7d7"), Color("#87d7ff"), Color("#87ff00"), Color("#87ff5f"),
    Color("#87ff87"), Color("#87ffaf"), Color("#87ffd7"), Color("#87ffff"),
    Color("#af0000"), Color("#af005f"), Color("#af0087"), Color("#af00af"),
    Color("#af00d7"), Color("#af00ff"), Color("#af5f00"), Color("#af5f5f"),
    Color("#af5f87"), Color("#af5faf"), Color("#af5fd7"), Color("#af5fff"),
    Color("#af8700"), Color("#af875f"), Color("#af8787"), Color("#af87af"),
    Color("#af87d7"), Color("#af87ff"), Color("#afaf00"), Color("#afaf5f"),
    Color("#afaf87"), Color("#afafaf"), Color("#afafd7"), Color("#afafff"),
    Color("#afd700"), Color("#afd75f"), Color("#afd787"), Color("#afd7af"),
    Color("#afd7d7"), Color("#afd7ff"), Color("#afff00"), Color("#afff5f"),
    Color("#afff87"), Color("#afffaf"), Color("#afffd7"), Color("#afffff"),
    Color("#d70000"), Color("#d7005f"), Color("#d70087"), Color("#d700af"),
    Color("#d700d7"), Color("#d700ff"), Color("#d75f00"), Color("#d75f5f"),
    Color("#d75f87"), Color("#d75faf"), Color("#d75fd7"), Color("#d75fff"),
    Color("#d78700"), Color("#d7875f"), Color("#d78787"), Color("#d787af"),
    Color("#d787d7"), Color("#d787ff"), Color("#d7af00"), Color("#d7af5f"),
    Color("#d7af87"), Color("#d7afaf"), Color("#d7afd7"), Color("#d7afff"),
    Color("#d7d700"), Color("#d7d75f"), Color("#d7d787"), Color("#d7d7af"),
    Color("#d7d7d7"), Color("#d7d7ff"), Color("#d7ff00"), Color("#d7ff5f"),
    Color("#d7ff87"), Color("#d7ffaf"), Color("#d7ffd7"), Color("#d7ffff"),
    Color("#ff0000"), Color("#ff005f"), Color("#ff0087"), Color("#ff00af"),
    Color("#ff00d7"), Color("#ff00ff"), Color("#ff5f00"), Color("#ff5f5f"),
    Color("#ff5f87"), Color("#ff5faf"), Color("#ff5fd7"), Color("#ff5fff"),
    Color("#ff8700"), Color("#ff875f"), Color("#ff8787"), Color("#ff87af"),
    Color("#ff87d7"), Color("#ff87ff"), Color("#ffaf00"), Color("#ffaf5f"),
    Color("#ffaf87"), Color("#ffafaf"), Color("#ffafd7"), Color("#ffafff"),
    Color("#ffd700"), Color("#ffd75f"), Color("#ffd787"), Color("#ffd7af"),
    Color("#ffd7d7"), Color("#ffd7ff"), Color("#ffff00"), Color("#ffff5f"),
    Color("#ffff87"), Color("#ffffaf"), Color("#ffffd7"), Color("#ffffff"),
    Color("#080808"), Color("#121212"), Color("#1c1c1c"), Color("#262626"),
    Color("#303030"), Color("#3a3a3a"), Color("#444444"), Color("#4e4e4e"),
    Color("#585858"), Color("#606060"), Color("#666666"), Color("#767676"),
    Color("#808080"), Color("#8a8a8a"), Color("#949494"), Color("#9e9e9e"),
    Color("#a8a8a8"), Color("#b2b2b2"), Color("#bcbcbc"), Color("#c6c6c6"),
    Color("#d0d0d0"), Color("#dadada"), Color("#e4e4e4"), Color("#eeeeee")
]

BLACK = c256[0]
DARKRED = c256[1]
DARKGREEN = c256[2]
DARKYELLOW = c256[3]
DARKBLUE = c256[4]
DARKPURPLE = c256[5]
DARKCYAN = c256[6]
LIGHTGRAY = c256[7]
GRAY = c256[8]
RED = c256[9]
GREEN = c256[10]
YELLOW = c256[11]
BLUE = c256[12]
PURPLE = c256[13]
CYAN = c256[14]
WHITE = c256[15]
