"""Create a missing field-voltage constant for one machine and wire it (port objects)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools

MACH = sys.argv[1]
NAME = sys.argv[2]
VAL = float(sys.argv[3])

app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')

sm = None
for c in main.components():
    try:
        if str(c.parameters().get('Name', '')) == MACH:
            sm = c
            break
    except Exception:
        pass
ptools.log('machine', sm is not None)
ef = tuple(sm.ports()['efldn'].location)
ptools.log('efldn', ef)

c = main.create_component('master:const', ef[0] - 3, ef[1] - 3, Name=NAME, Value=VAL)
try:
    main.create_connection(c.port('OUT'), sm.port('efldn'))
    ptools.log('wired')
except Exception as e:
    ptools.log('ERR', type(e).__name__, e)
pr.save()
ptools.log('saved', NAME)
