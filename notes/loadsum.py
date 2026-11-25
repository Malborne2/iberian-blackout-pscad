"""Sum the fixed_load / reactive_load ratings in the model."""
import re


def num(s, default=0.0):
    if not s:
        return default
    return float(s.split()[0])


s = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()
tot_p = tot_q = 0.0
n = 0
for m in re.finditer(r'<User classid="UserCmp"[^>]*?defn="master:fixed_load"[^>]*>.*?</User>',
                     s, re.S):
    blk = m.group(0)
    po = re.search(r'name="PO" value="([^"]*)"', blk)
    qo = re.search(r'name="QO" value="([^"]*)"', blk)
    sc = re.search(r'name="Scale" value="([^"]*)"', blk)
    nm = re.search(r'name="Name" value="([^"]*)"', blk)
    scale = num(sc.group(1), 1.0) if sc else 1.0
    if po:
        tot_p += num(po.group(1)) * scale
        n += 1
        print('  %-10s PO=%8.2f  scale=%.3f' % (nm.group(1) if nm else '', num(po.group(1)), scale))
    if qo:
        tot_q += num(qo.group(1))
print('fixed loads %d: sum PO %.1f MW/phase -> %.2f GW, QO %.0f Mvar' %
      (n, tot_p, 3 * tot_p / 1000, 3 * tot_q))
rq = 0.0
for m in re.finditer(r'<User classid="UserCmp"[^>]*?defn="master:reactive_load"[^>]*>.*?</User>',
                     s, re.S):
    q = re.search(r'name="S" value="([^"]*)"', m.group(0))
    if q:
        rq += num(q.group(1))
print('reactors: %.0f Mvar (S is the three-phase total)' % rq)
