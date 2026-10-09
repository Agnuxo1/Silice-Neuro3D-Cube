# Point 03 geometry — third attempt resource failure and correction

## Status and scope

The third complete Stage D attempt failed its existing time budget. Stage D
and Point 03 remain OPEN. Its complete and partial results are retained; no
optical propagation was performed. The correction below changes resource
sampling frequency in the driver. Candidate geometry, reference quadrature,
fixtures, selected cells, all tolerances and all time/resource limits remain
unchanged. The next attempt must start fresh and run the entire protocol.

## Frozen execution and retained evidence

- Execution source commit: `67a6debd459c31048235a2866a5de25396c484a7`.
- Directory: `resultados/codex/point03_geometry_20261006T233534Z`.
- Driver SHA-256: `c89d5384f9aa4ef92057ac7ca293da2d817eb530316579f4172ff1a7c50bd651`.
- Candidate SHA-256: `838bfc8e56886ebdfa6597450f17c0a3e135f26f20dbcbbe9e8d1e3bdcfe4622`.
- Reference SHA-256: `b95bf9044d8f6719c13c72dac4fd2bf920762e0a2f6e4ba3479e5270e2d0d1a1`.
- Contract SHA-256: `83b2cd5dcc3d0e225a8394282881a4dc3dd7b22a32fce4b3d728d2f9e7143717`.
- Manifest SHA-256: `36b80e5055c7240cffc52ae813961b79e4e6fffdb726563a33886716bd69314b`.
- Partial N320 NPZ SHA-256: `b1be40c9149ddb1f74d7896bad33692cfbe3788bd95500980187ed16de34bb97`.

All 22 synthetic fixtures and their prescribed invariances completed. The
full N256 grid completed in 29.728449599992018 s. The N320 worker stopped at
cell [173, 159], after 55,519 cells had been completed, of which 2,652 required
candidate geometry. Its error was `Geometry audit wall budget exhausted`.
The existing deadline minus four-second retention reserve triggered the stop.
N320 worker elapsed time was 31.054578899987973 s; partial arrays, diagnostics,
JSON and raw logs were retained. No N400/N500 grid, selected-cell reference
batch or global comparison was run.

The available N320 cells had zero unrepresentable events, maximum boundary
closure 2.7755575615628914e-16 um and six endpoint corrections, whose largest
absolute fraction correction was 2.220446049250313e-16. These are observations
on the partial grid and do not certify the missing cells or Stage D.

The driver took 70.28389789996436 s, including preparation and integrity
checks. Its maximum child time was 31.203079600003548 s. The first three
failed driver attempts together cost 91.98961499991128 s. The driver reports
`tracked_unchanged`, `frozen_unchanged` and `produced_unchanged` as true.

## Independent retained-data audit

The unchanged 352-line read-only auditor was run before modifying the driver.
It imports no geometry or quadrature implementation and only recalculates
metrics from saved arrays and JSON. It found zero integrity findings, zero
science findings and 17 completion findings: Stage D correctly remains FAIL.
Counts were 22 synthetic rows, 22 invariance suites, one complete grid, zero
selected-cell references and zero global comparisons, with three of 14
children launched. Audit elapsed time was 4.830679300008342 s under a 40 s
external limit; the audit child returned 1 for the expected incomplete result.

The sibling `_launch/independent_audit.json` SHA-256 is
`991328060139421729e888ae6fd7d6768b7441b859a09645d880faa39c208a96`.
The original launcher, audit source, audit wrapper, execution record and raw
logs are retained in the same sibling directory. Later current-source hash
mismatches on replay must not be confused with mutation during this attempt.

## Measured cause

A separate bounded diagnostic measured only operating-system resource and
clock queries in the approved environment. It evaluated no geometry, fields
or quadrature. Its source, 100 individual observations per resource variant,
1,000 clock observations, execution record and logs are retained in the
third attempt's sibling `_launch` directory.

| Query | Mean seconds per call | Samples |
|---|---:|---:|
| Monotonic clock | 3.486999776214361e-7 | 1,000 |
| Available memory | 0.009666487996582873 | 100 |
| Free disk | 0.00005749699950683862 | 100 |
| Memory and disk combined | 0.010063704006024637 | 100 |

The diagnostic completed with return code 0 in 1.9818530000047758 s internally
and 2.125525099982042 s externally, within its 25/40 s limits. Resource
thresholds were asserted when queried. Diagnostic source SHA-256:
`246b00699e42190977e8888931e8bcfc191f66e656ae8025efb8acbcbfac8cfa`.
Its `guard_cost.json` SHA-256 is
`296feed94c4c3b237a089f1a18ae4da835cd50b878be49e6f0c5757e7066fd29`.

The old driver queried resources before each row and each evaluated cell.
The 2,401 interior checks in N256 alone would take approximately 24.16 s
at the measured combined mean. This is a diagnostic cost estimate rather
than an attribution from a profiler or a promised speedup for another grid.

## Prospective minimal correction

Keep the full clock/RAM/disk guard before every grid row, the existing
worker entry/exit guards and the existing profile checks. Replace only the
inner candidate-cell full guard with the identical cheap monotonic deadline
condition. Record this schedule explicitly in each grid report.

Available RAM must still exceed 1.5 GiB and free disk 2 GiB. The 35 s internal
worker deadline, four-second retention reserve, 40 s child hard limit,
600 s complete-attempt limit, one-thread environment and 14 sequential
children are unchanged. Main arrays are allocated before the grid traversal;
there are no disk writes in its cell loop. Resource checks remain sampled,
with a bounded row cadence, rather than continuously monitored.

New driver SHA-256:
`1e937e953d7980d572c5ff9ef1406980047a25baddf2d43793ee92d71c0cf3d3`.
Updated launcher's only functional change is the required reviewed driver
hash; launcher SHA-256:
`f04f5001c397c1c877d9a69eff51ff2e258d04b71315e747b1a45e0e58026940`.
Both source files received syntax and static diff review before the next
fresh complete attempt. No test subset was used to accept this correction.
