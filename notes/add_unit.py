"""Replace one source3 with a synchronous machine + IEEE exciter + governor.

Chain (pattern taken from Examples/sync_machines/sync_multiplemachines.pscx):

    sync_machine2  NS (3-dim) -> generator branch, N = ground-type port (no symbol)
    exc_scrx       Vabc <- wired to the machine terminal, If <- cfldn,
                   Ef -> efldn, SP <- const 1.0
    hydro_gov      w <- speed, Tm0 <- tmeco, Tm -> tmech, SP <- const 1.0
                or th_gov + th_tur for thermal units

Usage: python notes/add_unit.py <bus> <x> <y> <MVA> <P0 MW> <H> <tap x,y> [hy|th]
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
GOV = sys.argv[8] if len(sys.argv) > 8 else 'hy'

app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')

def mk(defn, x, y, orient=0, **kw):
    return main.create_component(defn, x, y, orient, **kw)

def ports(c):
    return {k: (tuple(v.location), v.dim) for k, v in c.ports().items()}

def loc(c, name):
    return tuple(c.ports()[name].location)

def conn(a, b, **kw):
    try:
        r = main.create_connection(a, b, **kw)
        ptools.log('   wire ok', kw.get('label', ''), '' if r is None else r)
        return r
    except Exception as e:
        ptools.log('   WIRE ERR', type(e).__name__, e)
        return None

# ---- machine ---------------------------------------------------------------
sm = mk('master:sync_machine2', MX, MY, 0, Name='SM' + BUS,
        MVA=SMVA, Vbase_LL=400.0, FRE=50.0, H=H, NOM=1.0,
        Ra=0.002, Xp=0.15, Xd=1.9, Xd_=0.30, Tdo_=8.0, Xd__=0.20, Tdo__=0.03,
        Xq=1.85, Xq_=0.50, Xq__=0.20, MSat=0, MM=1, Neut=1,
        P0=P0, Q0=0.0, VT=1.0, Pheta=0.0, T_S2M=0.5,
        Iexc=0, Igov=0, Interface_E=0, Interface_G=0,
        POut='PSM' + BUS, QOut='QSM' + BUS)
ptools.log('machine', ports(sm))

# ---- exciter (IEEE SCRX) ---------------------------------------------------
ex = mk('master:exc_scrx', MX - 14, MY - 6, Name='EX' + BUS,
        T1=0.02, Ta=1.5, Tb=1.0, Te=0.02, K=100.0, Emax=5.0, Emin=-5.0,
        Vbase=230.94, Ibase=SMVA / (3 ** 0.5 * 400.0), Rrev=15000,
        IBSF=1, IRef=0, Enab=1, IExst=0)
ptools.log('exciter', ports(ex))

# ---- governor --------------------------------------------------------------
if GOV == 'hy':
    gv = mk('master:hydro_gov', MX + 2, MY + 12, Name='GV' + BUS, f=50.0, Enab=1)
else:
    gv = mk('master:th_gov', MX + 2, MY + 12, Name='GV' + BUS, T_GOV=1, INIT=1)
ptools.log('governor', ports(gv))

# ---- setpoint constants ----------------------------------------------------
cr = mk('master:const', loc(ex, 'SP')[0] - 4, loc(ex, 'SP')[1], Name='VR' + BUS, Value=1.0)
gsp = 'SP' if GOV == 'hy' else 'WREF'
cs = mk('master:const', loc(gv, gsp)[0] - 4, loc(gv, gsp)[1] + 4, Name='SR' + BUS, Value=1.0)
# conspd is a required input; its port only exists in some machine configurations
SM = sm.ports()
cp = None
if 'conspd' in SM:
    cp = mk('master:const', tuple(SM['conspd'].location)[0] - 4,
            tuple(SM['conspd'].location)[1], Name='CP' + BUS, Value=1.0)
else:
    ptools.log('   no conspd port on this machine')

# ---- wiring ---------------------------------------------------------------
conn(loc(sm, 'NS'), TAPPT, label='ND' + BUS, electrical=True)
mk('master:ground', loc(sm, 'N')[0], loc(sm, 'N')[1] - 1)   # external neutral
if cp is not None:
    conn(loc(cp, 'OUT'), loc(sm, 'conspd'))
conn(loc(sm, 'telect'), loc(ex, 'Vabc'))        # terminal voltage signal -> exciter
conn(loc(sm, 'cfldn'), loc(ex, 'If'))
conn(loc(ex, 'Ef'), loc(sm, 'efldn'))
conn(loc(cr, 'OUT'), loc(ex, 'SP'))

if GOV == 'hy':
    conn(loc(sm, 'speed'), loc(gv, 'w'))
    conn(loc(sm, 'tmeco'), loc(gv, 'Tm0'))
    conn(loc(gv, 'Tm'), loc(sm, 'tmech'))
    conn(loc(cs, 'OUT'), loc(gv, 'SP'))
else:
    conn(loc(sm, 'speed'), loc(gv, 'W'))
    conn(loc(cs, 'OUT'), loc(gv, 'WREF'))

pr.save()
ptools.log('saved')
