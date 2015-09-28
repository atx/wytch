#! /usr/bin/env python3

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
