"""Digitise the report's target figures from the PDF (Stage 0).

Method
------
* the page is rendered at 300 dpi (render_pages.py);
* axis calibration comes from the PDF **text layer** (exact tick-label centres),
  never from eyeballed pixel positions;
* curves are separated by their exact RGB colour, sampled from the render;
* where a curve is hidden behind another, the column is left empty rather than
  interpolated across the gap.

Every value written carries the page it came from, and the script prints the
residual against the anchor points listed in PLAN.md A3.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
import pymupdf
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "Resources" / "Final Report on the Grid Incident in Spain and Portugal on 28 April 2025.pdf"
PAGES = Path(__file__).with_name("pages")
SC = 300 / 72


def render(page_no: int) -> Image.Image:
    PAGES.mkdir(exist_ok=True)
    f = PAGES / f"pg{page_no:03d}.png"
    if not f.exists():
        doc = pymupdf.open(PDF)
        doc[page_no - 1].get_pixmap(dpi=300).save(f)
        doc.close()
    return Image.open(f).convert("RGB")


def words(page_no: int) -> list[tuple[str, float, float]]:
    doc = pymupdf.open(PDF)
    out = []
    for w in doc[page_no - 1].get_text("words"):
        out.append((w[4], (w[0] + w[2]) / 2 * SC, (w[1] + w[3]) / 2 * SC))
    doc.close()
    return out


def find(ws, text: str, nth: int = 0) -> tuple[float, float]:
    hits = [w for w in ws if w[0] == text]
    if len(hits) <= nth:
        raise SystemExit(f"label {text!r} not found (nth={nth})")
    return hits[nth][1], hits[nth][2]


class Axis:
    def __init__(self, p0: tuple[float, float], p1: tuple[float, float]):
        (x0, v0), (x1, v1) = p0, p1
        self.x0, self.v0 = x0, v0
        self.k = (v1 - v0) / (x1 - x0)

    def at(self, px: float) -> float:
        return self.v0 + (px - self.x0) * self.k


class Trace:
    """One coloured curve."""

    def __init__(self, rgb: str, name: str):
        self.rgb = np.array([int(rgb[i:i + 2], 16) for i in (0, 2, 4)])
        self.name = name


def extract(im: Image.Image, box: tuple[int, int, int, int], traces: list[Trace],
            tol: float = 70.0) -> dict[str, dict[int, float]]:
    x0, y0, x1, y1 = box
    a = np.asarray(im.crop((x0, y0, x1, y1))).astype(int)
    h, w, _ = a.shape
    out: dict[str, dict[int, float]] = {t.name: {} for t in traces}
    prev = {t.name: None for t in traces}
    for col in range(w):
        px = a[:, col, :]
        for t in traces:
            d = np.sqrt(((px - t.rgb) ** 2).sum(axis=1))
            rows = np.where(d < tol)[0]
            if rows.size == 0:
                continue
            # group into contiguous runs, pick the one closest to the previous sample
            runs, run = [], [rows[0]]
            for r in rows[1:]:
                if r - run[-1] <= 2:
                    run.append(r)
                else:
                    runs.append(run); run = [r]
            runs.append(run)
            if prev[t.name] is None:
                run = max(runs, key=len)
            else:
                run = min(runs, key=lambda rr: abs(np.mean(rr) - prev[t.name]))
            y = float(np.mean(run))
            prev[t.name] = y
            out[t.name][x0 + col] = y0 + y
    return out


def resample(cal: dict[str, Axis], raw: dict[str, dict[int, float]], t_axis: Axis,
             step_s: float = 0.25) -> list[dict[str, float]]:
    xs = sorted(set().union(*[set(v) for v in raw.values()]))
    if not xs:
        return []
    t_lo, t_hi = t_axis.at(xs[0]), t_axis.at(xs[-1])
    rows = []
    t = t_lo
    while t <= t_hi + 1e-9:
        px = (t - t_axis.v0) / t_axis.k + t_axis.x0
        rec = {"t_sim_s": round(t, 3)}
        for name, pts in raw.items():
            if not pts:
                continue
            cand = [x for x in pts if abs(x - px) <= 2]
            if cand:
                rec[name] = round(cal[name].at(float(np.mean([pts[x] for x in cand]))), 3)
            else:
                rec[name] = ""
        rows.append(rec)
        t = round(t + step_s, 6)
    return rows
