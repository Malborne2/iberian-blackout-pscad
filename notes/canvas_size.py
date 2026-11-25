"""Check whether the canvas size can be enlarged, then find free patches of canvas."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools

app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')
print('size before', main.size)
try:
    main.size = (200, 300)
    print('size after tuple assign', main.size)
except Exception as e:
    print('tuple assign failed:', type(e).__name__, e)
try:
    from mhi.pscad import Size
    main.size = Size(width=200, height=300)
    print('size after Size assign', main.size)
except Exception as e:
    print('Size assign failed:', type(e).__name__, e)
