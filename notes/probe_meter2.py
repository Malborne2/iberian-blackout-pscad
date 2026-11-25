"""Probe multimeter port positions for orient 0 and 3."""
import time
import mhi.pscad as p
import ptools

app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')
for o in (0, 3):
    c = main.create_component('master:multimeter', 300, 300, o, Name='PRB_M%d' % o)
    b = c.bounds
    rel = {k: (v.location[0] - 300, v.location[1] - 300) for k, v in c.ports().items()}
    ptools.log('meter o%d' % o, 'wh', (b.right - b.left, b.bottom - b.top), rel)
    c.delete()
