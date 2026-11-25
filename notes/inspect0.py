import mhi.pscad as p
app = p.connect()
pr = app.project('ieee_39_bus')
print('project', pr)
print('main attr', pr.main, type(pr.main))
print('current_canvas', pr.current_canvas, type(pr.current_canvas))
c = pr.current_canvas
print([x for x in dir(c) if not x.startswith('_')])
