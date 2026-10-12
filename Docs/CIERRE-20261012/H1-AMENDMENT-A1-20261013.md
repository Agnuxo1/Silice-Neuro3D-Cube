# H1 · Amendment A1 (dated 2026-10-13, before any measurement)

This amendment resolves the five ambiguities listed in `Docs/NOVEDAD-ESTADO-20261011.md` §5 and applies rule R1 of T26. It is published before any sample exists. The original H1 in `Docs/CONTRIBUCION-CENTRAL-T20.md` stays in the history unchanged. Measurements may only be analysed under this amended text.

## H1-A (feasibility)

> A trench waveguide (core n = 1.444, trench Δn = −0.005, core radius a = 6 µm, trench width t = 12 µm), written by fs laser in fused silica, has a total propagation loss of its **HE₁₁ (LP₀₁) mode** at **1550 nm** of at most **0.3 dB/cm**.

## H1-SOTA (state of the art, secondary)

> The same statement with threshold **0.06 dB/cm**, for the geometry fixed by the design study T20D (`resultados/agent/t20_trench_width_20261013/results.json`).

## The five points

1. **Mode and excitation.** HE₁₁ only. Excitation by butt coupling from SMF-28 with index-matching gel at 1550 nm, for two orthogonal input polarizations analysed separately. The output near field is imaged at every cut length. A length whose output is not single-mode (higher-order content visible above the camera noise floor) is excluded by a rule written before unblinding, and the exclusion is reported.
2. **One decision rule.** `agentkit.stats.three_zone_decision` on the 95 % confidence interval of the between-chip mean slope from `agentkit.metrology.fit_cutback` (at least three chips, at least four lengths per guide): CONFIRMED if u ≤ U and l ≥ F; FALSIFIED if l > U; MODEL_CONTROL_FAIL if u < F; INCONCLUSIVE otherwise. The earlier mixed criterion (95 % CI for F1 and 0.044 − 3σ for F2) is withdrawn.
3. **Origin of the thresholds.** U = 0.3 dB/cm comes from Bukharin, Khudyakov and Vartapetov, *Appl. Phys. A* 119, 397 (2015): a tubular guide in fused silica; the abstract does not state the wavelength. It is kept as a **feasibility** threshold. U = 0.06 dB/cm (H1-SOTA) is the lowest verified loss at 1550 nm in fused silica: Ackermann et al., *Opt. Lett.* 50, 2506 (2025), cut-back, 0.06 ± 0.02 dB/cm (type I, UV fs writing, not a depressed-cladding guide).
4. **Total propagation loss** = leakage + scattering + absorption, per unit length, taken as the slope of the cut-back regression. Coupling and facet losses are the intercept and are reported separately, never mixed into the slope.
5. **One leakage reference.** The floor F is the vector leakage of HE₁₁ from the layer solver, 0.044044 dB/cm for t = 12 µm (`experimentos/vectorial_claude/RESULTADOS-VECTORIAL-GEOMETRIA.md`). The scalar value 0.0443 dB/cm is no longer used as a reference. After the index profile of the actual samples is measured (T05), F is recomputed for that profile with its uncertainty, before unblinding.

## Feasibility of H1-SOTA with t = 12 µm

With F = 0.044 dB/cm, H1-SOTA can only be CONFIRMED if the whole 95 % interval lies within [0.044, 0.06] dB/cm: an interval narrower than 0.016 dB/cm that also leaves only 0.016 dB/cm for scattering and absorption. That is not a sensible test. H1-SOTA therefore uses a wider trench whose leakage is at most 10 % of 0.06 dB/cm, fixed by the registered design study T20D before any measurement.

## Blind analysis

Required for both hypotheses: a custodian who does not analyse holds a secret slope offset (`agentkit.blind`, scale 2 dB/cm, SHA-256 commitment published in the measurement protocol), and blinded powers are rounded to the instrument's significant digits. Number of chips: `agentkit.stats.sample_size_one_sided` with α = 0.025 and power 0.8 (table in `T28-FABRICATION-DOSSIER.md`), with σ between chips taken from a declared pilot run.
