# Point 03, Stage D — geometric coverage results

Date: 2026-10-06. **Stage D PASS; Point 03 remains OPEN.**
The fourth fresh attempt completed the unchanged D1–D5 acceptance gates.
An independent retained-data auditor also returned PASS with zero findings.
This establishes the recorded geometry checks; it does not establish optical
spatial convergence, close Point 03, or reverse historical Q4 or Stage B FAIL.

## Evidence and frozen execution

The accepted study is `resultados/codex/point03_geometry_20261006234649Z/`.
The spelling intentionally has no `T` between the date and time.
Source freeze commit: `da6a8d63a6dae4c057a5a8863fece0925c4462b1`.
The prospective [contract](POINT-03-GEOMETRY-CONTRACT.md) and the three
[run-1](POINT-03-GEOMETRY-ERRATA-RUN1.md), [run-2](POINT-03-GEOMETRY-ERRATA-RUN2.md)
and [run-3](POINT-03-GEOMETRY-ERRATA-RUN3.md) errata define the retained history.
No acceptance tolerance, fixture, selected-cell rule or resource limit was relaxed.

| Retained evidence | SHA256 |
|---|---|
| `audit_manifest.json` | `16b64deee8b53b5ed81e3aa15ed01fa533d11032e228b3b20d8b66ce13863512` |
| `execution.json` | `19ed15f1dc1bc6391553033946d216c636507ed2c32ffe690dd7cd32f882227d` |
| Sibling `_launch/independent_audit.json` | `94fb4234b68c0b49f9cc5c6d9c8fd1d8cc31d293818514b9b13ede66eb85a922` |
| Original `compact_result.json` | `abd998456fca7e5cc479bc18d2f7290df9c476db696cdd50df4f283ae24fb59e` |

This report was drafted from the supplied derivative compact summary and the
contract/errata. The compact summary is an index to original evidence; the
independent audit read the original JSON/NPZ files and recalculated their metrics.
Its 5.159317100013141 s cost is separate from the geometry driver cost.

## Fixed method and acceptance gates

The same unchanged track generator supplies 96 serialized SI centres, converted
to micrometres. Disks have nominal radius 1.25 um; their union is clipped by
the explicit concentric annulus with inner/outer radii 6/12 um. No dose rescaling
is applied. All grids have nominal width 128 um and even N; axes are
`(arange(N)-N//2)*(128.0/N)` with cells extending half a spacing on each side.
Unit conversion changes floating-point representation; nominal equivalence
does not assert byte identity between SI and micrometre coordinates.

The candidate integrates the oriented circular/linear boundary using a local
origin and compensated signed sums. Its corrected angular representation uses
Decimal topology. The independent reference merges vertical disk intervals,
clips the annulus and cell, and performs partitioned quadrature in local
coordinates at two fixed tolerances. It does not import the candidate.

| Gate | Frozen requirement | Retained result | Status |
|---|---|---|---|
| D1 | 22 fixtures; known/reference fractional differences <=1e-12; quality <=1e-13 without unresolved messages; invariance/subdivision errors <=1e-12 of parent-cell area | 22 fixtures accepted; maximum candidate/reference fraction difference 1.9579639266076244e-15; maximum reference quality 1.3211653992500908e-14; all prescribed suites accepted | PASS |
| D2 | Four complete finite grids; raw fraction in [-1e-12,1+1e-12]; closure <=1e-11 times shorter cell side; retain endpoint corrections | 577,936 cells complete; 20,772 candidate evaluations; 30 retained endpoint corrections; maximum correction 2.220446049250313e-16; zero unrepresentable events | PASS |
| D3 | 48 frozen unique cells per grid; raw/reference difference <=1e-12 conditional on quality; repeated candidate and first-eight invariances | 192/192 references resolved and accepted; maximum difference 9.325873406851315e-15; maximum quality 2.0087342503898e-14; 54 total invariance suites including D1 | PASS |
| D4 | Global reference quality; relative area disagreement <=1e-12; six frozen SS diagnostics retained | Reference quality 1.5247504789864415e-14; all 18 area comparisons accepted; maximum relative disagreement 1.038053190228779e-14; six diagnostics retained | PASS |
| D5 | Frozen/produced/tracked byte identity; 14 sequential children; 35/40 s internal/hard child limits; 600 s attempt; one thread, no GPU; sampled RAM/disk guards | 958 tracked files unchanged; frozen and produced checks unchanged; 14 children, all return code 0; driver 146.18630770000163 s, maximum child 22.829702899965923 s; independent audit zero findings | PASS |

Reference quality is fine estimated error + omitted-width bound + coarse/fine
disagreement, with no unresolved quadrature diagnostic. It is an acceptance
measure built from numerical estimates, not a certified mathematical error bound.
The 54 suites comprise 22 synthetic cases and the first eight frozen cells in
each of four grids. Their transformations and subdivision data were audited.

## Complete coverage grids and global consistency

The independent global coarse and fine areas both equal 323.0818752214932 um².
Candidate global raw/reported area is 323.081875221496 um², relative disagreement
8.62111971545935e-15. All complete corrected fractions are in [0,1].

| N | dx (um) | Complete / candidate-evaluated cells | Raw fraction min / max | Maximum closure (um) | Corrections / maximum magnitude |
|---:|---:|---:|---|---:|---|
| 256 | 0.5 | 65,536 / 2,401 | -4.1710370822819566e-17 / 1 | 2.42861286636753e-16 | 2 / 4.1710370822819566e-17 |
| 320 | 0.4 | 102,400 / 3,721 | 0 / 1.0000000000000002 | 2.7755575615628914e-16 | 10 / 2.220446049250313e-16 |
| 400 | 0.32 | 160,000 / 5,625 | 0 / 1.0000000000000002 | 2.662800535624399e-16 | 18 / 2.220446049250313e-16 |
| 500 | 0.256 | 250,000 / 9,025 | 0 / 1 | 2.498001805406602e-16 | 0 / 0 |

| N | Raw and corrected cell-area sums (um²) | Raw and corrected nominal fraction integrals (um²) | Largest of the four relative global differences |
|---:|---:|---:|---:|
| 256 | 323.0818752214959 | 323.0818752214959 | 8.445178496776506e-15 |
| 320 | 323.0818752214956 | 323.081875221496 | 8.62111971545935e-15 |
| 400 | 323.08187522149643 | 323.081875221496 | 1.0028649464922102e-14 |
| 500 | 323.08187522149655 | 323.081875221496 | 1.038053190228779e-14 |

The 18 checks are two candidate-global areas plus four integrals per grid:
raw/corrected cell-area sums and raw/corrected `sum(fraction)*dx_um**2`.
Their distinction retains cell-boundary rounding as well as the nominal
integrals relevant to an eventual field calculation. Support-disjoint cells
were checked against an independent bounding box and required exact zeros.
The 18 comparisons share one global reference and include dependent or equal
quantities; they are not 18 independent replications.

## Six SS32/SS64 comparisons — diagnostics only

Old fractions are recovered as `-dn/0.003` from the six frozen Stage B NPZ
inputs. Below, signed area means candidate minus old sampled area; L1 means
the integral of the absolute coverage difference. Neither is an optical error.
Candidate raw/corrected nominal area is the same displayed value in these cases.

| N / SS | Maximum absolute fraction difference | L1 area difference (um²) | Signed area difference (um²) | Old sampled area (um²) | Candidate area (um²) |
|---|---:|---:|---:|---:|---:|
| 256 / 64 | 0.0017490021199200179 | 0.02495519861242948 | -0.0008884503790332647 | 323.082763671875 | 323.0818752214959 |
| 320 / 64 | 0.0010805053745062132 | 0.021215450793150552 | -0.005781028504079174 | 323.08765625000007 | 323.081875221496 |
| 400 / 64 | 0.002449858485626788 | 0.01642877730870096 | +0.0002752214959490289 | 323.08160000000004 | 323.081875221496 |
| 400 / 32 | 0.002601898072289499 | 0.041855605762830046 | +0.009475221495948963 | 323.0724 | 323.081875221496 |
| 500 / 64 | 0.0017633109986279205 | 0.013656982838756817 | -0.0016127785040438254 | 323.083488 | 323.081875221496 |
| 500 / 32 | 0.004777446756561048 | 0.039472463707710244 | -0.0006207785040439828 | 323.082496 | 323.081875221496 |

## Attempts, costs and limits of the conclusion

| Attempt | Preserved result and correction before the next fresh attempt | Driver seconds |
|---|---|---:|
| 1 | FAIL: fixture 11 reference messages; local-coordinate conditioning corrected | 11.312012099951971 |
| 2 | FAIL: unresolved distinct absolute angles; Decimal angular representation corrected | 10.393704999994952 |
| 3 | FAIL: existing grid deadline; resource-query cadence corrected, limits unchanged | 70.28389789996436 |
| 4 | PASS: complete unchanged protocol and independent retained-data audit | 146.18630770000163 |

The three failures cost 91.98961499991128 s; all four drivers cost
238.1759226999129 s. These totals exclude separately retained launcher,
postrun-audit and bounded resource-diagnostic costs. The compact child cost
extract has null mode/N/batch fields; no workload attribution is inferred from them.
The accepted CPU environment was Python 3.13.7, NumPy 2.2.6, SciPy 1.15.1,
psutil 6.1.1, six numerical thread settings fixed to 1, and no GPU. RAM >1.5 GiB
and free disk >2 GiB were sampled at worker/row/profile guards; they were not
continuously monitored. Deadlines were also checked before evaluated cells.

Passing supports the fixed fixtures, 192 preselected cells and aggregate
global consistency. Independent cell references do not cover every grid cell;
global area agreement cannot bound a cancelling local error. Decimal predicates,
boundary closure and cancellation diagnostics are not universal correctness
certificates. The reference has its own finite-precision and quadrature limits.
No optical field was propagated in Stage D. The refractive-index profile
remains discretized by cell values even with improved coverage areas.
SS differences do not establish the cause or size of Stage B's failed optical
prediction. The historical Q4 FAIL and Stage B FAIL remain unchanged;
Stage C's separate solver-equivalence
PASS remains separate. **Point 03 remains OPEN.**
