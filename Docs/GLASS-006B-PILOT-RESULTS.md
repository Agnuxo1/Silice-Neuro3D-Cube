# Two-core coupling pilot — Codex, 2026-09-30

Contract a86141b before nine cases; refinement59f9049 before three new cases.
Actual scalar paraxial CPU propagation through an ideal index geometry.
NOT fabricated glass, full neural network, GPU, RT or validated modal CMT.
Same frozen BPM/coverage as007V2. No output/step normalization or fitted phase.

## Actual measured outputs

Powers in geometrical cores / launch power, z1mm. NearD14um, farD32um,
a6/t6um, dn-.005. Both cores untouched, union-of-cladding carved where
it intersects either core; this hypothesis is explicit, not a laser recipe.

| Input / geometry | Left core | Right core | Total surviving power |
|---|---:|---:|---:|
| Left / near, dx0.5um |0.654773|0.173623|0.993905|
| Right / near, dx0.5um |0.173623|0.654773|0.993905|
| (left+i right)/sqrt2 / near, dx0.5um |0.085662|0.742734|0.993905|
| Left / far, dx0.5um |0.807566|0.0000973|0.991534|
| Left / vacuum, near detector positions |0.020726|0.018263|0.918907|
| Left / near, dx0.4um |0.654406|0.173398|retained in raw report|
| (left+i right)/sqrt2 / near, dx0.4um |0.085652|0.742152|retained in raw report|

This is an exploratory geometry-dependent transfer effect, with explicit
vacuum/far controls. It does not prove a fabrication design or efficiency
advantage. Readout/launch use Gram-orthogonalized Gaussians, NOT eigenmodes;
Gaussian projected power and geometric core power are different quantities.

## Gates: preserve the failures

- Every one of12 children completed rc0 within30s. Geometry/balance/port
  orthogonality per-case PASS; maximum balance1.23e-13.
- Full-field coherent linearity:5.62e-15 nominal,6.12e-15 finer (<1e-10).
- Mirror symmetry/reciprocity:1.96e-14 nominal,1.66e-14 finer (<1e-8).
- dz2.5->2um: max port/core change0.000911 PASS (<.005).
- Wider domain at SAME coarse dx:0.0000633 PASS (<.005), not full boundary
  validation or global convergence; total power changes more than core power.
- dx coarse->nominal:0.0065448 FAIL (> .005). V1numeric_pass FALSE.
- NEW nominal->finer: left/right0.0063719, coherent0.0069769 FAIL (> .005).
  Fine-pair stability FALSE. No original failure replaced or threshold changed.
- Two-Gaussian Galerkin: maximum complex-port error0.16283 near1mm,
 0.09036 near0.5mm; finer0.16428. Threshold .05: FAIL retained. This is
  explicitly a nonmodal projection, no hidden calibration/attenuation fit.
  At1mm about0.0661 of launch power survives OUTSIDE those two Gaussian ports.
  Failure motivates actual guided/quasi-mode basis, not rejection of optics.

Post-hoc diagnostics (not new PASS gates): nominal->fine core-power max
change0.000367 for basis launches and0.000582 for coherent input, whereas
individual complex-port phase shifts are0.00684..0.00795rad. No phase
alignment used to turn failures into successes. Small intensity error is
insufficient for a coherent multi-component circuit with a fixed reference.

## Evidence and cost

- resultados/codex/glass006b_pilot_v1.json SHA256
 0b45ae75f812c51b1bb615633ef614aa782f285d940005cf39b8921727f82ae6.
- resultados/codex/glass006b_refinement_v2.json SHA256
 23d110a43f64dff147c4247f8d20ab5b571bcd93f48bb2a08a90358409619c41.
- Each case includes input/output complex fields, dn, both detectors,
  basis and projected generator in its hash-linked NPZ.12files, no caching
  or recomputation of old cases. All preparations/NPZ compression included.
- Read-only scripts/audit_glass006b.py independently recalculates port/core
  values, projection budgets, reduction errors and file hashes from arrays;
  NOT an independent wave solver. Audit6008a572... confirms the12records,
  including measured FAILs.34unit tests PASS1.226s (five new coupler tests).
- Nine-case supervisor41.2617s; finer three23.1644s; longest child8.04s.
  FreeRAM before original children >=3.87GiB; each needs>=1GiB AFTER256MiB
  reserve. Reported RSS after calculation<=45.27MiB, NOT certified peak.
  CPU1thread, noGPU/Blender/install. All own children have finished.

## Concrete collaboration

Claude receives coordinacion/tareas/GLASS-006B-PILOT-CLAUDE.md: independently
propagate near_left and optionally near_coherent with ADI using exact saved
input/dn/weights/basis; compare complex amplitudes AND core powers without
normalization, phase fitting or substituting matrix multiplication. Freeze
its tolerances before measurement. His discrete-cladding search remains
independent. Codex next: isolate phase/profile error with a new contract
and move toward actual coupled quasi-modes after independent contrast.

Acuse009c/010: new sources/contracts/data read, not executed or edited.
010 eigenvalue-to-loss arithmetic and24M4 flags checked from retainedJSON
SHAcd077e8f7fd4beba8a1902f6ee59ca732b62e01658e0b1c38588cf210105fdf5.
That is arithmetic audit, not independent eigensolver/convergence proof.
In010 Ptotal != Pmode+Prest: cross interference term computed by subtraction
is -0.01724865 for(10,12,-.003), +0.04411195 for(15,10,-.003) at2mm.
AskedClaude to report it and distinguish bilinear projections from exclusive
power fractions. His new geometry sampling/stencil changes do not isolate
radius as sole cause of every old006a failure.009c limits are ADI-vacuum
results, not automatically applicable to our FFT sponge or every guided case.

Primary context: depressed-cladding interaction-region design has a real
experimental precedent in [Tm:YAG couplers](https://pmc.ncbi.nlm.nih.gov/articles/PMC7019769/),
NOT silica1550nm and NOT our assumed recipe. [CMT review](https://opg.optica.org/josaa/abstract.cfm?uri=josaa-11-3-963)
is context, not a matched benchmark or proof of our Gaussian approximation.
JEV securityblock preserved/local fallback, no remote endorsement.
No remote push/publication/merge of this delivery; sharedboards remain local.
