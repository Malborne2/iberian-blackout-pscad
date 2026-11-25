"""Choose, for every generator bus, a 7x9 slot whose stator terminal x lies INSIDE the bus
span, so the stator lead is a single vertical segment (no run along a bus row)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools

# bus, x0, x1 (bus span in grid), y
BUSES = [('Bus30', 25, 29, 17), ('Bus31', 32, 37, 83), ('Bus32', 41, 45, 94),
         ('Bus33', 56, 60, 89), ('Bus34', 49, 53, 89), ('Bus35', 62, 66, 43),
         ('Bus36', 62, 67, 81), ('Bus37', 30, 34, 10), ('Bus38', 66, 71, 31),
         ('Bus39', 21, 27, 55)]

app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')

best = {}
for name, x0, x1, by in BUSES:
    cand = None
    for nsx in range(x0 + 1, x1):
        for w, h in ((7, 9), (7, 7), (5, 7)):
            try:
                r = main.closest_empty_rect(w, h, (nsx, by))
            except Exception:
                continue
            if r is None:
                continue
            mx = r.left + 3
            if abs(mx + 3 - nsx) > 1:
                continue
            gap = abs(r.top + 4 - by)
            if cand is None or gap < cand[0]:
                cand = (gap, mx, r.top + 4, (r.left, r.top, r.right, r.bottom), nsx)
            break
    best[name] = cand
    if cand:
        print('%-6s gap %2d  machine (%d,%d)  rect %s  NS.x %d (bus %d..%d)'
              % (name, cand[0], cand[1], cand[2], cand[3], cand[1] + 3, x0, x1))
    else:
        print('%-6s NO ALIGNED SLOT' % name)
