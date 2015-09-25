#! /usr/bin/env python3

from wytch import builder, colors, view, input, Wytch

w = Wytch()

class ColorButton(view.Widget):

    def __init__(self, color, board):
        super(ColorButton, self).__init__()
        self.color = color
        self.board = board
        self.focusable = False

    def render(self):
        if not self.canvas:
            return
        self.canvas.square(0, 0, self.canvas.width, self.canvas.height,
            bordercolor = self.color)

    def onmouse(self, me):
        if not me.pressed:
            return
        self.board.colors[me.button] = self.color

    @property
    def size(self):
        return (5, 2)

class DrawingBoard(view.Widget):

    def __init__(self):
        super(DrawingBoard, self).__init__()
        self.grid = None
        self.oldme = None
        self.colors = {}
        self.handlers.append(("c", self._onclear))

    def _onclear(self, kc):
        self.canvas.clear()

    def recalc(self):
        if not self.canvas:
            return
        if not self.grid or len(self.grid) != self.canvas.width \
                or len(self.grid[0]) != self.canvas.height:
            self.grid = [[False] * self.canvas.height for _ in range(self.canvas.width)]

    def onmouse(self, me):
        if me.released:
            key = self.oldme.button
        else:
            key = me.button
        color = self.colors.get(key, colors.DARKGREEN)
        if not self.oldme:
            self.canvas.set(me.x, me.y, " ", bg = color)
        else:
            self.canvas.line(self.oldme.x, self.oldme.y, me.x, me.y, bg = color)

        if me.released:
            self.oldme = None
        else:
            self.oldme = me


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
    board = DrawingBoard()
    w.root.handlers.append(("q", lambda _: w.exit()))
    with builder.Builder(w.root) as b:
        h = b.vertical() \
            .horizontal()
        for c in colors.c256[:16]:
            h.add(ColorButton(c, board))
        h.end().add(board)
