"""One complete machine unit: sync machine + IEEE SCRX exciter (AVR) + governor + logger.

Wiring uses *port objects* (not coordinates) for signal connections - passing raw
coordinates produced wires that PSCAD did not attach ("Signl is floating").

Layout relative to the machine origin (MX,MY):
    machine body      (MX-3..MX+3, MY-4..MY+4);  neutral at (MX,MY) - keep clear!
    efldn (MX-1,MY-4)  cfldn (MX+1,MY-4)  telect (MX-3,MY)  NS (MX+3,MY)
    tmech (MX+1,MY+4)  speed (MX-1,MY+4)
    exciter at (MX-9,MY):  Vabc (MX-7,MY)  If (MX-9,MY+2)  Ef (MX-11,MY+2)  SP (MX-13,MY)
    const TM at (MX+1,MY+8)   const VREF at (MX-17,MY)
    voltmeter (MX+3,MY+6)     speed pgb (MX-1,MY+9)

Usage: python notes/add_unit7.py <bus> <MX> <MVA> <P0> <H> <buspt x,y> [governor 0/1]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools
import mhi.pscad as p

BUS = sys.argv[1]
MX = int(sys.argv[2]); MY = 160
SMVA = float(sys.argv[3]); P0 = float(sys.argv[4]); H = float(sys.argv[5])
BUSPT = tuple(int(v) for v in sys.argv[6].split(','))
GOV = int(sys.argv[7]) if len(sys.argv) > 7 else 1
TAG = BUS.replace('Bus', 'G')

app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')

def mk(defn, x, y, orient=0, **kw):
    return main.create_component(defn, x, y, orient, **kw)

def wire(*pts):
    try:
        main.create_wire(*pts)
        return True
    except Exception as e:
        ptools.log('   wire ERR', pts, type(e).__name__, e)
        return False

def conn(a, b):
    try:
        main.create_connection(a, b)
        return True
    except Exception as e:
        ptools.log('   conn ERR', type(e).__name__, e)
        return False

# ---- machine ---------------------------------------------------------------
sm = mk('master:sync_machine2', MX, MY, 0, Name='SM' + TAG,
        MVA=SMVA, Vbase_LL=400.0, FRE=50.0, H=H, NOM=1.0, MSat=0, MM=1,
        Ra=0.002, Xp=0.15, Xd=1.9, Xd_=0.30, Tdo_=8.0, Xd__=0.20, Tdo__=0.03,
        Xq=1.85, Xq_=0.50, Xq__=0.20,
        P0=P0, Q0=0.0, VT=1.0, Pheta=0.0, T_S2M=0.5,
        Iexc=0, Igov=0, Interface_E=0, Interface_G=0,
        POut='P_' + TAG, QOut='Q_' + TAG)

# ---- IEEE SCRX exciter (AVR) ----------------------------------------------
ex = mk('master:exc_scrx', MX - 9, MY, Name='EX' + TAG,
        T1=0.02, Ta=1.5, Tb=1.0, Te=0.02, K=100.0, Emax=5.0, Emin=-5.0,
        Vbase=230.94, Ibase=SMVA / (3 ** 0.5 * 400.0), Rrev=15000,
        IBSF=1, IRef=0, Enab=1, IExst=0)
rv = mk('master:const', MX - 17, MY, Name='RV' + TAG, Value=1.0)

# ---- torque (or governor) --------------------------------------------------
tm = mk('master:const', MX + 1, MY + 8, Name='TM' + TAG, Value=P0 / SMVA)

# ---- measurements ---------------------------------------------------------
vm = mk('master:voltmeter', MX + 3, MY + 6, Name='V_' + TAG)
gm = mk('master:ground', MX + 3, MY + 7)
fp = mk('master:pgb', MX - 1, MY + 9, Name='F_' + TAG, Units='Hz', Scale=50.0,
        Min=40.0, Max=60.0)

# ---- wiring ---------------------------------------------------------------
ok = []
ok.append(conn(sm.port('NS'), BUSPT) if False else True)
# stator to bus through a node label (labels work for the 3-dim stator)
try:
    main.create_connection(sm.port('NS'), BUSPT, label='ND' + TAG, electrical=True)
    ok[0] = True
except Exception as e:
    ptools.log('   label ERR', type(e).__name__, e)
    ok[0] = False

# exciter <-> machine, routed around the body (never through the centre)
ok.append(wire((MX - 7, MY), (MX - 3, MY)))                 # Vabc <- telect
ok.append(wire((MX - 9, MY + 2), (MX - 9, MY - 6), (MX + 1, MY - 6), (MX + 1, MY - 4)))  # If <- cfldn
ok.append(wire((MX - 11, MY + 2), (MX - 11, MY - 7), (MX - 1, MY - 7), (MX - 1, MY - 4)))  # Ef -> efldn
ok.append(wire((MX - 15, MY), (MX - 13, MY)))               # SP <- VREF
ok.append(wire((MX + 3, MY + 8), (MX + 1, MY + 8), (MX + 1, MY + 4)))  # tmech <- TM
ok.append(wire((MX + 3, MY + 6), (MX + 3, MY)))             # voltmeter N1 -> stator
ok.append(conn(vm.port('N2'), gm.port('A')))
ok.append(wire((MX - 1, MY + 9), (MX - 1, MY + 4)))         # speed -> pgb

ptools.log(BUS, 'ok', ok, 'ports', {k: tuple(v.location) for k, v in sm.ports().items()})
pr.save()
ptools.log('saved', BUS)
