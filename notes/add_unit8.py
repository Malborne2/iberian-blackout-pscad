"""Complete machine unit (vertical layout): sync machine + IEEE SCRX AVR + torque + loggers.

Vertical layout keeps each unit only 14 grid units wide so six fit in one row:

    y=152  const VREF            exciter body 155..161
    y=166..174  machine body (neutral at (MX,170) - keep the centre clear!)
    y=166  voltmeter (right)     y=174  const TM (right)

Ports used (verified):
    machine: efldn (MX-1,166) cfldn (MX+1,166) telect (MX-3,170) NS (MX+3,170)
             tmech (MX+1,174) speed (MX-1,174)
    exciter: Vabc (MX+2,158) If (MX,160) Ef (MX-2,160) SP (MX-4,158)

Usage: python notes/add_unit8.py <bus> <MX> <MVA> <P0> <H> <buspt x,y> [log_speed 0/1]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools

BUS = sys.argv[1]
MX = int(sys.argv[2])
SMVA = float(sys.argv[3]); P0 = float(sys.argv[4]); H = float(sys.argv[5])
BUSPT = tuple(int(v) for v in sys.argv[6].split(','))
LOGSPD = int(sys.argv[7]) if len(sys.argv) > 7 else 0
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

sm = mk('master:sync_machine2', MX, 170, 0, Name='SM' + TAG,
        MVA=SMVA, Vbase_LL=400.0, FRE=50.0, H=H, NOM=1.0, MSat=0, MM=1,
        Ra=0.002, Xp=0.15, Xd=1.9, Xd_=0.30, Tdo_=8.0, Xd__=0.20, Tdo__=0.03,
        Xq=1.85, Xq_=0.50, Xq__=0.20,
        P0=P0, Q0=0.0, VT=1.0, Pheta=0.0, T_S2M=0.5,
        Iexc=0, Igov=0, Interface_E=1, Interface_G=1, Term=1,
        POut='P_' + TAG, QOut='Q_' + TAG)

ex = mk('master:exc_scrx', MX, 158, Name='EX' + TAG,
        T1=0.02, Ta=1.5, Tb=1.0, Te=0.02, K=100.0, Emax=5.0, Emin=-5.0,
        Vbase=230.94, Ibase=SMVA / (3 ** 0.5 * 400.0), Rrev=15000,
        IBSF=1, IRef=0, Enab=1, IExst=0)
rv = mk('master:const', MX - 6, 152, Name='RV' + TAG, Value=1.0)

tm = mk('master:const', MX + 6, 174, Name='TM' + TAG, Value=P0 / SMVA)

vm = mk('master:voltmeter', MX + 6, 166, Name='V_' + TAG)
gm = mk('master:ground', MX + 6, 167)

objs = {}
if LOGSPD:
    objs['fp'] = mk('master:pgb', MX - 1, 176, Name='F_' + TAG, Units='Hz', Scale=50.0,
                    Min=40.0, Max=60.0)

ok = []
try:
    main.create_connection(sm.port('NS'), BUSPT, label='ND' + TAG, electrical=True)
    ok.append('label')
except Exception as e:
    ptools.log('   label ERR', type(e).__name__, e)

ok.append(wire((MX + 2, 158), (MX - 6, 158), (MX - 6, 170), (MX - 3, 170)))   # Vabc <- telect
ok.append(wire((MX, 160), (MX, 163), (MX + 1, 163), (MX + 1, 166)))           # If <- cfldn
ok.append(wire((MX - 2, 160), (MX - 2, 164), (MX - 1, 164), (MX - 1, 166)))   # Ef -> efldn
ok.append(wire((MX - 4, 152), (MX - 4, 158)))                                 # SP <- VREF
ok.append(wire((MX + 8, 174), (MX + 1, 174)))                                 # tmech <- TM
ok.append(wire((MX + 6, 166), (MX + 6, 170), (MX + 3, 170)))                  # N1 -> stator
ok.append(conn(vm.port('N2'), gm.port('A')))
if LOGSPD:
    ok.append(wire((MX - 1, 176), (MX - 1, 174)))                             # speed -> F pgb

ptools.log(BUS, 'ok', ok)
pr.save()
ptools.log('saved', BUS)
