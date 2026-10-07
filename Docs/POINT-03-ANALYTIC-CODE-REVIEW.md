# Point 03 — analytic-input refinement code review

## Status and scope

This is a pre-execution review record for Stage E, not an optical result.
Point 03 remains open. Points 01 and 02 are closed; Stage D's geometry
validation passed. The original GLASS-009d Q4 failure, Stage B's refinement
failure, and all three failed Stage D attempts remain part of the record.

The governing contract is `POINT-03-ANALYTIC-PROPAGATION-CONTRACT.md`,
SHA256 `be0b3639bcfd463e49dd0fa1d433b5a6bb4f585fd66471c28ce12b6c54287d41`,
committed before new optical calculations at
`861a6fd40b3b14e63bd47a69abc9a2dc507641f4`.

Stage E changes both the track-profile representation and the primary
longitudinal step relative to Stage B. Its outcome alone must not be used
to attribute the Stage B failure solely to supersampling or to geometry.

## Roles and implementation boundaries

The propagation runner and the retained-array assessor were written by
different reviewers. The runner also received a separate full static
review. The assessor uses only NumPy and the standard library; it does not
import the runner, geometry code, ADI solver, SciPy, or GPU libraries.

The runner copies A0, sigma and detector weights from the frozen Stage B
inputs and checks dtype, shape and C-order array bytes. Its only profile
replacement is dn = -0.003 times the accepted Stage D corrected fraction.
The original B inputs and D grids are retained before array validation.
The accepted geometry is not recomputed in Stage E.

The Stage C sparse backend and the original ADI definitions remain
unchanged. The inherited initialization, Laplacian and step methods are
checked by object identity. Matrix structure, ordering, scaling, pivoting,
permutation identities and the number of solves are checked for every
chunk. The Stage C equivalence evidence remains the relevant numerical
check of this backend; this record is not a new solver comparison.

## Scientific checks reviewed before execution

- Four primary transverse grids use the same 128 micrometre domain and
  dz = 0.625 micrometres. Two N400/N500 controls use dz = 1.25 micrometres
  and two use dz = 0.3125 micrometres. All eight trajectories reach 2 mm.
- All 28,800 propagation steps are assigned to 144 complete 200-step
  chunks. The sequence and all eight case identities are fixed.
- The prediction for the primary N500 result is written exclusively after
  the first 48 chunks, before any new N500 propagation. An invalid fit is
  retained as such and does not justify omitting later valid trajectories.
- The spatial sign, order, stability and withheld-grid prediction screens
  retain the frozen Stage B thresholds.
- Longitudinal screening uses the three dz levels independently at N400
  and N500. The allowed observed-order interval is [1.8, 2.2]. The auxiliary
  radius uses the fixed lower order 1.8, not whichever fitted order makes
  the radius smallest.
- All four prescribed perturbation corners must pass the spatial screens.
  This finite corner check is not a proof over the full rectangle of
  possible errors, nor a check of errors on the coarser primary grids.
- The accepted Richardson/GCI-style indicator is null if any prerequisite
  or either final absolute/relative target fails. Diagnostic quantities
  may be retained without being promoted to accepted uncertainties.
- No power renormalization, phase alignment or retrospective trajectory
  selection is used. Field finiteness and raw total-power checks remain
  distinct from the scientific convergence verdict.

## ADI order and the absorber

The justification below concerns exact arithmetic at a fixed transverse
grid. It provides a consistency/stability argument for the time-independent
linear discrete problem; it does not establish the observed order of the
specific core-power functional.

Let A = Lx + V/2, B = Ly + V/2, h = dz/2, and L = A + B. The retained step is

```text
R = (I - h B)^(-1) (I + h A) (I - h A)^(-1) (I + h B).
```

Expansion without assuming that A and B commute gives

```text
R = I + 2 h (A+B) + 2 h^2 (A^2 + AB + BA + B^2) + O(h^3)
  = I + dz L + (dz^2/2) L^2 + O(dz^3).
```

The zero-ghost discrete Laplacians are real symmetric before multiplication
by the imaginary coefficient. The refractive-index contribution is
imaginary and the absorber sigma is real and nonnegative. Consequently,
A + A* = B + B* = -diag(sigma), where * denotes conjugate transpose.

For M equal to A or B,

```text
||(I-hM)v||^2 - ||(I+hM)v||^2 = -2h v* (M+M*) v >= 0.
```

Thus I-hM is invertible and its Cayley transform
C_M = (I+hM)(I-hM)^(-1) is contractive. With S = I-hB, the ADI step satisfies

```text
R = S^(-1) C_A C_B S,
||S R^k u|| <= ||S u||,
||R^k|| <= cond_2(S).
```

At a fixed grid, S tends to I as dz tends to zero. This stability bound
and the local O(dz^3) consistency support global second-order convergence
for that fixed finite-dimensional linear problem. The calculation does
not require commuting x/y operators or removal of the absorber.

The argument does not establish ordinary Euclidean-norm monotonicity at
every step, a bound uniform in transverse grid refinement, a floating-point
error bound, or a forced observed q=2 for a particular output functional.
Leading functional errors can cancel. Failure of the prospective
longitudinal screen therefore remains a failed screen, not proof that a
solution is less accurate. Boundary, field and phase validation remain
separate roadmap work.

## Evidence, limits and launch behavior

The assessor independently recomputes input and output powers from the
eight final complex fields. It verifies all 144 checkpoint NPZ hashes,
their reports and linked chronology without claiming to decompress every
intermediate field. It checks the copied input arrays, pinned upstream
evidence, source inventories and prediction timing.

The immutable propagation execution record is written before the assessor
starts. The final execution record can then include the assessment and
its raw stdout/stderr without a hash cycle. All partial fields, logs and
operational failures are retained. Scientific failure and operational
failure have distinct statuses and return codes.

Each numerical child has a 35-second internal budget and 40-second hard
timeout. Every successful chunk must complete all 200 assigned steps.
Available RAM and disk are sampled at entry/exit and every 20 propagation
steps, with a clock check on every step. The full fresh attempt, including
preparation and assessment, has a 3,600-second budget. The external launcher
allows 3,660 seconds and targets only the process tree it created on
timeout/interruption. Its cleanup cannot guarantee recovery of a process
that became orphaned after its parent had already exited.

Six numerical-library thread variables are set to one. This is not a
claim that CPU affinity was configured. The approved Point 01 environment
is used; no GPU or new package installation is part of Stage E.

## Workspace interruption and verification record

The temporary local execution service became unavailable while the last
assessor sections were being written. The committed Windows checkout
remained reachable and clean. Reviewed drafts are being preserved there
before scientific execution. Any reconstruction without an established
prior full-file hash is treated as a new draft requiring review.

The reconstructed assessor draft at SHA256
`87747cc443e3aab3848a5734aff72ac3b343f3c322d0c6bdceaab802cb8b29ec`
received full static review before execution. The reviewer found one
blocking interface mismatch: the input audit expected a simplified
three-key D_grid_identity, while the runner retains the complete nine-key
accepted D grid record, including both coordinate representations. The
correction compares the complete accepted record and validates the
coordinate representations. It changes neither optical data nor any
scientific threshold. The pre-correction draft is retained for review.

The corrected assessor has 900 lines and SHA256
`18f99c958e8766e57322ec637942c004a11aa7a4e2ae688b4f1a005f7964590a`.
A second reviewer read the entire earlier version and the correction; the
root reviewer also read all sections and the correction. No further
blocking finding was identified by static review. The 18 scalar and
parser self-checks remain to be executed after this source freeze.

The earlier 664-line runner at `174ad56c...` could not be recovered byte
for byte from the unavailable temporary execution service. A dedicated
recovery attempt returned no output within three minutes. A new runner
is therefore being implemented against the unchanged committed contract
and the reviewed assessor interface. It requires a new full review and
source freeze before any optical propagation. The earlier static review
does not automatically certify the replacement source.

The assessor's scalar self-checks may be completed independently while
the replacement runner is prepared. They generate no optical trajectory.
Final runner hashes and the bounded self-check outcome will be recorded
here before Stage E propagation.

## Method references

- NASA, examining spatial grid convergence:
  https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html
- Eca and Hoekstra, Journal of Computational Physics 262 (2014), 104-130:
  https://doi.org/10.1016/j.jcp.2014.01.006

These sources motivate convergence analysis and uncertainty estimation.
The numerical thresholds in the Stage E contract are local prospective
acceptance criteria; they are not presented as NASA standards or a
guarantee of global physical-model accuracy.
