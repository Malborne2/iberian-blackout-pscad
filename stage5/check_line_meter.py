"""Read paired-end metering evidence from a single archived PSCAD run."""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mhi.psout
import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('psout', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--start', type=float, default=0.4)
    args = parser.parse_args()
    with mhi.psout.File(str(args.psout)) as file:
        run = file.run(0)
        signals = {}
        for end in (1, 2):
            for quantity in ('P', 'Q', 'I', 'V', 'RMS'):
                key = f'LM{end}{quantity}'
                trace = run.call(f'Root/Main/{key}/0/1', sep='/')
                signals[key] = (np.array(trace.domain.data), np.array(trace.data))
    t = signals['LM1P'][0]
    w = (t >= args.start) & (t < t[-1])
    assert np.any(w)
    assert all(np.array_equal(t, x) and np.all(np.isfinite(y)) for x, y in signals.values())
    a, b = (signals[key][1] for key in ('LM1P', 'LM2P'))
    print(f'10 finite channels; end {t[-1]:.3f} s; window [{args.start}, {t[-1]}) s')
    print(f'Inward power: {a[w].mean():+.2f}, {b[w].mean():+.2f} MW; sum {(a+b)[w].mean():+.2f} MW')
    print('Opposite reported signs:', a[w].mean() * b[w].mean() < 0)
    print('Independent phase-power check remains open: these paths select one component, not all three phases.')
    args.output.mkdir(parents=True, exist_ok=False)
    fig, axes = plt.subplots(2, 1, sharex=True)
    for key, y in [('End 1', a), ('End 2', b), ('Sum', a+b)]:
        axes[0].plot(t, y, label=key)
    for end in (1, 2):
        axes[1].plot(t, signals[f'LM{end}RMS'][1], label=f'End {end}')
    for ax in axes:
        ax.axvspan(args.start, t[-1], alpha=0.12)
        ax.legend()
    axes[0].set_ylabel('Inward P [MW]')
    axes[1].set(xlabel='Time [s]', ylabel='RMS voltage [kV]')
    fig.tight_layout()
    fig.savefig(args.output / 'pilot_meters.png', dpi=150)


if __name__ == '__main__':
    main()
