# Point 03, Stage D — prospective geometric coverage audit

Date: 2026-10-06. This contract must be committed before any candidate or
reference area evaluation. Commit the reviewed implementation before the
first complete attempt. Stage C has passed its separate retained-array
audit; Stage B remains a scientific FAIL and Point 03 remains OPEN.

## Question and scope

Can circular-arc integration compute the cell coverage of the same nominal
96-track union with sufficiently small numerical disagreement against an
independent vertical-integration procedure, so that a later propagation
study need not use SS32/SS64 point sampling for the index profile?

This stage performs geometry and quadrature only. It does not propagate
optical fields, demonstrate spatial convergence, measure material properties
or change the interpretation of earlier failures. Coverage is an analytically
defined area evaluated in floating-point arithmetic, not an exact-real-number
certificate. The tolerances below are prospective local verification choices.

## Fixed geometry and units

Generate the 96 centers with the unchanged
`src/silice/tracks.py::track_centres(per_ring=32)`. Retain the exact serialized
SI centers and SHA, and their converted micrometre coordinates. The nominal
radii are 7.25, 9 and 10.75 um, with 32 disks per ring, middle-ring phase pi/32,
and disk radius 1.25 um.

The region is the union of those disks intersected with the annulus
6 <= radius < 12 um. Preserve this annulus clipping explicitly, including
floating-point tangency effects. Do not use equal-dose rescaling.

Candidate/reference input schema, in micrometres:

```json
{"disks": [[0.0, 0.0, 1.0]], "annulus": null}
```

The real geometry instead has 96 disk triples and
`"annulus": {"center": [0.0, 0.0], "inner": 6.0, "outer": 12.0}`.
An absent annulus means the disk union alone. Empty unions, repeated disks,
contained disks and coincident track/annulus circles are supported test cases.

Use the four even grids N=256,320,400,500, nominal width 128 um:
`dx_um=128.0/N`, `axis_um=(arange(N)-N//2)*dx_um`.
Each cell is centered on that axis with sides at center +/- dx_um/2.
Record the original SI grid spacing and the maximum discrepancy caused by
SI/um floating-point conversion of the coordinates. Nominal geometric
equivalence does not imply byte identity between unit representations.
Do not recenter the array or introduce an odd-N grid in this stage.

## Candidate construction

The candidate module is `scripts/point03_union_geometry.py`.
It builds the oriented boundary of the complete Boolean region, clips
circular arcs to a cell, and adds the covered segments of the cell's four
counterclockwise sides. Account for multiple overlaps, disconnected
components and holes; pairwise overlap subtraction alone is insufficient.

Treat coincident circles with multiple roles consistently so that a track
coincident with the outer annulus boundary is not counted twice, and a
track coincident with the inner boundary does not create positive area.
Classify the region on the two sides of each unique boundary circle.

Use a local origin and accumulate signed terms with math.fsum. For an arc:

```text
area = cross(q0,q1)/2 + r^2*(angle_span-sin(angle_span))/2
```

Use a stable small-angle evaluation of the final term. Reverse orientation
changes the sign. For a line segment use cross(q0,q1)/2. Record raw area,
signed closure vector, number of arcs/segments and sum of absolute area
contributions. Define cancel_ratio=abs(raw_area)/sum_abs, or 1 when sum_abs=0;
a smaller ratio indicates greater cancellation. It is a diagnostic, not
an error bound.

Use filtered floating-point predicates and a standard-library decimal
fallback for ambiguous signs/intersections. Do not discard features with a
fixed angular epsilon. An unrepresentable ambiguous interval must produce
a retained diagnostic and an unresolved/failing result.

The helper exposes UnionRegion(spec), cell(rect, origin=None),
support_bounds(), global_area(), and JSON-compatible diagnostics. The driver
owns the grid arrays and retains partial results if a cell or worker fails.

## Independent reference

The independently written module is
`scripts/point03_geometry_reference.py`. It must not import the candidate.

At each x, construct the vertical intervals of all intersected disks, merge
their union, intersect with the outer annulus interval, subtract the inner
interval and clip to the cell. Integrate the resulting length. Normalize:

```text
fraction = integral_0^1 L(xmin+u*width)/height du
```

The normalized integrand is in [0,1], so tolerances describe fractions of a
cell rather than SI square metres. Partition at disk extrema, circle-circle
intersection abscissae (including annulus circles), intersections with the
cell's horizontal sides and the cell boundaries.

Use SciPy 1.15.1 quad with full diagnostics and two preselected tolerances:
1e-13 and 2.5e-14. Distribute the absolute tolerance between partition
intervals; use the corresponding relative tolerance. Retain returned error
estimates, convergence messages, evaluation counts and partition information.
Those error estimates are not certified mathematical bounds.

Extremely narrow partition intervals may be omitted only with an explicit
sum-of-widths bound <=1e-14 in normalized coordinates, using the fact that
the integrand is <=1. Record every omission.

Define reference_quality = fine estimated absolute error + omitted-width
bound + abs(fine_fraction-coarse_fraction). Require it <=1e-13 and no
unresolved quadrature diagnostic. Do not silently replace an unresolved
reference by the candidate result or by a favorable alternative.

## D1 — fixed synthetic geometry cases

All listed coordinates and radii are in um. A disk is (cx,cy,r); rect means
(xmin,xmax,ymin,ymax). U denotes the union. A named expected area below is
for the intended analytic configuration, subject to ordinary representation
rounding. Also evaluate every case with the independent reference.

| ID | Disks / annulus | Rectangle | Expected area when available |
| --- | --- | --- | --- |
| empty | no disks | (-2,2,-2,2) | 0 |
| filled | (0,0,10) | (-0.5,0.5,-0.5,0.5) | 1 |
| whole_disk | (0,0,1) | (-2,2,-2,2) | pi |
| half_disk | (0,0,1) | (0,2,-2,2) | pi/2 |
| quarter_disk | (0,0,1) | (0,2,0,2) | pi/4 |
| disjoint_pair | (-0.75,0,0.4), (0.75,0,0.4) | (-1.5,1.5,-1.5,1.5) | 0.32*pi |
| overlapping_pair | (-0.5,0,1), (0.5,0,1) | (-2,2,-2,2) | 4*pi/3+sqrt(3)/2 |
| duplicate | (0,0,1) twice | (-2,2,-2,2) | pi |
| contained | (0,0,1), (0.2,0,0.3) | (-2,2,-2,2) | pi |
| external_tangent | (-1,0,1), (1,0,1) | (-2.5,2.5,-2.5,2.5) | 2*pi |
| near_external_overlap | (-1,0,1), (1-1e-10,0,1) | (-2.5,2.5,-2.5,2.5) | reference |
| near_external_gap | (-1,0,1), (1+1e-10,0,1) | (-2.5,2.5,-2.5,2.5) | reference |
| internal_tangent | (0,0,1), (0.5,0,0.5) | (-2,2,-2,2) | pi |
| triple_overlap | (-0.5,0,1), (0.5,0,1), (0,0.6,1) | (-2,2,-2,2) | reference |
| hole_three | (0.9,0,0.8), (-0.45,+0.45*sqrt(3),0.8), (-0.45,-0.45*sqrt(3),0.8) | (-2,2,-2,2) | reference |
| annulus_filled | (0,0,3); annulus center(0,0), inner1, outer2 | (-3,3,-3,3) | 3*pi |
| annulus_outer_coincident | (0,0,2); same annulus | (-3,3,-3,3) | 3*pi |
| annulus_inner_coincident | (0,0,1); same annulus | (-3,3,-3,3) | 0 |
| cell_corner_tangent | (1.5,1.5,sqrt(0.5)) | (-1,1,-1,1) | 0 |
| wrapped_arc | (1,0,1) | (1.5,2.5,-0.5,0.5) | reference |
| near_empty_cell | (0,0,1) | (1-1e-6,2-1e-6,0,1) | reference |
| near_full_cell | (0,0,0.7070) | (-0.5,0.5,-0.5,0.5) | reference |

For every synthetic case, test reversed disk order, insertion of a duplicate
first disk when nonempty, translation of disks/annulus/rectangle by
(17.25,-11.5), reflection of the whole configuration across the y axis,
a local integration origin offset by (width/7,-height/9) from the cell
center, and subdivision into four equal rectangles.

Require absolute fractional error <=1e-12 against known area and reference;
the reference quality requirement also applies. Every invariance and the
difference between a parent area and the sum of its four subcell areas
must be <=1e-12 times the parent cell area.

## D2 — complete real coverage grids

Construct all four complete N-by-N raw coverage arrays. Outside the proven
support bounding box, zero coverage follows from the geometry; do not
silently leave uncomputed in-support cells at zero.

For every evaluated cell require finite raw coverage in [-1e-12,1+1e-12]
and the maximum absolute component of its signed boundary closure vector
<=1e-11*min(cell_width,cell_height). Only endpoint violations within the
fraction tolerance may be corrected to 0 or 1. Preserve raw values, the
signed correction, its count and maximum magnitude. Larger violations fail.

Save both raw and endpoint-corrected arrays, nominal spacing, support
bounds, completion information and aggregate diagnostics. All array values
must be finite on a complete run.

## D3 — preselected independent checks on real cells

Select 48 unique cells per grid before computing candidate coverage errors:

1. Cells containing the 16 points at radius 6 and angles 2*pi*j/16.
2. Cells containing the 16 points at radius 12 and the same angles.
3. Eight track/track circle-intersection points: remove exact duplicate
   points; sort by (atan2(y,x), hypot(x,y), x, y); choose indices
   floor(k*(M-1)/7), k=0..7, from M sorted points.
4. Choose eight further distinct cells with NumPy PCG64(20261006), reset
   per grid, from unused cells whose centers satisfy 5<=radius<=13.
5. Deduplicate the first three groups while preserving order. If fewer
   than 48 unique cells result after the random group, complete with unused
   cells from that same pool in lexicographic (iy,ix) order.

A physical point maps to index floor(point/dx + N//2 + 0.5), checked to be
in bounds. Record the actual list, reason and geometry before area tests.
Do not substitute a cell because its coverage is 0 or 1, because a test
fails, or because quadrature is difficult.

Split each grid list into two fixed batches of 24. For all 192 cells,
require abs(raw_candidate_fraction-reference_fine_fraction)<=1e-12 and
the reference quality condition. Also compare the saved grid value with
a new candidate evaluation.

For the first eight cells in each grid's frozen list, repeat the complete
invariance and four-subcell checks specified in D1. These are predetermined
geometric verification checks, not additional selected optical results.

## D4 — independent global area and old sampling diagnostics

Compute one independent reference over rectangle (-13,13,-13,13), which
contains the entire annulus. Require its reference quality and compare:

- the candidate's global oriented-boundary area;
- the area from every raw coverage grid;
- the area from every endpoint-corrected coverage grid.

All must agree with the independent global area to relative error <=1e-12.
Retain each comparison, including any failed one.

Using the exact six prepared Stage B input NPZ files, derive old coverage
as -dn/0.003 and report its difference from the corresponding new grid:
maximum absolute coverage difference, integral absolute area difference,
signed area difference and both modified areas. These SS32/SS64 comparisons
are diagnostics, not acceptance gates or measurements of optical error.
A geometric discrepancy alone does not establish the cause of Stage B's
failed power-series prediction.

## D5 — provenance, bounds and failure policy

The driver is `scripts/audit_point03_geometry.py`. Freeze contract,
candidate, reference, driver, source track generator, imported project
geometry definitions, Stage B manifest and its six input NPZ files by SHA.
Record all regular tracked source/evidence files before and after. Require
byte identity throughout the attempt.

Use only the isolated Point 01 CPU environment: Python 3.13.7,
NumPy 2.2.6, SciPy 1.15.1, psutil 6.1.1, one numerical thread, no GPU and
no dependency installation.

Run at most 14 sequential children: one synthetic batch, four complete
grids, eight real-cell reference batches, and one global reference. Each
child has a 35 s internal deadline and 40 s hard timeout. The complete
attempt, including preparation and integrity checks, has a 600 s wall
budget. Require available RAM >1.5 GiB and free disk >2 GiB.

Use a fresh output directory and exclusive files. Preserve inputs, every
completed comparison, raw partial arrays, source/array hashes, stdout,
stderr, execution status and available numerical diagnostics on failure.
Stop after a failed child; do not continue on a favorable subset or resume
automatically. Report costs of all attempts.

An implementation defect may be corrected in a reviewed, committed new
version followed by a fresh complete attempt with the same case set and
acceptance criteria. Retain the failed attempt and explain the correction.
Do not relax a precision gate or reinterpret an unresolved reference as
agreement after seeing its outcome.

## Acceptance and interpretation

D1-D5 must all pass. Review the actual retained results before using the
candidate geometry in a later propagation experiment. Passing supports
these known cases, preselected real cells and global consistency checks;
it does not mean every cell has been checked by an independent algorithm
or provide a certified bound on all floating-point predicates.

Any later propagation study needs its own prospective plan, input identity,
longitudinal controls and convergence assessment. Stage D alone cannot
close Point 03 or reverse the historical Q4 and Stage B failures.

## Primary methodological references

- Hughes and Chraibi, *Calculating Ellipse Overlap Areas* (2011), sections
  on Green integration and circular/elliptical segments:
  https://arxiv.org/abs/1106.3787 .
  This supports the boundary-area method, not a ready-made 96-disk audit.
- CGAL, *2D Regularized Boolean Set-Operations*, orientation and holes:
  https://doc.cgal.org/latest/Boolean_set_operations_2/index.html .
  CGAL is a methodological reference; it is not installed or used here.
- SciPy 1.15.1, *quad*, break points, returned error estimates and narrow
  feature limitations:
  https://docs.scipy.org/doc/scipy-1.15.1/reference/generated/scipy.integrate.quad.html .
