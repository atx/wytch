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

import asyncio
import concurrent
import tty
import sys
import time
import signal
from functools import wraps
from wytch import view, canvas, input, builder

class WytchExitError(RuntimeError):
    pass

class Wytch:

    def __init__(self, debug = False, debug_redraw = False, ctrlc = True, fps = 20):
        self.debug = debug
        self.debug_redraw = debug_redraw
        self.ctrlc = ctrlc
        self.fps = fps
        self.event_loop = asyncio.get_event_loop()
        self._sigwinch = False
        self._intransport = None

    def __enter__(self):
        self.consolecanvas = canvas.ConsoleCanvas()
        self.rootcanvas = canvas.BufferCanvas(self.consolecanvas,
                                         debug = self.debug_redraw)
        self.realroot = view.ContainerView()
        self.root = self.realroot
        self.realroot.canvas = self.rootcanvas
        if self.debug:
            console = view.Console(minheight = 10)
            self.root = view.ContainerView()
            with builder.Builder(self.realroot) as b:
                b.vertical() \
                    .box("Console").add(console).end() \
                    .add(self.root)

            def _print(*args, sep = " ", end = "\n", file = sys.stdout, flush = False):
                s = ""
                for x in args[:-1]:
                    s += str(x) + sep
                if args:
                    s += str(args[-1]) + "\n"
                else:
                    s += "\n"
                for li in s.split("\n")[:-1]:
                    console.push(li)
            self.origprint = print
            __builtins__["print"] = _print

        return self

    def _cleanup(self):
        if self.debug:
            __builtins__["print"] = self.origprint
        self.consolecanvas.destroy()
        print() # Newline

    def exit(self):
        raise WytchExitError

    @asyncio.coroutine
    def _input_loop(self):
        reader = asyncio.StreamReader()
        self._intransport, _ = yield from self.event_loop.connect_read_pipe(
                                            lambda: asyncio.StreamReaderProtocol(reader),
                                            sys.stdin)
        while True:
            b = yield from reader.readexactly(1)
            mouse = False
            if self.ctrlc and b == b"\x03":
                raise KeyboardInterrupt
            elif b == b"\x1b":
                # TODO: Do some testing on a bunch of different terminals
                b += yield from reader.readexactly(1)
                if chr(b[-1]) in {"[", "O"}:
                    b += yield from reader.readexactly(1)
                    if chr(b[-1]) == "M":
                        b += yield from reader.readexactly(3)
                        mouse = True
                    else:
                        while b[-1] in range(ord("0"), ord("9") + 1):
                            b += yield from reader.readexactly(1)
                        if chr(b[-1]) == ";":
                            b += yield from reader.readexactly(1)
                            while b[-1] in range(ord("0"), ord("9") + 1):
                                b += yield from reader.readexactly(1)
                else: # TODO: Figure out if this eves happens
                    pass
            else:
                # Decode unicode
                c = 0
                k = b[0]
                while k & 0x80:
                    k <<= 1
                    c += 1
                b += yield from reader.readexactly(c)
            if mouse:
                me = input.MouseEvent(b)
                self.root.onmouse(me)
            else:
                kc = input.KeyEvent(b.decode("utf-8"))
                self.root.onevent(kc)

    @asyncio.coroutine
    def _render_loop(self):
        nxt = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers = 1) as e:
            fut = None
            while True:
                if self._sigwinch:
                    self.consolecanvas.update_size()
                    self.rootcanvas.update_size()
                    self.realroot.dirty = True
                    self._sigwinch = False
                self.realroot.precalc()
                self.realroot.recalc()
                if fut:
                    # The actual console write does not have to be synchronous
                    # but we do not want to modify the BufferCanvas while it is in progress
                    yield from fut
                self.realroot.render()
                fut = self.event_loop.run_in_executor(e, self.rootcanvas.flush)
                now = time.time()
                if now < nxt:
                    yield from asyncio.sleep(nxt - now)
                nxt = time.time() + 1 / self.fps

    def _sigwinch_handler(self, sig, stack):
        self._sigwinch = True

    @asyncio.coroutine
    def _main(self):
        if self.root.focusable:
            self.root.focused = True
        try:
            cors = [self._input_loop(), self._render_loop()]
            done, pending = yield from \
                                asyncio.wait(cors, return_when = asyncio.FIRST_EXCEPTION)
            while pending:
                pending.pop().cancel()
            done.pop().result()
        except Exception as e:
            self._cleanup()
            if self._intransport:
                self._intransport.close()
            self.event_loop.stop()
            if not isinstance(e, WytchExitError):
                raise e

    def start_event_loop(self):
        signal.signal(signal.SIGWINCH, self._sigwinch_handler)
        self.event_loop.run_until_complete(self._main())

    def __exit__(self, extype, exval, trace):
        if extype is not None:
            self._cleanup()
            return False
        self.start_event_loop()
