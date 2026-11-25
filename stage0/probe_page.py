"""Print dominant saturated colours and candidate axis labels on rendered pages."""
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from digitise import words  # noqa: E402

for pg in [int(a) for a in sys.argv[1:]]:
    f = Path(__file__).with_name("pages") / f"pg{pg:03d}.png"
    a = np.asarray(Image.open(f).convert("RGB")).astype(int)
    sat = (a.max(axis=2) - a.min(axis=2)) > 60
    c = Counter(map(tuple, a[sat][::5]))
    print(f"\n=== page {pg} ===")
    for col, n in c.most_common(8):
        print("   #%02X%02X%02X" % col, n)
    ws = words(pg)
    nums = [(w, round(x), round(y)) for w, x, y in ws
            if any(ch.isdigit() for ch in w) and len(w) <= 8]
    print("   numeric labels:", nums[:45])
