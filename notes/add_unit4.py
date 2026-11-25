"""Convert one source3 into a synchronous machine with FIXED excitation and torque.

The exciter/governor chain triggers a 'GND' signal contention inside `sync_machine2`, so
this version drives `efldn` (field voltage, pu) and `tmech` (mechanical torque, pu)
directly from `const` blocks.  That still gives real inertia and frequency dynamics - the
machine swings against the network imbalance - which is what the frequency figures need.

Usage: python notes/add_unit4.py <bus> <x> <y> <MVA> <P0 MW> <H> <bus_y> [efld]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools
import mhi.pscad as p

BUS = sys.argv[1]
MX, MY = int(sys.argv[2]), int(sys.argv[3])
SMVA = float(sys.argv[4]); P0 = float(sys.argv[5]); H = float(sys.argv[6])
BUSY = int(sys.argv[7])
EF = float(sys.argv[8]) if len(sys.argv) > 8 else 1.0
NEUT = int(sys.argv[9]) if len(sys.argv) > 9 else 0
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
        Neut=NEUT, RNeut=1.0e5,
        Ra=0.002, Xp=0.15, Xd=1.9, Xd_=0.30, Tdo_=8.0, Xd__=0.20, Tdo__=0.03,
        Xq=1.85, Xq_=0.50, Xq__=0.20,
        P0=P0, Q0=0.0, VT=1.0, Pheta=0.0, T_S2M=0.5,
        Iexc=0, Igov=0, Interface_E=0, Interface_G=0,
        POut='P_' + TAG, QOut='Q_' + TAG)
S = ports(sm)
ptools.log(BUS, 'ports', S)

ef = mk('master:const', S['efldn'][0] - 5, S['efldn'][1], Name='EF' + TAG, Value=EF)
tm = mk('master:const', S['tmech'][0] - 5, S['tmech'][1], Name='TM' + TAG, Value=P0 / SMVA)
vm = mk('master:voltmeter', MX + 7, MY + 2, Name='V_' + TAG)
V = ports(vm)
gm = mk('master:ground', V['N2'][0], V['N2'][1] + 1)
GM = ports(gm)
ptools.log('  ef', ports(ef), 'tm', ports(tm))

conn(S['NS'], (S['NS'][0], BUSY))          # stator -> bus
conn(ports(ef)['OUT'], S['efldn'])
conn(ports(tm)['OUT'], S['tmech'])
conn(V['N1'], (V['N1'][0], BUSY))
conn(V['N2'], GM['A'])

pr.save()
ptools.log('saved', BUS)
