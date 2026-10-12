# T25 · 3D versus planar mesh scaling (model study, 2026-10-12)

**Status: PASS for the registered computational criteria (7/7). Model only.** No device was designed, fabricated or measured. The study does not establish any advantage of the project's hardware; it states where an advantage could exist and what measurement would decide it.

- Protocol: `experimentos/t25_escalado_claude/PROTOCOL-T25-r2.json` (amendment of `PROTOCOL-T25.json`).
- Commitments: `resultados/agent/prereg/T25_commitment.json` (commit `e640f9f`) and `resultados/agent/prereg/T25r2_commitment.json` (commit `ff1c449`), both verified on the GitHub server before running.
- Code: `experimentos/t25_escalado_claude/run_t25.py`; kit modules `agentkit/mesh.py`, `agentkit/mzi.py`.
- Output: `resultados/agent/t25_scaling_20261012/results.json`, `fig_t25_scaling.png`, `fig_t25_scaling.pdf`.
- Reproduce (CPU, one thread, about 8 s): `python -B experimentos/t25_escalado_claude/run_t25.py --outdir <new folder>`.

## Amendment (dated, before any result was read)

Attempt 1 crashed while writing `results.json`: a NumPy `int64` from the brute-force path count is not JSON-serializable. No metric was printed or read. The two figure files written before the crash were not opened and are kept unchanged in `resultados/agent/t25_scaling_20261012_attempt1_failed/`. The fix casts two counts to `int`; analysis, seeds, criteria and interpretation rules are unchanged. The amended protocol was committed and published as a new experiment identifier before the rerun.

## 1. Depth of universal meshes

| N | Lower bound N − 1 | Clements (measured) | Triangular (measured) | MZIs N(N − 1)/2 |
|---|---|---|---|---|
| 3 | 2 | 3 | 3 | 3 |
| 4 | 3 | 4 | 5 | 6 |
| 8 | 7 | 8 | 13 | 28 |
| 16 | 15 | 16 | 29 | 120 |

For every N from 3 to 16 the rectangular (Clements-ordered) synthesis has depth N and the triangular synthesis 2N − 3. The largest spectral reconstruction error was 3.8·10⁻¹⁵. The dimension-count bound of guide v2 §39 holds: no mesh of two-mode elements, planar or 3D, can realize every unitary in fewer than N − 1 layers. **Writing in 3D cannot reduce the logical depth of a universal mesh.** Any 3D advantage must come from crossings, density, routing length or structured (non-universal) transforms.

## 2. Crossings of a planar butterfly

The radix-2 butterfly realizes the unitary DFT with (N/2)·log₂N couplers in log₂N stages (factorization error 2.2·10⁻¹⁴ against the normalized DFT, N = 2 to 64). Its couplers join guides i and i + 2ˢ, which are not adjacent in a planar chip. In the layout used here, adjacent swaps (one crossing each) bring partners together before each stage and inverse swaps restore the order afterwards.

| N | Couplers | Total crossings | Worst-path crossings | Break-even crossing loss (dB) |
|---|---|---|---|---|
| 4 | 4 | 2 | 2 | 0.200 |
| 8 | 12 | 16 | 7 | 0.057 |
| 16 | 32 | 88 | 18 | 0.022 |
| 32 | 80 | 416 | 41 | 0.0098 |
| 64 | 192 | 1824 | 88 | 0.0045 |
| 256 | 1024 | 31616 | 374 | 0.0011 |

The total equals N(N − 1 − log₂N)/2 for every N tested (closed form checked), and the worst-path dynamic programme matches brute-force enumeration of all paths for N ≤ 32. The break-even loss is the per-crossing loss at which the worst-path difference between the planar and the 3D butterfly equals 2U, with U = 0.2 dB, a planning value (ASSUMPTION) for the repeatability of an insertion-loss difference between two fiber-coupled chips. **This layout is an upper-bound construction.** A better planar layout could need fewer crossings, which would raise the break-even loss.

## 3. Worst-path loss model

Worst-path insertion loss = stages × stage loss + crossings × crossing loss, plus stages × vertical-transition loss in 3D. Crosstalk is not modeled. Selected rows (stage loss 0.1 dB, vertical transition 0.05 dB per stage; the full grid is in `results.json`):

| N | Crossing loss | Planar Clements | Planar butterfly | 3D butterfly |
|---|---|---|---|---|
| 16 | 0.02 dB | 1.60 dB | 0.76 dB | 0.60 dB |
| 16 | 0.10 dB | 1.60 dB | 2.20 dB | 0.60 dB |
| 64 | 0.02 dB | 6.40 dB | 2.36 dB | 0.90 dB |
| 64 | 0.10 dB | 6.40 dB | 9.40 dB | 0.90 dB |

A planar Clements mesh needs no crossings but has depth N and is universal. The butterfly is not universal: it realizes only transforms of FFT structure (with programmable phases, a subset of dimension much lower than N²). Comparing it with Clements therefore compares different function classes. The comparison is valid only for a task that needs exactly a structured transform such as the DFT.

## 4. Error accumulation (DFT, splitter-angle errors σ = 0.02 rad, 200 realizations)

| N | Correlation | Clements couplers | Butterfly couplers | Clements mean / 5th pct fidelity | Butterfly mean / 5th pct fidelity |
|---|---|---|---|---|---|
| 4 | 0.0 | 12 | 4 | 0.99879 / 0.99766 | 0.99960 / 0.99912 |
| 4 | 0.8 | 12 | 4 | 0.99888 / 0.99623 | 0.99960 / 0.99866 |
| 8 | 0.0 | 56 | 12 | 0.99717 / 0.99575 | 0.99940 / 0.99898 |
| 8 | 0.8 | 56 | 12 | 0.99803 / 0.99386 | 0.99942 / 0.99801 |
| 16 | 0.0 | 240 | 32 | 0.99404 / 0.99226 | 0.99920 / 0.99885 |
| 16 | 0.8 | 240 | 32 | 0.99686 / 0.99110 | 0.99920 / 0.99757 |

With fewer couplers the butterfly accumulates less splitter error. A shared error component barely changes the mean but widens the tail, as in H10b and guide v2 §43. Both meshes are uncalibrated; in-situ recalibration (T27) can recover part of the Clements loss. The 5th percentiles are descriptive statistics of the model, not tolerance bounds for fabricated parts.

## 5. Interpretation under the registered rules

- **I3 (against planar Clements).** The 3D butterfly saves N − log₂N stages: 12 stages at N = 16 and 58 at N = 64 (1.2 dB and 5.8 dB at 0.1 dB per stage), at the cost of universality.
- **I2 (errors).** Reported above; no threshold was registered.
- **I1 (crossings).** It needs the lowest verified per-crossing loss XC for fs-written glass waveguides from T26 (rule R4). It is evaluated in `Docs/CIERRE-20261012/T20-DECISION.md`. At N = 16 the break-even loss is 0.022 dB per crossing.

## 6. Limits

- Ideal transfer algebra; no waveguide geometry, bend radius, mode mismatch or crosstalk.
- The crossing count is for one explicit planar layout and is an upper bound, not a minimum.
- The 3D vertical-transition loss is a parameter grid. Whether 3D fs routing can realize butterfly stages without its own excess loss is untested (T08 and T14).
- U = 0.2 dB is a planning assumption, not a measured repeatability.

## Errata after the adversarial review (T30), 2026-10-13

1. **Depth bound.** With the output phase screen and the redundancy of general U(2) elements, the bound is N − 1 for even N and N for odd N. A cylindrical (3D-only) brick wall reaches local full rank at N − 1, for example 64/64 at depth 7 for N = 8 (`resultados/agent/t30_redteam_20261013/depth_rank.py`). The sentence "three-dimensional writing cannot reduce the logical depth of a universal mesh" is therefore corrected to: **three-dimensional connectivity can save at most one layer.**
2. **Crossing layout.** The layout here is optimal within its family for fixed input and output order. Freeing the output order (the DFT output is permuted anyway) halves the total crossings and gives worst paths of 4, 11, 26 and 57 for N = 8, 16, 32 and 64 (`butterfly_crossings.py`). Any planar layout still needs Θ(N²) crossings.
3. **Vertical transitions.** The grid of 0–0.1 dB per stage is optimistic. The source of the crossing value reports 0.4–0.5 dB per S-bend at R = 50 mm.
4. **Nature of the criteria.** The seven registered criteria are verification gates on the computation. They could not fail on the physics.
