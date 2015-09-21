#! /usr/bin/env python3

from wytch import builder, colors, view, Wytch

w = Wytch()

with w:
    popup = builder.Popup(w.root)
    label = view.Label("-", fg = colors.GREEN)
    def ongroup(w):
        label.text = w.label
    group = view.Radio.Group(onchange = ongroup)
    with popup:
        x = popup.align().box("Popup").vertical()
        for s in ["alpha", "beta", "gamma", "delta", "epsilon"]:
            r = view.Radio(s)
            r.group = group
            x.align(halign = view.HOR_LEFT).add(r)
        x.add(view.Button("Ok", onclick = lambda _: popup.close()))
    with builder.Builder(w.root) as b:
        b.align().box("Popup demo").vertical() \
            (label) \
            .hline() \
            (view.Button("Open", onclick = lambda _: popup.open())) \
            (view.Button("Exit", onclick = lambda _: w.exit()))
