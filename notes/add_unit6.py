"""Synchronous machine unit laid out from the measured port geometry.

Machine at (MX,MY): body (MX-3..MX+3, MY-4..MY+4)
    efldn (MX-1,MY-4)  cfldn (MX+1,MY-4)   NS (MX+3,MY)   N (MX,MY)  <- centre!
    tmech (MX+1,MY+4)  speed (MX-1,MY+4)   telect (MX-3,MY)  tmeco (MX-3,MY+2)

Everything is placed relative to those offsets so nothing crosses the body centre:
    const EF  above  -> efldn
    const TM  below  -> tmech
    pgb  V    left   -> telect   (no voltmeter, so no extra ground)
    NS        -> node label to the bus point
Usage: python notes/add_unit6.py <bus> <X> <Y> <MVA> <P0> <H> <buspt x,y> [efld]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools
import mhi.pscad as p

BUS = sys.argv[1]
MX = int(sys.argv[2]); MY = int(sys.argv[3])
SMVA = float(sys.argv[4]); P0 = float(sys.argv[5]); H = float(sys.argv[6])
BUSPT = tuple(int(v) for v in sys.argv[7].split(','))
EF = float(sys.argv[8]) if len(sys.argv) > 8 else 1.03
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

# consts: OUT port is at (x+2, y)
ef = mk('master:const', S['efldn'][0] - 1, S['efldn'][1] - 3, Name='EF' + TAG, Value=EF)
tm = mk('master:const', S['tmech'][0] - 1, S['tmech'][1] + 3, Name='TM' + TAG, Value=P0 / SMVA)
E = ports(ef); T = ports(tm)

# voltage: voltmeter inside the patch, wired to the machine terminal (N1) and ground (N2)
vm = mk('master:voltmeter', S['NS'][0], S['NS'][1] + 6, Name='V_' + TAG)
V = ports(vm)
gm = mk('master:ground', V['N2'][0], V['N2'][1] - 1)
GM = ports(gm)

ok = [conn(S['NS'], BUSPT, label='ND' + TAG, electrical=True),
      conn(E['OUT'], S['efldn']),
      conn(T['OUT'], S['tmech']),
      conn(V['N1'], S['NS']),
      conn(V['N2'], GM['A'])]
ptools.log(BUS, 'ports', S, 'ok', ok)
pr.save()
ptools.log('saved', BUS)
