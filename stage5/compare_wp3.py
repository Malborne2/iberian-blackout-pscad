"""Compare frequency and aggregate governor response without a new run."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mhi.psout
import numpy as np

work = Path(r'C:\PSCAD_work')
for label, path in [('instrumented', work/'s22/wp3_meter_5s.psout'),
                    ('run16', work/'s21/ib4hv_run16_hvdc_20s.psout')]:
    with mhi.psout.File(str(path)) as file:
        traces = {k: x for x,k in file.run(0).trace_paths()}
        def read(i, q):
            x = traces[f'Root/Main/SyncUnit[{i}]/{q}/0/1']
            return np.asarray(x.domain.data), np.asarray(x.data)
        fig, axes = plt.subplots(2, 1, sharex=True)
        t = read(1, 'Wspd')[0]
        fs = []
        for i in range(1, 6):
            f = read(i, 'Wspd')[1]/(2*np.pi)
            fs.append(f)
            axes[0].plot(t, f, linewidth=.7)
            axes[1].plot(t, read(i, 'DPGOV')[1], linewidth=.7)
        for end in sorted({5, int(t[-1])}):
            w = (t >= end-.5) & (t <= end)
            vals = np.asarray(fs)[:,w]
            print(label, end, 'Hz mean, min, max', vals.mean(), vals.min(), vals.max())
        axes[0].set(ylabel='Frequency [Hz]', ylim=(49.4,50.6))
        axes[0].axhspan(49.98,50.02, alpha=.2)
        axes[1].set(xlabel='Time [s]', ylabel='Governor increment [pu]')
        out = Path('results/stage5')/f's22_wp3_{label}_governor'
        out.mkdir(parents=True, exist_ok=False)
        fig.tight_layout()
        fig.savefig(out/'frequency_governor.png', dpi=150)
        plt.close(fig)
