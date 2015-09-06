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
        # Find the deepest element
        at = self
        while at.focused_child:
            at = at.focused_child
        # Bubble up until handled or until we have to handle it
        while at is not self and not at.onevent(kc):
            at = at.parent

        if kc.raw == "\t":
            return self.focus_next()

        if at is self and kc.isescape:
            if kc.raw[2] == "B":
                return self.focus_next()
            elif kc.raw[2] in ["A", "Z"]:
                return self.focus_prev()
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


class Button(Widget):

    def __init__(self, label = "Button", onclick = lambda : None):
        super(Widget, self).__init__()
        self.label = label
        self.onclick = onclick

    def onevent(self, kc):
        if kc.raw == "\r":
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
        if kc.raw in string.ascii_letters + string.digits + \
                string.punctuation + " \n":
            if len(self.value) < self.length:
                self.cursor += 1
                self.value = self.value[:self.cursor] + kc.raw + self.value[self.cursor:]
            return True
        elif kc.raw == chr(127):
            if len(self.value):
                self.cursor -= 1
                self.value = self.value[:-1]
            return True
        elif kc.isescape and kc.raw[2] in ["C", "D"]:
            if kc.raw[2] == "C" and self.cursor < len(self.value):
                self.cursor += 1
            elif kc.raw[2] == "D" and self.cursor > 0:
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
