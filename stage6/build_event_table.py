"""Stage 6 - Case A event ledger from data/events.csv (S22).

Builds the time-ordered, signed cumulative-imbalance staircase that Case A must force, and
checks it against the digitised report curves (data/targets_fig3-7a/b.csv).

Sign convention (report Table 3-1, p.116-135): mw_imbalance > 0 is a *loss of generation* or an
*increase of load* (imbalance up); mw_imbalance < 0 is load shedding / pump disconnection
(imbalance down). Line, tie-line and HVDC-block rows carry no MW and are listed separately.

Outputs
  stage6/event_table.csv            per-event ledger with running cumulative imbalance
  results/stage6/stage6_event_ledger.png
  console table of digitised-vs-ledger residuals

usage: python stage6/build_event_table.py
"""
import csv
import datetime as dt
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
T0 = dt.datetime.combine(dt.date(2025, 4, 28), dt.time(12, 32, 0))


def parse_time(s):
    s = (s or "").strip()
    if not s:
        return None
    s = s.replace("13:33:19.780", "12:33:19.780")   # data/events.csv note for cluster 11
    if ":" in s:
        hh, mm, ss = s.split(":")
        return dt.datetime.combine(T0.date(), dt.time(int(hh), int(mm))) + dt.timedelta(
            seconds=float(ss))
    return T0 + dt.timedelta(seconds=float(s))


def main():
    rows = []
    with open(ROOT / "data" / "events.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            t = parse_time(r["time"])
            mw = (r["mw_imbalance"] or "").strip()
            try:
                mw = float(mw)
            except ValueError:
                mw = 0.0
            rows.append({
                "cluster": r["cluster"].strip(),
                "country": r["country"].strip(),
                "t": t,
                "t_rel": (t - T0).total_seconds() if t else None,
                "type": r["type"].strip(),
                "desc": r["description"].strip(),
                "mw": mw,
            })

    timed = [r for r in rows if r["t_rel"] is not None]
    timed.sort(key=lambda r: r["t_rel"])

    cum = 0.0
    gross = 0.0
    for r in timed:
        # cluster "2a/b" is the report's own 208 MW summary of its 2a/2b detail rows; using both
        # double-counts 208 MW, so the summary row is dropped from both columns (documented).
        if r["cluster"] == "2a/b":
            r["cum"] = cum
            r["gross"] = gross
            continue
        cum += r["mw"]
        if (r["mw"] > 0
                and r["type"].startswith(("Generation loss", "Net load increase",
                                          "Fast downward change"))):
            gross += r["mw"]
        r["cum"] = cum
        r["gross"] = gross

    # ---- self-check against the recorded G0 total (Table 3-2, p.131) ---------------------
    # G0 (`stage0/check_events.py`) compares the *Spain* generation rows inside
    # 12:33:20.000-12:33:25.000 with Table 3-2; the whole-file total is not that number.
    lo = 80.000
    hi = 85.000
    gen = sum(r["mw"] for r in timed
              if lo <= r["t_rel"] <= hi and r["country"] == "ES" and r["mw"] > 0
              and r["type"].startswith(("Generation loss", "Net load disconnection")))
    print(f"rows: {len(rows)}  timed: {len(timed)}")
    print(f"Table 3-2 window (ES, generation, 12:33:20-25): {gen:9.2f} MW   "
          f"(G0 p.131: 7,609.27)")
    print(f"net cumulative imbalance at the last timed event: {timed[-1]['cum']:9.2f} MW "
          f"at t = {timed[-1]['t_rel']:.3f} s")

    # ---- write the ledger ----------------------------------------------------------------
    out = ROOT / "stage6" / "event_table.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["idx", "t_sim_s", "clock", "cluster", "country", "type", "description",
                    "mw_imbalance", "net_imbalance_MW", "gross_generation_loss_MW"])
        for i, r in enumerate(timed, 1):
            w.writerow([i, f"{r['t_rel']:.3f}", r["t"].strftime("%H:%M:%S.%f")[:-3],
                        r["cluster"], r["country"], r["type"], r["desc"],
                        f"{r['mw']:.2f}", f"{r['cum']:.2f}", f"{r['gross']:.2f}"])
    print(f"written: {out.relative_to(ROOT)}")

    # ---- compare with the digitised Fig 3-7 curves ---------------------------------------
    def target_point(path):
        t, c = [], []
        with open(path, newline="", encoding="utf-8") as f:
            rd = csv.reader(f)
            next(rd)
            for row in rd:
                if len(row) < 2:
                    continue
                try:
                    t.append(float(row[0]))
                    c.append(float(row[1]))
                except ValueError:
                    continue
        return np.asarray(t), np.asarray(c)

    ta, ca = target_point(ROOT / "data" / "targets_fig3-7a.csv")
    tb, cb = target_point(ROOT / "data" / "targets_fig3-7b.csv")
    tgt = np.concatenate([ta, tb])
    cm = np.concatenate([ca, cb])

    times = np.array([r["t_rel"] for r in timed])
    cums = np.array([r["gross"] for r in timed])
    # events.csv gives a step function: a digitised sample at t sees every event with t_ev <= t
    led = np.array([cums[times <= t][-1] if (times <= t).any() else 0.0 for t in tgt])

    ok = np.isfinite(tgt) & np.isfinite(cm)
    tgt, cm, led = tgt[ok], cm[ok], led[ok]
    err = led - cm
    print(f"\ndigitised samples: {len(tgt)}   max |gross ledger - Fig 3-7|: {np.max(np.abs(err)):.1f} MW"
          f"   median |error|: {np.median(np.abs(err)):.1f} MW")

    print("\nG7 check window (\\u00b120 % of Fig 3-7 cumulative lost generation):")
    print("  clock      t_sim [s]   Fig 3-7 [MW]   ledger [MW]   error")
    for hh, mm, ss in ((12, 33, 17), (12, 33, 18), (12, 33, 19), (12, 33, 20)):
        t = (dt.datetime.combine(T0.date(), dt.time(hh, mm, ss)) - T0).total_seconds()
        j = int(np.argmin(np.abs(tgt - t)))
        e = led[j] - cm[j]
        band = 0.20 * cm[j]
        print(f"  {hh:02d}:{mm:02d}:{ss:02d}   {tgt[j]:9.3f}   {cm[j]:11.1f}   "
              f"{led[j]:11.1f}   {e:+8.1f}  ({'inside' if abs(e) <= band else 'outside'} "
              f"\\u00b1{band:.1f})")

    # ---- figure --------------------------------------------------------------------------
    outdir = ROOT / "results" / "stage6" / "stage6_event_ledger"
    outdir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.step(times, cums, where="post", lw=1.6, label="events.csv - cumulative lost generation")
    ax.plot(tgt, cm, ".", ms=2.5, alpha=.6, label="Fig 3-7a/b digitised (p.129)")
    ax.set_xlabel("t_sim [s]  (12:32:00 = 0)")
    ax.set_ylabel("cumulative lost generation [MW]")
    ax.set_title("Stage 6 / Case A - event ledger vs report Fig 3-7")
    ax.grid(alpha=.3)
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(outdir / "stage6_event_ledger.png", dpi=150)
    print(f"figure: {outdir.relative_to(ROOT)}/stage6_event_ledger.png")


if __name__ == "__main__":
    main()
