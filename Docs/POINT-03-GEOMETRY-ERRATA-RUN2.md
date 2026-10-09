# Point 03, Stage D — second attempt and angular representation correction

Date: 2026-10-06. Point 03 remains OPEN. The first attempt remains an
indeterminate-reference FAIL, as recorded in POINT-03-GEOMETRY-ERRATA-RUN1.

## Retained second attempt

The second complete attempt used source/evidence commit
`2b29479f19c620ebe97abebbec1e5f9a50e661fe` and the unchanged prospective
geometry contract. Its files are in
`resultados/codex/point03_geometry_20261006T232258Z/`, with external launch
evidence in the sibling `_launch` directory. Manifest SHA256:
`b6aa7e5f06a8ac9c99164233948bbe3bb4ecbebb69a6f2fe4e14f4a0dd4a5b8b`.

The complete 22-case synthetic battery passed after the reference coordinate
conditioning correction. The first real grid, N=256, then stopped at cell
(iy,ix)=(104,121). The grid report records 26,745 completed cells, including
17 candidate evaluations; support-disjoint cells are separately identified.
The retained partial NPZ has SHA256
`502d7cdca516d96117b46453477811c5196a5a99698ce665dab72d8968c6bb3d`.
There is no completed real grid, real-cell reference audit, global area
comparison or optical propagation from this attempt.

The candidate raised `GeometryResolutionError: circle_pair_angles` when
processing these exact serialized input circles, in micrometres:

```text
track:  cx=6.582476545417024e-16, cy=10.75, r=1.25
outer:  cx=0.0, cy=0.0, r=12.0
```

The high-precision incidence predicate found two distinct intersections.
Their absolute `atan2` angles collapsed to the same binary64 value. The
code retained the diagnostic and stopped, as required by the contract;
it did not discard the feature, change the centers or treat a partial grid
as a complete result.

Total driver cost was 10.393704999994952 s. The largest child cost was
3.6151344000245444 s; the grid worker itself recorded 1.5772707000141963 s.
The two failed attempts together used 21.705717099946923 s of driver time,
including preparation and integrity checks. External launcher overhead is
retained separately in each launch result.

An independent postrun auditor read the saved JSON and NPZ files, recomputed
the available metrics and checked the actual current bytes before changing
the candidate source. It found zero integrity discrepancies and zero
numerical discrepancies in the available completed checks: 22 synthetic
cases and 22 invariance suites. Its overall result is FAIL, with 18
completion findings, because only two of fourteen children ran and no real
grid completed. Missing later outputs are expected consequences of the
stop-on-failure policy. This is not acceptance of the incomplete geometry.
The audit used 4.749476300028618 s under a 40 s external limit. Its JSON is
`point03_geometry_20261006T232258Z_launch/independent_audit.json`, SHA256
`f27b708a7b3d1a77952af32e408a19bd18ff56fe075f0441ce8f2ff190a859db`;
the auditor source, command and logs are retained alongside it.

## Correct the angular representation, preserve the geometry and gates

The proposed correction preserves the Boolean disk-union/annulus algorithm
and represents angular events, ordering, sectors and differences with
high-precision Decimal arithmetic. Intersection vectors remain in Decimal
until a high-precision atan2 calculation; converting them first to binary64
would risk losing the separation before calculating the angle.

Arctangent uses a convergent power series after argument reduction, and
cached coherent Decimal constants define pi and a complete turn. The
topological operations must execute in the explicit precision context,
not the default Decimal context. Only after subtracting two angular events
is the preserved arc length converted to binary64 for the existing Green
area and closure summations. Line relationships are cached to bound repeated
work. Decimal diagnostics are serialized as strings when needed.

This is a finite-precision implementation correction, not an exact-real
certificate. A distinct event that still cannot be resolved must continue
to raise a retained failure. No angular epsilon may delete it. No source
coordinates, annulus constraints, fixed cases, reference selection,
precision gates, independent-reference code or resource limits are relaxed.
The corrected implementation will be reviewed and committed before another
fresh complete attempt; the second attempt remains FAIL.

Reviewed candidate revision SHA256:
`838bfc8e56886ebdfa6597450f17c0a3e135f26f20dbcbbe9e8d1e3bdcfe4622`.
The selected representation uses 128 Decimal digits with 144 digits for
arctangent working arithmetic. Half-angle reduction brings the series
argument to at most 1/8. Public cell/global integration calls install the
explicit topology context; importing the module does not calculate angles
or geometry. A nearly complete arc uses its preserved small complement
for the chord and separate full-disk/complementary-segment contributions.
This distinction is made before any span is converted to binary64.

Primary mathematical reference for the arctangent series and addition
identity used in argument reduction:
https://dlmf.nist.gov/4.24 (equations 4.24.3 and 4.24.15).
These identities support the arithmetic construction; the complete Stage D
audit still determines whether this implementation meets its fixed tests.
