# T30 · Response to the adversarial review (2026-10-13)

The review (`T30-REDTEAM-REPORT.md`, scripts in `resultados/agent/t30_redteam_20261013/`) was done by a separate agent with read-only access that did not write any of the material. Its recomputations were rerun by the author agent before any change. They reproduce the T24 budget to a relative difference of 10⁻¹⁶, the crossing counts, the free-output-order layouts and the Jacobian ranks. **This is an internal AI review. It does not replace external human review (still required, T30 stays PARTIAL).**

## Verdict of the review and our decision

The direction of the central claim survives: there is no energy advantage at N = 64 and no headline 3D advantage. Its numbers did not hold as first written. The central claim is revised as **C-T20-DELIMIT v2** (see `T20-DECISION.md`, revision section). The first wording stays in the history.

## Point-by-point response

| Id | Severity | Accepted? | Change made |
|---|---|---|---|
| O1 | critical | **Yes** | Claim (b) now rests on the architecture-independent converter floor: converters plus modulator alone cost 71.6 fJ per MAC at N = 64 and 8 bits, which is 4.5× the 3 nm macro at 0.5 V and about 1.4× at nominal voltage. The 440× and 6300× figures are kept only as "for the single cited MZI stage loss in an SVD mesh", together with the break-even stage loss against 2014 (≤ 0.131 dB). T24 keeps its registered verdict text. The robust part (fails against the modern reference even with a lossless core) and the fragile part (the 2014 kill depends on stage loss and realization, both chosen after the commitment) are now stated separately. |
| O2 | major | Yes | "Most favorable value found per quantity; the mesh-stage loss is a single 2020 EAGLE XG measurement" replaces "most favorable cited components". |
| O3 | major | Yes | Claim (c) now reads: crossings alone do not decide. The worst planar path at N = 16 has 11 crossings with free output order (18 with fixed order). At ≤ 0.01 dB (80°, an upper bound), that is ≤ 0.11–0.18 dB, while the same source reports 0.4–0.5 dB per S-bend, so the net 3D gain at N ≤ 32 is not established and may be negative. Rule I1 recomputed with the better layout: H-B is retained only for N ≥ 64 (57 × 0.01 = 0.57 dB), at the edge of the rule, and stays non-headline. |
| O4 | minor | Yes | The falsifier of (c) now refers to a measured net worst-path advantage ≥ 0.4 dB at N = 16. The layout clause moved to the I1 discussion. |
| O5 | major | **Yes** | Claim (a) corrected: three-dimensional connectivity can save **at most one layer**. The bound, with phase redundancy, is N − 1 for even N and N for odd N. Planar rectangular meshes need N, and a cylindrical (3D-only) brick wall reaches local full rank at N − 1 (its global universality is untested). The manuscript states the counting with the output phase screen and U(2) redundancy. |
| O6 | minor | Yes | The margin against the modern reference is reported as 1.4–4.5× for a lossless core. |
| O7 | minor | Yes | Stated: the optimistic set is lenient on electronics (k = 1, NRZ modulator energy, ENOB 7.3 ADC, 0 W static) and harsh on the mesh. |
| O8 | minor | Yes | Explained: 128 MZI layers carry loss, and the depth check counts 2N + 1 = 129 layers including the passive attenuator column, which is assumed lossless beyond its function. |
| O9 | major | **Yes** | T25 and T26 criteria are called **verification gates**. Only T24 and T27 had falsifiable criteria, and the manuscript says so. |
| O10 | major | Yes | H-C is scoped as "N ≤ 8, σ ≤ 0.02 rad, ideal transfer-matrix access". N = 16/32 and an intensity-only, noisy loop are listed as the next model tests. |
| O11 | major | Yes | The central claim's own decisive measurements are named: (b) a measured per-stage MZI loss in fs-written silica (≤ 0.13 dB would reverse the 2014 comparison) and verified converter energies; (c) series crossings and 3D transitions (coupon B). H1 is kept as the separate next test of the waveguide programme. |
| O12 | minor | Yes | The claim says "glass". Borrowed values are flagged: the stage loss and heater data come from EAGLE XG borosilicate, and the nominal static power from a silicon-photonics module TEC. |

## Pre-mortem accepted as risk register

1. **Strawman energy test.** Mitigated by moving the claim to the converter floor, which does not depend on the mesh.
2. **No advance and no data.** Not mitigated: the result is a delimitation and the physical tests are unrun. The manuscript says this plainly.
3. **Unmodeled routing and process trust.** Partly mitigated: S-bend costs are cited, and the agent-run process is disclosed. Self-recorded timestamps remain a limit, and an external timestamp (archive DOI) is the titular's decision.
