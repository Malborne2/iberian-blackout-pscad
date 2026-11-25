"""Cross-check France boundary power using recorded phase waveforms."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mhi.psout
import numpy as np

with mhi.psout.File(r'C:\PSCAD_work\s22\wp3_fr39_5s.psout') as file:
    run = file.run(0)
    fig, axes = plt.subplots(2, 1, sharex=True)
    for end, ax in enumerate(axes, 1):
        def trace(quantity, phase=1):
            return run.call(f'Root/Main/FR{end}{quantity}/0/{phase}', sep='/')

        p = trace('P')
        t = np.asarray(p.domain.data)
        w = (t >= 4.5) & (t < 5)
        raw = np.zeros_like(t)
        for phase in (1, 2, 3):
            v, i = trace('V', phase), trace('I', phase)
            assert np.array_equal(t, v.domain.data) and np.array_equal(t, i.domain.data)
            raw += np.asarray(v.data) * np.asarray(i.data)
        reported = np.asarray(p.data)
        print(f'FR{end}: meter {reported[w].mean():+.2f} MW, phase sum {raw[w].mean():+.2f} MW, '
              f'difference {(reported-raw)[w].mean():+.2f} MW')
        ax.plot(t, reported, label='Meter')
        ax.plot(t, raw, alpha=.6, label='Σ phase v·i')
        ax.axvspan(4.5, 5, alpha=.15)
        ax.set_ylabel(f'FR{end} [MW]')
        ax.legend()
    axes[-1].set_xlabel('Time [s]')
    fig.tight_layout()
    out = Path('results/stage5/s22_wp3_fr39')
    out.mkdir(parents=True, exist_ok=False)
    fig.savefig(out/'phase_power_check.png', dpi=150)
