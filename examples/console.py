#! /usr/bin/env python3

import time
from wytch import builder, colors, view, Wytch

w = Wytch(debug = True)

with w:
    with builder.Builder(w.root) as b:
        b.align().box("Debug console demo").vertical() \
            (view.Button("Greet", onpress = lambda _: print("Hello!"))) \
            (view.Button("Time", onpress = lambda _: print(time.time()))) \
            (view.Button("Exit", onpress = lambda _: w.exit()))
