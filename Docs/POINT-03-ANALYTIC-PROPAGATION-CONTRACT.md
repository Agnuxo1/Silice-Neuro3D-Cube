# Point 03, Stage E — prospective analytic-coverage propagation contract

Date: 2026-10-06. **Prospective contract: commit before any Stage E propagation.**
Freeze this contract, runner, assessor and scientific sources before execution.
The gates are local prospective choices, not universal NASA/ASME requirements.
Stage D is accepted; Point 03 remains OPEN. Historical Q4 and Stage B remain FAIL.

## Question, scope and fixed model

Does the same scalar ADI model at z=2 mm meet the spatial consistency and
conditional accuracy screens when its index uses the accepted Stage D cell
coverage and its four primary solutions all use dz=0.625 um?
The longitudinal controls investigate the two finest spatial grids only.
This is a new experiment, not a replacement of any historical result.

Keep vacuum wavelength 1550 nm, reference index 1.444, the 96-track geometry,
track radius 1.25 um, annulus radii 6/12 um, nominal width 128 um and even grids
N=256,320,400,500. Keep the original quartic absorber, Gaussian input with
waist 6 um, implicit zero ghost values and analytic radius-6-um detector.
Grid axes remain `(arange(N)-N//2)*dx_m`, with `dx_m=128e-6/N`.
Intensity and index remain represented by values on cells; integration of
geometric coverage does not eliminate spatial discretization of the operator.
No field, checkpoint or output phase alignment, fitting or renormalization.

Boundary placement/reflection, field/phase convergence and Point 05 are outside
this contract. Fixed nominal width alone does not validate the boundaries.
No experimental accuracy, hardware advantage or independent wave model is claimed.

## Accepted geometry and exact preparation identities

Use the accepted D directory `resultados/codex/point03_geometry_20261006234649Z`.
Preserve its name, including the absence of `T` between date and time.
Verify D manifest SHA256
`16b64deee8b53b5ed81e3aa15ed01fa533d11032e228b3b20d8b66ce13863512`
and sibling independent-audit SHA256
`94fb4234b68c0b49f9cc5c6d9c8fd1d8cc31d293818514b9b13ede66eb85a922`.
Require accepted D audit status, complete grids and their frozen specifications.

| N | Accepted D grid NPZ SHA256 |
|---:|---|
| 256 | `06223d91e242847e811dfb47b07c6e824096e60d46af606f76504bdc817257be` |
| 320 | `f0ca2b4c3b3ab2bc4fbf6921c12b3d8d9590edd5e98fca99e345ecc896aa5dce` |
| 400 | `c66374c40a35ef0fcf0bad030a315a2bbc959ee6f9a423ced0fe833d220766cf` |
| 500 | `756fe138bb2d8bcc481d258b3101f067cb23d0c2e8e278f4b624e2fe6e17a641` |

Reuse the corresponding frozen Stage B SS64 input arrays A0, sigma and detector
weights byte-exactly; verify the original Stage B manifest and input NPZ hashes.
Stage B study: `resultados/codex/point03_refinement_20261006T220909702270Z`;
manifest SHA256 `b09c57d05e190b8fdcc6ad54108e50a05a28570acdc4b82ae12501995c9a0e73`.
Prepare exactly four new inputs. The only changed profile array is float64
`dn=-0.003*fraction`, using D's endpoint-corrected fraction without rescaling.
Retain D's raw fractions, signed floating-point endpoint corrections, their
counts/magnitudes and original grid identity. Do not import geometry helpers,
recalculate coverage, run SS sampling or reconstruct Gaussian/absorber/weights.
Check array bytes, shape, dtype, axis convention and finite values before saving;
freeze each new input NPZ SHA before propagation. All dz cases at a given N
reuse the same new input NPZ byte-for-byte. Retain sources before validity checks
can reject an input; preserve available preparation evidence on every failure.

## Unchanged accepted backend

Use `scripts/point03_sparse_adi.py`, SHA256
`362d4d0fbb56663f0e05fc211cd0c4db031fe20394367c090fea634134ab48bd`,
with the unchanged definitions-only `experimentos/glass009_claude/adi2d.py`, SHA256
`e4f729bf40a64c545b81f93ab45b282c580349e47612ff20421dea82f1e600fb`.
Use the accepted `make_sparse_stepper` factory. Verify inherited `__init__`,
`_lap` and `step` are the original method objects; only factor/solve are replaced.
Preserve complex128 algebra, potential splitting, x/y ordering and line cuts.
Keep `splu(permc_spec='NATURAL',diag_pivot_thresh=0.0,options={'Equil':False})`.
Record factor structure/cost and row/column permutations; require both identity.
Retain rejected permutation diagnostics and available arrays before stopping.
Stage C equivalence supports substitution on its tested cases, not an independent
physical validation or an unconditional guarantee for the new profile.

## Exactly eight new solutions and execution order

| Case ID | Role | N | dz (um) | Steps | 200-step chunks |
|---|---|---:|---:|---:|---:|
| n256_geom_z0625 | primary | 256 | 0.625 | 3200 | 16 |
| n320_geom_z0625 | primary | 320 | 0.625 | 3200 | 16 |
| n400_geom_z0625 | primary | 400 | 0.625 | 3200 | 16 |
| n500_geom_z0625 | primary | 500 | 0.625 | 3200 | 16 |
| n400_geom_z125 | coarse_control | 400 | 1.25 | 1600 | 8 |
| n500_geom_z125 | coarse_control | 500 | 1.25 | 1600 | 8 |
| n400_geom_z03125 | fine_control | 400 | 0.3125 | 6400 | 32 |
| n500_geom_z03125 | fine_control | 500 | 0.3125 | 6400 | 32 |

All eight reach exactly z=2 mm: 28,800 steps and 144 propagation chunks.
Execute the first three primary cases, then exclusively save the fourth-grid
prediction record BEFORE any new N500 propagation. Record source/input/final-field
hashes, P0/P1/P2, differences, candidate order, predicted P3 or null, validity
flags and chronological evidence. An invalid fit still produces this record.
Then complete the N500 primary and the four controls in the table's order.
No historical field fills a row. Do not refit the frozen prediction using N500.
An operational or field-validity failure stops the attempt; a failed scientific
screen does not stop otherwise valid cases or suppress unfavorable outputs.

## Evidence and numerical validity gates

**E1.** All eight unique IDs must complete their exact specifications and inputs.
Freeze source, environment, D/B evidence, new inputs and contract hashes before
propagation. Record all regular tracked files before/after; require byte identity.
Retain complete checkpoint chains, raw logs, final arrays and all failed attempts.

**E2.** Fields must be finite complex128 with the expected shape; other arrays and
metrics must be finite with their fixed dtypes. Let raw input power be P_in.
Require `abs(P_in-1)<=1e-12`, weights in [0,1] and analytic detector area within
relative 1e-12 of pi*(6 um)^2. Define P_total as raw final total/P_in and P_core
as the weighted final core/P_in. Require 0<=P_core<=P_total+1e-12 and
raw final total power<=1.001, retaining Stage B's raw-power ceiling.
Retain raw and normalized powers. This sanity screen is not a
complete ADI energy-budget validation; impose no per-step/checkpoint L2 monotonicity.

**E3.** A separate assessor must read retained arrays without importing any
propagation implementation, recompute initial/total/core powers and check all
reported powers to absolute 1e-12. Verify all source/input/output hashes, eight
case identities, frozen prediction chronology, exact step counts, every chain
back to its input and absence of disconnected completed checkpoint evidence.
Require unchanged full tracked inventory and retained produced-output bytes.
Internal arithmetic verification is not external replication or a wave solver.

## E4–E5: unchanged primary spatial screens

Let P0,P1,P2,P3 denote primary core fractions, coarse to fine; r=1.25 and
D0=P1-P0, D1=P2-P1, D2=P3-P2. Labels P0 here denote a primary result,
not the raw input normalization P_in.

**E4.** Require finite differences, each abs(Dj)>1e-12, all with the same sign.
Compute p0=log(abs(D0/D1))/log(r), p1=log(abs(D1/D2))/log(r).
Both must be finite and strictly positive. Do not assume spatial order two
or take an absolute final logarithm to turn a negative order positive.

**E5.** Require abs(p1-p0)/max(abs(p0),abs(p1))<=0.20.
Using ONLY P0,P1,P2, freeze Ppred=P2+D1/(r**p0) as specified above.
Require abs(P3-Ppred)<=0.10*abs(D2). These are related algebraic consistency
screens, not independent replications. Preserve diagnostic orders and null
prediction when prerequisites fail; never substitute a favorable fit.

## E6: longitudinal sensitivity and fixed robustness screen

For i=400,500 define a_i=P_i,coarse-P_i,mid and b_i=P_i,mid-P_i,fine,
where coarse/mid/fine dz are 1.25/0.625/0.3125 um. Require finite a_i,b_i,
abs(a_i)>1e-12, abs(b_i)>1e-12, the same sign, and finite
q_i=log(abs(a_i/b_i))/log(2) within the inclusive fixed band [1.8,2.2].
Both tiny contrasts still fail this order-resolvability screen; retain them
without assigning q=2 or changing the threshold after seeing results.

At fixed N and fixed autonomous split operators, the reviewed PR algebra gives
I+dz*L+dz**2*L**2/2+O(dz**3), motivating expected longitudinal order two.
The q band is a local quadratic-predominance screen, not a standard requirement.
A functional's leading error coefficient can cancel; failure need not prove
less accuracy. Three levels give one q, not a separate order-stability test
or proof of an asymptotic regime. Retain these qualifications on acceptance.

Use q_min=1.8 and Fs=1.25. Only when the corresponding q gate passes, accept
S_i=abs(b_i)*(1+Fs/(2**q_min-1)); otherwise accepted S_i is null.
The fixed denominator is conservative within the accepted order band and
avoids tightening the radius with a favorable fitted q. It represents the
observed mid/fine distance plus a conditional fine-grid Richardson-style
indicator; it is not a certified uncertainty bound or conventional mid-grid GCI.
Require each abs(a_i), abs(b_i) and accepted S_i <=2.5e-4, and
S_400+S_500<=0.10*abs(D2). No SS comparison enters this new sensitivity radius.

Keep P0/P1 fixed and evaluate exactly four combinations
(P2 +/- S_400,P3 +/- S_500). Every corner must pass E4/E5, recomputing its
differences, orders, prediction and 0.10*abs(perturbed D2) threshold.
These are prospective fine-grid sensitivity screens; their sum budget does
not guarantee corner acceptance. They do not prove robustness over the full
rectangle or quantify longitudinal uncertainty on N256/N320.

## E7: conditional spatial and combined indicators

Only if E1–E6 pass, calculate u_space=1.25*abs(D2)/(r**p1-1),
u_total=u_space+S_500, and require both u_total<=1e-3 and
u_total<=0.01*abs(P3). Retain any extrapolated value as a conditional estimate.
Accepted indicator fields must be null if any prerequisite or final target
fails; diagnostic differences/orders remain available. These indicators are
not rigorous bounds, experimental confidence intervals or global model accuracy.
D does not quantify geometry-induced power uncertainty; do not claim a zero
geometry-error term or attach a power bound to D's fractional area tolerance.

## Execution bounds, retention and interpretation

Use only the Point 01 CPU environment: Python 3.13.7, NumPy 2.2.6,
SciPy 1.15.1, psutil 6.1.1, one numerical thread, no GPU/dependency installation.
Runner: `scripts/run_point03_analytic.py`; assessor: `scripts/assess_point03_analytic.py`.
Use a fresh exclusive output directory and stable precomputed inputs. Propagation
children are sequential, each at most 200 steps, with 35 s internal deadline
and 40 s hard timeout; successful complete chunks are exactly 200 steps.
Use a cheap monotonic-clock check before every step with a four-second retention
reserve; full RAM/disk guards at child start/end and every 20 steps.
Require available RAM>1.5 GiB and free disk>2 GiB; checks are sampled, not continuous.
The final independent assessor is also bounded by 35/40 s and included in the
3600 s attempt budget, together with preparation, propagation, prediction and
integrity checks. C-based 32–36 min planning is a projection, not a guarantee.

Successful chains continue within the same attempt. After a failed child,
retain all available partial fields, inputs, diagnostics and logs; no automatic
resume, overwrite or favorable-subset acceptance. Retain evidence even on a
validity error, and report all failed-attempt costs. A correction to propagation
or input preparation requires review, a new freeze commit and a fresh complete
attempt with the same scientific gates. A corrected independent assessor may
re-evaluate complete unchanged retained trajectories after review and a new
freeze commit, recording the defect, source versions and all earlier assessments;
this does not permit changing gates or silently resuming a propagation attempt.
Scientific FAIL remains reportable after all eight valid cases.
Passing supports only this fixed model, profile family, input, detector and z.
Review actual retained data before any Point 03 status decision; this contract
alone does not close Point 03 or reinterpret earlier failures.

## Methodological and local evidence references

- [NASA NPARC spatial convergence](https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html): Richardson assumptions, observed order, distinct discretization directions and GCI factor-of-safety methodology; not authority for E's local gates.
- [NASA Turbulence Modeling Resource](https://www.nasa.gov/nasa-turbulence-modeling-resource/): context for model implementation verification versus validation. NASA identifies its current site as https://tmbwg.github.io/turbmodels/ ; its CFD cases do not validate this optical model.
- [Stage B contract](POINT-03-Q4-REFINEMENT-CONTRACT.md) and [results](POINT-03-Q4-REFINEMENT-RESULTS.md): frozen historical spatial/robustness gates and retained FAIL.
- [Stage C contract](POINT-03-SPARSE-ADI-CONTRACT.md) and [results](POINT-03-SPARSE-ADI-RESULTS.md): accepted backend scope and implementation identity.
- [Stage D contract](POINT-03-GEOMETRY-CONTRACT.md) and [results](POINT-03-GEOMETRY-RESULTS.md): accepted coverage grids, raw corrections and limits of the geometric checks.
