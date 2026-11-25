# Mini-plan — `Qmode = 2` (grid-forming converter), WP6 item 5

Status: design approved for implementation; interface parameter added in S21 §49, control law next.

## 1. Why

All 18 plants are today **grid-following** (`Qmode = 0`): a SRF-PLL supplies `THETA`, a dq current loop
tracks `IDREF`/`IQREF` from the power set-point, and the converter is a current source behind the filter. The
report's mitigation **M11** (grid-forming / synthetic inertia) and Scenario O need a converter that can hold
voltage and frequency on its own — i.e. a voltage source behind an impedance, synchronised by the power it
delivers rather than by a PLL.

## 2. What is modelled (droop-based grid-forming, minimal and testable)

State: internal angle `THETA_GF` and voltage magnitude `Vgf`.

```
P_meas = VD*ID + VQ*IQ                     (module already exports VD, VQ, ID, IQ)
Q_meas = VD*IQ - VQ*ID
omega  = W0 + Kp*(Pref - P_meas) + Kq*(Vset - VDF)          [rad/s]      (P-f droop + V-Q droop)
THETA_GF = integral(omega dt), clamped to [0, 2*pi)          [rad]
id_ref = PI(Vd_ref - VD)   ,  Vd_ref = Vset
iq_ref = PI(Vq_ref - VQ)   ,  Vq_ref = 0                     (voltage loop, limits +/-Imax)
```

The existing inner current loop, filter (`Lf`, `Cf`, `Rf`), gate blocking, overvoltage relay, sub-block
staging, `RampLim` and `MeasSide` are **reused unchanged** — only the source of `THETA` and of
`IDREF`/`IQREF` changes.

Selection is by the published parameter `Qmode` (0 = PLL + power loop, 2 = grid-forming), implemented with the
same constant-carrier trick already proven for `MeasSide`/`Share_k`:
`const 1.0 -> hardlimit(UL = Qmode, LL = -1) -> QM`, then
`THETA = THETA_PLL + QM*(THETA_GF - THETA_PLL)` and the same for the two current references, so `Qmode = 0`
is bit-identical to today's model (that equality is the first gate).

## 3. Parameters (published, with defaults that reproduce today)

| name | meaning | default |
| --- | --- | --- |
| `Qmode` | 0 = grid-following, 2 = grid-forming | 0 |
| `Kp_gf` | P-f droop gain [rad/s per pu] | 0.05 |
| `Kq_gf` | V-Q droop gain [pu/pu] | 5.0 |
| `Tf_gf` | measurement filter on P/Q [s] | 0.02 |
| `Vgf0` | initial internal angle source (PLL at t = 0, for a bumpless start) | — |

## 4. Gate (bench first, then network)

1. **Equality gate (no run beyond the standard check):** `Qmode = 0` reproduces the accepted baseline exactly
   (plant 13,940.6 MW, machines 15,333.4 MW, HVDC −1,000.6 MW). Any difference means the selector is not
   transparent.
2. **Voltage-step gate (bench, per PLAN.md):** ±5 % step on the AC source with the plant in `Qmode = 2`; the
   reactive output must follow the droop within **2 %** of `Kq_gf * dV` and settle in < 0.5 s.
3. **Frequency-step gate (bench):** ±0.2 Hz step; the plant must inject `Kp_gf`-proportional power for a
   sustained time (synthetic inertia), without PLL loss of lock (there is no PLL in this mode).
4. **Network smoke test:** one plant in `Qmode = 2`, 6 s, no trip, baseline within 1 % — then two plants, and
   only then the cluster cases (Case B) that need it.

## 5. Risks and how they are contained

| risk | containment |
| --- | --- |
| the module's `THETA` feeds the *modulator* and both dq transforms, so a wrong selector corrupts everything | implement the selector last, after the GF loop runs standalone; keep `Qmode = 0` bit-identical as gate 1 |
| integrator wind-up / angle offset at t = 0 | initialise `THETA_GF` from the PLL angle at `Tstart` (the module already arms at 0.5 s) |
| the droop loop needs P/Q *measured*, which the module only exports as channels | they are already labels (`VD`, `VQ`, `ID`, `IQ`), so no new measurement chain |
| more blocks on a nearly full region | the definition canvas is 800x800 and rows 100+ are free (used by `MeasSide`/chains); place GF blocks at y >= 200 |

## 6. Implementation order (each step a build, not a rewrite)

1. publish `Qmode`, `Kp_gf`, `Kq_gf`, `Tf_gf` (defaults reproduce today) — **done in S21 §49**;
2. P/Q measurement and the droop integrator at rows 200+ (`THETA_GF`), not connected;
3. voltage loop producing `id_ref`/`iq_ref` (GF) at rows 220+;
4. the three-selector switch on `THETA`, `IDREF`, `IQREF` driven by `QM`;
5. gates 1-4 above.
