# Point 01 — CPU environment reproduction results

Date: 2026-10-06. Status: CLOSED for the tested Windows CPU target.
Contract: `Docs/POINT-01-ENVIRONMENT-CONTRACT.md`, commit `3dc9b8e`.
Executed implementation: `d53d1a020e7968ba73a3a96ba5439186314dda6d`.
Base research revision: `a15025159cf8c67477e8b1020e1cc368586a2cda`.

## Question and method

Can a fresh, isolated installation execute the current CPU suite and a
representative set of research checks without relying on global packages,
changing historical evidence, or concealing expected scientific failures?
The acceptance criteria E1–E8 were committed before execution. Dependencies
were downloaded from PyPI as binary wheels and pinned with SHA-256 hashes.
The actual clean installation used those wheels offline. The online default
is available and code-reviewed, but was not a separate fresh-install trial.

The tested host is Windows 10 x64, CPython 3.13.7. The six exact versions are
NumPy 2.2.6, SciPy 1.15.1, psutil 6.1.1, pip 25.3, setuptools 82.0.1 and
wheel 0.45.1. The environment is `.venv` in the isolated research worktree.
No global package installation, GPU run, remote publication or merge occurred.

## Evidence

Reports are under:
`resultados/codex/env_20261006T212931610919Z_27db3c22/`.

| Criterion | Observed evidence | Result |
|---|---|---|
| E1: isolated, pinned installation | New environment; `environment_reused=false`; six hash-checked wheel versions; no system site packages | PASS |
| E2: actual package installation | Noneditable install; isolated `-I` import from an external temporary directory; all four inspected modules under `.venv`; `pip check` returned 0 | PASS |
| E3: complete CPU suite | 51 discovered methods, 51 executed, zero failures, errors or skips; no torch import | PASS |
| E4: GLASS-004 | Nominal and negative controls passed; peer hashes unchanged; independent/CMT field difference 2.0014830212433607e-16 | PASS |
| E5: GLASS-003 V2 | 15 complete cases; nine comparisons recalculated; balance passed; convergence FAIL and return code 2 retained | PASS as environment reproduction |
| E6: GLASS-007 V2 history | 13 cases, four reused, nine later children; own gates pass; Q4 of T96d remains false; boundary/global claims remain false | PASS as saved-report audit |
| E7: preservation and provenance | 339 tracked files before and after; no changed hash; commands, versions, BLAS and thread settings retained | PASS |
| E8: bounded CPU work | All numerical children below 40 s; one numerical-library thread; failures preserved | PASS |

Bootstrap elapsed time was 69.163 s. Verification took 15.636 s. The CPU
suite itself took 1.419 s; GLASS-004 took 2.304 s; GLASS-003 V2 took 9.095 s.
These are execution records for this host, not comparative performance claims.

Verification report SHA-256:
`76eeac8d11dd2b7612c9b87a98a96796f91fb3a24906b899e8e3981029f1b6ce`.

Dependency lock SHA-256:
`d5dc1a35a876a4059d25f318f551ec0169fc6bf8492e64f284a7b9f957866bf7`.

A separate evidence manifest records every retained output hash. Preflight
records retain the original PowerShell stderr-orchestration failure and the
successful Python-supervised baseline. The former is not a failed scientific
experiment and is not silently discarded.

## Scientific failures remain visible

GLASS-003 V2 still fails two comparisons at delta_n = -0.005:

- Domain 144 to 192 micrometres: absolute core-power difference
  0.0060477191472576575 exceeds the original 0.005 limit.
- Longitudinal-step refinement: absolute difference 0.024204798711249476
  exceeds the same limit.

All 15 balance checks pass. The report does not claim combined convergence.
The historical 96-track Q4 failure is unchanged. Successful installation is
not evidence that these numerical questions have been solved.

## Review and operational correction

An independent assistant reviewed the complete scripts, test runner, frozen
contract and reference BPM producer before execution and found no blocker.
Its post-run review used the primary operator's evidence summary and the
previously inspected code; it did not perform a second measurement or open
the complete raw output again. This is internal code/evidence review, not
external laboratory replication or peer-reviewed publication.

The offline dependency installation took 37.288 s of its initial 40 s budget.
After review, only that installation timeout was increased to 180 s to allow
wheel download and extraction on the online path. This is an operational
correction after the recorded run; no scientific threshold, solver, metric,
case selection or numerical-child timeout changed. The original reports
remain tied to d53d1a0. No extra scientific rerun was needed for that change.

## Closure and next point

Point 01 is closed for this exact platform and verification scope. Other
platforms, a fresh online installation, and reproduction by an external
researcher are not claimed as completed tests. Physical fabrication,
full numerical convergence and GPU performance are outside this closure.

The next authorized point is Point 02: reconcile the project milestone
inventory against the newer local research revision and the retained evidence.

## Primary documentation

- https://pip.pypa.io/en/stable/topics/repeatable-installs/
- https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
