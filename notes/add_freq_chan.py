"""Add a frequency channel (from a machine's speed) and a bus-voltage channel.

Uses Port objects for the signal connection - passing coordinates left the pgb floating.

Usage: python notes/add_freq_chan.py <machine Name> <channel name> [scale]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools

MACH = sys.argv[1]
NAME = sys.argv[2]
SCALE = float(sys.argv[3]) if len(sys.argv) > 3 else 50.0

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
sp = tuple(sm.ports()['speed'].location)
ptools.log('speed port', sp)

pg = main.create_component('master:pgb', sp[0], sp[1] + 3, Name=NAME, Units='Hz',
                           Scale=SCALE, Min=45.0, Max=55.0)
try:
    main.create_connection(sm.port('speed'), pg.port('Signl'))
    ptools.log('connected via port objects')
except Exception as e:
    ptools.log('ERR', type(e).__name__, e)
pr.save()
ptools.log('saved', NAME)
