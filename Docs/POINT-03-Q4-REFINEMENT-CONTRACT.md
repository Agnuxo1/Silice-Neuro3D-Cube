# Point 03, Stage B — prospective 96-track refinement contract

Date: 2026-10-06. Freeze and commit this contract before ANY new propagation.
The numerical thresholds below are local prospective acceptance choices,
not universal requirements imposed by NASA, ASME or a prize committee.

## Question and scope

Does the 96-track scalar ADI calculation at z = 2 mm exhibit a consistent
spatial convergence regime and an acceptably small conditional uncertainty
indicator after detector, nominal-domain and auxiliary-error controls?

The original GLASS-009d Q4 failure is retained. Stage A passed its audit
gates but found that Q4 fails with all four detectors. This Stage B is a
new experiment, not a replacement or reinterpretation of old evidence.

The solver is the unmodified definitions-only module
`experimentos/glass009_claude/adi2d.py`, using its complex128
Peaceman-Rachford ADI step. Do not import `run009d.py`, which writes results
at import. Do not edit `bpm.py`, `CellGrid` limits or peer experiments.

## Frozen physical model and discretization family

- Scalar paraxial field; vacuum wavelength 1550 nm; reference index 1.444.
- Exactly 96 circular tracks: 32 per ring at radii 7.25, 9.00 and 10.75 um;
  the middle ring is offset by pi/32. Track radius 1.25 um. Union coverage
  is clipped to the annulus with core radius 6 um and thickness 6 um.
- Index change is -0.003 times that union's cell coverage. Use existing
  `silice.coverage.union_coverage` and `silice.tracks.track_centres`.
- Gaussian initial amplitude waist 6 um, centered, no tilt; initial power
  is normalized to 1 by the original Gaussian definition. No output or
  checkpoint renormalization, fitting or removal of unfavorable results.
- Nominal width W = 128 um; N = 256, 320, 400, 500, all even; dx = W/N;
  coordinates are `(arange(N) - N//2)*dx`, as in the original solver.
  Successive spatial refinement ratio is exactly 1.25.
- Absorber is the original quartic sigma map: 4e4 per metre at nominal
  outer scale, onset at 80 percent of the semidomain; implicit zero ghost
  values are retained. Physical ghost-node positions still depend on dx.
  Fixed nominal W alone does NOT validate boundary placement or reflection.
- Primary detector: analytic circle/cell weights for radius 6 um on every
  case. Intensity remains piecewise constant within each cell. Retain
  final complex fields, initial fields, index, sigma and detector weights.

## Exactly eight new solutions

| Case ID | N | dx (um) | Profile samples per axis | dz (um) | Steps |
| --- | --- | --- | --- | --- | --- |
| n256_ss64_z125 | 256 | 0.500 | 64 | 1.250 | 1600 |
| n320_ss64_z125 | 320 | 0.400 | 64 | 1.250 | 1600 |
| n400_ss64_z125 | 400 | 0.320 | 64 | 1.250 | 1600 |
| n500_ss64_z125 | 500 | 0.256 | 64 | 1.250 | 1600 |
| n400_ss32_z125 | 400 | 0.320 | 32 | 1.250 | 1600 |
| n500_ss32_z125 | 500 | 0.256 | 32 | 1.250 | 1600 |
| n400_ss64_z0625 | 400 | 0.320 | 64 | 0.625 | 3200 |
| n500_ss64_z0625 | 500 | 0.256 | 64 | 0.625 | 3200 |

All stop at 2 mm. All four primary solutions are new; historical solutions
use different dz/profile sampling and cannot fill a new row. Prepare six
unique NPZ inputs keyed by N and profile samples. Longitudinal controls
must reuse the exact corresponding SS64 NPZ input, checked by SHA-256.

## Evidence and numerical validity gates

B1. All eight unique IDs must complete exactly the frozen specifications.
Freeze source, contract, environment and input hashes before propagation;
retain every checkpoint, failed attempt, execution log and final field.
Verify tracked inputs and original evidence remain byte-for-byte unchanged.

B2. Arrays and metrics must be finite with correct shapes and dtypes.
Initial power must differ from 1 by at most 1e-12. Analytic detector area
must agree with pi*(6 um)^2 within relative 1e-12, with weights in [0,1].
Require 0 <= final core power <= final total/input power + 1e-12 and final
total power <= 1.001. This is a numerical sanity screen, not a complete
ADI energy-budget verification. Do not require per-step or per-checkpoint
L2 monotonicity: this factorized scheme need not preserve that norm exactly.

B3. A separate assessor must recompute initial, total and core powers from
the retained arrays and check agreement with reported values to absolute
1e-12, together with hashes, case identity and exact completed step count.
Reusing the same propagation code is internal verification, not external
replication or an independent wave solver.

## Prospective convergence and accuracy gates

Let P0, P1, P2, P3 be the four primary core powers, coarse to fine. Define
D0 = P1-P0, D1 = P2-P1, D2 = P3-P2 and r = 1.25.

B4. All three differences must be finite, have absolute value > 1e-12 and
have the same sign. Compute p0 = log(abs(D0/D1))/log(r) and
p1 = log(abs(D1/D2))/log(r). Both must be finite and strictly positive.
Do not assume order two or take the absolute value of the final logarithm
to turn a negative order into a positive one.

B5. Require abs(p1-p0)/max(abs(p0),abs(p1)) <= 0.20. Using ONLY the first
three powers, predict the fourth as Ppred = P2 + D1/(r**p0). Require
abs(P3-Ppred) <= 0.10*abs(D2). The order and prediction checks are related
algebraic consistency tests; they are not independent replications.

B6. For i = 400,500 define S_i = abs(P_i,SS32-P_i,primary) +
abs(P_i,dz0.625-P_i,primary). Require S_400 + S_500 <= 0.10*abs(D2),
and each of the four individual auxiliary components <= 2.5e-4.
This is an error-separation screen, not a certified uncertainty in p.
At r=1.25 even modest perturbations can strongly affect inferred order.
As a prospective robustness screen, keep P0 and P1 fixed and evaluate all
four combinations (P2 +/- S_400, P3 +/- S_500). Every corner must still
pass the signed-difference, positive-order, order-stability and prediction
gates B4-B5. This tests the estimated fine-grid sensitivities only; it is
not a rigorous bound and does not establish auxiliary accuracy on the
coarser two grids. If any corner changes that conclusion, the asymptotic
interpretation remains unresolved.

B7. Only if B1-B6 pass, calculate an accepted conditional spatial indicator
u_space = 1.25*abs(D2)/(r**p1-1), and u_total = u_space + S_500.
Require u_total <= 1e-3 AND u_total <= 0.01*abs(P3). These are absolute
fractions of unit input power and one percent relative to final core power.
This GCI-style indicator is not a rigorous bound or an experimental
confidence interval. Accepted GCI fields must be null when prerequisites
fail; diagnostic signed differences and candidate orders remain available.

Record the original-style magnitude inequalities separately as diagnostics.
They cannot substitute for B4-B7 or change the historical Q4 result.

## Resources, continuation and stopping rule

Use the Point 01 isolated CPU environment and one numerical thread.
No GPU, Torch or CuPy. Each child advances at most 200 steps, uses an
internal 35-second deadline and a parent hard limit of 40 seconds.
Check available RAM > 1.5 GiB and free disk > 2 GiB. The total execution
attempt budget is 1800 seconds. The plan contains 16000 propagation steps
(80 chunks if every child reaches 200); short chunks may require more.

Use unique attempt IDs, exclusive new output files and chained SHA-256
checkpoints. Never overwrite a failed log or a previous final result.
Operational interruption may resume from the last verified checkpoint
under the same frozen inputs; record all attempts and total cost, including
failures and reused checkpoints. A source or input change forbids silent
resume. No tracked-file edits are allowed during the measured execution.

Execute all eight cases even if an early scientific criterion fails, unless
an operational/resource/invalid-field guard requires stopping. After the
eight cases, any scientific failure blocks acceptance of an asymptotic
claim under this contract. A justified extension requires a new prospective
contract; do not discard a grid, change a threshold or fit a favorable
subset after observing these data.

## Permitted conclusion and references

Passing every gate supports only local spatial convergence and the stated
conditional error indicator for this fixed profile, input, z, model and
grid family. Boundary/reflection, full complex field and phase, physical
material and device validation remain outside Stage B and Point 03.

The reasoning is informed by the official
[NASA spatial-convergence tutorial](https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html),
[NASA verification assessment](https://www.grc.nasa.gov/www/wind/valid/tutorial/verassess.html)
and [TMR uncertainty summary](https://tmbwg.github.io/turbmodels/Papers/uncertainty_summary.pdf).
They motivate grid families, observed order, error separation and caution
with oscillation; the local tolerances above are our prospective choices.
