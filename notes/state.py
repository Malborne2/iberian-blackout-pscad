"""Report PSCAD state: open projects, canvas size, whether a dialog is up."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools
import mhi.pscad as p

app = p.connect()
print('projects', ptools.names(app))
try:
    pr = app.project('Spanish_grid_model')
    main = pr.canvas('Main')
    print('size', main.size, 'bounds', main.bounds)
    print('dirty', pr.dirty())
except Exception as e:
    print('project not loaded:', type(e).__name__, e)
