"""Make the figure set for a stage from the run's own .psout file.

One place for every stage's plots, so a finished stage always leaves the same artefacts:

    results/stage2a_bench/       two `SyncUnit` instances on one stiff bus
    results/stage2b_network/     four synchronous units + France in the 39-bus model

Each stage gets, as separate PNGs plus a 2x2 overview:
    voltage, active power, reactive power, frequency.
Whatever else the gate needed (field voltage, bus angles) is an extra panel.

Every figure is built from the same .psout the numbers were read from, and the means printed
to stdout are the ones quoted in RUNLOG.md. Two things to know when reading the panels:

  * power traces are instantaneous, so they carry the 100 Hz ripple; they are shown with a
    20 ms moving average (the envelope), which is what the gate compares.
  * `SyncUnit[n]` numbering follows PSCAD's own component order, and that order can change
    between builds. The bus each instance belongs to is therefore checked here through
    P/Pmec (unique per Sbase) and printed, never assumed.

Usage:
    python results/make_figures.py stage2a
    python results/make_figures.py stage2b
    python results/make_figures.py all
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import mhi.psout  # noqa: E402

RESULTS = Path(__file__).resolve().parent
F0 = 50.0
OMEGA0 = 2.0 * np.pi * F0          # 314.159 rad/s electrical
STRIDE = 20                        # plot every 20th sample (20 us step -> 0.4 ms)

COLOURS = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e", "#8c564b"]


# --------------------------------------------------------------------------- reading
def moving_mean(y: np.ndarray, samples: int) -> np.ndarray:
    """Centred moving average with edge replication.

    NB: np.convolve(..., mode="same") zero-pads, which drags the ends of a signal that has a
    large DC offset towards zero. Measured: a speed trace that really swings 0.049 rad/s
    reported a 157 rad/s peak-to-peak from that artefact.
    """
    samples = max(1, int(samples))
    if samples == 1 or y.size == 0:
        return y
    kernel = np.ones(samples) / samples
    pad = samples // 2
    padded = np.pad(y, (pad, samples - 1 - pad), mode="edge")
    return np.convolve(padded, kernel, mode="valid")


class Run:
    """Lazy access to one .psout run, cached per channel."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._cache: dict[str, tuple[np.ndarray, np.ndarray]] = {}
        self.dt = 0.0                      # plotting sample interval, set on first read

    def get(self, channel: str) -> tuple[np.ndarray, np.ndarray]:
        if channel not in self._cache:
            with mhi.psout.File(str(self.path)) as f:
                run = f.run(0)
                tr = run.call(channel, sep="/")
                data = np.asarray(tr.data, dtype=float)
                dom = tr.domain
                times = np.asarray(dom.data, dtype=float) if dom is not None else np.arange(len(data), dtype=float)
            t = times[::STRIDE]
            if len(t) > 1:
                self.dt = float(np.median(np.diff(t)))
            self._cache[channel] = (t, data[::STRIDE])
        return self._cache[channel]

    def tail_mean(self, channel: str, span: float = 1.0) -> float:
        t, y = self.get(channel)
        sel = t >= (t[-1] - span)
        return float(np.mean(y[sel])) if sel.any() else float("nan")

    def peak_to_peak(self, channel: str, span: float = 5.0, smooth: float = 0.02) -> float:
        t, y = self.get(channel)
        sel = t >= (t[-1] - span)
        y = moving_mean(y[sel], round(smooth / self.dt)) if smooth else y[sel]
        return float(np.max(y) - np.min(y)) if y.size else float("nan")


def panel(ax, run: Run, series, title, ylabel, *, rel=None, hlines=(), marker=None, smooth=0.0,
          marker_text: str = "exciter released"):
    """One axes: series = [(channel, label, colour_index, scale)]."""
    for ch, label, ci, scale in series:
        t, y = run.get(ch)
        y = y * scale
        if smooth:
            y = moving_mean(y, round(smooth / run.dt))
        if rel is not None:
            y = y - rel
        ax.plot(t, y, color=COLOURS[ci % len(COLOURS)], lw=1.1, label=label)
    for yv, txt in hlines:
        ax.axhline(yv, color="0.55", ls="--", lw=0.8)
        if txt:
            ax.annotate(txt, xy=(0.005, yv), xycoords=("axes fraction", "data"),
                        va="bottom", ha="left", fontsize=7.5, color="0.4")
    if marker is not None:
        ax.axvline(marker, color="0.6", ls=":", lw=1.0)
        ax.annotate(marker_text, xy=(marker, 1), xycoords=("data", "axes fraction"),
                    xytext=(3, -10), textcoords="offset points", fontsize=7.5, color="0.45")
    ax.set_title(title, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="best")
    ax.tick_params(labelsize=8)


def save(fig, out: Path, name: str):
    p = out / name
    fig.tight_layout()
    fig.savefig(p, dpi=130)
    plt.close(fig)
    print("  wrote", p.relative_to(RESULTS.parent))


def overview(draws, out: Path, name: str, suptitle: str, sharex: bool = True):
    fig, axes = plt.subplots(2, 2, figsize=(13, 7.5), sharex=sharex)
    for ax, draw in zip(axes.ravel(), draws):
        draw(ax)
    fig.suptitle(suptitle, fontsize=11)
    save(fig, out, name)


def single(draw, out: Path, name: str, title: str, height: float = 4.2):
    fig, ax = plt.subplots(figsize=(10, height))
    draw(ax)
    ax.set_xlabel("time (s)", fontsize=9)
    ax.set_title(title, fontsize=10)
    save(fig, out, name)


# --------------------------------------------------------------------------- stage 2a
SU1 = r"C:\PSCAD_work\su1.gf81_x86\su1.psout"


def stage2a() -> None:
    """Two SyncUnit instances on a 3000 MVA / 400 kV source (bench `su1`)."""
    out = RESULTS / "stage2a_bench"
    out.mkdir(parents=True, exist_ok=True)
    run = Run(SU1)
    I1, I2 = "Root/Main/SyncUnit[1]", "Root/Main/SyncUnit[2]"
    tags = {I1: "unit A  (Pmec 0.25, H 6 s)", I2: "unit B  (Pmec 0.20, H 3.12 s)"}

    print("stage 2a - bench su1, means over the last second (19-20 s)")
    for k, tag in tags.items():
        p = run.tail_mean(f"{k}/POUT/0/1") * 300
        q = run.tail_mean(f"{k}/QOUT/0/1") * 300
        v = run.tail_mean(f"{k}/VIT/0/1")
        f = run.tail_mean(f"{k}/Wspd/0/1") / OMEGA0 * F0
        e = run.tail_mean(f"{k}/EFD0ch/0/1")
        print(f"  {tag}: V {v:.4f} pu | P {p:6.1f} MW | Q {q:7.1f} Mvar | f {f:9.4f} Hz | EFD {e:.3f}")
    psrc = run.tail_mean("Root/Main/Psrc/0/1") * 3000
    print(f"  source Psrc {psrc:.1f} MW")

    def draw_v(ax):
        panel(ax, run, [(f"{k}/VIT/0/1", tags[k], i, 1.0) for i, k in enumerate(tags)],
              "Terminal voltage", "pu", hlines=[(1.0, "1.0 pu")], marker=0.5)
        for i, k in enumerate(tags):
            ax.axhline(run.tail_mean(f"{k}/VREFO/0/1"), color=COLOURS[i], ls="--", lw=0.7, alpha=0.6)

    def draw_p(ax):
        panel(ax, run, [(f"{k}/POUT/0/1", tags[k], i, 300.0) for i, k in enumerate(tags)],
              "Active power", "MW", marker=0.5, smooth=0.02)

    def draw_q(ax):
        panel(ax, run, [(f"{k}/QOUT/0/1", tags[k], i, 300.0) for i, k in enumerate(tags)],
              "Reactive power", "Mvar", hlines=[(0.0, "")], marker=0.5, smooth=0.02)

    def draw_f(ax):
        panel(ax, run, [(f"{k}/Wspd/0/1", tags[k], i, F0 / OMEGA0) for i, k in enumerate(tags)],
              "Frequency", "Hz", rel=F0, marker=0.5)

    def draw_e(ax):
        panel(ax, run, [(f"{k}/EFD0ch/0/1", tags[k], i, 1.0) for i, k in enumerate(tags)],
              "Field voltage (per unit)", "pu", marker=0.5)

    single(draw_v, out, "01_voltage.png", "su1 bench - terminal voltage (dashed = each unit's own Vref)")
    single(draw_p, out, "02_active_power.png", "su1 bench - active power")
    single(draw_q, out, "03_reactive_power.png", "su1 bench - reactive power")
    single(draw_f, out, "04_frequency.png", "su1 bench - frequency (no governor on the bench)")
    single(draw_e, out, "05_field_voltage.png", "su1 bench - excitation (no collapse, no negative field)")
    overview([draw_v, draw_p, draw_q, draw_f], out, "00_overview.png",
             "Stage 2a - two SyncUnit instances, 3000 MVA / 400 kV source, 20 s run (su1)")


# --------------------------------------------------------------------------- stage 2b
IBERIA3 = r"C:\PSCAD_work\iberia3.gf81_x86\iberia3.psout"
# instance index -> (bus, Sbase MVA, Pmec pu)   [Sbase and Pmec were set on the instance]
BUSES = {1: (30, 6113, 0.1749), 2: (37, 12838, 0.1749), 3: (32, 15292, 0.1749),
         4: (31, 13548, 0.1749), 5: (39, 200000, 0.0210)}


def stage2b() -> None:
    """Four Iberian units + France equivalent in iberia3, 30 s run."""
    out = RESULTS / "stage2b_network"
    out.mkdir(parents=True, exist_ok=True)
    run = Run(IBERIA3)
    tag = {i: f"bus {b}  ({s:,} MVA)" for i, (b, s, _pm) in BUSES.items()}

    print("stage 2b - network iberia3, means over the last second (29-30 s)")
    print("  (instance -> bus is checked by P/Pmec, which is unique per Sbase)")
    for i, (b, s, pm) in BUSES.items():
        p = run.tail_mean(f"Root/Main/SyncUnit[{i}]/POUT/0/1") * s
        q = run.tail_mean(f"Root/Main/SyncUnit[{i}]/QOUT/0/1") * s
        v = run.tail_mean(f"Root/Main/SyncUnit[{i}]/VIT/0/1")
        f = run.tail_mean(f"Root/Main/SyncUnit[{i}]/Wspd/0/1") / OMEGA0 * F0
        pp = run.peak_to_peak(f"Root/Main/SyncUnit[{i}]/Wspd/0/1", span=5.0) / OMEGA0 * F0 * 1000
        print(f"  bus {b:>2}: V {v:.4f} pu | P {p:8.1f} MW | Q {q:8.1f} Mvar | "
              f"f {f:9.4f} Hz | f pp (last 5 s) {pp:6.2f} mHz | P/Pmec {p / (pm * s):.3f}")

    def draw_v(ax):
        panel(ax, run, [(f"Root/Main/SyncUnit[{i}]/VIT/0/1", tag[i], i - 1, 1.0) for i in BUSES],
              "Terminal voltage", "pu", hlines=[(1.0, "1.0 pu")], marker=0.5)

    def draw_p(ax):
        panel(ax, run, [(f"Root/Main/SyncUnit[{i}]/POUT/0/1", tag[i], i - 1, float(s))
                        for i, (b, s, _pm) in BUSES.items()],
              "Active power", "MW", marker=0.5, smooth=0.02)

    def draw_q(ax):
        panel(ax, run, [(f"Root/Main/SyncUnit[{i}]/QOUT/0/1", tag[i], i - 1, float(s))
                        for i, (b, s, _pm) in BUSES.items()],
              "Reactive power", "Mvar", hlines=[(0.0, "")], marker=0.5, smooth=0.02)

    def draw_f(ax):
        panel(ax, run, [(f"Root/Main/SyncUnit[{i}]/Wspd/0/1", tag[i], i - 1, F0 / OMEGA0) for i in BUSES],
              "Frequency deviation", "Hz", rel=F0, marker=0.5)

    def draw_ang(ax):
        series = [(f"Root/Main/Ph{b}/0/1", f"bus {b}", i, 1.0)
                  for i, b in enumerate([31, 32, 33, 34, 35, 36, 37, 38, 39])]
        panel(ax, run, series, "Bus voltage angle (multimeter Ph)", "degrees", marker=0.5)

    single(draw_v, out, "01_terminal_voltage.png", "iberia3 - terminal voltages, Stage 2b, 30 s")
    single(draw_p, out, "02_active_power.png", "iberia3 - active power, Stage 2b, 30 s")
    single(draw_q, out, "03_reactive_power.png", "iberia3 - reactive power, Stage 2b, 30 s")
    single(draw_f, out, "04_frequency.png", "iberia3 - frequency deviation, Stage 2b, 30 s")
    single(draw_ang, out, "05_bus_angles.png", "iberia3 - bus angles, Stage 2b, 30 s", height=4.6)
    overview([draw_v, draw_p, draw_q, draw_f], out, "00_overview.png",
             "Stage 2b - four synchronous units + France equivalent, 30 s run (iberia3)")


# --------------------------------------------------------------------------- stage 3a
CV1 = r"C:\PSCAD_work\cv1.gf81_x86\cv1.psout"
CV1_FSW = 1650.0                   # SVM/carrier frequency set on the bench
CV1_AMP = 0.85                     # modulation index set on the bench (const on Main)


def _fundamental(t: np.ndarray, y: np.ndarray, window=(0.30, 0.36)) -> tuple[float, float, float]:
    """Amplitude (peak), phase (deg) and mean of the 50 Hz component in a window."""
    sel = (t >= window[0]) & (t <= window[1])
    tt, yy = t[sel], y[sel]
    dt = tt[1] - tt[0]
    n = len(yy)
    w = np.hanning(n)
    y0 = yy - yy.mean()
    s = np.fft.rfft(y0 * w)
    f = np.fft.rfftfreq(n, dt)
    lo = np.argmin(abs(f - 30.0))
    hi = np.argmin(abs(f - 70.0))
    k = lo + np.argmax(np.abs(s[lo:hi]))
    amp = 2 * abs(s[k]) / w.sum()
    return amp, float(np.degrees(np.angle(s[k]))), float(yy.mean())


def stage3a() -> None:
    """Stage 3 step (a): 2-level IGBT bridge + ideal DC rail + filter reactor + stiff sources."""
    out = RESULTS / "stage3a_bench"
    out.mkdir(parents=True, exist_ok=True)
    run = Run(CV1)
    ph = ("A", "B", "C")
    vch = {p: f"Root/Main/Vbr{p}/0/1" for p in ph}
    ich = {p: f"Root/Main/Isrc{p}/0/1" for p in ph}

    # raw (undecimated) traces for the zoom panels and the spectrum
    raw: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    with mhi.psout.File(CV1) as f:
        rr = f.run(0)
        for ch in list(vch.values()) + list(ich.values()) + ["Root/Main/Vrail/0/1"]:
            tr = rr.call(ch, sep="/")
            raw[ch] = (np.asarray(tr.domain.data, dtype=float), np.asarray(tr.data, dtype=float))

    t = raw[vch["A"]][0]
    print("stage 3a - converter bench cv1, window 0.30-0.36 s (three fundamental periods)")
    vres = {}
    for p in ph:
        amp, phase, mean = _fundamental(*raw[vch[p]])
        vres[p] = (amp, phase, mean)
        print(f"  Vbr{p}: mean {mean:7.1f} kV | fundamental peak {amp:7.2f} kV | phase {phase:8.1f} deg")

    amps = [vres[p][0] for p in ph]
    spread = 100 * (max(amps) - min(amps)) / np.mean(amps)
    dAB = (vres["B"][1] - vres["A"][1] + 180) % 360 - 180
    dBC = (vres["C"][1] - vres["B"][1] + 180) % 360 - 180
    print(f"  phase spacing A-B {dAB:.1f} deg, B-C {dBC:.1f} deg | amplitude spread {spread:.2f} %")

    _, _, vdc = _fundamental(*raw["Root/Main/Vrail/0/1"])
    expected = CV1_AMP * vdc / 2.0
    print(f"  DC rail {vdc:.1f} kV -> hand value AMP*Vdc/2 = {expected:.2f} kV peak "
          f"(B: {100 * (vres['B'][0] / expected - 1):+.2f} %, C: {100 * (vres['C'][0] / expected - 1):+.2f} %)")
    for p in ph:
        amp, _ph, _m = _fundamental(*raw[ich[p]])
        print(f"  Isrc{p}: fundamental peak {amp * 1000:7.0f} A")

    # spectrum of VbrA
    sel = (t >= 0.30) & (t <= 0.36)
    tt, yy = t[sel], raw[vch["A"]][1][sel]
    n = len(yy)
    w = np.hanning(n)
    spec = np.fft.rfft((yy - yy.mean()) * w)
    freq = np.fft.rfftfreq(n, tt[1] - tt[0])
    amp = 2 * np.abs(spec) / w.sum()
    fund = amp[np.argmin(abs(freq - 50.0))]
    harmonics = freq > 100.0
    thd = 100 * np.sqrt(np.sum(amp[harmonics] ** 2)) / fund
    print(f"  VbrA spectrum: fundamental {fund:.1f} kV, THD (2nd..Nyquist) {thd:.1f} % "
          f"(carrier component peaks near {CV1_FSW:.0f} Hz)")

    zoom = (0.3300, 0.3360)
    tlim = 0.10                 # steady state starts after the source/DC ramp-in
    keep = t >= tlim

    def draw_v(ax):
        for i, p in enumerate(ph):
            ax.plot(t[keep], raw[vch[p]][1][keep], color=COLOURS[i], lw=0.8, label=f"phase {p}")
        ax.axhline(vdc / 2.0, color="0.55", ls="--", lw=0.8)
        ax.annotate("Vdc/2", xy=(0.005, vdc / 2.0), xycoords=("axes fraction", "data"),
                    va="bottom", fontsize=7.5, color="0.4")
        ax.axhline(vdc / 2.0 + expected, color="0.55", ls=":", lw=0.8)
        ax.annotate("Vdc/2 + AMP*Vdc/2", xy=(0.005, vdc / 2.0 + expected),
                    xycoords=("axes fraction", "data"), va="bottom", fontsize=7.5, color="0.4")
        ax.set_title("Bridge terminal voltage, phase to ground", fontsize=10)
        ax.set_ylabel("kV", fontsize=9)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8, loc="lower right")
        ax.tick_params(labelsize=8)

    def draw_vzoom(ax):
        sel2 = (t >= zoom[0]) & (t <= zoom[1])
        for i, p in enumerate(ph):
            ax.plot(t[sel2] * 1000, raw[vch[p]][1][sel2], color=COLOURS[i], lw=1.0, label=f"phase {p}")
        ax.set_title(f"Zoom {zoom[0]*1000:.0f}-{zoom[1]*1000:.0f} ms - switched waveform", fontsize=10)
        ax.set_ylabel("kV", fontsize=9)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8, loc="best")
        ax.tick_params(labelsize=8)

    def draw_i(ax):
        for i, p in enumerate(ph):
            ax.plot(t[keep], raw[ich[p]][1][keep] * 1000, color=COLOURS[i], lw=0.9, label=f"source {p}")
        ax.set_title("Source (grid-side) current", fontsize=10)
        ax.set_ylabel("A", fontsize=9)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8, loc="best")
        ax.tick_params(labelsize=8)

    def draw_dc(ax):
        ax.plot(t[keep], raw["Root/Main/Vrail/0/1"][1][keep], color=COLOURS[3], lw=1.0)
        ax.axhline(650.0, color="0.55", ls="--", lw=0.8)
        ax.annotate("set 650 kV", xy=(0.005, 650.0), xycoords=("axes fraction", "data"),
                    va="bottom", fontsize=7.5, color="0.4")
        ax.set_title("Shared DC rail (ideal DC source)", fontsize=10)
        ax.set_ylabel("kV", fontsize=9)
        ax.grid(alpha=0.3)
        ax.tick_params(labelsize=8)

    def draw_spec(ax):
        m = freq <= 4000.0
        ax.semilogy(freq[m], np.maximum(amp[m], 1e-3), color=COLOURS[0], lw=0.8)
        ax.set_xlabel("frequency (Hz)", fontsize=9)
        ax.set_ylabel("kV (peak)", fontsize=9)
        ax.set_title("VbrA spectrum (0-4 kHz): 50 Hz fundamental + carrier sidebands", fontsize=10)
        ax.grid(alpha=0.3, which="both")
        ax.tick_params(labelsize=8)

    single(draw_v, out, "01_phase_voltage.png",
           "Stage 3a - bridge terminal voltages, 3-phase, 0.85 modulation, 1650 Hz carrier (cv1)")
    single(draw_vzoom, out, "02_switched_waveform_zoom.png",
           "Stage 3a - switched output over 6 ms (interpolation off; see RUNLOG Session 12)")
    single(draw_i, out, "03_phase_current.png",
           "Stage 3a - grid-side currents through the 0.15 pu filter reactor")
    single(draw_dc, out, "04_dc_rail.png",
           "Stage 3a - shared DC rail held by the ideal DC source")
    single(draw_spec, out, "05_spectrum.png", "Stage 3a - harmonic spectrum of phase A voltage")
    overview([draw_v, draw_i, draw_dc, draw_spec], out, "00_overview.png",
             "Stage 3a - 2-level IGBT bridge + ideal DC rail + filter reactor + stiff 3-phase source (cv1)",
             sharex=False)


# --------------------------------------------------------------------------- stage 3b
def stage3b() -> None:
    """Stage 3 step (b): PLL lock and dq decomposition on the converter bench (cv1)."""
    out = RESULTS / "stage3b_pll"
    out.mkdir(parents=True, exist_ok=True)
    run = Run(CV1)
    V_BASE = 326.5986
    I_BASE = 0.612372

    vd = run.tail_mean("Root/Main/VD/0/1", span=0.2)
    vq = run.tail_mean("Root/Main/VQ/0/1", span=0.2)
    idd = run.tail_mean("Root/Main/ID/0/1", span=0.2)
    iq = run.tail_mean("Root/Main/IQ/0/1", span=0.2)
    print("stage 3b - PLL / dq on cv1, means over the last 0.2 s (1.3-1.5 s)")
    print(f"  vd {vd:+.4f} pu | vq {vq:+.4f} pu  (locked when vq -> 0 and vd = |V|)")
    print(f"  id {idd:+.4f} pu | iq {iq:+.4f} pu")
    print(f"  P = {vd*idd:+.4f} pu = {vd*idd*300:+.1f} MW | Q(absorbed) = {-vd*iq:+.4f} pu = {-vd*iq*300:+.1f} Mvar")
    print(f"  hand check: (1 - 0.85*Vdc/2/326.6)/0.15 = {(1 - 0.85*650/2/V_BASE)/0.15:.3f} pu absorbed")

    def draw_v(ax):
        panel(ax, run, [("Root/Main/VD/0/1", "vd (grid d-axis)", 0, 1.0),
                        ("Root/Main/VQ/0/1", "vq (grid q-axis)", 1, 1.0)],
              "PLL-aligned grid voltage", "pu", hlines=[(0.0, ""), (1.0, "1.0 pu")], marker=0.1,
              marker_text="d-axis dq transform on")

    def draw_i(ax):
        panel(ax, run, [("Root/Main/ID/0/1", "id", 0, 1.0), ("Root/Main/IQ/0/1", "iq", 1, 1.0)],
              "dq currents (open loop, fixed modulation)", "pu", hlines=[(0.0, "")], marker=0.1,
              marker_text="d-axis dq transform on")

    def draw_th(ax):
        panel(ax, run, [("Root/Main/THETA_TR/0/1", "PLL angle (wrapped 0..2pi)", 2, 1.0)],
              "PLL angle", "rad", marker=0.1)

    def draw_dc(ax):
        panel(ax, run, [("Root/Main/Vrail/0/1", "DC rail", 3, 1.0)],
              "Shared DC rail", "kV", hlines=[(650.0, "650 kV set")])

    single(draw_v, out, "01_dq_voltage.png",
           "Stage 3b - dq grid voltage: vd = 0.9998, vq = 0.0000 (PLL locked, d aligned to the voltage)")
    single(draw_i, out, "02_dq_current.png",
           "Stage 3b - dq currents with fixed modulation (iq = -1.018 pu = 1.02 pu absorbed)")
    single(draw_th, out, "03_pll_angle.png", "Stage 3b - PLL angle (50.00000 Hz)")
    single(draw_dc, out, "04_dc_rail.png", "Stage 3b - DC rail held at 650 kV")
    overview([draw_v, draw_i, draw_th, draw_dc], out, "00_overview.png",
             "Stage 3b - PLL lock and dq decomposition on the converter bench (cv1)", sharex=False)


# --------------------------------------------------------------------------- stage 3d
def stage3d() -> None:
    """Stage 3 steps (c)/(d): closed-loop dq current control + fixed-PF law (bench `cv1`).

    Run: PSET 0.5 pu (t < 0.5 s) -> 0.1 (0.5..1.0) -> 0.5 (t > 1.0), 1.5 s at a 5 us step.
    Bench: SCR 5 source (Z = 0.2 pu, Z/R = 19), L_f = 0.15 pu, C_f = 0.35 uF/phase,
    Vdc = 800 kV. Every number printed here is the one quoted in RUNLOG Session 16.
    """
    out = RESULTS / "stage3d_loop"
    out.mkdir(parents=True, exist_ok=True)
    run = Run(CV1)
    SBASE, PF = 300.0, 0.985
    KQ = np.tan(np.arccos(PF))

    ch = {k: f"Root/Main/{k}/0/1" for k in ("VD", "VQ", "ID", "IQ", "IsrcA", "VbrA", "VbrC", "VsrcDc")}

    def mean(key, lo, hi):
        t, y = run.get(ch[key])
        s = (t >= lo) & (t <= hi)
        return float(np.mean(y[s]))

    print("stage 3d - closed-loop dq current control, bench cv1 (20 ms means)")
    for lo, hi, pset in ((0.30, 0.48, 0.50), (0.80, 0.98, 0.10), (1.30, 1.50, 0.50)):
        vd, vq = mean("VD", lo, hi), mean("VQ", lo, hi)
        idd, iq = mean("ID", lo, hi), mean("IQ", lo, hi)
        p = vd * idd + vq * iq
        q = vd * iq - vq * idd
        print(f"  {lo:4.2f}-{hi:4.2f} s  PSET {pset:4.2f}: id {idd:+.4f} (ref {pset:+.4f}, "
              f"{100 * (idd / pset - 1):+5.2f} %)  iq {iq:+.4f} (ref {KQ * pset:+.4f}, "
              f"{100 * (iq / (KQ * pset) - 1):+5.2f} %)")
        print(f"                   P {p * SBASE:+7.1f} MW (ref {pset * SBASE:+7.1f})   "
              f"Q {q * SBASE:+7.1f} Mvar (ref {KQ * pset * SBASE:+7.1f})   "
              f"vd {vd:.4f} vq {vq:+.4f}  Vdc {mean('VsrcDc', lo, hi):.1f} kV")

    # step settling on the 20 ms mean
    t, idraw = run.get(ch["ID"])
    dt = t[1] - t[0]
    idm = moving_mean(idraw, round(0.02 / dt))
    for t_step, target in ((0.50, 0.10), (1.00, 0.50)):
        s = (t > t_step) & (t < t_step + 0.45)
        outside = np.where(np.abs(idm[s] - target) > 0.05 * target)[0]
        settled = 1000 * (t[s][outside[-1]] - t_step) if len(outside) else 0.0
        print(f"  step {t_step:.2f} s -> {target:.2f} pu: last sample outside +-5 % at {settled:.1f} ms")

    # THD at the two PSET 0.5 windows, from the raw (undecimated) POI current
    with mhi.psout.File(CV1) as f:
        rr = f.run(0)
        tr = rr.call(ch["IsrcA"], sep="/")
        tr_raw = (np.asarray(tr.domain.data, dtype=float), np.asarray(tr.data, dtype=float))
        trv = rr.call(ch["VbrA"], sep="/")
        vr_raw = (np.asarray(trv.domain.data, dtype=float), np.asarray(trv.data, dtype=float))
    t_raw, i_raw = tr_raw
    for lo, hi in ((0.30, 0.48), (1.30, 1.50)):
        s = (t_raw >= lo) & (t_raw <= hi)
        y = i_raw[s] - i_raw[s].mean()
        w = np.hanning(len(y))
        amp = 2 * np.abs(np.fft.rfft(y * w)) / w.sum()
        freq = np.fft.rfftfreq(len(y), t_raw[1] - t_raw[0])
        fund = amp[np.argmin(abs(freq - 50.0))]
        thd = 100 * np.sqrt(np.sum(amp[(freq > 60) & (freq < 3000)] ** 2)) / fund
        print(f"  POI current {lo}-{hi} s: fundamental {fund * 1000:.1f} A peak, "
              f"THD(60-3000 Hz) {thd:.2f} %  (h5 {1000 * amp[np.argmin(abs(freq - 250))]:.1f} A, "
              f"h7 {1000 * amp[np.argmin(abs(freq - 350))]:.1f} A)")

    t_raw_v, v_raw = vr_raw
    window = (t_raw >= 0.30) & (t_raw <= 0.48)
    yv = v_raw[window] - v_raw[window].mean()
    wv = np.hanning(len(yv))
    amp_v = 2 * np.abs(np.fft.rfft(yv * wv)) / wv.sum()
    freq_v = np.fft.rfftfreq(len(yv), t_raw[1] - t_raw[0])

    def draw_id(ax):
        panel(ax, run, [(ch["ID"], "id", 0, 1.0)], "d-axis current", "pu",
              hlines=[(0.5, "ref 0.50"), (0.1, "ref 0.10")], smooth=0.02)

    def draw_iq(ax):
        panel(ax, run, [(ch["IQ"], "iq", 1, 1.0)], "q-axis current (fixed power factor)",
              "pu", hlines=[(KQ * 0.5, "0.17525 x ref")], smooth=0.02)

    def draw_vdq(ax):
        panel(ax, run, [(ch["VD"], "vd", 0, 1.0), (ch["VQ"], "vq", 1, 1.0)],
              "dq grid voltage (PLL frame)", "pu", smooth=0.002)

    def draw_pq(ax):
        t_, vd = run.get(ch["VD"])
        _, vq = run.get(ch["VQ"])
        _, idd = run.get(ch["ID"])
        _, iq = run.get(ch["IQ"])
        ax.plot(t_, moving_mean(vd * idd + vq * iq, round(0.02 / run.dt)) * SBASE,
                color=COLOURS[2], lw=1.2, label="P (MW)")
        ax.plot(t_, moving_mean(vd * iq - vq * idd, round(0.02 / run.dt)) * SBASE,
                color=COLOURS[3], lw=1.2, label="Q (Mvar, absorbed)")
        ax.axhline(150.0, color="0.55", ls="--", lw=0.8)
        ax.set_title("Active and reactive power (20 ms mean)", fontsize=10)
        ax.set_ylabel("MW / Mvar", fontsize=9)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
        ax.tick_params(labelsize=8)

    def draw_spec(ax):
        m = freq_v <= 3000.0
        ax.semilogy(freq_v[m], np.maximum(amp_v[m], 1e-3), color=COLOURS[0], lw=0.8)
        ax.set_title("VbrA spectrum (0-3 kHz)", fontsize=10)
        ax.set_ylabel("kV (peak)", fontsize=9)
        ax.grid(alpha=0.3, which="both")
        ax.tick_params(labelsize=8)

    zoom = (1.400, 1.440)
    selz = (t_raw >= zoom[0]) & (t_raw <= zoom[1])

    def draw_zoom(ax):
        ax.plot(t_raw[selz] * 1000, v_raw[selz] / 1000.0, color=COLOURS[0], lw=0.7, label="VbrA (MV)")
        ax.plot(t_raw[selz] * 1000, i_raw[selz], color=COLOURS[1], lw=0.9, label="IsrcA (kA)")
        ax.set_title(f"Zoom {zoom[0] * 1000:.0f}-{zoom[1] * 1000:.0f} ms: switched voltage and POI current",
                     fontsize=10)
        ax.set_ylabel("MV / kA", fontsize=9)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
        ax.tick_params(labelsize=8)

    def draw_dc(ax):
        panel(ax, run, [(ch["VsrcDc"], "DC rail", 4, 1.0)], "Shared DC rail", "kV",
              hlines=[(800.0, "800 kV set")], smooth=0.002)

    single(draw_id, out, "01_id_step.png",
           "Stage 3d - d-axis current tracks PSET 0.5 -> 0.1 -> 0.5 pu")
    single(draw_iq, out, "02_iq_fixed_pf.png",
           "Stage 3d - q-axis current follows the fixed-PF law iq = tan(acos(0.985)) id")
    single(draw_pq, out, "03_power.png", "Stage 3d - P and Q at the converter terminals")
    single(draw_vdq, out, "04_dq_voltage.png", "Stage 3d - dq grid voltage (PLL locked)")
    single(draw_zoom, out, "05_switched_waveform.png",
           "Stage 3d - switched output and POI current with the 0.35 uF filter capacitor")
    single(draw_spec, out, "06_voltage_spectrum.png", "Stage 3d - bridge voltage spectrum")
    overview([draw_id, draw_iq, draw_pq, draw_vdq], out, "00_overview.png",
             "Stage 3d - closed-loop dq current control + fixed power factor (cv1, SCR 5)", sharex=True)


# --------------------------------------------------------------------------- main
STAGES = {"stage2a": stage2a, "stage2b": stage2b, "stage3a": stage3a, "stage3b": stage3b,
          "stage3d": stage3d}


def main() -> None:
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, fn in STAGES.items():
        if which in ("all", name):
            fn()
    print("done")


if __name__ == "__main__":
    main()
