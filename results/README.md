# Figures — one directory per stage or major run

Every gate in `PLAN.md` (rule 7, procedure **F4**) is signed off only when its figure set exists
here. All figures are generated from the run's own `.psout`, so they show exactly what the gate
table in `RUNLOG.md` measured.

Regenerate everything:

```
python results\make_figures.py all
python results\make_figures.py stage2a      # one stage
```

The generator prints the means it plots; if a printed number and the `RUNLOG.md` table disagree,
the table is what needs fixing, not the plot.

## Contents

| directory | run | what it shows |
| --- | --- | --- |
| `stage2a_bench\` | `C:\PSCAD_work\su1` — two `SyncUnit` instances on a 3000 MVA / 400 kV source, 20 s | terminal voltage vs each unit's own Vref, P and Q per unit (73.7 / 58.9 MW), frequency (no governor on the bench), field voltage |
| `stage2b_network\` | `C:\PSCAD_work\iberia3` — four units + France equivalent in the 39-bus model, 30 s | terminal voltages, P, Q and frequency of the five machines, and the bus angles from the multimeters |
| `stage2c_governor_bench\` | `C:\PSCAD_work\su2` (`stage2\su2_governor_island.pscx`) — island, two `SyncUnit`s with governor (Kgov 20 / 0), +13.3 MW at 10 s, 25 s | V, P, Q, island frequency vs the droop-law line. Script `stage2\fig_stage2c.py bench` |
| `stage2c_governor_network\` | `C:\PSCAD_work\iberia4` (`stage2\iberia4_gov.pscx`) — network with governors, 40 s, vs the 20 s run without | machine frequencies and governor outputs. Script `stage2\fig_stage2c.py network` |
| `stage3h_module\` | `C:\PSCAD_work\rp1` (`stage3\s17\rp1_stage3h.pscx`) — two `RES_Plant` modules on one 800 kV rail, SCR 5, 1.5 s | POI voltage, P, Q (absorbing PF), PLL frequency, trip flags (relay 0.2 s, forced trip), shared-rail circulating current. Script `stage3\s17\fig_stage3h.py` |
| `stage3i_network_b33\` | `C:\PSCAD_work\iberia4` (`stage3\s17\iberia4_b33.pscx`) — bus 33 ideal source replaced by Granada + temporary bulk-33 plant, 20 s at 5 µs | bus-33 and machine voltages, plant P/Q, PLL and machine frequency. Script `stage3\s17\fig_stage3i.py` |

Each directory carries `00_overview.png` (the four mandatory panels: voltage, active power, reactive
power, frequency) plus the individual panels.

## Reading the panels

* Active and reactive power are **instantaneous** traces; they are plotted with a 20 ms moving
  average so the 100 Hz ripple does not hide the envelope.
* The dotted vertical line at 0.5 s is the exciter release (`Tstart`).
* Dashed horizontal lines in the voltage panel are each unit's own `VREFO` set point.
* `SyncUnit[n]` is PSCAD's component order, which can change between builds — the bus each instance
  belongs to is printed by the generator (checked through `P/Pmec`) and written into the legend.

Stages 4 onwards must additionally overlay the digitised report targets (`data\targets_*.csv`).
