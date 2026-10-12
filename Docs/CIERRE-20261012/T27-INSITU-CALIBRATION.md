# T27 · In-situ recalibration of a mesh with fabrication errors (model, 2026-10-12)

**Status: PASS for the registered model criteria (3/3) at the primary point. Model only.** Splitter errors were drawn from an assumed distribution, not measured, and the "hardware" is a simulated mesh. H-C is supported only as a model result. Its decisive test is physical (T10, T14, T15).

- Protocol: `experimentos/t27_calibracion_claude/PROTOCOL-T27.json`; commitment `resultados/agent/prereg/T27_commitment.json` (commit `1407c62`), verified on the GitHub server before running.
- Code: `experimentos/t27_calibracion_claude/run_t27.py` (analytic gradient; check against central differences: relative error 2.7·10⁻⁹).
- Output: `resultados/agent/t27_calibration_20261012/results.json` (all 540 realizations, 1056 s on one CPU thread).

## Setup

A Clements mesh in the `agentkit.mzi` convention realizes a Haar-random target unitary (a new target per realization). Each directional coupler has a splitting-angle error ε = shared + local, Gaussian with total standard deviation σ and a shared fraction ("correlation") of the variance, as for a common writing bias. The figure of merit is the infidelity 1 − |Tr(U†V)|/N.

- **A, ideal programming:** phases computed for an error-free mesh.
- **B, in situ:** all 2·N(N−1)/2 + N phases re-optimized on the erroneous device with exact access to its transfer matrix (L-BFGS-B from A).
- **B, 8-bit:** the phases of B rounded to an 8-bit DAC over 2π.
- **C, model-based:** phases optimized on a model whose splitter errors were characterized with an error of 0.1σ, then applied to the true device.

## Primary point (N = 8, σ = 0.02 rad, correlation 0.8, 60 realizations)

| Strategy | Median infidelity | Distribution-free 95/95 upper bound |
|---|---|---|
| A, ideal programming | 1.6·10⁻³ | 1.5·10⁻² |
| B, in situ | 5·10⁻¹⁴ | **1.3·10⁻⁴** |
| B, 8-bit DAC | 1.8·10⁻⁴ | 3.7·10⁻⁴ |
| C, model-based (0.1σ characterization error) | 2.7·10⁻⁵ | 1.6·10⁻⁴ |

Registered criteria: gradient check 2.7·10⁻⁹ ≤ 10⁻⁶ (met); 95/95 upper bound after calibration 1.32·10⁻⁴ ≤ 10⁻³ (met); median improvement factor ≥ 10 (met). The median improvement factor is 3·10¹⁰. It is dominated by post-calibration values at machine precision and should not be read as a physical ratio; the medians and bounds in the table carry the result. In 55 of 60 realizations the in-situ result is below 10⁻⁶. In the other five (5·10⁻⁶ to 1.3·10⁻⁴) the erroneous couplers cannot reach the target exactly, and two optimizations stopped at the iteration limit. With 60 runs the 95/95 bound is the largest observed value (Wilks, first order).

## Secondary grid (descriptive, 60 realizations each)

| N | σ (rad) | Correlation | A: 95/95 bound | B: 95/95 bound | B 8-bit: median | C: 95/95 bound |
|---|---|---|---|---|---|---|
| 4 | 0.02 | 0.0 | 3.6·10⁻³ | 6.7·10⁻¹⁵ | 6.2·10⁻⁵ | 4.5·10⁻⁵ |
| 4 | 0.02 | 0.8 | 5.5·10⁻³ | 1.2·10⁻¹⁴ | 6.5·10⁻⁵ | 3.8·10⁻⁵ |
| 4 | 0.05 | 0.0 | 2.1·10⁻² | 2.0·10⁻⁴ | 6.5·10⁻⁵ | 3.0·10⁻⁴ |
| 4 | 0.05 | 0.8 | 3.3·10⁻² | 4.5·10⁻⁴ | 7.1·10⁻⁵ | 6.0·10⁻⁴ |
| 8 | 0.02 | 0.0 | 4.2·10⁻³ | 8.5·10⁻⁶ | 1.7·10⁻⁴ | 5.2·10⁻⁵ |
| 8 | 0.02 | 0.8 | 1.7·10⁻² | 1.0·10⁻⁴ | 1.8·10⁻⁴ | 1.2·10⁻⁴ |
| 8 | 0.05 | 0.0 | 2.9·10⁻² | **2.3·10⁻³** | 1.7·10⁻⁴ | 2.5·10⁻³ |
| 8 | 0.05 | 0.8 | 1.1·10⁻¹ | 8.6·10⁻⁴ | 1.8·10⁻⁴ | 1.0·10⁻³ |

## Reading

1. **Calibration absorbs splitter errors of 0.02 rad almost completely** for N = 4 and 8, correlated or not: the remaining infidelity is limited by unreachable targets in a few realizations, not by the optimizer.
2. **At σ = 0.05 rad and N = 8 the 1·10⁻³ level is not reached** (95/95 bound 2.3·10⁻³ for independent errors). Larger errors make more targets unreachable for a Clements mesh; error-tolerant architectures (Saygin et al. 2020) are the registered alternative to test.
3. **The 8-bit DAC sets a floor of about 2·10⁻⁴** in median infidelity at N = 8. Reaching 10⁻⁴ needs finer phase control.
4. **Model-based precompensation needs characterization error well below σ.** With 0.1σ its 95/95 bound (1.6·10⁻⁴) is close to the in-situ bound at the primary point, but its median (2.7·10⁻⁵) stays far above the in-situ median.
5. **A correlated (shared) error component is harder for uncalibrated meshes** (95/95 bound 1.7·10⁻² against 4.2·10⁻³ at N = 8, σ = 0.02) but is removed by calibration, as H-C states.

## What this does not show

- No thermal crosstalk between heaters, no loss, no phase drift, no measurement noise in the in-situ loop, no heater power budget (see T24 for the energy cost of programmable meshes in glass).
- σ = 0.02 rad is a model value. The real splitter-error distribution of fs-written couplers is unmeasured (T14).
- Exact access to the device transfer matrix is assumed. A real loop measures intensities or interferograms with noise and drift.
- Fixed-phase (written, non-programmable) meshes cannot be recalibrated at all; for them only strategy C applies, with characterization before writing the phases.
