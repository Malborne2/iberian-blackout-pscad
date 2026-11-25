import mhi.pscad as p

app = p.connect()
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')

for orient in range(8):
    c = main.create_component('master:xfmr-3p2w', 20 + orient * 6, 20, orient=orient,
                              Name=f'TX{orient}', Tmva=5000.0, f=50.0, V1=400.0, V2=128.155,
                              Xl=0.12, YD1=0, YD2=0, Lead=1, Tap=0, Ideal=0)
    b = c.bounds
    print(orient, 'bounds', (b.left, b.top, b.right, b.bottom),
          {k: (v.x, v.y) for k, v in c.ports().items()})
    c.delete()
