# Point 03, Stage A — detector diagnosis results

Date: 2026-10-06. Scope: remeasurement of six preserved final fields;
no new propagation. Point 03 remains OPEN.

## Evidence and result

The prospective [contract](POINT-03-DETECTOR-AUDIT-CONTRACT.md) was committed
as `ae11658` before execution. The implementation is
[`scripts/audit_point03_detector.py`](../scripts/audit_point03_detector.py).
All five audit gates passed in 2.0318803 seconds on one CPU thread.
The [machine-readable report](../resultados/codex/point03_detector_20261006T215200970875Z/summary.json)
retains all metrics, source hashes and current hashes of the six original
arrays. Exact byte copies of those arrays are stored alongside the report.

The historical SSR16 detector was reproduced with absolute error **0.0**
for all six fields. The largest relative area error of the analytic
circle/cell detector was 5.551115123125783e-16. The latter is exact for
circle/cell geometry to numerical precision, but still integrates a
piecewise-constant approximation of optical intensity.

## All T96d measurements

Powers are fractions of the original unit input power at z = 2 mm.

| dx (um) | SSR16 | SSR32 | SSR64 | Analytic circle/cell |
| --- | --- | --- | --- | --- |
| 0.625 | 0.33263167400842963 | 0.33265818312894724 | 0.33263349618037474 | 0.3326400758753467 |
| 0.500 | 0.33223675582032003 | 0.3322468452547463 | 0.3322331730863075 | 0.3322301242147393 |
| 0.400 | 0.33267434735736884 | 0.33266760260353545 | 0.33267219533068204 | 0.33267070420883776 |

The original Q4 magnitude inequality fails with **all four detectors**.
With analytic circle/cell integration, the signed successive changes are
-0.0004099516606074216 and +0.0004405799940984667. Thus detector quadrature
alone does not explain or resolve this failure. The sequence is oscillatory;
it does not establish an asymptotic convergence regime.

The continuous-ring control Cd passes the original magnitude inequality
with all four detectors, but it also changes direction. Its analytic
powers are 0.36342751173273513, 0.3630824377099454 and 0.3631782553035993.
The changes are -0.00034507402278971533 and +0.00009581759365390186.
The old Q4 label must therefore not be read as proof that P itself is
monotonic or that an asymptotic expansion has been demonstrated.

## Interpretation and next experiment

Current hashes authenticate the arrays available for this audit; they do
not retroactively authenticate the historical propagation. Those original
fields also mix physical widths of 128.125 and 128 um. No ordinary
Richardson extrapolation or accepted GCI is reported for them.

The next step is the prospective
[Stage B refinement contract](POINT-03-Q4-REFINEMENT-CONTRACT.md): four new
even grids at fixed nominal width, a fixed analytic detector, and separate
geometry and longitudinal-step controls. The historical Q4 FAIL remains
unchanged regardless of the new experiment's outcome.

The distinction between a small difference, an observed convergence order
and a defensible uncertainty indicator follows the official
[NASA grid-convergence tutorial](https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html)
and the [TMR uncertainty procedure](https://tmbwg.github.io/turbmodels/Papers/uncertainty_summary.pdf).
Neither source validates this optical model or certifies its physical accuracy.
