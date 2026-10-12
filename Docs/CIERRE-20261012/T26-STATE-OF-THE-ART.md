# T26 · State of the art for H1 and H-B (literature review, 2026-10-13)

**Status: PASS for the registered review criteria (3/3).** 31 records, all 31 identifiers verified against Crossref or arXiv by `verify_refs.py`. Every extracted value records where it appears. This is a literature synthesis, not a measurement, and absence of a record found here does not prove that no such record exists.

- Protocol: `experimentos/t26_estado_arte_claude/PROTOCOL-T26.json`; commitment `resultados/agent/prereg/T26_commitment.json` (commit `e640f9f`, verified on the server before the search).
- Records: `resultados/agent/t26_sota_20261012/records.json` (41 logged queries, 31 included, 12 documented gaps). Identifier check: `resultados/agent/t26_sota_20261012/verification.json`.
- Search done by a separate agent under the frozen strategy. The two values that decide the rules (R1 and R4) were then checked by a second reader in the primary full text (below).
- Search date 2026-10-12/13. OpenAlex was used only to find candidates; every record was re-checked by DOI or arXiv identifier.

## Second-reader checks of the decisive values

| Value | Source read | What the text says |
|---|---|---|
| R1: 0.06 ± 0.02 dB/cm at 1550 nm | Open full text of Ackermann et al., *Opt. Lett.* 50, 2506 (2025), EPFL Infoscience copy | Cut-back from 13 cm down to 2.5 cm, light at 1550 nm butt-coupled from SMF-28; «The lowest propagation loss measured is 0.06 ± 0.02 dB/cm» (UV 343 nm, 450 fs pulses, fused silica). After annealing 0.02 ± 0.04 dB/cm (uncertainty larger than the value). |
| R4: ≤ 0.01 dB per crossing | arXiv:2512.01972v1 (Djogo, Rahimnouri, Herman; published in *J. Lightwave Technol.* 2026, DOI 10.1109/JLT.2026.3720907) | Fused silica, 1550 nm, crossing angle 80°: «No significant additional loss was incurred with up to 16 waveguide crosses, yielding at most 0.01 dB per intersect»; crosstalk below the 40 dB noise floor. This is an upper bound, not a measured value. |

## Rule R1: propagation loss at 1530–1565 nm in fused silica

| Record | Loss (dB/cm) | λ | Method | Note |
|---|---|---|---|---|
| Ackermann et al. 2025, *Opt. Lett.* 50, 2506 | **0.06 ± 0.02** | 1550 nm | cut-back | UV fs writing; verified in full text |
| Tan et al. 2022, *Opt. Lett.* 47, 4766 | 0.07 | not in abstract | — | 1550 nm attributed by citing papers; abstract only |
| Lee et al. 2021, *Sci. Rep.* 11, 23770 | 0.15 | 1550 nm | — | bend-loss paper (≈1 dB/cm at R = 10 mm) |
| Djogo et al. 2019, *Int. J. Extreme Manuf.* 1, 045002 | 0.30 | 1550 nm | two lengths | read through a summarizing tool (medium confidence) |
| Djogo et al. 2026, *J. Lightwave Technol.* | 0.2 | 1550 nm | insertion loss minus coupling | interposer, depth 50–320 µm |
| Skryabin et al. 2024, *Phys. Rev. Appl.* 22, 064079 | 0.07 | **920 nm** | — | not at 1550 nm |

**R1 result.** S1550 = 0.06 dB/cm (Ackermann et al. 2025) < 0.3 dB/cm. By rule R1, the 0.3 dB/cm threshold of H1 becomes a **feasibility threshold**, and a secondary hypothesis **H1-SOTA with threshold 0.06 dB/cm** is registered under the same three-zone rule (see `H1-AMENDMENT-A1-20261013.md`).

## Rule R3: depressed-cladding (type III) guides at 1530–1565 nm in any glass

No verified record. Bukharin et al. 2015 (*Appl. Phys. A* 119, 397; tubular guide in fused silica, 0.3 dB/cm) gives no wavelength in the abstract. Likhov et al. 2025 (K8 borosilicate, 0.8 dB/cm) states only "telecom range". Zhou et al. 2025 (*Opt. Mater.* 159, 116651; telecom-band depressed-cladding guides in SK1310) has no abstract in Crossref or Semantic Scholar, and the publisher page was not readable. **This is a gap in what we could verify, not evidence that no such measurement exists:** Zhou et al. 2025 very likely reports telecom-band losses and must be read before any priority statement.

## Rule R4: crossings

XC ≤ 0.01 dB per crossing at 80° (Djogo et al. 2026). It is the only verified data point. No data were found for 90° or shallow angles, nor a per-crossing value for fs-written 3D overpasses (Peri et al. 2026 use a 3D crossing in a 90° hybrid but report only total insertion loss). Applied in `T20-DECISION.md` through rule I1 of T25.

## Rule R5: programmable and 3D fs-written networks in glass

| Record | What it is | Relevance |
|---|---|---|
| Crespi et al. 2016, *Nat. Commun.* 7, 10469 | 4- and 8-mode **3D fast-Fourier-transform** circuits, passive | Direct precedent for a crossing-free 3D butterfly (H-B) |
| Hoch et al. 2022, *npj Quantum Inf.* 8, 55 | 32-mode continuously coupled 3D interferometer, 16 heaters | 3D programmable network |
| Pentangelo et al. 2024, *Nanophotonics* 13, 2259 | 6-mode universal processors at 785 and 1550 nm, ≈2.5 dB total IL at 1550 nm | Programmable mesh at 1550 nm |
| Kondratyev et al. 2024, *Photonics Res.* 12, A28 | 8-port error-tolerant interferometer, 56 shifters, 0.33 W per 2π | Error tolerance (H-C) |
| Barzaghi et al. 2025, arXiv:2505.01609 | 24-mode universal processor, 552 couplers, 576 heaters, < 10 W | Largest fs-written universal processor found |
| Di Micco et al. 2026, arXiv:2605.04162 | 128-mode reconfigurable 3D continuously coupled circuit | Largest 3D programmable circuit found |
| Cao et al. 2026, *Nat. Commun.* 17, 5476 (LAMP) | 8-layer 8×8 photonic-lantern cascade, heaters (146 and 161 mW per π) | 3D multilayer photonic neural network in glass |
| Ceccarelli et al. 2019, 2020, 2024; Albiero 2022; Lichtenegger 2026 | thermal shifters: 102 → 18.5 mW per π in air with trenches, below 1 mW per π in vacuum | Static power of programmable meshes (T24) |

**R5 result.** Programmable fs-written meshes at 1550 nm, error-tolerant designs, crossing-free 3D Fourier circuits and a 3D multilayer neural network in glass all have precedents. None of claims (a), (b) or the 3D part of (e) in `Docs/NOVEDAD-ESTADO-20261011.md` can be presented as new.

## Registered criteria

| Criterion | Value | Result |
|---|---|---|
| all_identifiers_verified | 31/31 | met |
| n_verified_records ≥ 8 | 31 | met |
| every_value_has_location | true | met |

## Limits

- One search agent plus a second reader for two values. Other extracted values carry the agent's confidence label and were not all re-read.
- Paywalled pages (Optica, ScienceDirect, Wiley, MDPI) were not bypassed; values from those sources are abstract-level or come from open copies.
- Crossref title search misses records; snowballing found Tan 2022, Lee 2021 and Cao 2026.
