# Point 03, Stage D — first attempt and reference conditioning correction

Date: 2026-10-06. Point 03 remains OPEN. This note preserves an unsuccessful
geometry verification attempt and documents a numerical implementation
correction. It does not change the prospective geometry acceptance criteria.

## Retained first attempt

- Frozen implementation commit: `dfff051841cbc0cd736fe053513058ab88f0eab5`.
- Contract SHA256: `83b2cd5dcc3d0e225a8394282881a4dc3dd7b22a32fce4b3d728d2f9e7143717`.
- Results: `resultados/codex/point03_geometry_20261006T231355Z/`.
- External launch evidence: the sibling directory with suffix `_launch`.
- Manifest SHA256: `6c0eb2ebe9217d4f672d16a7f409269d6197293e795ef4a95015946e6508c236`.
- Synthetic report SHA256: `b6949d8eb5d94b8373bc7f0f76dc015c83c8316ac785c50695d39bda65a258fa`.
- Synthetic array SHA256: `41fb87821a469c6b62ca69f79430e1c40d2c94101dd9bc47750f13bc517addac`.

The first ten synthetic cases completed the driver checks. The eleventh,
`near_external_overlap`, stopped the attempt at the independent-reference
quality/message gate. No real grid, real-cell reference batch, global area
comparison or optical propagation was run in this attempt. Its reported
tracked, frozen-input and produced-output before/after checks passed.

Total driver cost, including preparation and integrity checks, was
11.312012099951971 s. The sole child took 6.275504600023851 s; its own measured
worker time was 6.064829199982341 s. This is retained failed-attempt cost,
not a successful geometry benchmark.

The candidate raw fraction was 0.25132741228718336. The reference returned
0.2513274122871761 at the coarse tolerance and 0.2513274122871828 at the fine
tolerance. Fine estimated error was 1.1907142094226682e-14, stability was
6.716849298982197e-15, and the omitted-width bound was zero. Their prescribed
sum, 1.862399139320888e-14, met the numerical quality limit. Nevertheless,
QUADPACK reported roundoff preventing its requested interval accuracy in
both tolerance passes. The contract requires no unresolved message, so the
reference and the complete attempt remain FAIL/indeterminate for acceptance.

The affected normalized intervals were [0.49999999998, 0.49999999999] and
[0.49999999999, 0.5]. Each had width 1.000000082740371e-11, integral about
4.8758064172503196e-17 and estimated error 7.756093887922041e-23. Each pass
used 861 evaluations and 21 QUADPACK subintervals on each affected interval.
The absolute interval budgets were 1.000000082740371e-24 and
2.5000002068509275e-25, respectively.

## Identified conditioning defect and unchanged acceptance

Code review and the retained diagnostics identify an avoidable conditioning
problem: sampling a tiny interval through a global binary64 coordinate near
0.5 loses local resolution. Computing a displacement close to a disk radius
and then subtracting it from that radius can further lose the small positive
distance controlling the lens section. This diagnosis is an inference from
the implementation and saved diagnostics; successful correction still
requires a complete new attempt.

For each existing partition [a,b], use a local integration coordinate
t in [0,1], with u=a+(b-a)t. Preserve this affine coordinate before rounding
away its small increments. The identity

```text
integral_a^b f(u) du = (b-a) integral_0^1 f(a+(b-a)t) dt
```

means that a local absolute request of tau, followed by multiplying both
the result and its error estimate by (b-a), preserves the previous absolute
budget tau*(b-a). The relative request remains tau. The two values of tau
remain 1e-13 and 2.5e-14. Returned diagnostics must state whether QUADPACK
coordinates and local error estimates refer to t or u.

The reviewed implementation revision must preserve the fixed partition,
omission policy, synthetic fixtures, real-cell selection, candidate code,
geometry, quality formula, message rejection, all precision gates and
resource limits. It must be committed before the next complete attempt.
The original attempt is neither resumed nor reclassified as successful.

The new reference SHA256 is
`b95bf9044d8f6719c13c72dac4fd2bf920762e0a2f6e4ba3479e5270e2d0d1a1`.
It forms both interval endpoints and four endpoint-to-circle-extremum gaps
with Fraction before converting the individual gaps to binary64. Local
interpolation uses compensated summation; the discriminant is the product
of the left and right gaps. Ambiguous signs or nonrepresentable operations
use the independent Decimal fallback with the exact affine x coordinate.
The diagnostic field `quadpack_t` retains local QUADPACK coordinates,
values and errors; enclosing interval records retain their normalized
counterparts, the scale, tolerance requests and exact rational x mapping.
The root and a separate reviewer read the complete diff, and AST syntax
validation passed. No new area evaluation preceded this source revision's
commit; numerical efficacy remains subject to the next complete attempt.

SciPy documents the absolute/relative accuracy request, the returned error
estimate and the full-output convergence message separately:
https://docs.scipy.org/doc/scipy-1.15.1/reference/generated/scipy.integrate.quad.html .
An error estimate alone does not override an unresolved convergence message.
