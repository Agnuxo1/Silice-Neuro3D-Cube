# Project status — Silice-Neuro3D-Cube

Reconciled on 2026-10-06. This is the current milestone inventory for the
scientific-closure branch. The research baseline is local revision
`a15025159cf8c67477e8b1020e1cc368586a2cda`, followed by the Point 01 work.
It supersedes older status summaries, not their underlying experimental
records. Historical reports remain unchanged, with their original dates,
test counts, assumptions, failed criteria and uncertainty statements.

## Reading the status correctly

**Executed** means that retained output exists. **PASS** applies only to
the named criteria and cases. **PARTIAL** means completed work with limited
scope or unresolved criteria. **OPEN** means that the required evidence is
not yet available. A consistency audit verifies saved evidence; it is not
another electromagnetic solver, external replication or fabrication.

The project has a tested CPU environment, scalar wave models, ideal
coupled-mode calculations, bounded CUDA comparisons and analytical geometry
diagnostics. It has no demonstrated fabricated optical cube, complete
physical neural system or measured system-level speed/energy advantage.

## Current software and execution state

| Item | Evidence and status | Scope |
|---|---|---|
| CPU installation | **PASS:** fresh isolated Windows 10 x64 / CPython 3.13.7 installation; six pinned packages; noneditable installed-package probe | Offline installation tested; online path available but not a separate fresh-install trial |
| CPU suite | **PASS:** 51 discovered and executed tests, no errors, failures or skips | Counts of 11–45 in older reports are historical snapshots |
| Environment verification | **PASS:** CMT, 15-case BPM reproduction and historical V2 audit; 339 tracked hashes unchanged | Expected scientific failures remain false/PARTIAL |
| Evidence preservation | **PASS:** 31 retained output/metadata files match their original and staged Git hashes | Nested evidence is protected against line-ending normalization |
| Current compute authority | CPU work only for this session; previous GPU window expired on 2026-10-05 at 13:13:06 UTC | Historical CUDA results remain valid records; no new GPU run is implied |

Sources: [reproduction guide](CPU-REPRODUCTION.md),
[Point 01 result](POINT-01-RESULTS.md),
[environment reports](../resultados/codex/env_20261006T212931610919Z_27db3c22/verification.json),
[Git byte check](../resultados/codex/point01_git_evidence_check.json).

Documentary review details are retained in the [numerical reconciliation](POINT-02-NUMERICAL-REVIEW.md)
and the [newer milestone review](POINT-02-NEW-MILESTONES.md).

## Research milestone inventory

| Milestone | Executed work and approved criteria | Failed criteria or remaining limits | Primary project evidence |
|---|---|---|---|
| GLASS-001 | Literature/feasibility review; architecture and measurement needs identified | Material recipe and six-face registration unverified; no physical prototype | [review](../coordinacion/respuestas/GLASS-001-CLAUDE.md) |
| GLASS-002 | Ideal four-port coupled-mode/DFT calculation, port-order and negative controls | Intensity agreement does not establish coherent field equivalence; original mean-error tolerance is not a 95th-percentile guarantee | [experiment](../coordinacion/respuestas/GLASS-002-CLAUDE.md), [corrections](../coordinacion/respuestas/GLASS-005-CLAUDE.md) |
| GLASS-003 V1/V2 | Scalar paraxial propagation and power bookkeeping; V2 contains 15 cases | V1 and V2 general convergence criteria **FAIL**. V2 delta_n=-0.005 fails both domain and dz comparisons. Later selected refinements do not retrospectively pass V2 | [V1](GLASS-003-004-PRIMER-HITO.md), [V2](GLASS-003-V2-RESULTS.md) |
| GLASS-004 | Independent closed-form couplers agree with CMT to about 2e-16 in field; nominal/negative/loss controls pass | Output phases matter for coherent composition; Monte Carlo samples are hypothetical, not manufactured devices | [audit and noise tails](GLASS-003-004-PRIMER-HITO.md) |
| GLASS-005 | Radial m=0 finite-difference/ECS reference, sign/unit review and dz diagnosis | Selected scalar cases only; material source incomplete; ideal leakage is not measured propagation loss or a universal bound for real tracks | [review](../coordinacion/respuestas/GLASS-005-CLAUDE.md) |
| GLASS-006a | 20 geometries, 18 selected modes; decay sign passes for those modes; four tunnel-ratio comparisons pass | G2 convergence **7/18 PASS, 11/18 FAIL**. Two geometries have no selected mode. Search failure does not prove mode absence | [audit](GLASS-006a-CODEX-REVIEW.md) |
| GLASS-006b | **Executed pilot:** 12 CPU cases with saved complex fields; linearity, symmetry and selected dz/domain checks pass | Historical dx/coherent-port and Gaussian Galerkin criteria fail. Gaussian ports are not eigenmodes; modal CMT and independent ADI comparison remain open | [pilot](GLASS-006B-PILOT-RESULTS.md), [refinement contract](GLASS-006B-REFINEMENT-CONTRACT.md) |
| GLASS-007 V1 | Ten discrete-cladding cases with retained timeout/continuation lineage | Pixel geometry/observable bias and boundary limits remain in the historical formulation | [result](GLASS-007-RESULTS.md) |
| GLASS-007 V2 | 13 cases, four reused by hash and nine subsequent children; own coverage/detector/refinement/ADI comparisons pass | No global convergence or full-boundary certification; GLASS-009d Q4 failure remains. Two prior software failures retained | [result](GLASS-007-V2-RESULTS.md) |
| GLASS-008 | Independent geometric reconstruction, fill fractions, wedge and signed-mode review | Overlapping ideal disks are not measured laser tracks; equal index integral is not equal fabrication dose | [review](../coordinacion/respuestas/GLASS-008-CLAUDE.md) |
| GLASS-009 | Independent 2D ADI scalar propagator and matched-mask comparisons | Original K1, K2, K4-dx and K5 failures retained; both methods can share observable bias | [report](../coordinacion/respuestas/GLASS-009-CLAUDE.md) |
| GLASS-009b/d | Partial-area detector and coverage-based index; improved selected scalar comparisons | Historical 009b P3 and **009d Q4 for 96 tracks remain FAIL**. Small successive differences do not by themselves satisfy Q4 | [009b](../coordinacion/respuestas/GLASS-009b-CLAUDE.md), [009d](../coordinacion/respuestas/GLASS-009d-CLAUDE.md) |
| GLASS-009c | **Executed; PARTIAL:** vacuum ADI controls include complex-field error without phase alignment in a specified observation region | Domain/distance/angle restrictions; isolated absorber reflection and guided-network phase/coherence not validated. Not a general FFT boundary certificate | [report](../coordinacion/respuestas/GLASS-009c-CLAUDE.md) |
| GLASS-010 | Six selected radial cases report passing M4 convergence with the revised formulation; saved arithmetic reviewed | Not a rerun of all 20 GLASS-006a cases. Nine old G2 failures and two old no-selection cases remain outside this study. Coherent cross terms and causal attribution need correction/control | [report](../coordinacion/respuestas/GLASS-010-CLAUDE.md) |
| GLASS-GPU-001 | Eight actual CUDA runs: four complex128 cases pass their numerical criteria | Four complex64 cases fail power balance; the 320-squared case also fails field/port/core comparisons. Failures retained without renormalization. Selected timings are not whole-system photonic speed measurements | [GPU results](GLASS-GPU-2026-10-05-RESULTS.md) |
| GLASS-GPU-002 | Eight further complex128 runs and selected finer dx/dz/coverage comparisons pass locally; CPU/GPU field parity checked | Restricted geometry/grid domain; no independent ADI confirmation, modal-basis closure or general scalability result | [GPU results](GLASS-GPU-2026-10-05-RESULTS.md) |
| MEGA-001 | Analytical CPU geometry/optical-path diagnostic: 24 affine hits and four criteria pass; six added unit tests | Extension enumeration is not an RT pipeline benchmark. Triangle counts are not neuron counts; no certified 80M/500M capacity or full-wave result | [research and diagnostic](MEGAGEOMETRY-OPTICAL-RESEARCH-2026-10-05.md) |

### Quantities that must retain their scope

GLASS-007 V2 reports core power divided by input power of 0.36177143 for
the ideal continuous annulus and 0.33109153 for 96 tracks at the nominal
settings. Their ratio is 0.915195. This is a result within the specified
scalar model, not fabricated throughput or neuronal efficiency.

The GLASS-004 phase-noise experiment at sigma=0.10 rad has a mean bright-port
error of 11.10%, a 95th percentile of 18.97%, and 56.25% of hypothetical
samples above 10%. The 15.35% percentile and 36.75% exceedance numbers belong
to the different coupling-noise setting sigma_kL=0.05 rad.

GLASS-010 operates in a radial m=0 model. Neither that restriction nor one
dominant computed mode establishes the absence of angular/polarization
modes in a real guide. Total coherent power includes the interference cross
term between the mode and residual fields; their separately evaluated powers
are not generally additive. Coefficients above one are not physical conversion
efficiencies.

For GLASS-009c at normal incidence and dx=0.5 micrometres, the 128-micrometre
domain gives an approximately 1.4 mm interval below 2% complex-field error;
the sampled error is about 10% at 2 mm. The 256-micrometre domain stays below
2% over the sampled 2 mm, with a maximum near 0.725%. The nominal-domain
interval is zero at 0.08 rad: a power-check flag within that empty interval
does not certify a positive propagation distance.

GPU-002 contains six required and two descriptive passing comparisons.
Its dx sequence is not monotonic, so the local passing criteria do not
establish convergence order or a continuum extrapolation. Its readback audit
has 29 consistency checks and explicitly retains four GPU-001 complex64
failures. These counts describe distinct tests of evidence and propagation.

## Status of the requested 25-point roadmap

| Point | Current state | Evidence needed for closure / next work |
|---|---|---|
| 1. CPU environment | **CLOSED for tested platform** | External replication and other platforms remain separate claims |
| 2. Milestone inventory | **CLOSED by this reconciliation** | Update this inventory after each subsequent point; preserve dated reports |
| 3. Track convergence Q4 | **OPEN / original FAIL retained** | New prospective convergence evidence and numerical error analysis |
| 4. Earlier modal sweep | **OPEN** | Review the original eleven G2 failures: nine not revisited and two passing under the different GLASS-010 protocol; retain two no-selection cases |
| 5. Boundary, field and phase | **PARTIAL** | Joint error bounds for actual guide/coupler geometry, including absorber-return diagnostics |
| 6. Modal interpretation | **OPEN** | Explicit coherent cross terms and justified modal/radiation statements |
| 7. Measured track/index profiles | **OPEN** | Actual material/writing data with uncertainty; literature is not a measurement of this sample |
| 8. Electromagnetic approximations | **OPEN** | Suitable vectorial comparisons and a justified scalar domain of validity |
| 9. Two-guide coupler | **PARTIAL** | Modal basis and coherent transfer validated beyond the existing pilot/refinements |
| 10. Bends/crossings/3D routes | **OPEN** | Validated loss/crosstalk/curvature envelope |
| 11. Deep writing and face registration | **OPEN** | Demonstrated connection and tolerances across writing orientations |
| 12. Phase control/stability | **PARTIAL concept and ideal noise studies** | Measured/correlated error budget and a realizable control method |
| 13. Network-to-geometry conversion | **OPEN** | Target transform mapped to calibrated, fabricable components with verified response |
| 14. Full neural function | **OPEN** | Frozen task, weights/training/detection/activation definition and independent test data |
| 15. Calibration fabrication | **NOT DEMONSTRATED** | Physical samples and prospective measurement comparison |
| 16. Optical characterization | **NOT DEMONSTRATED** | Measured loss, modal content, polarization, phase and transfer |
| 17. Source/readout/control integration | **NOT DEMONSTRATED** | Repeatable end-to-end physical operation |
| 18. Independent-test task | **NOT DEMONSTRATED for a physical system** | Frozen evaluation and suitable comparison methods |
| 19. Full-system performance/energy | **NOT DEMONSTRATED** | Measured source, detection, electronics, control and transfer costs |
| 20. Fabrication scalability | **NOT DEMONSTRATED** | Multiple devices and sizes with reproducibility and uncertainty |
| 21. Demonstrable novelty | **OPEN** | Explicit comparison against the closest primary literature and demonstrated differentiator |
| 22. Central contribution | **OPEN** | One falsifiable, scientifically significant contribution and decisive test |
| 23. External reproduction/review | **OPEN** | Researchers outside this development reproduce results and later measurements |
| 24. Wider scientific impact | **NOT ESTABLISHED** | Demonstrated use or consequences beyond this project |
| 25. Nobel procedure | **Context, not an engineering completion gate** | Scientific achievement and official nomination rules are separate; no progress percentage or award guarantee |

## Reconciliation and collaboration record

The older README stated 29 tests, no GPU use, an unexecuted GLASS-006b,
and combined GLASS-009c/010 in an over-broad row. Those statements are
superseded by the evidence above. GLASS-009c is completed with partial
validation; phase-sensitive vacuum controls already exist.

The original main worktree contained newer, uncommitted shared-board text.
The CHECKPOINT and queue were read and their exact originals retained in a
Point 02 snapshot before incorporating their factual updates into this
isolated branch. Original main-worktree files, TABLON and THINKTANK were not
overwritten or staged by this work. The queue links here for scientific
status so that old historical summaries do not act as competing inventories.

No new propagation experiment is attributed to Point 02. It is a document
and evidence reconciliation, performed after Point 01 and before Point 03.
