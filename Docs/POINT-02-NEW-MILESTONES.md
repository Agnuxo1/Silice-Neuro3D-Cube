# New milestone inventory: GLASS-006b, GPU-001/002, and MEGA-001
Date of read-only inventory: 2026-10-06; no experiments or tests were rerun.
Source checkout: D:\PROJECTS\Silice-Neuro3D-Cube-work-20261006.
Observed HEAD: 9d32a6bb40c3b78a6e6dc54c459df49e47bc74f2.
This inventory distinguishes completed execution, numerical gates, and evidence consistency.
The five primary summary SHA256 values checked here match the SHA256 values stated in the official local narratives.
Contracts were frozen locally before runs: a86141b/59f9049 (006b), a8b4b5b/64cd7ea (GPU), and f4e9dcd (MEGA); no external registration is claimed.

## Primary retained sources

- GLASS-006b contracts: Docs/GLASS-006B-PILOT-CONTRACT.md; Docs/GLASS-006B-REFINEMENT-CONTRACT.md.
- GLASS-006b narrative: Docs/GLASS-006B-PILOT-RESULTS.md.
- GLASS-006b JSON: resultados/codex/glass006b_pilot_v1.json; resultados/codex/glass006b_refinement_v2.json.
- GLASS-006b array audit: resultados/codex/glass006b_array_audit_v1.json; scripts/audit_glass006b.py.
- GPU contracts: Docs/GLASS-GPU-001-CONTRACT.md; Docs/GLASS-GPU-002-CONTRACT.md.
- GPU narrative: Docs/GLASS-GPU-2026-10-05-RESULTS.md.
- GPU JSON: resultados/codex/glass_gpu001_20261005_v1.json; resultados/codex/glass_gpu002_20261005_v1.json.
- GPU audits: resultados/codex/glass_gpu_readback_20261005_v1.json; resultados/codex/glass_gpu_readback_20261005_v2.json.
- GPU guard records: resultados/codex/glass_gpu001_20261005_v1__guard.json; resultados/codex/glass_gpu002_20261005_v1__guard.json.
- MEGA contract/narrative: Docs/MEGAGEOMETRY-ANALYTIC-CONTRACT.md; Docs/MEGAGEOMETRY-OPTICAL-RESEARCH-2026-10-05.md.
- MEGA JSON/script: resultados/codex/megageometry_analytic_20261005_v1.json; scripts/audit_megageometry_optics.py.

## GLASS-006b: twelve retained CPU wave cases

The ideal two-core profile uses wavelength 1550 nm, reference index 1.444, core radius 6 um, cladding thickness 6 um, and delta_n=-0.005.
Near/far centre separation is 14/32 um; the cladding union explicitly excludes both intact cores.
The frozen scalar paraxial SSFM uses orthonormalized Gaussian launch/readout ports, which are not guided eigenmodes.
Nine pilot cases are near_left, near_right, near_coherent, far_left, vacuum_left, near_half, near_dz, near_coarse, and near_wide.
Their child evidence uses resultados/codex/glass006b_pilot_v1__CASE.json and the same basename with .npz.
Three additional refinement cases are near_left, near_right, and near_coherent at 320 squared points, dx=0.4 um.
Their child evidence uses resultados/codex/glass006b_refinement_v2__CASE.json and the same basename with .npz.
All twelve children completed with per-case numeric_pass=true; geometry, balance, and Gaussian-basis orthogonality passed.
Pilot aggregate numeric_pass=false; refinement fine_pair_stability_pass=false; both aggregate reduction_pass=false.
Pilot linearity and mirror/reciprocity PASS: errors 5.6184e-15 and 1.9524e-14 respectively.
Pilot dz PASS: 0.000911006 < 0.005; equal-dx wider-domain comparison PASS: 0.0000633166 < 0.005.
Pilot coarse-to-nominal dx FAIL: 0.00654480 >= 0.005.
Refinement nominal-to-fine dx FAIL for left/right/coherent: 0.00637189 / 0.00637189 / 0.00697687 >= 0.005.
Refinement linearity and mirror/reciprocity PASS: 6.1212e-15 and 1.6591e-14.
Two-Gaussian Galerkin reduction FAIL against the 0.05 complex-port threshold: near basis errors about 0.162833, half-length 0.090361, and finer basis 0.164276.
The coherent rows additionally report reduction errors 0.169685 nominal and 0.171232 finer; 0.162833 is not the maximum over all twelve diagnostic rows.
Near-left core powers/input are 0.654773 / 0.173623; coherent input changes these to 0.085662 / 0.742734.
Far-left right-core power is 0.00009730; vacuum controls are retained, without a preregistered efficacy/advantage gate.
The saved array audit reports evidence_consistent=true for both summaries, preserving their measured_status=false and reduction_pass=false.
That audit recomputes array arithmetic and hashes; it is not a second wave solver.
Independent-peer, boundary, and global-convergence certification remain absent; smaller intensity errors do not erase fixed-reference complex-port failures.
Pilot/refinement supervisor times were 41.2617 / 23.1644 s; all twelve bounded children completed within 30 s.

## GPU-001: backend equivalence with an explicit single-precision failure

Four CPU fixtures are pilot_v1 near_left/near_right/near_coherent and refinement_v2 near_left.
Each fixture was propagated in complex128 and complex64: eight retained CUDA outputs, not eight independent physical geometries.
Output evidence uses resultados/codex/glass_gpu001_20261005_v1__FIXTURE__PRECISION.npz; exact paths and SHA256 are in the summary.
Execution completed on RTX 3090 with torch 2.6.0+cu124/CUDA 12.4, but the aggregate pass_=false.
All four complex128 records PASS: maximum field-relative/port-absolute/core-absolute errors 7.8068e-14 / 6.2356e-14 / 9.4813e-14.
All four complex64 records FAIL numerical balance: 0.000109854 to 0.000221976, exceeding the 0.0001 threshold.
The 320-squared complex64 case also FAILs field, port, and core errors: 0.000114346 / 0.000100016 / 0.000152631.
Coherent linearity PASS in both precisions: 5.4488e-15 for complex128 and 3.02065e-6 for complex64.
Linearity alone therefore does not establish numerical accuracy; the aggregate scientific FAIL and rc2 are retained.
Warm propagation-plus-budget timings for one nominal case have a descriptive CPU/CUDA128 median ratio about 22.3.
Those timings exclude other separately recorded stages and do not establish end-to-end inference, energy benefit, or general benchmark superiority.
The completed child elapsed 16.5331 s; guard telemetry and output/source hashes remain in retained reports.
This is the same scalar paraxial model on a new backend; CPU/GPU equivalence is not independent physical validation.
Older GLASS-006b dx and Gaussian-reduction failures remain unchanged.

## GPU-002: eight double-precision refinements and controls

Eight cases are n384L, n512L, n640L, n512R, n512C, n512Lcoverage32, n512Ldz, and n640Ldz.
Output evidence uses resultados/codex/glass_gpu002_20261005_v1__CASE.npz, with paths/hashes in the summary.
All eight rows have pass_=true; the summary local_stability_pass=true.
The 320->384 and 384->512 dx gates PASS at 0.00194887 / 0.00302594, but are explicitly descriptive, required=false.
The required 512->640 dx gate PASSes at 0.000662141 < 0.005.
Required dz gates PASS at 0.00151372 for 512 and 0.00153703 for 640.
Required coverage16->32 gate PASSes at 0.000459868 < 0.005.
Required full-field linearity and mirror gates PASS at 5.58054e-15 / 3.00597e-14.
Thus the saved summary contains eight passing comparison gates: six required and two descriptive.
The opt-in fine grid preserves earlier Grid/CellGrid limits; it does not redefine the old failed experiments.
New CPU SSFM comparisons at 512/640 support backend equivalence, not a second solver.
global_convergence_certified=false, independent_ADI_gate=false, guided_eigenmodes=false, and old_failures_preserved=true.
The dx sequence is not monotonic; these results establish local contract stability without convergence order or continuum extrapolation.
GPU-002 child elapsed 85.4150 s; retained guard supervision is about 86.816 s, within its separate historical GPU contract.
The retained V1 GPU readback audit has 21 checks; V2 expands its scope rather than replacing the original evidence.
The V2 readback audit has 29 consistency checks and consistent=true, while explicitly retaining all four complex64 numeric failures.
Its filename is V2, although its experiment label remains GLASS-GPU-readback-audit-v1; this is an expanded saved-data audit, not a new solver.

## MEGA-001: CPU analytical diagnostics and driver metadata

Six affine transforms times four rays produced 24 retained hits; all pass, with maximum hit error about 1.90166e-21 m.
Four aggregate analytic gates PASS: affine hits, four interference examples, phase budget, and detection of wrong reference length.
A scale of 1.001 yields a 0.023414 rad phase error if reference length is reused over a physical segment near 4 um.
The adversarial PASS means that erroneous approximation was detected, not that reference-length reuse was validated.
The illustrative 0.01 rad budget corresponds to 2.46690 nm optical path or 1.70838 nm physical length at index 1.444.
A hypothetical 200 nm length difference gives 1.17070 rad phase and 0.305246 dark-port power in the ideal two-arm example.
Memory and image-ray calculations are hypothetical accounting examples; none measures neural capacity or real scene throughput.
Driver metadata enumerates RTX 3090, driver 581.29, and four named Vulkan acceleration/RT extensions; both queries returned rc0.
Enumeration does not establish feature enablement, BVH construction, shader execution, a working RT pipeline, or hardware optical accuracy.
The JSON has operational_pass=true and elapsed_s=0.374034; its scope explicitly states CPU diagnostics and no GPU workload.
The narrative records six added tests and a historical 51-test CPU PASS; its earlier three import errors are retained as an invocation incident.
The 34/45/51 test totals in successive milestone narratives describe different historical suites and must not be added together.
MEGA-002 through MEGA-006 are future preparation, not executed milestones or frozen GPU evidence.
All four milestones remain digital/model evidence: no fabricated silica device, trained full optical network, Maxwell validation, or measured optical advantage.
