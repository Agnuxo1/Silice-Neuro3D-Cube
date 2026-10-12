# T24 · Energy kill test of H-A (parametric budget, 2026-10-13)

**Result: H-A is DISCARDED under its registered rule.** At the registered point (dense passive 64 × 64 layer, 8 bits, 1 GS/s), even the optimistic parameter set needs about 6300 times more energy per multiply–accumulate than the modern digital reference and about 440 times more than a 45 nm reference from 2014. The registered criterion `optimistic_advantage_vs_modern ≥ 1` fails (1.6·10⁻⁴). This is a parametric budget from cited component values, not a measurement.

- Protocol: `experimentos/t24_energia_claude/PROTOCOL-T24.json`; commitment `resultados/agent/prereg/T24_commitment.json` (commit `e640f9f`, verified on the server before any value was gathered).
- Inputs, frozen and published (commit `fb78678`) before the computation: `params_nominal.json`, `params_optimistic.json`, `digital_references.json`, `sources.json`, built by `build_params.py` from the raw search `raw_parameter_search_20261013.json`.
- Outputs: `resultados/agent/t24_energy_20261012/budget.json`, `sources_verification.json` (22/22 DOIs resolve with matching title and year).
- Model: `agentkit.limits.layer_budget` (shot plus thermal noise, k = 1 at half an LSB; laser, modulators, DACs, ADCs, static power).

## Parameters (each value carries its source in the parameter files)

| Quantity | Nominal | Optimistic | Source (nominal / optimistic) |
|---|---|---|---|
| Photodetector quantum efficiency at 1550 nm | 0.76 | 0.92 | InGaAs PIN datasheet / Ge PIN, *Light Sci. Appl.* 2025 |
| TIA input noise | 10 pA/√Hz | 2 pA/√Hz | SiGe TIA product page / *Micromachines* 2025 (2.5 GHz) |
| ADC energy per sample | 5.35 pJ | 1.11 pJ | ISSCC 2023, 2.6 GS/s / ISSCC 2023, 8b 2.7 GS/s |
| DAC energy per sample | 4.67 pJ | 3.14 pJ | ISSCC 2015, 8b 18 GS/s / *JSSC* 2021, 8b 28 GS/s |
| Modulator plus driver per symbol | 1.17 pJ | 0.33 pJ | *JSSC* 2024 / VLSI 2018 |
| Laser wall-plug efficiency (single-mode) | 0.10 | 0.30 | DFB datasheet / ISLC 2024 tapered DFB |
| Optical transmission | −47.3 dB | −46.3 dB | 2 facets + 2 cm + modulator + mesh of 2N = 128 stages × 0.35 dB (Ceccarelli et al. 2020) |
| Static power (passive chip) | 1.2 W | 0 W (ASSUMPTION) | measured module TEC, *Microelectronics* 2026 / protocol rule |
| Digital reference | old: 0.23 pJ/MAC (45 nm, 2014) | modern: 0.016 pJ/MAC | Horowitz ISSCC 2014 / 3 nm INT8 digital CIM, 124.6 TOPS/W at 0.5 V, *JSSC* 2026 |

Two applications of the frozen rules are stated in `build_params.py`. First, the laser values are those of a **single-mode** laser, because a coherent waveguide mesh needs one; the search's multimode values (50 % wall-plug efficiency, 4.9 W) are recorded but not used, and using them would not change the verdict. Second, the mesh loss is that of the SVD realization the kit compiles for a general passive layer (two Clements meshes, 2N MZI layers).

## Results at the registered point (N = 64, 8 bits, 1 GS/s)

| | Nominal | Optimistic |
|---|---|---|
| Energy per MAC | 1.2 nJ | 0.10 nJ |
| Dominant term | laser (1.20 nJ/MAC) | laser (0.10 nJ/MAC) |
| DAC / ADC / modulator per MAC | 73 / 84 / 18 fJ | 49 / 17 / 5 fJ |
| Advantage vs modern (0.016 pJ) | 1.3·10⁻⁵ | **1.6·10⁻⁴** |
| Advantage vs old (0.23 pJ) | 1.9·10⁻⁴ | **2.3·10⁻³** |
| Stages allowed by laser power and loss | 22 | 77 |
| Stages needed (SVD mesh, 2N + 1) | 129 | 129 |
| Programmable variant: heater power | 128 W | 1.5 W (vacuum package) |

Registered criteria: `all_parameters_sourced` met; `all_dois_verified` met (22/22); `optimistic_advantage_vs_modern ≥ 1` **not met**. Verdict by the registered rule: the optimistic case does not beat even the lenient 2014 reference, so H-A is discarded and kept as a registered negative.

## Why it fails (sensitivity; exploratory, not part of the registered test)

1. **Mesh loss dominates.** About 45 dB of mesh loss at 0.35 dB per stage multiplies the required laser energy by about 3·10⁴. A dense 64 × 64 passive layer cannot even be powered: the laser budget allows 22 (nominal) or 77 (optimistic) stages, against the 129 needed.
2. **Even a lossless mesh does not win at N = 64.** Without mesh loss, the optimistic set gives 0.075 pJ/MAC (advantage 0.21 versus the modern reference). The DAC alone (E_DAC/M = 49 fJ per MAC) is three times the digital MAC. The break-even with the modern reference is reached only near N ≈ 300 (`paper/figures/fig_t24_energy.pdf`, panel b), a size whose mesh would be hundreds of decibels long at present stage losses.
3. **Programmable glass meshes add static power.** With 4032 thermo-optic shifters at 31.5 mW each, the heaters alone draw 127 W in air. Only vacuum-packaged shifters (0.36 mW mean) bring this to watts.

## Limits

- Budget per MAC excludes memory traffic on both sides; the digital reference is a macro-level figure at 0.5 V and best case.
- The registered fan-in sweep keeps the N = 64 mesh transmission for every N. It is therefore optimistic for N > 64 and pessimistic for N < 64.
- Several parameter values were read from abstracts or datasheets by search agents (flagged in the raw search file). None of them changes the verdict by orders of magnitude.
- Other architectures (free-space or photoelectric multiplication with fan-out instead of a mesh, wavelength multiplexing) are outside H-A as registered. They would need their own protocol.
