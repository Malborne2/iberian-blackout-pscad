"""Probe master:sync_machine geometry, ports and the main parameters."""
import mhi.pscad as p
import ptools
import inspect

app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')
c = main.create_component('master:sync_machine', 330, 330, 0, Name='PRB_SM')
b = c.bounds
ptools.log('wh', (b.right - b.left, b.bottom - b.top))
for k, v in c.ports().items():
    ptools.log('  port %-8s %s dim=%s type=%s' % (k, tuple(v.location), v.dim, v.type))
ptools.log('params', sorted(c.parameters().keys()))
c.delete()
