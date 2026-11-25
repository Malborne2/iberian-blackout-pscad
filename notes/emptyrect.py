"""Inspect PSCAD's own empty-rectangle helpers (they know the real occupancy incl. ports)."""
import inspect
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools

app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')
cls = type(main)
for n in ('closest_empty_rect', 'get_empty_rects', 'size', 'bounds'):
    if hasattr(cls, n):
        obj = getattr(cls, n)
        if callable(obj) and not isinstance(obj, property):
            print('==', n, inspect.signature(obj))
            print((inspect.getdoc(obj) or '')[:900])
        else:
            print('==', n, '(property)')

print('--- try closest_empty_rect near Bus30 ---')
for args in [((486, 306), (108, 144)), ((486, 306), 6, 8), ((79, 17), 6, 8)]:
    try:
        print(args, '->', main.closest_empty_rect(*args))
    except Exception as e:
        print(args, 'ERR', type(e).__name__, e)
