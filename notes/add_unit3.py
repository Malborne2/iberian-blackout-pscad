"""Convert the source3 at one bus into a synchronous machine + exciter + governor.

No node labels: the machine is placed just above its bus and the stator is wired with a
plain wire (the pattern the shipped examples use).  The machine publishes its P/Q under the
old channel names (P_Gxx / Q_Gxx) so the existing 30-channel set keeps working; the pgb
scale is corrected in the XML afterwards (pu of SMVA -> pu of 100 MVA).

Usage: python notes/add_unit3.py <bus> <x> <y> <MVA> <P0 MW> <H>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools
import mhi.pscad as p

BUS = sys.argv[1]
MX, MY = int(sys.argv[2]), int(sys.argv[3])
SMVA = float(sys.argv[4]); P0 = float(sys.argv[5]); H = float(sys.argv[6])
BUSY = int(sys.argv[7]) if len(sys.argv) > 7 else MY + 7
TAG = BUS.replace('Bus', 'G')

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

sm = mk('master:sync_machine2', MX, MY, 0, Name='SM' + TAG,
        MVA=SMVA, Vbase_LL=400.0, FRE=50.0, H=H, NOM=1.0, MSat=0, MM=1,
        Ra=0.002, Xp=0.15, Xd=1.9, Xd_=0.30, Tdo_=8.0, Xd__=0.20, Tdo__=0.03,
        Xq=1.85, Xq_=0.50, Xq__=0.20,
        P0=P0, Q0=0.0, VT=1.0, Pheta=0.0, T_S2M=0.5,
        Iexc=0, Igov=0, Interface_E=0, Interface_G=0,
        POut='P_' + TAG, QOut='Q_' + TAG)
S = ports(sm)
ptools.log('machine', S)

ex = mk('master:exc_scrx', MX - 14, MY - 6, Name='EX' + TAG,
        T1=0.02, Ta=1.5, Tb=1.0, Te=0.02, K=100.0, Emax=5.0, Emin=-5.0,
        Vbase=230.94, Ibase=SMVA / (3 ** 0.5 * 400.0), Rrev=15000,
        IBSF=1, IRef=0, Enab=1, IExst=0)
X = ports(ex)
ptools.log('exciter', X)

gv = mk('master:hydro_gov', MX + 2, MY + 12, Name='GV' + TAG, f=50.0, Enab=1)
G = ports(gv)
ptools.log('governor', G)

cr = mk('master:const', X['SP'][0] - 4, X['SP'][1], Name='VR' + TAG, Value=1.0)
cs = mk('master:const', G['SP'][0] - 4, G['SP'][1] + 4, Name='SR' + TAG, Value=1.0)
CR = ports(cr)
CS = ports(cs)

vm = mk('master:voltmeter', MX + 6, MY + 4, Name='V_' + TAG)
V = ports(vm)
gm = mk('master:ground', V['N2'][0], V['N2'][1] + 1)
GM = ports(gm)

# ---- wiring ---------------------------------------------------------------
conn(S['NS'], (S['NS'][0], BUSY))          # stator down to the bus line
conn(X['Vabc'], S['NS'])
conn(S['cfldn'], X['If'])
conn(X['Ef'], S['efldn'])
conn(CR['OUT'], X['SP'])
conn(S['speed'], G['w'])
conn(S['tmeco'], G['Tm0'])
conn(G['Tm'], S['tmech'])
conn(CS['OUT'], G['SP'])
conn(V['N1'], (V['N1'][0], BUSY))
conn(V['N2'], GM['A'])

pr.save()
ptools.log('saved', BUS, 'machine at', (MX, MY), 'stator', S['NS'])
