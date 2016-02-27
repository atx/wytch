# The MIT License (MIT)
# 
# Copyright (c) 2016 Josef Gajdusek
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

import inspect
import collections
from functools import wraps

_unbound_handlers = {}

def _fullname(o):
    if hasattr(o, "__module__") and o.__module__:
        return o.__module__ + "." + o.__qualname__
    return o.__qualname__


def handler(evname, **kwargs):
    """
    Mark a method as a handler for an Event of the specified name.

    Usage:
      class A(EventSource):
          
          @handler("key")
          def onkey(self, event):
              pass

          @handler("key", invert = True, key = "\r"):
          def onkey(self, event):
              pass
    """
    def decor(fn):
        # As there is no way to get the class object at this point, put the
        # event handler into a global map and then .class_bind it properly when
        # the constructor first gets called.
        # Also note that we are using string name instead of the actual function
        # reference. This is because @wraps does not fix the == operator.
        nm = _fullname(fn)
        if nm not in _unbound_handlers:
            _unbound_handlers[nm] = []
        _unbound_handlers[nm].append((evname, kwargs))
        return fn
    return decor



class EventSource:

    """
    Base class for all classes that want to fire events.
    """

    class Handler:

        def __init__(self, evname, fn, mkws = {}):
            self.evname = evname
            self.fn = fn
            self.mkws = mkws

    def __init__(self):
        self._bind_handlers()
        self._handlers = {}
        self._inherit_handlers()

    @classmethod
    def _class_bind(cls, evname, fn, **kwargs):
        """
        Bind a method of this class (or a parent) to an event. These methods
        will get translated to bound methods on instantiation.
        """
        if evname not in cls._class_handlers:
            cls._class_handlers[evname] = []
        cls._class_handlers[evname].append(EventSource.Handler(evname, fn, kwargs))

    @classmethod
    def _bind_handlers(cls):
        """
        Bind all class handlers from @handler.
        Recursively calls ._bind_handlers() on all base classes.
        """
        # Use __dict__ to check that the variable exists in this class and not a superclass
        if "_class_handlers" in cls.__dict__:
            return
        for base in cls.__bases__:
            if hasattr(base, "_bind_handlers"):
                base._bind_handlers()
        cls._class_handlers = {}
        for x in cls.__dict__.values():
            if not callable(x):
                continue
            nm = _fullname(x)
            if nm in _unbound_handlers:
                for evname, mkws in _unbound_handlers[nm]:
                    cls._class_bind(evname, x, **mkws)

    def _inherit_handlers(self):
        """ .bind class handlers from all parent classes. """
        for parent in [p for p in inspect.getmro(self.__class__) \
                        if hasattr(p, "_class_handlers")]:
            for ev, hdls in parent._class_handlers.items():
                for h in hdls:
                    # Find the appropriate bound method of self
                    for metname in self.__dir__():
                        # Notice that we cannot just getattr on self as that could
                        # attempt to dereference properties depending on uninitialized variables
                        clfn = getattr(self.__class__, metname, None)
                        if clfn and clfn == h.fn:
                            self.bind(ev, getattr(self, metname), **h.mkws)

    def bind(self, evname, fn, **kwargs):
        """
        Bind an handler for an event with the provided name.

        Returns a reference to an instance of EventSource.Handler which can be then passed
        to .unbind
        """
        if evname not in self._handlers:
            self._handlers[evname] = []
        h = EventSource.Handler(evname, fn, kwargs)
        self._handlers[evname].append(h)
        return h

    def unbind(self, handler):
        """ Unbind a handler registered with the .bind method. """
        self._handlers[handler.evname].remove(handler)

    def fire(self, event):
        """
        Fire an event from this object and return True when at least one
        handler was found and executed.
        """
        if self._handlers.get(event.name, []):
            ret = False
            for h in self._handlers[event.name]:
                kws = h.mkws.copy()
                if "matcher" in kws:
                    kws.pop("matcher")
                    matcher = lambda **kwargs: h.mkws["matcher"](event, **kwargs)
                else:
                    matcher = event.matches
                if "invert" in kws:
                    flip = kws["invert"]
                    kws.pop("invert")
                else:
                    flip = False
                if flip ^ matcher(**kws):
                    h.fn(event)
                    ret = True
            return ret
        return False


class Event:

    """
    Base class for events.
    """

    def __init__(self, name, source = None):
        self.name = name
        self.source = source

    def matches(self):
        """
        Method to be implemented by a subclass that wants to provide more
        specific matching than by name.
        """
        return True


class KeyEvent(Event):

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
        super(KeyEvent, self).__init__("key")
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

    def matches(self, key = None, keys = None):
        return (keys is None and keys is None) or \
               (key and self.val == key) or (self.val in keys)

    def __str__(self):
        return "<input.KeyEvent shift = %r alt = %r ctrl = %r val = %r>" % \
                (self.shift, self.alt, self.ctrl, self.val)


class MouseEvent(Event):

    LEFT = 0
    MIDDLE = 1
    RIGHT = 2
    RELEASED = 3

    def __init__(self, s = None):
        super(MouseEvent, self).__init__("mouse")
        if not s:
            s = b"\x1b[M\x00!!"
        if s[0:3] != b"\x1b[M" or len(s) != 6:
            raise ValueError("Invalid escape sequence %r" % s)
        self.raw = s
        code = s[3]
        self.button = code & 0x03
        self.drag = bool(code & 0x40)
        self.released = self.button == MouseEvent.RELEASED
        self.pressed = not self.released and not self.drag
        # Start at 0 0
        self.x = s[4] - 32 - 1
        self.y = s[5] - 32 - 1
        if self.x < 0:
            self.x += 255
        if self.y < 0:
            self.y += 255

    def shifted(self, x, y):
        ret = MouseEvent(self.raw)
        ret.x = self.x - x
        ret.y = self.y - y
        return ret

    def matches(self, button = None):
        return self.button is None or \
               (self.button == button)

    def __str__(self):
        return "<input.MouseEvent x = %d y = %d button = %d pressed = %r drag = %r released = %r>" % \
                (self.x, self.y, self.button, self.pressed, self.drag, self.released)
