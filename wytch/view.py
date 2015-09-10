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

import random
import string
from math import ceil
from wytch import colors
from wytch import canvas

HOR_LEFT = 1
HOR_MID = 2
HOR_RIGHT = 3

VER_TOP = 1
VER_MID = 2
VER_BOT = 3

class View:

    def __init__(self):
        self.zindex = 0
        self._focused = False
        self._canvas = None
        self.parent = None
        self._focusable = True

    def onfocus(self):
        pass

    def onunfocus(self):
        pass

    def onevent(self, kc):
        """Returns True if the event was consumed"""
        return False

    def onchildfocused(self, c):
        pass

    @property
    def focused_child(self):
        return None

    @property
    def focused(self):
        return self._focused

    @focused.setter
    def focused(self, f):
        if self._focused == f:
            return
        if f and not self.focusable:
            raise NotImplementedError("This view is not focusable")
        self._focused = f
        # Bubble up until the root
        if f:
            self.onfocus()
            if self.parent:
                self.parent.focused = True
                # Unfocus other children of parent
                self.parent.onchildfocused(self)
        else:
            self.onunfocus()

    @property
    def canvas(self):
        return self._canvas

    @canvas.setter
    def canvas(self, c):
        self._canvas = c
        self.recalc()

    def recalc(self):
        """Called on canvas change"""
        pass

    def render(self):
        pass

    @property
    def size(self):
        if self.canvas:
            return (self.canvas.width, self.canvas.height)
        return (1, 1)

    @property
    def focusable(self):
        return self._focusable

    @focusable.setter
    def focusable(self, f):
        self._focusable = f

    def __str__(self):
        return "<%s.%s zindex = %d focused = %r focusable = %r size = %r>" % \
                (self.__class__.__name__, self.__class__.__module__,
                        self.zindex, self.focused, self.focusable, self.size)


class ContainerView(View):

    def __init__(self, canvas = None):
        super(ContainerView, self).__init__()
        self.children = []

    def onfocus(self):
        super(ContainerView, self).onfocus()
        if any([c.focused for c in self.children]):
            return # The focus came from child
        # Focus first focusable child
        if len(self.children) > 0:
            for c in self.children:
                if c.focusable:
                    c.focused = True

    def onunfocus(self):
        super(ContainerView, self).onunfocus()
        for c in self.children:
            c.focused = False

    def onchildfocused(self, cf):
        super(ContainerView, self).onchildfocused(cf)
        for c in self.children:
            if c.focused and c != cf:
                c.focused = False

    def _focused_child_index(self):
        for i, c in enumerate(self.children):
            if c.focused:
                return i, c
        return None, None

    @property
    def focused_child(self):
        _, c = self._focused_child_index()
        return c

    def onevent(self, kc):
        super(ContainerView, self).onevent(kc)
        # See if child can handle the event
        if self.focused_child.onevent(kc):
            return True
        # Can we handle it?
        if kc.val == "<up>" or kc.val == "\t" and kc.shift:
            return self.focus_prev()
        elif kc.val in ["<down>", "\t"]:
            return self.focus_next()
        return False

    def focus_next(self, step = 1):
        if len(self.children) == 0:
            return
        i, _ = self._focused_child_index()
        if i is None:
            i = 0

        i += step
        while i in range(0, len(self.children)):
            if self.children[i].focusable:
                self.children[i].focused = True
                return True
            i += step
        return False

    def focus_prev(self):
        return self.focus_next(step = -1)

    def add_child(self, c):
        c.parent = self
        self.children.append(c)
        self.recalc()

    def remove_child(self, c):
        c.parent = None
        self.children.remove(c)
        self.recalc()

    def recalc(self):
        """Called on canvas change an addition/removal of a child"""
        self.children.sort(key = lambda x: x.zindex)
        for c in self.children:
            c.canvas = self.canvas

    def render(self):
        for c in self.children:
            c.render()

    @property
    def focusable(self):
        return any([c.focusable for c in self.children])

    @property
    def size(self):
        return (max([c.size[0] for c in self.children]),
                max([c.size[1] for c in self.children]))

class Align(ContainerView):

    def __init__(self, halign = HOR_MID, valign = VER_MID):
        super(Align, self).__init__()
        self.halign = halign
        self.valign = valign

    def recalc(self):
        if not self.canvas:
            return
        if self.halign == HOR_LEFT:
            x = 0
        elif self.halign == HOR_MID:
            x = int(self.canvas.width / 2 - self.size[0] / 2)
        else:
            x = self.canvas.width - self.size[0]
        if self.valign == VER_TOP:
            y = 0
        elif self.valign == VER_MID:
            y = int(self.canvas.height / 2 - self.size[1] / 2)
        else:
            y = self.canvas.height - self.size[1]
        subc = canvas.SubCanvas(self.canvas, x, y, self.size[0], self.size[1])
        for c in self.children:
            c.canvas = subc

    def __str__(self):
        if halign == HOR_LEFT:
            hstr = "HOR_LEFT"
        elif halign == HOR_MID:
            hstr = "HOR_MID"
        else:
            hstr = "HOR_RIGHT"
        if valign == VER_TOP:
            vstr = "VER_TOP"
        elif valign == VER_MID:
            vstr = "VER_MID"
        else:
            vstr = "VER_BOT"
        return "<%s.%s zindex = %d focused = %r focusable = %r size = %r " \
                "halign = %s valign = %s>" % \
                (self.__class__.__name__, self.__class.__name__,
                    self.zindex, self.focused, self.focusable, self.size,
                    hstr, vstr)


class Box(ContainerView):

    def __init__(self, title = None, bg = colors.BLACK):
        super(Box, self).__init__()
        self.title = title
        self.bg = bg

    def recalc(self):
        if not self.canvas:
            return
        subc = canvas.SubCanvas(self.canvas, 2, 1,
                self.canvas.width - 4, self.canvas.height - 2)
        for c in self.children:
            c.canvas = subc

    def render(self):
        super(Box, self).render()
        self.canvas.box(0, 0, self.canvas.width - 1, self.canvas.height - 1,
                bg = self.bg)
        if self.title:
            self.canvas.text(1, 0, " " + self.title + " ")

    @property
    def size(self):
        ss = super(Box, self).size
        return (ss[0] + 4, ss[1] + 2)

    def __str__(self):
        return "<%s.%s zindex = %d focused = %r focusable = %r size = %r " \
                "title = \"%s\" bg = %r>" % \
                (self.__class__.__name__, self.__class__.__name__,
                    self.zindex, self.focused, self.focusable, self.size,
                    self.title, self.bg)


class Vertical(ContainerView):

    def __init__(self, width = 0):
        super(Vertical, self).__init__()
        self._width = width
        self._height = 0

    def recalc(self):
        if not self.canvas:
            return
        h = self.canvas.height
        for c in self.children:
            c.recalc()
            ch = c.size[1]
            if ch == 0:
                ch = 1 # TODO 0 means "any height", implement properly...
            if ch > h:
                break
            c.canvas = canvas.SubCanvas(self.canvas, 0, self.canvas.height - h,
                    self.canvas.width, ch)
            h -= ch

    @property
    def size(self):
        if len(self.children) == 0:
            return (0, 0)
        return (max([c.size[0] for c in self.children]),
                sum([max(c.size[1], 1) for c in self.children]))


class Horizontal(ContainerView):

    def __init__(self, height = 0):
        super(Horizontal, self).__init__()
        self._height = height

    def recalc(self):
        if not self.canvas:
            return
        w = self.canvas.width
        for c in self.children:
            c.recalc()
            cw = c.size[0]
            if cw == 0:
                cw = 1 # TODO 0 means "any height", implement properly...
            if cw > w:
                break
            c.canvas = canvas.SubCanvas(self.canvas, self.canvas.width - w, 0,
                   cw, self.canvas.height)
            w -= cw
        self._width = self.canvas.width - w

    @property
    def size(self):
        if len(self.children) == 0:
            return (0, 0)
        return (sum([max(c.size[0], 1) for c in self.children]),
                max([c.size[1] for c in self.children]))


class Grid(ContainerView):

    class Cell:

        def __init__(self, child, colspan, rowspan):
            self.child = child
            self.colspan = colspan
            self.rowspan = rowspan

    def __init__(self, width, height):
        super(Grid, self).__init__()
        self.width = width
        self.height = height
        self.grid = [[None] * width for _ in range(height)]

    def set(self, x, y, child, colspan = 1, rowspan = 1):
        if self.grid[y][x]:
            self.remove_child(self.grid[y][x].child)
        self.grid[y][x] = Grid.Cell(child, colspan, rowspan)
        self.add_child(child)

    def recalc(self):
        if not self.canvas:
            pass
        # Row heights
        rhs = []
        self.rhs = rhs
        over = [None] * len(self.grid)
        for row in self.grid:
            rhs.append(1)
            for i, (c, o) in enumerate(zip(row, over)):
                if o: # We have some overflow from rowspan > 1
                    c = o[0] # Cell
                    rh = o[1] # Remaining height
                    rr = o[2] # Remaining rows
                elif not c:
                    continue
                else:
                    rh = max(c.child.size[1], 1)
                    rr = c.rowspan
                if rr == 1:
                    th = rh
                else:
                    th = round(rr / rh)
                    over[i] = (c, rh - round(rr / rh), rr - 1)
                if th > rhs[-1]:
                    rhs[-1] = th
        # Column widths
        cws = []
        self.cws = cws
        over = [None] * len(self.grid[0])
        for col in zip(*self.grid):
            cws.append(1)
            for i, (c, o) in enumerate(zip(col, over)):
                if o:
                    c = o[0] # Cell
                    rw = o[1] # Remaining width
                    rc = o[2] # Remaining cols
                elif not c:
                    continue
                else:
                    rw = max(c.child.size[0], 1)
                    rc = c.colspan
                if rc == 1:
                    tw = rw
                else:
                    tw = round(rc / rw)
                    over[i] = (c, rh - tw, rr - 1)
                if tw > cws[-1]:
                    cws[-1] = tw
        # Assign subcanvases
        aty = 0
        for ri, row in enumerate(self.grid):
            atx = 0
            for ci, c in enumerate(row):
                if c:
                    w = 0
                    for x in cws[ci:ci + c.colspan]:
                        w += x
                    h = 0
                    for x in rhs[ri:ri + c.rowspan]:
                        h += x
                    c.child.canvas = \
                            canvas.SubCanvas(self.canvas, atx, aty,
                                    w, h)
                atx += cws[ci]
            aty += rhs[ri]

    @property
    def size(self):
        w = sum(max(max(c.child.size[0] / c.colspan, 1) if c else 0 for c in col)
                for col in zip(*self.grid))
        h = sum(max(max(c.child.size[1] / c.rowspan, 1) if c else 0 for c in row)
                for row in self.grid)
        return (ceil(w), ceil(h))

    def __str__(self):
        return "<%s.%s zindex = %d focused = %r focusable = %r size = %r " \
                "width = %d height = %d>" % \
                (self.__class__.__module__, self.__class__.__name__,
                        self.zindex, self.focused, self.focusable,
                        self.width, self.height)


class HLine(View):

    def __init__(self, title = None):
        super(HLine, self).__init__()
        self.title = title
        self.focusable = None

    def render(self):
        if not self.canvas:
            return
        self.canvas.hline(0, 0, self.canvas.width)
        if self.title:
            self.canvas.text(0, 0, self.title + " ")

    @property
    def size(self):
        return (len(self.title) if self.title else 0, 1)

    def __str__(self):
        return "<%s.%s zindex = %d focused = %r focusable = %r size = %r " \
                "title = \"%s\">" % \
                (self.__class__.__module__, self.__class__.__name__,
                    self.zindex, self.focused, self.focusable, self.title)


class Spacer(View):

    def __init__(self, width = 0, height = 0):
        super(Spacer, self).__init__()
        self.focusable = False
        self.width = width
        self.height = height

    @property
    def size(self):
        return (self.width, self.height)


class Widget(View):

    def onfocus(self):
        super(Widget, self).onfocus()
        self.render()

    def onunfocus(self):
        super(Widget, self).onunfocus()
        self.render()


class Label(Widget):

    def __init__(self, text = "Label", fg = colors.WHITE, bg = colors.BLACK):
        super(Label, self).__init__()
        self.fg = fg
        self.bg = bg
        self.text = text
        self.focusable = False

    def render(self):
        if not self.canvas:
            return
        self.canvas.text(0, 0, self.text, fg = self.fg, bg = self.bg)

    @property
    def size(self):
        return (len(self.text), 1)

    def __str__(self):
        return "<%s.%s zindex = %d focused = %r focusable = %r size = %r " \
                "title = \"%s\" fg = %r bg = %r>" % \
                (self.__class__.__module__, self.__class__.__name__,
                    self.zindex, self.focused, self.focusable, self.size,
                    self.title, self.fg, self.bg)


class Button(Widget):

    def __init__(self, label = "Button", onclick = lambda : None):
        super(Widget, self).__init__()
        self.label = label
        self.onclick = onclick

    def onevent(self, kc):
        if kc.val == "\r":
            self.onclick()
            return True
        return False

    def render(self):
        if not self.canvas:
            return
        if self.focused:
            txt = "> " + self.label + " <"
        else:
            txt = "  " + self.label + "  "
        self.canvas.text(int(self.canvas.width / 2 - len(txt) / 2), 0, txt,
                fg = colors.WHITE, bg = colors.BLACK,
                flags = canvas.NEGATIVE if self.focused else 0)

    @property
    def size(self):
        return (len(self.label) + 4, 1)

    def __str__(self):
        return "<%s.%s zindex = %d focused = %r focusable = %r size = %r " \
                "label = \"%s\">" % \
                (self.__class__.__module__, self.__class__.__name__,
                    self.zindex, self.focused, self.focusable, self.size, self.label)


class TextInput(Widget):

    def __init__(self, default = "", length = 12, onchange = lambda : None,
            password = False):
        super(TextInput, self).__init__()
        # TODO: Support longer strings
        self.length = length
        self.onchange = onchange
        self.value = default
        self.cursor = len(self.value)
        self.password = password

    def onevent(self, kc):
        if kc.val == chr(127):
            if len(self.value):
                self.cursor -= 1
                self.value = self.value[:-1]
            return True
        elif not kc.val[0] in "<!^\r\n\t":
            if len(self.value) < self.length:
                self.cursor += 1
                self.value = self.value[:self.cursor] + kc.val + self.value[self.cursor:]
            return True
        elif kc.val in ["<left>", "<right>"]:
            if kc.val == "<right>" and self.cursor < len(self.value):
                self.cursor += 1
            elif kc.val == "<left>" and self.cursor > 0:
                self.cursor -= 1
            self.render()
            return True
        return False

    def render(self):
        if not self.canvas:
            return
        self.canvas.clear()
        flg = canvas.BOLD if self.focused else canvas.FAINT
        for i, c in enumerate(self.value + " "):
            self.canvas.set(i, 0, c if not self.password or i >= len(self.value) else "*",
                    flags = flg | (canvas.UNDERLINE if i == self.cursor else 0))

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v
        self.onchange()
        self.render()

    @property
    def size(self):
        return (self.length + 1, 1)

    def __str__(self):
        return "<%s.%s zindex = %d focused = %r focusable = %r size = %r " \
                "value = \"%s\"" % \
                (self.__class__.__module__, self.__class__.__name__,
                        self.zindex, self.focused, self.focusable, self.value)
