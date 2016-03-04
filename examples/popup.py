#! /usr/bin/env python3
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

from wytch import builder, colors, view, Wytch

w = Wytch()

with w:
    popup = builder.Popup(w.root)
    label = view.Label("-", fg = colors.GREEN)
    def ongroup(ve):
        label.text = ve.new.label
    group = view.Radio.Group(onvalue = ongroup)
    with popup:
        x = popup.align().box("Popup").vertical()
        for s in ["alpha", "beta", "gamma", "delta", "epsilon"]:
            r = view.Radio(s)
            r.group = group
            x.align(halign = view.HOR_LEFT).add(r)
        x.add(view.Button("Ok", onpress = lambda _: popup.close()))
    with builder.Builder(w.root) as b:
        b.align().box("Popup demo").vertical() \
            (label) \
            .hline() \
            (view.Button("Open", onpress = lambda _: popup.open())) \
            (view.Button("Exit", onpress = lambda _: w.exit()))
