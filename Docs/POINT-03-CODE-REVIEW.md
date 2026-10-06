# Point 03 — internal review of the numerical evidence pipeline

Date: 2026-10-06. This review concerns the Stage B implementation committed
as `552a93a45d1ebdba1fba97033c65b127ea733d9b`. It is an internal code and
method review, not external scientific replication.

## Reviewed sources and scope

- Runner: `scripts/run_point03_refinement.py`, SHA-256
  `fc28de576fea0c69a0a0bebfd68845ccba9794ba7690bf1694a09085507f3880`.
- Separate assessor: `scripts/assess_point03_refinement.py`, SHA-256
  `6af62709ed61523e5aa6080b4790db8778f72a8bf54e7bd793bc03f26d654afc`.
- Prospective contract: `Docs/POINT-03-Q4-REFINEMENT-CONTRACT.md`, SHA-256
  `1cadbf948074434363376a5e4f059c686121d3146fa07831cda8ed8ac3de9036`.

The runner author, a separate assessment author, an additional reviewer
and the coordinating reviewer examined the implementation. The assessment
does not import the runner or propagate fields; it recomputes powers from
the retained complex fields and the recorded detector arrays. Both codes
still belong to the same project and use NumPy. They are not independent
physical experiments or independent wave solvers.

## Findings corrected before input preparation

1. The first runner draft froze only the selected solver and helper files.
   B1 also requires preserving tracked evidence. The final runner records
   SHA-256 maps of every regular tracked file before and after execution;
   the assessor checks equality and rereads their actual bytes.
2. A completed case initially bypassed its intermediate checkpoint chain
   when reused. Reuse now verifies the chain, final checkpoint pointer and
   digest, exact step count and final field identity as well as powers.
3. An interrupted parent could lose its elapsed-cost report. An exclusive
   attempt marker is now written first. KeyboardInterrupt is recorded;
   an attempt without a closing execution report blocks silent resumption
   because its cost is unknown. The 1800-second budget is not reset.
4. The original Q4 diagnostic must include equality. The assessor now uses
   the original non-strict magnitude inequality, while the new scientific
   acceptance still requires differences above the prescribed floor.
5. A missing mandatory SHA must not behave like an optional unchecked
   read. Mandatory hash validation rejects that case explicitly.
6. The contract's auxiliary-sensitivity clause was made quantitative before
   propagation: all four prescribed fine-grid perturbation corners must
   preserve B4-B5. This is a limited robustness screen, not proof of a
   rigorous uncertainty interval or an uncertainty in the observed order.

## Checks completed before propagation

Both scripts passed syntax inspection. The separate assessor passed six
synthetic groups, including known order two and its extrapolated limit;
oversized error indicators; sign changes; nonpositive order and constant
sequences; withheld-grid prediction failure; auxiliary contamination and
a corner failure despite a passing scalar budget; nonfinite/incomplete
data, duplicate JSON keys and a missing mandatory hash.

The synthetic groups were also executed in the actual isolated Windows
environment. The existing regression suite passed all **51 tests**, with
zero failures, errors or skips, in 1.369516399980057 seconds. The six
prepared inputs passed shape, finiteness, unit-input-power, detector-area
and passive-profile checks. Source hashes matched the reviewed bytes.

The complete preflight took 5.435111200029496 seconds; it performed **zero
propagations**. Its [report](../resultados/codex/point03_preflight_20261006T220909702270Z/preflight.json),
[synthetic evidence](../resultados/codex/point03_preflight_20261006T220909702270Z/assessor_self_check.json)
and [regression result](../resultados/codex/point03_preflight_20261006T220909702270Z/regression_suite.json)
are retained with commands and raw logs.

These successful checks establish that the pipeline is ready to test the
optical convergence question. The eight-case scientific result must be
read separately; a software-test PASS cannot make a convergence FAIL pass.
