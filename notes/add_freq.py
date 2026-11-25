"""Add a frequency meter on a machine bus, with an output channel.

freq-meas (single-line view) has one electrical port N (dim 3) plus Volts/FREQ/PHASE signal
outputs. N goes to the bus through a node label (3-dim -> 3-dim works); FREQ drives a pgb.

Usage: python notes/add_freq.py <tag> <meter x> <meter y> <buspt x,y> <pgb x> <pgb y>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools

TAG = sys.argv[1]
FX, FY = int(sys.argv[2]), int(sys.argv[3])
BUSPT = tuple(int(v) for v in sys.argv[4].split(','))
PX, PY = int(sys.argv[5]), int(sys.argv[6])

app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')
fm = main.create_component('master:freq-meas', FX, FY, Name='FM' + TAG, F=50.0,
                           Vbas=230.94, Cnfg=0, PCnfg=1, View=1, Ts=0.02)
ptools.log('fm ports', {k: (tuple(v.location), v.dim) for k, v in fm.ports().items()})
pg = main.create_component('master:pgb', PX, PY, Name='F_' + TAG, UseSignalName='NO',
                           enab='YES', Display='YES', Units='Hz', Scale=1.0,
                           Min=45.0, Max=55.0)
ptools.log('pgb params', {k: str(v) for k, v in pg.parameters().items()})

ok = []
try:
    main.create_connection(fm.port('N'), BUSPT, label='NF' + TAG, electrical=True)
    ok.append('label')
except Exception as e:
    ptools.log('  label ERR', type(e).__name__, e)
try:
    main.create_connection(fm.port('FREQ'), pg.port('Signl'))
    ok.append('freq->pgb')
except Exception as e:
    ptools.log('  freq ERR', type(e).__name__, e)
ptools.log('ok', ok)
pr.save()
ptools.log('saved FM' + TAG)
