"""List the channels of a .psout file without touching PSCAD.

Run: python psout_channels.py <psout path>
"""
import sys

import mhi.psout

path = sys.argv[1]
with mhi.psout.File(path) as f:
    run = f.run(0)
    for trace, p in run.trace_paths():
        print(f"{str(trace):<30} {str(p)}")
