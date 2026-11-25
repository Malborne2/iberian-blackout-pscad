import time
import mhi.pscad as p

app = p.connect()
pr = app.project('Spanish_grid_model')
ps = pr.parameters()
print('before', ps['PlotType'], ps['time_duration'], ps['sample_step'])
pr.parameters(PlotType='PSOUT', time_duration=2.0, sample_step=500.0)
ps = pr.parameters()
print('after ', ps['PlotType'], ps['time_duration'], ps['sample_step'])
pr.save()
time.sleep(1)
