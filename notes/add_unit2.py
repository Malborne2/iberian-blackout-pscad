"""Convert the source3 at one bus into a synchronous machine + exciter + governor.

Deleted (XML, by position): the source3 and its multimeter.
Created (API):
    sync_machine2   NS -> bus through a node label, POut/QOut signals PSM_/QSM_
    exc_scrx        Vabc *wired electrically to the machine terminal* (as in the example),
                    If <- cfldn, Ef -> efldn, SP <- const 1.0
    hydro_gov       w <- speed, Tm0 <- tmeco, Tm -> tmech, SP <- const 1.0
    voltmeter       named V_Gxx on the bus (keeps the existing V channel working)
    datalabel+pgb   for PSM_Gxx and QSM_Gxx

Usage: python notes/add_unit.py <bus> <x> <y> <MVA> <P0 MW> <H> <buspt x,y> <tag>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools
import mhi.pscad as p

BUS = sys.argv[1]
MX, MY = int(sys.argv[2]), int(sys.argv[3])
SMVA = float(sys.argv[4]); P0 = float(sys.argv[5]); H = float(sys.argv[6])
BUSPT = tuple(int(v) for v in sys.argv[7].split(','))
TAG = sys.argv[8] if len(sys.argv) > 8 else BUS.replace('Bus', 'G')

app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')

def mk(defn, x, y, orient=0, **kw):
    return main.create_component(defn, x, y, orient, **kw)

def ports(c):
    return {k: tuple(v.location) for k, v in c.ports().items()}

def conn(a, b, **kw):
    try:
        r = main.create_connection(a, b, **kw)
        ptools.log('   ok', kw.get('label', ''), '' if r is None else r)
        return r
    except Exception as e:
        ptools.log('   ERR', type(e).__name__, e)
        return None

# ---- machine ---------------------------------------------------------------
sm = mk('master:sync_machine2', MX, MY, 0, Name='SM' + TAG,
        MVA=SMVA, Vbase_LL=400.0, FRE=50.0, H=H, NOM=1.0, MSat=0, MM=1,
        Ra=0.002, Xp=0.15, Xd=1.9, Xd_=0.30, Tdo_=8.0, Xd__=0.20, Tdo__=0.03,
        Xq=1.85, Xq_=0.50, Xq__=0.20,
        P0=P0, Q0=0.0, VT=1.0, Pheta=0.0, T_S2M=0.5,
        Iexc=0, Igov=0, Interface_E=0, Interface_G=0,
        POut='PSM_' + TAG, QOut='QSM_' + TAG)
S = ports(sm)
ptools.log('machine', S)

# ---- exciter ---------------------------------------------------------------
ex = mk('master:exc_scrx', MX - 14, MY - 6, Name='EX' + TAG,
        T1=0.02, Ta=1.5, Tb=1.0, Te=0.02, K=100.0, Emax=5.0, Emin=-5.0,
        Vbase=230.94, Ibase=SMVA / (3 ** 0.5 * 400.0), Rrev=15000,
        IBSF=1, IRef=0, Enab=1, IExst=0)
X = ports(ex)
ptools.log('exciter', X)

# ---- governor --------------------------------------------------------------
gv = mk('master:hydro_gov', MX + 2, MY + 12, Name='GV' + TAG, f=50.0, Enab=1)
G = ports(gv)
ptools.log('governor', G)

# ---- constants -------------------------------------------------------------
cr = mk('master:const', X['SP'][0] - 4, X['SP'][1], Name='VR' + TAG, Value=1.0)
cs = mk('master:const', G['SP'][0] - 4, G['SP'][1] + 4, Name='SR' + TAG, Value=1.0)

# ---- voltmeter (keeps the V_ channel alive) --------------------------------
vm = mk('master:voltmeter', BUSPT[0] + 3, BUSPT[1] + 2, Name='V_' + TAG)
V = ports(vm)
gm = mk('master:ground', V['N2'][0], V['N2'][1] + 1)

# ---- channels for the machine P/Q -----------------------------------------
for sig, units, dy in (('PSM_' + TAG, 'MW', 0), ('QSM_' + TAG, 'Mvar', 3)):
    dl = mk('master:datalabel', 100, 160 + dy, Name=sig)
    pg = mk('master:pgb', 108, 160 + dy, Name=sig, UseSignalName='YES', Units=units)
    conn(dl.port('A').location, pg.port('Signl').location)

# ---- wiring ---------------------------------------------------------------
conn(S['NS'], BUSPT, label='ND' + TAG, electrical=True)
conn(X['Vabc'], S['NS'])              # electrical voltage measurement of the terminal
conn(S['cfldn'], X['If'])
conn(X['Ef'], S['efldn'])
conn(cr.port('OUT').location, X['SP'])
conn(S['speed'], G['w'])
conn(S['tmeco'], G['Tm0'])
conn(G['Tm'], S['tmech'])
conn(cs.port('OUT').location, G['SP'])
conn(V['N1'], (V['N1'][0], BUSPT[1]))
conn(V['N2'], gm.port('A').location)

pr.save()
ptools.log('saved', BUS)
