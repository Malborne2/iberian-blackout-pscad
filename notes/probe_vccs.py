"""Probe src_voltage_dependent_current geometry (Dim=1 and Dim=3)."""
import mhi.pscad as p
import ptools

app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')
for dim in (1, 3):
    c = main.create_component('master:src_voltage_dependent_current', 300, 300, 0,
                              Name='PRB_VCCS%d' % dim, Dim=dim, G_VDCS=-0.05, dir=0)
    b = c.bounds
    rel = {k: (v.location[0] - 300, v.location[1] - 300, v.dim) for k, v in c.ports().items()}
    ptools.log('Dim=%d' % dim, 'wh', (b.right - b.left, b.bottom - b.top), rel)
    c.delete()
