# Point 03, Stage C — sparse ADI equivalence results

Date: 2026-10-06. **PASS for the contracted solver-equivalence audit.**
Point 03 remains **OPEN**: this result neither repairs Stage B's failed
convergence gates nor establishes continuum or physical accuracy.

## Frozen procedure and review

The contract and both implementation files were committed before any
factorization comparison or propagation:
`005dae057df0a264ad8372be905d24644715373a`.

- Contract: [POINT-03-SPARSE-ADI-CONTRACT.md](POINT-03-SPARSE-ADI-CONTRACT.md).
- Candidate: [point03_sparse_adi.py](../scripts/point03_sparse_adi.py).
- Driver: [audit_point03_sparse_adi.py](../scripts/audit_point03_sparse_adi.py).
- Reference: the unchanged definitions in
  [adi2d.py](../experimentos/glass009_claude/adi2d.py).
- Study: [retained C directory](../resultados/codex/point03_sparse_20261006T223947Z/).
- Independent arithmetic audit:
  [independent_audit.json](../resultados/codex/point03_sparse_20261006T223947Z/independent_audit.json).

Internal code review confirmed the block structure, x/y ordering, inherited
ADI equations, independent dense comparisons, resource bounds and evidence
chain. Two retention defects were fixed before the freeze: small inputs are
saved before factorization; rejected permutations carry diagnostics and raw
arrays into the failure report. No acceptance tolerance changed.

These are separate internal implementations and reviews. They are not
replication by an outside laboratory.

## Results against the prospective gates

| Gate | Evidence | Result |
| --- | --- | --- |
| C1 | Four independently assembled dense matrices (N=8 and N=11, x/y), twelve retained solve pairs, line cuts, nonzero counts and residuals | PASS |
| C2 | Six full-trajectory pairs at steps 1, 16 and 64 | PASS |
| C3 | Two full 1600-step optical reproductions using the exact Stage B inputs and reference fields | PASS |
| C4 | CPU-only fixed environment, 18 sequential bounded children, immutable source/input/output inventories, complete chains | PASS |
| Separate postrun arithmetic | C1/C2 residuals and retained pairs, all 16 optical checkpoints, both final fields and powers recomputed without importing any propagation solver | PASS |

All fields were compared as raw complex128 arrays. There was no phase
alignment, fitting, or output renormalization.

| Case | Relative L2 field difference | Relative maximum-norm difference | Absolute total-power difference | Absolute core-power difference |
| --- | ---: | ---: | ---: | ---: |
| N=256, SS64, dz=1.25 um | 4.8607362063250983e-14 | 4.842118448264815e-14 | 2.3092638912203256e-14 | 2.5535129566378600e-15 |
| N=500, SS64, dz=1.25 um | 1.7571345278064465e-14 | 4.5004024181252775e-15 | 1.1324274851176597e-14 | 2.2204460492503131e-16 |

Every C3 limit was 1e-12. The largest C1 normalized infinity residual was
1.2067529895798715e-16 against a 1e-13 limit. The largest small-trajectory
relative L2 difference was 2.8063440030307387e-15. Recorded block leakage
was zero. All four sparse/dense matrix comparisons were exactly equal.

The independent auditor recomputed the recorded quantities with a maximum
difference of **0.0**. It used the saved inputs, dense operators, solve and
trajectory pairs and checkpoint fields, rather than calling either
propagation implementation.

## Execution and resource evidence

- Environment: Python 3.13.7, NumPy 2.2.6, SciPy 1.15.1, psutil 6.1.1.
- One numerical thread; no GPU libraries in the driver.
- Driver wall time: **208.05124439997599 s**, within its 600 s budget.
- Outer launch observed time: 208.2484012999921 s.
- 18 children: two small-profile checks and sixteen optical chunks.
- Each optical chunk completed exactly 200 steps; two chains reached 1600.
- Maximum child wall time: **18.864731499983463 s**, below 40 s.
- Independent postrun wrapper: **5.246883200015873 s**, below 40 s.
- **759** regular tracked files were unchanged.
- **36** factor metadata records had identity row/column permutations.
- Maximum reported Windows process peak working set: **326909952 bytes**.
  This is a per-process peak, not aggregate study memory.
- Available-RAM and free-disk guards passed in the driver; their numerical
  telemetry was not retained, so no minimum available-memory figure is claimed.

| Optical case | Propagation time (s) | Time inside solves (s) | Factor setup time (s) |
| --- | ---: | ---: | ---: |
| N=256 | 45.12564400001429 | 11.586604099255055 | 0.7785451999516226 |
| N=500 | 134.57351150008617 | 48.28810530039482 | 3.0178042000625283 |

These are observed costs from this audit, not a controlled speedup benchmark.
For N=500 the solves account for about 35.9% of the propagation time.
Even removing their cost entirely would leave about 86.29 s, an optimistic
1.56-fold ceiling for a solve-only optimization. Another backend is therefore
reserved for a demonstrated resource need; it is not part of this result.

## Provenance and replay limits

| Artifact | SHA-256 |
| --- | --- |
| Frozen contract | 59629e1689a91b181e7cdad617d16e4e62ebafd0762174e72c62d7dcb2da5a60 |
| Sparse helper | 362d4d0fbb56663f0e05fc211cd0c4db031fe20394367c090fea634134ab48bd |
| Driver | 96e5251f2ac3ef16dd83e7dc1b08f3bb3c2e5256c63732972c6b1cbed7690da5 |
| Audit manifest | c11722129bc5b1e4f90e0afff1429cce9655d5c2f69841a943a0f02e620db13b |
| Independent audit implementation | b86f4d376acbc50e11d1b6eec27e79d54442d35b04865e32db7827dc6e36ca0c |
| Independent audit report | 0d2a3578708c1a5bab53a3d4a142a17156ccb10a9388ecddf7be9d7f9e400f72 |

The independent audit checks the driver's declared tracked inventory and
current bytes, not Git index membership by a second Git command. Successful
raw permutation arrays and native LU objects were not saved: their recorded
identity hashes were checked independently, and the retained field/residual
comparisons provide separate numerical evidence.

The original C outputs are distinguished from the later compact summary,
auditor, packaging files and this report. An exact replay of the strict
postrun output inventory needs the original execution-stage file set, plus
the two named optional summary auxiliaries; later packaging is recorded in
the evidence manifest. Reuse the frozen source commit when reproducing the
historical audit after subsequent tracked documentation changes.

## Scientific interpretation and next work

The candidate is accepted for further numerical work on the tested
finite-dimensional ADI equations, subject to the same source and input
controls. It is an alternative implementation of the same discretization,
not an independent physical solver. Extrapolation to larger grids remains
subject to resource and numerical checks.

The historical GLASS-009d Q4 FAIL and the Stage B prediction/sensitivity FAIL
remain unchanged. Stage D will first test a geometric cell-area construction
against an independent integration procedure. Only a separately frozen later
propagation study can establish whether that change resolves the observed
convergence problem.

Primary implementation references:
[SciPy 1.15.1 splu](https://docs.scipy.org/doc/scipy-1.15.1/reference/generated/scipy.sparse.linalg.splu.html)
and [SuperLU.solve](https://docs.scipy.org/doc/scipy-1.15.1/reference/generated/scipy.sparse.linalg.SuperLU.solve.html).
