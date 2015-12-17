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

from wytch import view, colors

class Builder:

    def __init__(self, view, parent = None):
        self.view = view
        self.parent = parent
        self.nested = []

    def add(self, c):
        self.nested.append(Builder(c, parent = self))
        return self

    __call__ = add

    def labels(self, strs, fg = colors.WHITE, bg = colors.BLACK):
        for s in strs:
            self.add(view.Label(s, fg = fg, bg = bg))
        return self

    def spacer(self, width = 0, height = 0):
        return self.add(view.Spacer(width = width, height = height))

    def hline(self, title = None):
        return self.add(view.HLine(title = title))

    def nest(self, cont):
        #self.view.add_child(cont)
        ret = Builder(cont, parent = self)
        self.nested.append(ret)
        return ret

    def align(self, halign = view.HOR_MID, valign = view.VER_MID):
        return self.nest(view.Align(halign = halign, valign = valign))

    def grid(self, width, height):
        ret = GridBuilder(view.Grid(width, height), parent = self)
        self.nested.append(ret)
        return ret

    def vertical(self, width = 0):
        return self.nest(view.Vertical(width = width))

    def horizontal(self, height = 0):
        return self.nest(view.Horizontal(height = height))

    def box(self, title = None):
        return self.nest(view.Box(title = title))

    def endall(self):
        self.end()
        if self.parent:
            self.parent.endall()

    def end(self):
        return self.parent

    def __enter__(self):
        return self

    def __exit__(self, extype, exval, trace):
        if extype:
            return False
        for b in self.nested:
            b.__exit__(extype, exval, trace)
        if self.parent:
            self.parent.view.add_child(self.view)
        return self.parent

class GridBuilder(Builder):

    def __init__(self, view, parent = None):
        super(GridBuilder, self).__init__(view, parent = parent)
        self.atx = 0
        self.aty = 0

    def add(self, c = None, rowspan = 1, colspan = 1):
        if c:
            self.view.set(self.atx, self.aty, c,
                    rowspan = rowspan, colspan = colspan)
        self.atx += 1
        if self.atx >= self.view.width:
            self.atx = 0
            self.aty += 1
        return self

    __call__ = add


class Popup(Builder):

    def __init__(self, root):
        super(Popup, self).__init__(view.ContainerView(), parent = Builder(root))
        self.view.zindex = 1
        self._savedfocus = None

    def __enter__(self):
        return self

    def __exit__(self, extype, exval, trace):
        if extype:
            return False
        for b in self.nested:
            b.__exit__(extype, exval, trace)
        return self.parent

    def open(self):
        self._savedfocus = self.parent.view.focused_leaf
        self.parent.view.add_child(self.view)
        self.view.focused = True

    def close(self):
        self.parent.view.remove_child(self.view)
        self._savedfocus.focused = True
