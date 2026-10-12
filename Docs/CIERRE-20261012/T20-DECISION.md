# T20 · Central claim decision record (2026-10-13)

Decision taken after the four registered kill tests (T24, T25, T26, T27) and before any fabrication or measurement. Advice: JEV, `provenance=jev`, `remote_decision=true` (central claim "delimit", confidence 0.97; next physical test "trench", 0.89; withdraw the energy headline, 0.93; independent adversarial review needed, 0.64). The decision is the agent's, checked against the evidence below.

## Central claim (headline)

> **C-T20-DELIMIT.** For femtosecond-laser-written waveguide meshes in glass with present component performance:
> (a) writing in three dimensions cannot reduce the depth of a universal mesh of two-mode elements below N − 1 layers (the rectangular synthesis reaches N);
> (b) a dense passive 64 × 64 layer at 8 bits and 1 GS/s needs, with the most favorable cited components, about 440 times the energy per multiply–accumulate of a 45 nm digital MAC (2014) and about 6300 times that of a 3 nm INT8 macro (2026), mainly because of mesh loss;
> (c) with the lowest verified crossing loss (≤ 0.01 dB at 80°), a crossing-free three-dimensional butterfly gains at most 0.18 dB on its worst path at N = 16, below a 0.4 dB detectability margin.

- **Scope:** numerical model plus identifier-verified literature. Not a measurement.
- **Evidence:** T25 (`resultados/agent/t25_scaling_20261012/results.json`, audit PASS), T24 (`resultados/agent/t24_energy_20261012/budget.json`, registered negative), T26 (`resultados/agent/t26_sota_20261012/`, audit PASS).
- **Falsifiers:** (a) is a dimension count, so a counterexample would be a mesh of two-mode elements realizing a dense set of U(N) in fewer than N − 1 layers. (b) is falsified by a verified set of component values that gives an optimistic advantage of at least 1 at the registered point, for example a measured per-stage mesh loss low enough that the laser term drops below the digital MAC energy together with converter energies below about 1 pJ per sample at 8 bits. (c) is falsified by a measured loss per fs-written crossing above 0.022 dB at the angles a planar butterfly needs, or by a planar layout with far fewer crossings than N(N − 1 − log₂N)/2.
- **What it does not claim:** that fs-written networks are useless; that no other architecture (free space, wavelength multiplexing, photoelectric multiplication with fan-out) can win; that the bound in (a) is new mathematics (it is a standard dimension count, applied here to the 3D question).

## Rule I1 of T25 (crossings), applied

XC = 0.01 dB per crossing (T26 rule R4; an upper bound at 80°). Break-even at N = 16 is 0.022 dB, and XC < 0.022 dB. The smallest N with worst-path crossings × XC ≥ 2U = 0.4 dB is N = 32 (41 × 0.01 = 0.41 dB), which is ≤ 64. **H-B is therefore retained only for N ≥ 32 and only for structured transforms, not as a headline.** Because XC is an upper bound, the true threshold N may be larger. Crossing-free 3D Fourier circuits were already demonstrated in 2016 (Crespi et al., *Nat. Commun.* 7, 10469), so H-B carries no novelty.

## Status of every candidate hypothesis

| Candidate | Status | Reason |
|---|---|---|
| H-A energy advantage | **WITHDRAWN** (registered negative) | T24: optimistic advantage 1.6·10⁻⁴ (modern) and 2.3·10⁻³ (2014 reference) |
| H-B crossings / 3D routing | secondary, N ≥ 32 only | T25 + T26 (rule I1); precedent of 3D FFT circuits |
| H-C in-situ calibration | supported in model; secondary | T27 PASS at σ = 0.02 rad; fails at 0.05 rad independent errors; calibration of fs meshes is established practice |
| H-D trench guides at 1550 nm | **next decisive physical test** | H1-A (0.3 dB/cm, feasibility) and H1-SOTA (0.06 dB/cm, t = 16 µm) registered with amendment A1 and design study T20D |
| H-E graphics pipeline as computer | not a headline | R1, R2, P1 negative; R3 is representation only |

## Next physical test (registered, not run)

Blind cut-back of HE₁₁ at 1550 nm on trench guides with t = 12 µm (H1-A) and t = 16 µm (H1-SOTA), at least four lengths and at least the number of chips given by the T28 table for the σ observed in a declared pilot. Ideal leakage floors from the vector solver (T20D): 0.0440 dB/cm at 12 µm and 0.0020 dB/cm at 16 µm. The smallest width with leakage ≤ 10 % of 0.06 dB/cm is t_min ≈ 14.6 µm (log-linear interpolation between 14 and 15 µm); by the registered rule the H1-SOTA coupon uses 16 µm. Fabrication partner and authorization pending (T28).

## Effect on the task matrix

T20 becomes **PARTIAL**: the central claim is chosen and supported numerically, while the physical decisive test of the next phase (H1-SOTA) awaits samples. T19 stays without an established original contribution: C-T20-DELIMIT is a delimitation, not a claim of priority.
