# T28 · Fabrication and collaboration dossier (2026-10-12)

**Status: dossier written; fabrication BLOCKED.** No laboratory has been contacted. Any contact, purchase or data-sharing agreement needs the titular's explicit authorization each time. This document is what a partner laboratory would receive.

## 1. What we ask a partner to fabricate and measure

All parts in one glass lot, written with one laser recipe chosen and validated by the partner. The project does not prescribe laser parameters for an unknown machine–material pair (guide §17).

| Coupon | Purpose (claim) | Contents | Chips |
|---|---|---|---|
| A. Straight trench guides | H1 and H1-SOTA: blind cutback at 1550 nm | Trench guide (core n = 1.444, trench Δn = −0.005, t = 12 µm, a = 6 µm) at 4 or more lengths, 1–4 cm, two guides per length, plus an unwritten control track | ≥ 5 (see §3) |
| B. Crossings | H-B: per-crossing loss and crosstalk | Planar crossings at 90°, 45° and 20°; 3D overpasses with 1–2 pitch vertical offset; 0, 1, 2, 4, 8, 16 crossings in series on otherwise identical guides | ≥ 3 |
| C. Directional couplers | T07: κ and transfer | Gaps 14, 16, 20, 26 µm; lengths covering one transfer length | ≥ 3 |
| D. Bends | T08: bend envelope | S-bends and 90° arcs, radii 10–60 mm | ≥ 3 |
| E. Two-face registration | T09 | Common fiducials; one connection written from two faces | ≥ 3 |
| F. 4×4 Clements mesh with thermal shifters | H-C: in-situ calibration | Six MZIs, 12 thermo-optic shifters, isolation trenches if the partner has them | ≥ 3 |

## 2. Measurements and data format

- **Cutback (A):** P_in and P_out calibrated, length, λ, polarization, chip, guide, temperature, repetition. CSV columns exactly as `agentkit.metrology cutback` expects: `chip_id,guide_id,length_m,wavelength_m,polarization,input_power_w,output_power_w,sigma_loss_db`. Declared excitation: SMF-28 butt coupling with index matching; mode content imaged at the output (HE11 is the hypothesis' mode).
- **Index profile (A–F):** refracted near-field or quantitative phase imaging, with calibration and resolution; raw maps kept.
- **Crossings (B):** insertion loss per crossing from the slope versus number of crossings (same principle as cutback), crosstalk into the crossing guide, both polarizations.
- **Mesh (F):** complex transfer matrix before and after calibration, heater power per π, drift over 1 h and 24 h, temperature.
- Raw files, instrument identity and calibration certificates are retained. Hashes are recorded at transfer.

## 3. Sample size (guide §42.2)

One-sided test, α = 0.025 (consistent with a two-sided 95 % interval), power 0.8, chips as independent units, σ between chips as a planning value (`agentkit.stats.sample_size_one_sided`):

| Expected margin below the threshold | σ = 0.02 dB/cm | σ = 0.05 dB/cm | σ = 0.10 dB/cm |
|---|---|---|---|
| 0.20 dB/cm | 3 | 3 | 5 |
| 0.10 dB/cm | 3 | 5 | 10 |
| 0.05 dB/cm | 4 | 10 | 34 |
| 0.02 dB/cm | 10 | 52 | 199 |
| 0.01 dB/cm | 34 | 199 | 787 |

A test against the 0.3 dB/cm feasibility threshold is cheap if the guides are good. A test against the state of the art (T26) needs a margin of hundredths of dB/cm and many chips. The pilot run (3 chips) estimates σ and is declared as pilot data, never reused as confirmatory data.

## 4. Analysis rules fixed before measuring

- **Blind analysis** (`agentkit.blind`): a custodian who does not analyse holds a secret slope offset (scale 2 dB/cm, commitment published in the protocol), rounds blinded powers to the instrument's significant digits, and reveals the offset only after the analysis freeze is committed.
- **Decision** (`agentkit.stats.three_zone_decision`): CONFIRMED, FALSIFIED, INCONCLUSIVE or MODEL_CONTROL_FAIL, with the floor F recomputed for the measured profile (T05).
- **Preregistration** (`agentkit.prereg`): protocol, sources and planned artifacts committed and published before data arrive.

## 5. Authorship, data and credit

- CRediT roles agreed before fabrication; the laboratory's contribution is authorship, not acknowledgment, if it designs or runs measurements.
- Data shared under the license the titular chooses (pending); raw data archived with a DOI.
- Negative results are published under the same rules as positive ones.

## 6. Candidate partners (not contacted; verify before any contact)

- Groups that published fs-written programmable circuits or low-loss silica guides (authors in `Docs/CIERRE-20261012/T26-STATE-OF-THE-ART.md`).
- In Spain: the Laser Applications and Photonics group of the University of Salamanca, and groups in Madrid that worked on fs-inscribed waveguides in glass (affiliation and current equipment to be verified).
- Shared facilities with external-user access, or commercial fs micromachining services that offer graded-index waveguide writing with metrology (not verified).

## 7. What stays blocked until parts exist

T05, T09, T13, T14, T15, T17 and the physical parts of T10, T18, H1, H-B and H-C.

## Addendum after T30 (2026-10-13)

Coupon F must report the **per-stage MZI loss** in silica (loss versus number of cascaded MZIs). A value of at most 0.13 dB would reverse the 2014 comparison of claim (b), so this is a decisive measurement for the central claim. Coupon B must report loss versus number of series crossings at the shallow angles a planar butterfly uses, and the loss of one 3D transition (vertical S-bend), as the decisive measurement for claim (c).

## Addendum (2026-10-13): coupon A widths

Coupon A must include **both** trench widths: t = 12 µm (H1-A, feasibility) and t = 16 µm (H1-SOTA, fixed by the registered design study T20D, ideal HE₁₁ leakage 0.0020 dB/cm). Each width needs 4 or more lengths and the number of chips in §3. Candidate partners are listed in `LAB-PARTNERS-20261013.md`.
