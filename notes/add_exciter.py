"""Add an IEEE SCRX exciter to one machine and drop its fixed field const.

exc_scrx: Vabc (Vt in, electrical), If (in), Ef (out), SP (Vref in), Exst (unused).
The exciter is placed left of the machine; Vabc is wired to the machine terminal (NS).

Usage: python notes/add_exciter.py <TAG> <machine x> <machine y>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools
import mhi.pscad as p

TAG = sys.argv[1]
MX = int(sys.argv[2]); MY = int(sys.argv[3])
SMVA = float(sys.argv[4]) if len(sys.argv) > 4 else 1130.0

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

sm = []
for c in main.components():
    try:
        if str(c.parameters().get('Name', '')) == 'SM' + TAG:
            sm.append(c)
    except Exception:
        pass
ptools.log('machine found', len(sm))
mx = sm[0]
S = {k: tuple(v.location) for k, v in mx.ports().items()}

ex = mk('master:exc_scrx', MX - 12, MY, Name='EX' + TAG,
        T1=0.02, Ta=1.5, Tb=1.0, Te=0.02, K=100.0, Emax=5.0, Emin=-5.0,
        Vbase=230.94, Ibase=SMVA / (3 ** 0.5 * 400.0), Rrev=15000,
        IBSF=1, IRef=0, Enab=1, IExst=0)
X = ports(ex)
cr = mk('master:const', X['SP'][0] - 4, X['SP'][1], Name='RV' + TAG, Value=1.0)
CR = ports(cr)
ptools.log('exciter', X)

ok = [conn(X['Vabc'], S['telect']),        # telect is the 1-dim terminal-voltage port
      conn(S['cfldn'], X['If']),
      conn(X['Ef'], S['efldn']),
      conn(CR['OUT'], X['SP'])]
ptools.log('wired', ok)
pr.save()
ptools.log('saved exciter', TAG)
