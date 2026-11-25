"""Create the missing field const for SMG31 at a known position and wire it by coordinates."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools

app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')
c = main.create_component('master:const', 21, 153, Name='EFG31', Value=1.05)
ptools.log('const ports', {k: tuple(v.location) for k, v in c.ports().items()})
try:
    main.create_wire((23, 153), (23, 156))
    ptools.log('wired 23,153 -> 23,156')
except Exception as e:
    ptools.log('ERR', type(e).__name__, e)
pr.save()
ptools.log('saved')
