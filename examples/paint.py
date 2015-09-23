#! /usr/bin/env python3

from wytch import builder, colors, view, input, Wytch

w = Wytch()

class DrawingBoard(view.Widget):

    def __init__(self):
        super(DrawingBoard, self).__init__()
        self.grid = None
        self.oldme = None
        self.color = colors.RED
        self.handlers.append(("c", self._onclear))

    def _onclear(self, kc):
        self.canvas.clear()

    def onmouse(self, me):
        if me.button == input.MouseEvent.LEFT:
            self.color = colors.DARKBLUE
        elif me.button == input.MouseEvent.RIGHT:
            self.color = colors.DARKRED

        if not self.oldme:
            self.canvas.set(me.x, me.y, " ", bg = self.color)
        else:
            self.canvas.line(self.oldme.x, self.oldme.y, me.x, me.y, bg = self.color)
        if me.released:
            self.oldme = None
        else:
            self.oldme = me

    def recalc(self):
        if not self.canvas:
            return
        if not self.grid or len(self.grid) != self.canvas.width \
                or len(self.grid[0]) != self.canvas.height:
            self.grid = [[False] * self.canvas.height for _ in range(self.canvas.width)]


    def render(self):
        if not self.canvas:
            return
        for x, col in enumerate(self.grid):
            for y, v in enumerate(col):
                self.canvas.set(x, y, " ")

    @property
    def size(self):
        return (0, 0)

with w:
    w.root.add_child(DrawingBoard())
