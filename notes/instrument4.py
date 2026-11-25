"""Recreate the 30 output channels: datalabel (signal source) -> pgb (channel)."""
import time
import mhi.pscad as p

def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)

app = p.connect()
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')

# --- channel list from the multimeters -------------------------------------
comps = main.components()
meters = [c for c in comps if 'multimeter' in str(getattr(c, 'definition', ''))]
meters.sort(key=lambda c: c.parameters().get('P', ''))
names = []
for c in meters:
    ps = c.parameters()
    for k in ('P', 'Q', 'Vrms'):
        v = str(ps.get(k, ''))
        if v and v.upper() not in ('NONE', ''):
            names.append((v, k))
log('channels', len(names))

# --- remove old channels ---------------------------------------------------
old = [c for c in comps if str(getattr(c, 'definition', '')) == 'Definition[master:pgb]'
       or str(getattr(c, 'definition', '')) == 'Definition[master:datalabel]']
log('removing old blocks', len(old))
for c in old:
    try:
        c.delete()
    except Exception as e:
        log('del err', e)

UNITS = {'P': 'MW', 'Q': 'Mvar', 'Vrms': 'kV'}
made = 0
for i, (name, kind) in enumerate(names):
    y = 2500 - 60 * i
    dl = main.create_component('master:datalabel', 1500, y, Name=name)
    pg = main.create_component('master:pgb', 1580, y, Name=name, UseSignalName='YES',
                               enab='YES', Display='YES', Units=UNITS[kind],
                               Scale=1.0, Min=-3.0, Max=3.0)
    try:
        main.create_connection(dl.port('A'), pg.port('Signl'))
        made += 1
    except Exception as e:
        log('conn err', name, e)
    if i % 5 == 0:
        log('...', i, name)

log('channels wired', made)
pr.save()
time.sleep(1)
log('saved')
