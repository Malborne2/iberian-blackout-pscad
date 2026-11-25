"""Probe freq-meas port dimensions and the timed-breaker parameters."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools

app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')
fm = main.create_component('master:freq-meas', 300, 400, Name='PRBFM', F=50.0,
                           Vbas=230.94, Cnfg=0, View=1)
ptools.log('freq-meas ports',
           {k: (tuple(v.location), v.dim, str(v.type)) for k, v in fm.ports().items()})
ptools.log('freq-meas params', sorted(fm.parameters().keys()))
fm.delete()

tb = main.create_component('master:tbreakn', 320, 400, Name='PRBTB')
ptools.log('tbreakn ports',
           {k: (tuple(v.location), v.dim) for k, v in tb.ports().items()})
ptools.log('tbreakn params', {k: str(v) for k, v in tb.parameters().items()})
tb.delete()
pr.save()
