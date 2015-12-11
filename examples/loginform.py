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

w = Wytch(debug = False, ctrlc = False)

def clicked(user, pwd):
    if pwd == "pass":
        w.exit()

with w:
    tusr = view.TextInput()
    tpwd = view.TextInput(password = True)
    rem = view.Checkbox("Remember me")
    with builder.Builder(w.root) as b:
        b.align().box("Login").grid(3, 4) \
            (view.Label("Username", fg = colors.BLUE)).spacer(width = 2)(tusr) \
            (view.Label("Password", fg = colors.BLUE))()(tpwd) \
            (rem, colspan = 3)()() \
            (view.Button("Ok", onpress = lambda _: clicked(tusr.value, tpwd.value)), colspan = 3)
print("Bye %s!" % tusr.value)
if rem.value:
    print("You will be remembered")
