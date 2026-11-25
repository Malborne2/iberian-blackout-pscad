"""Place a synchronous machine NEXT TO its generator bus and wire it directly.

The slot comes from PSCAD's own `closest_empty_rect` (it knows the real occupancy), so the
machine body never contains another component's port.  Layout inside an 11 x 15 rect:

    machine at (left+5, top+7)          body   (left+2..left+8, top+3..top+11)
    efldn  (left+4, top+3)   <- const at (left+2, top+1)
    tmech  (left+6, top+11)  <- const at (left+4, top+13)
    NS     (left+8, top+7)   -> wire -> (left+8, bus_y) -> (bus_x, bus_y)
    voltmeter (left+9, top+5), N1 -> NS, N2 -> ground

Usage: python notes/unit_at_bus.py <bus> <txml> <tyml> <bx> <by> <MVA> <P0> <H> <tag>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools

BUS = sys.argv[1]
SX, SY = int(sys.argv[2]), int(sys.argv[3])
BX, BY = int(sys.argv[4]), int(sys.argv[5])
SMVA = float(sys.argv[6]); P0 = float(sys.argv[7]); H = float(sys.argv[8])
TAG = sys.argv[9] if len(sys.argv) > 9 else BUS.replace('Bus', 'G')

app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')

USED = getattr(main, '_used_rects', None)
rect = None
for w, h in ((11, 15), (11, 17), (13, 15), (13, 17), (11, 19), (15, 15)):
    r = main.closest_empty_rect(w, h, (BX, BY))
    if r is None:
        continue
    key = (r.left, r.top)
    if not hasattr(main, '_used_rects'):
        main._used_rects = set()
    if key in main._used_rects:
        continue
    main._used_rects.add(key)
    rect = r
    break
if rect is None:
    ptools.log(BUS, 'NO SLOT')
    raise SystemExit(1)

L, T = rect.left, rect.top
ptools.log(BUS, 'rect', (rect.left, rect.top, rect.right, rect.bottom))

def mk(defn, x, y, orient=0, **kw):
    return main.create_component(defn, x, y, orient, **kw)

def wire(*pts):
    try:
        main.create_wire(*pts)
        return True
    except Exception as e:
        ptools.log('   wire ERR', pts, type(e).__name__, e)
        return False

mx, my = L + 5, T + 7
sm = mk('master:sync_machine2', mx, my, 0, Name='SM' + TAG,
        MVA=SMVA, Vbase_LL=400.0, FRE=50.0, H=H, NOM=1.0, MSat=0, MM=1,
        Ra=0.002, Xp=0.10, Xd=0.45, Xd_=0.25, Tdo_=8.0, Xd__=0.15, Tdo__=0.03,
        Xq=0.43, Xq_=0.22, Xq__=0.14,
        P0=P0, Q0=0.0, VT=1.0, Pheta=0.0, T_S2M=0.5,
        Iexc=0, Igov=0, Interface_E=0, Interface_G=0,
        POut='P_' + TAG, QOut='Q_' + TAG)

ef = mk('master:const', L + 2, T + 1, Name='EF' + TAG, Value=1.05)
tm = mk('master:const', L + 4, T + 13, Name='TM' + TAG, Value=P0 / SMVA)
# voltmeter to the RIGHT of the stator terminal, so its N1 wire never passes N2 (ground)
vm = mk('master:voltmeter', L + 9, T + 7, Name='V_' + TAG)
gm = mk('master:ground', L + 9, T + 8)      # port lands exactly on N2

ok = []
ok.append(wire((L + 4, T + 1), (L + 4, T + 3)))                      # efldn
ok.append(wire((L + 6, T + 13), (L + 6, T + 11)))                    # tmech
ok.append(wire((L + 9, T + 7), (L + 8, T + 7)))                      # voltmeter N1 -> NS
ok.append(wire((L + 8, T + 7), (L + 8, BY), (BX, BY)))               # stator -> bus

ptools.log(BUS, 'machine at', (mx, my), 'NS', (L + 8, T + 7), 'ok', ok)
pr.save()
ptools.log('saved', BUS)
