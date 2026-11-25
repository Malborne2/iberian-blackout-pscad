"""Compact machine unit placed in the small empty rect next to its bus.

Only the stator lead is ELECTRICAL and must be short; the field (efldn) and torque (tmech)
leads are SIGNAL wires, which may cross the schematic without shorting anything.

Layout inside a 7 x 9 rect (left..right, top..bottom):
    machine (left+3, top+4)     body = the whole rect
    NS      (left+6, top+4)     -> short electrical wire to the bus
    efldn   (left+2, top)       <- signal wire from a const above/left
    tmech   (left+4, top+8)     <- signal wire from a const below
    voltmeter at the old multimeter position, N1 -> bus, N2 -> ground

Usage: python notes/unit_compact.py <bus> <sx> <sy> <mmx> <mmy> <bx> <by> <MVA> <P0> <H> <tag>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools

BUS = sys.argv[1]
SX, SY = int(sys.argv[2]), int(sys.argv[3])
MMX, MMY = int(sys.argv[4]), int(sys.argv[5])
BX, BY = int(sys.argv[6]), int(sys.argv[7])
SMVA = float(sys.argv[8]); P0 = float(sys.argv[9]); H = float(sys.argv[10])
TAG = sys.argv[11]

app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')

rect = main.closest_empty_rect(7, 9, (BX, BY))
L, T = rect.left, rect.top
ptools.log(BUS, 'rect', (L, T, rect.right, rect.bottom))

def mk(defn, x, y, orient=0, **kw):
    return main.create_component(defn, x, y, orient, **kw)

def wire(*pts, kind='sig'):
    try:
        main.create_wire(*pts)
        return True
    except Exception as e:
        ptools.log('   %s wire ERR' % kind, pts, type(e).__name__, e)
        return False

mx, my = L + 3, T + 4
sm = mk('master:sync_machine2', mx, my, 0, Name='SM' + TAG,
        MVA=SMVA, Vbase_LL=400.0, FRE=50.0, H=H, NOM=1.0, MSat=0, MM=1,
        Ra=0.002, Xp=0.10, Xd=0.45, Xd_=0.25, Tdo_=8.0, Xd__=0.15, Tdo__=0.03,
        Xq=0.43, Xq_=0.22, Xq__=0.14,
        P0=P0, Q0=0.0, VT=1.0, Pheta=0.0, T_S2M=0.5,
        Iexc=0, Igov=0, Interface_E=0, Interface_G=0,
        POut='P_' + TAG, QOut='Q_' + TAG)
S = {k: tuple(v.location) for k, v in sm.ports().items()}

# consts just outside the rect (graphics may overlap neighbours; only ports matter)
ef = mk('master:const', L - 3, T, Name='EF' + TAG, Value=1.05)
tm = mk('master:const', L + 3, T + 11, Name='TM' + TAG, Value=P0 / SMVA)

ok = []
ok.append(wire((L - 1, T), S['efldn'], kind='sig'))                 # efldn (signal)
ok.append(wire((L + 5, T + 11), S['tmech'], kind='sig'))            # tmech (signal)
# stator: two short electrical segments to the bus
ok.append(wire(S['NS'], (S['NS'][0], BY), (BX, BY), kind='ELEc'))

# voltmeter on the old multimeter spot: N1 -> bus, N2 -> ground
vm = mk('master:voltmeter', MMX, MMY, Name='V_' + TAG)
V = {k: tuple(v.location) for k, v in vm.ports().items()}
gm = mk('master:ground', V['N2'][0], V['N2'][1] + 1)
if V['N1'][1] != BY:
    ok.append(wire(V['N1'], (V['N1'][0], BY), kind='elec'))
else:
    ok.append(wire(V['N1'], (BX, BY), kind='elec'))

ptools.log(BUS, 'machine', (mx, my), 'NS', S['NS'], 'vm', V, 'ok', ok)
pr.save()
ptools.log('saved', BUS)
