# Verification of the full paper (paper/full/paper.pdf), 2026-10-13

An independent verifier agent (read-only, did not write the paper) checked the numbers of `paper/full/paper.tex` against the primary files, not against the author's `NUMBERS.md`. It re-ran T24 (`run_t24.py`) and T27 (`run_t27.py`, 1143 s), and both gave results identical to the committed JSON. It checked 50/50 DOIs against Crossref and 3 arXiv identifiers. The internal AI review shares a model family with the authors, so it is not full independence.

**Verdict:** the numbers reproduce. The central claim matches C-T20-DELIMIT v2, and "no device was fabricated or measured" is stated in the abstract, the title page, the scope and the conclusions.

## Corrections applied after the check

| Item | Change |
|---|---|
| D1 | "0.10 nJ per operation" → "per multiply–accumulate (optimistic set)" |
| D2 | Of the five unreachable targets, only one stopped at the iteration limit (two of 60 did) |
| D4 | The SVD layer has twice the 4032 shifters of one mesh |
| D5 | "tens of chips" → "tens to hundreds of chips" |
| D7 | Reference typo "H. d. Riedmatten" → "H. de Riedmatten" |
| S1 | "Tests that could have failed" now states that only two had physically falsifiable criteria (abstract, introduction, conclusions) |
| S2 | The abstract and conclusions state that AI agents designed and ran the tests, with self-recorded timestamps |
| S3 | The conclusions scope the literature verification (one search; two decisive values re-read in full text) |
| S4 | The depth bound is restricted to two-mode elements, and continuously coupled 3D circuits are excluded |
| S5 | The calibration result is scoped (N ≤ 8, exact access; fails at 0.05 rad) |
| S9 | The Linux CI confirmation is cited from the archived run |

Items left for the author's review: D3 (two realizations of the same setting differ, 1.5·10⁻²/1.3·10⁻⁴ against 1.7·10⁻²/1.0·10⁻⁴), D6, D8–D11, S6–S8, S10 and the risks R4–R8 (for example, the 4×4 coupon may be too short to separate 0.13 from 0.35 dB per stage). The abstract is now about 290 words.
