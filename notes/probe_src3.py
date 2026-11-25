"""Probe source3 single-line ports (names, dims, offsets)."""
import mhi.pscad as p
import ptools

app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')
for o in (0, 7):
    c = main.create_component('master:source3', 320, 260, o, Name='PRB_S%d' % o,
                              MVA=4300.0, Vm=132.0, F=50.0, Term=1,
                              PCtrl=1, Pdes=-1.0, VCtrl=0)
    b = c.bounds
    info = {k: (v.location[0] - 320, v.location[1] - 260, v.dim) for k, v in c.ports().items()}
    ptools.log('source3 o%d' % o, 'wh', (b.right - b.left, b.bottom - b.top), info)
    c.delete()
