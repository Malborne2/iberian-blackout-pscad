"""Create ONLY the sync_machine2 (no exciter/governor) and tie it to a bus node label."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools
import mhi.pscad as p

BUS = sys.argv[1]
MX, MY = int(sys.argv[2]), int(sys.argv[3])
SMVA = float(sys.argv[4]); P0 = float(sys.argv[5]); H = float(sys.argv[6])
TAPPT = tuple(int(v) for v in sys.argv[7].split(','))

app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')
sm = main.create_component('master:sync_machine2', MX, MY, 0, Name='SM' + BUS,
                           MVA=SMVA, Vbase_LL=400.0, FRE=50.0, H=H,
                           P0=P0, Q0=0.0, VT=1.0, T_S2M=0.5,
                           POut='PSM' + BUS, QOut='QSM' + BUS)
ptools.log('ports', {k: (tuple(v.location), v.dim) for k, v in sm.ports().items()})
try:
    r = main.create_connection(sm.ports()['NS'].location, TAPPT,
                               label='ND' + BUS, electrical=True)
    ptools.log('label ok', r)
except Exception as e:
    ptools.log('LABEL ERR', type(e).__name__, e)
pr.save()
ptools.log('saved')
