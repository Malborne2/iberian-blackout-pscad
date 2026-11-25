"""Replace one source3 with a sync_machine2 (pilot for Bus30).

Machine layout (grid units, relative to the creation point):
    NS (x+3,y) 3-phase terminal, N (x,y) neutral, speed/tmeco/telect/cfldn = outputs,
    efldn (x-1,y-4) and tmech (x+1,y+4) = real inputs.

Usage: python notes/add_machine.py <bus> <x> <y> <MVA> <P0 MW> <H> <tap x,y>
"""
import re, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools
import mhi.pscad as p

BUS = sys.argv[1]
MX, MY = int(sys.argv[2]), int(sys.argv[3])
SMVA = float(sys.argv[4])
P0 = float(sys.argv[5])
H = float(sys.argv[6])
TAPPT = tuple(int(v) for v in sys.argv[7].split(','))

app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')

def mk(defn, x, y, orient=0, **kw):
    return main.create_component(defn, x, y, orient, **kw)

def conn(a, b, **kw):
    try:
        r = main.create_connection(a, b, **kw)
        ptools.log('   wire ok', kw.get('label', ''), '' if r is None else r)
        return r
    except Exception as e:
        ptools.log('   WIRE ERR', type(e).__name__, e)
        return None

sm = mk('master:sync_machine2', MX, MY, 0, Name='SM' + BUS,
        MVA=SMVA, Vbase_LL=400.0, FRE=50.0, H=H, NOM=1.0,
        Ra=0.002, Xp=0.15, Xd=1.9, Xd_=0.30, Tdo_=8.0, Xd__=0.20, Tdo__=0.03,
        Xq=1.85, Xq_=0.50, Xq__=0.20, MSat=0, MM=1,
        P0=P0, Q0=0.0, VT=1.0, Pheta=0.0, T_S2M=0.3,
        Iexc=0, Igov=0, Interface_E=0, Interface_G=0,
        POut='PSM' + BUS, QOut='QSM' + BUS)
S = {k: tuple(v.location) for k, v in sm.ports().items()}
ptools.log('machine ports', S)

# inputs: tmech (mechanical torque, pu) and efldn (field voltage, pu)
tm = mk('master:const', S['tmech'][0] - 2, S['tmech'][1] + 3, Name='TM' + BUS,
        Value=P0 / SMVA)
ef = mk('master:const', S['efldn'][0] - 3, S['efldn'][1], Name='EF' + BUS, Value=1.0)
T = {k: tuple(v.location) for k, v in tm.ports().items()}
E = {k: tuple(v.location) for k, v in ef.ports().items()}
ptools.log('   TM', T, ' EF', E)

# neutral ground: the ground port sits at creation + (0,+1)
gnd = mk('master:ground', S['N'][0], S['N'][1] - 1)

conn(T['OUT'], S['tmech'])
conn(E['OUT'], S['efldn'])
lbl = conn(S['NS'], TAPPT, label='ND' + BUS, electrical=True)
ptools.log('   NS label', lbl, '->', TAPPT)

pr.save()
ptools.log('saved')
