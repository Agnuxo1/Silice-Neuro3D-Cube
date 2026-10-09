# Point 03, Stage A — detector diagnosis before new propagation

Date: 2026-10-06. This contract is fixed before executing the new diagnosis.
It does not close the 96-track convergence question.

## Question and fixed inputs

How much of the original Q4 sequence depends on detector quadrature when
the exact same saved complex fields are measured in four different ways?
No wave propagation, index change, fit or field renormalization is allowed
in this stage. The original Q4 failure and all historical files are retained.

Inputs are the six current arrays in the original main worktree:
`experimentos/glass009d_claude/out/state_{Cd,T96d}_dx{6,5,4}.npy`.
Their shapes are 205, 256 and 320 squared, complex128; dx is respectively
0.625, 0.5 and 0.4 micrometres. The first physical width is 128.125
micrometres; the other two are 128. The original Gaussian input power is 1.
Each imported array is retained with its current SHA-256 before and after
reading. Those hashes identify the files available now; they do not
retroactively authenticate execution of the historical experiment.

The retained report is `experimentos/glass009d_claude/resultados009d.json`.
Its fixed core-power targets in coarse-to-fine order are:

- Cd: 0.36341858760421314, 0.36308954401493865, 0.3631821542545893.
- T96d: 0.33263167400842963, 0.33223675582032003, 0.33267434735736884.

## Measurements and acceptance of this audit

D1. All six files must have the expected dimensions, finite complex128
values and stable current hashes. Copy their original bytes to one unique
new result directory. Never overwrite main-worktree files or a prior output.

D2. Recalculate the original detector using midpoint supersampling 16 by 16
with the original coordinates and strict radius comparison. Its core power
must reproduce each target to absolute error <=1e-12. A mismatch prevents
using that input for historical interpretation and remains a recorded failure.

D3. On EVERY same field, also use midpoint detectors 32 by 32 and 64 by 64,
and the existing analytic circle/cell area routine in `silice.coverage`.
The analytic detector's total geometric area must agree with pi*(6um)^2
within relative 1e-12. Analytic geometry still treats intensity as constant
per cell; it is not an exact integral of an unknown continuum optical field.
All core powers must be nonnegative and no larger than total field power
apart from 1e-12 numerical tolerance.

D4. Record signed successive differences and the original Q4 inequality
for every detector/profile combination. These are diagnostic outputs, not
new convergence acceptance criteria. A changed flag after changing the
observable does not erase the original FAIL or establish asymptotic order.

D5. Record code/contract/report and all tracked-input hashes, package/host
identity, runtime and memory availability. Tracked research files and the
original arrays must be unchanged. Numerical work uses one library thread,
no GPU, at least 1.5 GiB available RAM and a total 40 s numerical deadline.
Retain the summary and errors even if the audit fails or is incomplete.

## Interpretation and next stage

Stage A can quantify detector sensitivity and identify a lineage mismatch.
It cannot identify the sole cause of the Q4 failure, certify boundaries or
replace a finer-grid study. Before new propagation, a separate Stage B
contract will freeze the spatial family, common observable, geometric and
longitudinal controls, criteria and stopping rule. It will preserve the
original failure and will not compute an accepted ordinary Richardson/GCI
estimate from oscillatory or non-positive-order data.

Four even grids at fixed 128um width (N=256,320,400,500) are the candidate
family, with ratio 1.25. N=625 is excluded from that candidate to avoid the
odd/even registration change in the legacy coordinate convention. This
paragraph authorizes no propagation before the separate contract is fixed.

## Primary method references

- https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html
- https://www.grc.nasa.gov/www/wind/valid/tutorial/verassess.html
- https://tmbwg.github.io/turbmodels/Papers/uncertainty_summary.pdf

These verification references guide the separation of errors. The numerical
thresholds D1–D5 are local prospective choices, not requirements quoted from
NASA/ASME, and the scalar paraxial model is not validated by CFD guidance.
