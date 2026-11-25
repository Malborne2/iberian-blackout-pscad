import json, os
import mhi.pscad as p

BASE = r"C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model"
app = p.connect()
pr = app.project('Spanish_grid_model')

def safe(fn, *a, **k):
    try:
        return fn(*a, **k)
    except Exception as e:
        return f"<<ERR {e}>>"

out = {}
out['name'] = pr.name
out['directory'] = safe(lambda: pr.directory)
out['namespace'] = safe(lambda: pr.namespace) if hasattr(pr, 'namespace') else None
out['parameters'] = safe(lambda: pr.parameters())
out['definitions'] = safe(lambda: pr.definitions())
out['canvases'] = safe(lambda: [c.name for c in pr.canvases()])
out['projects'] = safe(lambda: [x['name'] if isinstance(x, dict) else x.name for x in app.projects()])

print("name", out['name'])
print("dir", out['directory'])
print("canvases", out['canvases'])
print("--- project parameters ---")
for k, v in (out['parameters'] or {}).items():
    print(f"  {k!r}: {v!r}")

with open(os.path.join(BASE, 'notes', 'proj_dump.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=1, default=str)
