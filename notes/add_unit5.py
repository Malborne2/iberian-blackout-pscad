"""Synchronous machine unit in the free band + voltmeter at the old source position.

The stator is tied to its bus with node labels (works for a 3-dim port).  The voltmeter is
placed where the source3 used to be and wired to the bus with a short wire (a label cannot
bridge the voltmeter's 1-dim node and the 3-dim bus).

Usage: python notes/add_unit5.py <bus> <X> <MVA> <P0 MW> <H> <buspt x,y> [efld] [vx,vy]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools
import mhi.pscad as p

BUS = sys.argv[1]
MX = int(sys.argv[2]); MY = 160
SMVA = float(sys.argv[3]); P0 = float(sys.argv[4]); H = float(sys.argv[5])
BUSPT = tuple(int(v) for v in sys.argv[6].split(','))
EF = float(sys.argv[7]) if len(sys.argv) > 7 else 1.0
VPT = tuple(int(v) for v in sys.argv[8].split(',')) if len(sys.argv) > 8 else None
TAG = BUS.replace('Bus', 'G')

app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')

def mk(defn, x, y, orient=0, **kw):
    return main.create_component(defn, x, y, orient, **kw)

def ports(c):
    return {k: tuple(v.location) for k, v in c.ports().items()}

def conn(a, b, **kw):
    try:
        main.create_connection(a, b, **kw)
        return True
    except Exception as e:
        ptools.log('   ERR', type(e).__name__, e)
        return False

sm = mk('master:sync_machine2', MX, MY, 0, Name='SM' + TAG,
        MVA=SMVA, Vbase_LL=400.0, FRE=50.0, H=H, NOM=1.0, MSat=0, MM=1,
        Ra=0.002, Xp=0.15, Xd=1.9, Xd_=0.30, Tdo_=8.0, Xd__=0.20, Tdo__=0.03,
        Xq=1.85, Xq_=0.50, Xq__=0.20,
        P0=P0, Q0=0.0, VT=1.0, Pheta=0.0, T_S2M=0.5,
        Iexc=0, Igov=0, Interface_E=0, Interface_G=0,
        POut='P_' + TAG, QOut='Q_' + TAG)
S = ports(sm)

ef = mk('master:const', S['efldn'][0] - 3, S['efldn'][1] - 3, Name='EF' + TAG, Value=EF)
tm = mk('master:const', S['tmech'][0] - 3, S['tmech'][1] + 3, Name='TM' + TAG, Value=P0 / SMVA)
E = ports(ef); T = ports(tm)

ok = [conn(S['NS'], BUSPT, label='ND' + TAG, electrical=True),
      conn(E['OUT'], S['efldn']),
      conn(T['OUT'], S['tmech'])]

if VPT:
    vm = mk('master:voltmeter', VPT[0], VPT[1], Name='V_' + TAG)
    V = ports(vm)
    gm = mk('master:ground', V['N2'][0], V['N2'][1] + 1)
    if V['N1'][1] != BUSPT[1]:
        ok.append(conn(V['N1'], (V['N1'][0], BUSPT[1])))
    ok.append(conn(V['N2'], ports(gm)['A']))

ptools.log(BUS, 'machine ports', S, 'ok', ok)
pr.save()
ptools.log('saved', BUS)
