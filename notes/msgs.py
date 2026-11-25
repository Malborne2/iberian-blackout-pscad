"""Print the project's build/load messages (errors first)."""
import mhi.pscad as p

app = p.connect()
pr = app.project('Spanish_grid_model')
msgs = pr.messages()
print('total', len(msgs))
errs = [m for m in msgs if str(m.status).lower().startswith('err')]
print('errors', len(errs))
for m in errs[:60]:
    print('---', m.name, '|', m.scope, '|', m.status)
    print(m.text)
print('=== warnings (first 20) ===')
ws = [m for m in msgs if 'warn' in str(m.status).lower()]
print('warnings', len(ws))
for m in ws[:20]:
    print('---', m.name, '|', m.status)
    print(m.text[:300])
