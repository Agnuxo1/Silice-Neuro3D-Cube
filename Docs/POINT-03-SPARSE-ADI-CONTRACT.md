# Point 03, Stage C — prospective sparse-ADI equivalence audit

Date: 2026-10-06. Draft until committed. Complete and assess Stage B first;
commit this contract and the reviewed implementation before any Stage C
factorization comparison or propagation. This does not change Stage B.

## Question

Can compiled sparse LU replace the Python Thomas loops while preserving
the exact finite-dimensional ADI equations and their numerical result to
the tolerances below? The purpose is to make further resolution studies
practical if needed, not to change the physical model or assert speed in
advance of measurement.

The reference is the unchanged definitions-only module
`experimentos/glass009_claude/adi2d.py`. The candidate helper is
`scripts/point03_sparse_adi.py`, used by
`scripts/audit_point03_sparse_adi.py`. Its factory subclasses the original
Stepper and overrides ONLY `_fact` and `_solve`; `__init__`, `_lap` and
`step` remain inherited. Do not import the historical result-writing scripts.

## Fixed algebra and options

With h = dz/2, c = i/(2*beta0*dx^2) and V = i*k0*dn-sigma, each solve has
diagonal D = 1+2*h*c-h*V/2 and off-diagonals -h*c. Build two independent
CSC complex128 block-diagonal matrices of dimension N^2:

- x uses D flattened in C order;
- y uses D.T flattened in C order;
- remove every link between flattened indices j*N-1 and j*N;
- each matrix has exactly 3*N^2-2*N nonzero entries;
- solve normal systems, restoring the original array shape and transpose.

Use full `scipy.sparse.linalg.splu`, SciPy 1.15.1, with `NATURAL`,
`diag_pivot_thresh=0.0` and `Equil=False`. Record observed row and column
permutations and reject unexpected nonidentity permutations. Keep the
original potential splitting, absorber, order of sweeps and field dtype.

For this passive model, writing h*c=i*alpha gives Re(D)>=1. The Thomas
pivots satisfy u_i=D_i+alpha^2/u_(i-1), so induction gives Re(u_i)>=1
in exact arithmetic. This supports the nonzero-pivot assumption; it does
not replace numerical residual checks or prove bitwise equivalence.

## C1 — matrix structure and separate solves

Use NumPy's generator with seed 20261006 and two deliberately asymmetric
test profiles: N=8, dx=0.5 um, dz=1.25 um; N=11, dx=0.256 um, dz=0.625 um.
Generate dn within [-0.003,0], sigma within [0,4e4] per metre, and a complex
RHS normalized to unit discrete power. Retain the test arrays and their
hashes. These are algebraic verification cases, not additional T96 optics.

Independently assemble dense reference matrices from the original diagonal
and line-neighbor definition. Require exact elementwise equality with the
candidate sparse matrices, the expected nonzero counts and no connections
between distinct line blocks. Use impulses next to a line break to ensure
that a solve creates no response in another block.

Compare both x and y solves to the original Thomas implementation. Require
relative L2 field difference <=1e-12 and normalized infinity residual
||M*x-b||inf/(||M||inf*||x||inf+||b||inf) <=1e-13. The y solve must use its
own reordered matrix; transposing the x linear system is not equivalent.

## C2 — complete small ADI trajectories

On each same asymmetric test profile, compare original and candidate
trajectories after 1, 16 and 64 complete ADI steps. Require relative L2
field difference <=1e-12 and absolute total-power difference <=1e-12.
No phase alignment or renormalization is allowed after defining the input.
Record all comparison results, not only the smallest difference.

## C3 — two complete paired optical reproductions

Use the immutable Stage B study
`resultados/codex/point03_refinement_20261006T220909702270Z/manifest.json`.
Reproduce exactly these two primary cases, using their same input NPZ files
and recorded SHA-256 rather than rebuilding geometry:

| Case | N | Profile samples | dz (um) | Steps | z (mm) |
| --- | --- | --- | --- | --- | --- |
| n256_ss64_z125 | 256 | 64 | 1.25 | 1600 | 2 |
| n500_ss64_z125 | 500 | 64 | 1.25 | 1600 | 2 |

Compare each final candidate complex field with its retained Stage B field.
Require relative L2 and relative maximum-norm field differences <=1e-12,
absolute total-power difference <=1e-12, and absolute analytic-core-power
difference <=1e-12. Use the frozen detector weights and unit-input-power
convention. Record raw field identity, differences and both measured powers.
No common-phase removal, output rescaling or fitting is permitted.

Every field must be finite complex128 of the expected shape. Preserve the
Stage B initial, detector and final-power sanity requirements. The final
comparison must reach exactly 1600 steps; a short run cannot stand in for it.

## C4 — provenance and execution limits

Freeze contract, helper, driver, original solver, Stage B manifest, selected
case reports, input NPZ and reference final fields by SHA-256. Verify their
identities before and after execution. Keep all regular tracked files
unchanged during the study, recording before/after hashes. Use only the
isolated Point 01 CPU environment with one numerical thread and no GPU.

Run numerical children sequentially: at most 200 propagation steps per
child, internal deadline 35 seconds, parent hard limit 40 seconds. Stop on
a resource or numerical failure; preserve its report and all available
fields/logs. Require available RAM >1.5 GiB and free disk >2 GiB. The study
wall budget is 600 seconds. No automatic resume or replacement of failed
cases is required in this audit; any follow-up must retain the failure.

Use exclusive new result directories and files. Save the small-case inputs,
candidate fields, checkpoint chain and final reports. Record setup, solve,
total elapsed time, matrix/factor nonzeros, observed permutations, versions
and memory measurements. Distinguish a current RSS sample from a measured
process peak. Include the cost of failed attempts if any.

## Acceptance and interpretation

All C1-C4 requirements must pass. Before using the candidate backend in a
new scientific refinement, a separate review must verify the actual output
and independently recompute the final paired field/power differences from
the saved arrays. A failed comparison blocks substitution under this
contract; do not relax its tolerances after observing results.

Passing supports equivalence of this implementation on the tested algebraic
and optical cases. It does not make it an independent physical model or
validate the continuum approximation. It does not change the historical
Q4 or Stage B results. Timing describes this audit on this host; it is not
a system benchmark or evidence of a photonic device advantage.

Primary API references: [SciPy 1.15.1 splu](https://docs.scipy.org/doc/scipy-1.15.1/reference/generated/scipy.sparse.linalg.splu.html)
and [SuperLU.solve](https://docs.scipy.org/doc/scipy-1.15.1/reference/generated/scipy.sparse.linalg.SuperLU.solve.html).
The local numerical tolerances above are prospective choices for this audit.
