"""Bisect the GND contention: add only the exciter (no governor)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools
import mhi.pscad as p

app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')
MX, MY = 35, 145
sm = main.create_component('master:sync_machine2', MX, MY, 0, Name='SMB30',
                           MVA=1130.0, Vbase_LL=400.0, FRE=50.0, H=5.0,
                           P0=1000.0, Q0=0.0, VT=1.0, T_S2M=0.5, MSat=0, MM=1)
S = sm.ports()
ex = main.create_component('master:exc_scrx', MX - 14, MY - 6, Name='EXB30',
                           Vbase=230.94, Ibase=1.631, IExst=0)
X = ex.ports()
ptools.log('machine', {k: tuple(v.location) for k, v in S.items()})
ptools.log('exciter', {k: tuple(v.location) for k, v in X.items()})


def c(a, b):
    try:
        main.create_connection(a, b)
        ptools.log('  ok')
    except Exception as e:
        ptools.log('  ERR', type(e).__name__, e)


c(S['NS'].location, (27, 17))
c(S['telect'].location, X['Vabc'].location)
c(S['cfldn'].location, X['If'].location)
c(X['Ef'].location, S['efldn'].location)
pr.save()
ptools.log('saved: machine + exciter only')
