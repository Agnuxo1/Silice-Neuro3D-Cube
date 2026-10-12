# T30 · Red team and pre-mortem of C-T20-DELIMIT (2026-10-13)

Reviewer: independent agent (Claude Opus), read-only on `D:\PROJECTS\Silice-Neuro3D-Cube-closure-20261012`. JEV not consulted for this review.

**Verdict.** The *direction* of the central claim survives: no energy advantage at N = 64 and no headline 3D advantage. Its **numbers do not hold as stated**. Claim (b)'s 440×/6300× comes from one realization choice (a 2N-stage SVD mesh at 0.35 dB per stage, the same value in both sets). Claim (c)'s "at most 0.18 dB" is not a bound. The manuscript's depth argument is incomplete. Restate (b) as an architecture-independent converter floor and (c) as "crossings alone do not decide".

## 1. Objections

| id | sev. | target | objection | evidence | changes verdict? | fix |
|---|---|---|---|---|---|---|
| O1 | critical | T24, claim (b) | The 2N-stage SVD mesh was chosen after the commitment (`build_params.py`; the protocol only says "mesh excess loss"). It is the lossiest way to build a dense layer, and the optimistic stage loss equals the nominal one (0.35 dB, EAGLE XG at 0.29 dB/cm, 2020). | Recomputed: the "kill vs 2014" rule flips at ≤ 0.131 dB per stage (mesh ≤ 16.7 dB). At 0.07 dB per stage (1.2 cm MZI × T26's own 0.06 dB/cm), optimistic = 98 fJ/MAC: 2.3× **better** than 2014 and 6× worse than 3 nm. A fan-out tree (~12 stages) gives ≈ 80 fJ/MAC (illustrative only). | **Yes** for "DISCARDED" (kill) and for the 440×/6300× magnitudes. **No** for "withdrawn vs modern". | Lead with the robust result: best cited converters plus modulator alone cost **71.6 fJ/MAC = 4.5× the 3 nm macro**, for any optical core at N = 64. Report the 6300× as specific to the SVD mesh, with the 0.13 dB per stage break-even. Use one label: WITHDRAWN (T24 says DISCARDED, T20 says WITHDRAWN). |
| O2 | major | claim (b) wording | "With the most favorable cited components" is false for the dominant term. Only one per-MZI value was found, and it is borosilicate, not silica. | `raw_parameter_search…json`: "optimistic = nominal" for `loss_per_stage_db`. | No | Say "most favorable value found per quantity; the mesh loss is a single 2020 EAGLE XG measurement". |
| O3 | major | claim (c), T25 rule I1 | (i) XC ≤ 0.01 dB is an upper bound at 80°. The S-bend swaps of a planar butterfly cross at shallow angles, where no data exist. (ii) Routing is not modeled. The *same source* (Djogo 2026) reports **0.4–0.5 dB per S-bend** at R = 50 mm, both lateral and vertical. That is 40–50× the crossing bound, and above T25's vertical-transition grid (0–0.1 dB). (iii) The planar layout is not minimal (§2b). | T26 record `djogo2026_jlt`; scratch `butterfly_crossings.py` | Partly. H-B stays non-headline, but "N ≥ 32" becomes N ≥ 64 (57 × 0.01 = 0.57 dB; 26 × 0.01 = 0.26 dB at N = 32), at the edge of rule I1. The 3D gain may even be negative. | Replace "gains at most 0.18 dB" with "crossing loss alone contributes ≤ 0.11–0.18 dB at N = 16; the comparison is dominated by unmeasured routing (bend) losses on both sides". |
| O4 | minor | T20 falsifier of (c) | Logically inverted. A planar layout with *fewer* crossings makes the 3D gain smaller, which confirms "at most", not falsifies it. | T20 text | No | Move this clause to the falsifiers of rule I1 or H-B. |
| O5 | major | manuscript §T25, depth | Two problems. (1) The argument "two phases × ⌊N/2⌋ per layer ⇒ N − 1" omits the output phase screen; without it the arithmetic gives N. It also ignores general U(2) elements, which have 4 parameters. (2) The bound is N − 1 for even N and **N for odd N**. A cylindrical (3D-only) brick wall reaches local rank N² at depth N − 1. So the bold sentence "3D cannot reduce the logical depth" is false by up to one layer. | §2c | No (T20's claim (a) itself is correct) | Use the counting with redundancy: the effective dimension of a D-layer mesh of two-mode elements is ≤ N(D+1) for even N and ≤ N(D+1) − D for odd N. State that 3D can save at most one layer for even N and none for odd N. |
| O6 | minor | T24 digital reference | Best case at 0.5 V, with an unknown toggle convention. At nominal voltage it is about 3× worse (≈ 0.05 pJ). | `digital_references.json` | No. The converter floor is still 1.4× above it, though the margin shrinks from 4.5× to 1.4×. | Report the vs-modern margin as 1.4–4.5× for a lossless core. |
| O7 | minor | T24 leniency | The k = 1 at ½ LSB criterion, an NRZ microring energy used for an 8-bit analog modulator, an ADC with ENOB 7.33, and 0 W static power all favour optics. The "optimistic" set is lenient on electronics and harsh on the mesh. | params files | No (it strengthens the negative) | Say so explicitly. |
| O8 | minor | T24 | 128 stages are used in the loss and 129 in the depth check. | budget.json | No | Unify. |
| O9 | major | framing (T25, T26) | The "7/7 PASS" of T25 consists of software self-consistency checks. T26's criteria are bookkeeping. Neither could fail on the physics, yet the manuscript says "four registered tests could have failed; one did". | protocols | No | Call them verification gates. Only T24 and T27 had falsifiable criteria. |
| O10 | major | H-C (T27) | Tested only at N ≤ 8, with exact matrix access, no loss imbalance, no crosstalk and no drift. σ = 0.05 rad (ΔR ≈ 5 %, a plausible fs-coupler spread) already fails at N = 8. Clements error tolerance worsens with N for Haar targets (Pai et al. 2019). Fixed passive meshes cannot be calibrated at all. | T27 grid | Could flip H-C at N ≥ 16 or with a measured σ ≥ 0.05. Not the central claim (H-C is secondary). | Scope as "N ≤ 8, σ ≤ 0.02 rad, ideal access". Add N = 16/32 and an intensity-only, noisy loop. |
| O11 | major | "decisive test" | The trench cut-back (H1, H1-SOTA) tests none of claims (a)–(c). | T20 | No | Link it: a measured MZI-stage loss ≤ 0.13 dB would falsify the 2014 part of (b). Register that measurement, or call H1 a separate claim. |
| O12 | minor | scope | Material drift. The title says "silica", but the stage loss and heater data are EAGLE XG, and the nominal static power is a silicon-photonics TEC. | params, T26 | No | Say "glass" consistently, or flag each borrowed value. |

## 2. Independent recomputation

All scripts are in `redteam/scratch/`, run with `python -I`, and import nothing from the repository.

**(a) T24 energy** (`t24_recompute.py`). Core lines:

```python
sth = i_n*np.sqrt(fs/2)*(1/fs)/q;  a = 4*k**2*L**2
Ne  = (a + np.sqrt(a**2 + 4*a*sth**2))/2          # k*sqrt(Ne+sth^2) = Ne/(2L)
laser = M*Ne/eta*h*c/lam/(T*wpe);  E = (laser + N*(Emod+Edac) + M*Eadc + P/fs)/(N*M)
```

| | Recomputed | Repository |
|---|---|---|
| Nominal | 1.2042e-9 J/MAC (σ_th 1395.6 e⁻, 1.128e6 photons per detector) | identical |
| Optimistic | 1.0159e-10 J/MAC (σ_th 279.1 e⁻, 353 250 photons); advantage 1.58e-4 / 2.26e-3 | relative difference 1e-16 |
| Max stages | 22 / 77 | match |
| Optimistic, lossless mesh | 75.0 fJ/MAC (advantage 0.214 vs modern, 3.07 vs 2014); converters plus modulator 71.6 fJ | — |
| Lossless break-even N | ≈ 300 | confirmed |
| Break-even stage loss vs 2014 | 0.131 dB | none vs modern |

**(b) Butterfly crossings** (`butterfly_crossings.py`). Layered layouts are evaluated by exact inversion counts, with a DP for the worst path. Bit-permutation orderings are searched exhaustively for N ≤ 32 and by beam search for N = 64.

| N | Repo layout: total / worst | Same family, fixed I/O | Free output order (DFT is output-permuted anyway): total / worst |
|---|---|---|---|
| 8 | 16 / 7 | 16 / 7 | 8 / 4 |
| 16 | 88 / 18 | 88 / 18 | 44 / 11 |
| 32 | 416 / 41 | 416 / 41 | 208 / 26 |
| 64 | 1824 / 88 | — | 912 / ≤ 57 |

The closed form N(N−1−log₂N)/2 is reproduced exactly, and the repository layout is optimal within its family when I/O order is fixed. Freeing the output order halves the total. Known theory: a bounded-degree graph's crossing number is ≥ c·bw² − O(n) (Leighton; Pach–Shahrokhi–Szegedy), and the butterfly bisection width is Θ(N), so any planar layout needs Θ(N²) crossings. Only the constant improves.

**(c) Depth bound** (`depth_rank.py`). Jacobian rank of the general layered U(2) mesh (θ plus full phase screens):

| N | Planar brick wall | Cylindrical brick wall |
|---|---|---|
| 4 | rank 14/16 at D = 3 | 16/16 at D = 3 = N − 1 |
| 6 | 32/36 at D = 5 | 36/36 at D = 5 |
| 8 | 58/64 at D = 7 | 64/64 at D = 7 |
| 5 (odd) | 21/25 at D = 4 | same; both need D = 5 |

So N − 1 is correct for even N and N for odd N, for any two-mode elements, because a common-mode phase commutes with a beam splitter. The planar brick wall needs N. The cylindrical brick wall is locally full-rank at N − 1; its global universality is untested. "Dense" implies surjective because the image is compact.

## 3. Overstatements

- **T20 (b)** "most favorable cited components" (O2). **T20 (c)** "at most 0.18 dB" (O3). "H-B retained for N ≥ 32" depends on the layout.
- **T24** "DISCARDED" and "fails by more than two orders of magnitude" depend on the stage loss (O1). "Even a lossless mesh does not win" holds against the 3 nm reference only; against 2014 it wins 3×.
- **Manuscript abstract (ii)** "stays below 0.18 dB" and **(iii)** "most favorable"; bold "3D cannot reduce the logical depth" (O5); Discussion "robust to the parameter choices we could defend" (false for the stage loss); Process "four tests could have failed" (O9). Better to say "lowest verified value found" than "state of the art" for 0.06 dB/cm.
- **T20 header**: JEV confidences (0.97…) are not evidence and should not read as support.

## 4. Pre-mortem: rejection in one year

1. **Strawman energy test.** A referee shows that the 6300× comes from choosing the lossiest realization with a single 2020 borosilicate MZI loss, that the converter floor (already argued by Hamerly 2019 and McMahon 2023) decides the modern comparison, and that 0.07 dB per stage beats the 2014 reference. Verdict: "known result, fragile numbers".
2. **No advance and no data.** Claim (a) is textbook dimension counting (Reck/Clements). Claims (b) and (c) are parametric, with an assumed U and an upper-bound XC. The only physical test is unrun and unrelated to the claim. Outcome: "insufficient novelty; out of scope for a photonics journal".
3. **Unmodeled physics and process trust.** Routing and bend loss (0.4–0.5 dB per S-bend in the cited source) is ignored. The planar layout is not minimal. Calibration is shown at N ≤ 8 with ideal access. Every test was designed, run and audited by AI agents within about an hour, with self-asserted timestamps and no license. The "integrity framework" is not credited as a contribution.

## 5. Integrity

- **Order.** Protocol commits precede results in all cases:

| Test | Protocol | Frozen inputs or commitment | Results | Note |
|---|---|---|---|---|
| T24 | 23:38:44 | parameters frozen 00:33:31 | budget 00:36:27 | |
| T25 | 23:38:44 → r2 23:40:53 | | 23:42:14 | |
| T26 | 23:38:44 | | 00:21:00 | |
| T27 | 23:44:26 | commitment record 23:44:31 | 00:03:14 | 1056 s run ⇒ started ≈ 23:45:38 |
| T20D | 00:21:00 | commitment 00:21:05 | 00:38:11 | 987 s run ⇒ started ≈ 00:21:44, about 40 s margin; the t = 12 µm pre-solve is disclosed |
| H1-A1 amendment | 00:21:54 | — | — | before any sample |

- **T25 failure retained.** It consists of `t25_scaling_20261012_attempt1_failed/` (2 figures) and `prereg/T25_attempt1_status.json`.
  - The code diff is exactly two `int()` casts.
  - The r2 protocol differs only in its id, JSON formatting and the amendment block.
  - The attempt-1 PNG is byte-identical to the final one (sha256 `f2867a96…`), so the rerun is deterministic and "unopened" is immaterial.
- **Caveats.**
  - Commit times and the `ls-remote` checks are self-recorded; there is no third-party timestamp.
  - The T24 choices (SVD realization, single-mode laser, optimistic = nominal stage loss) were made after the commitment. They are disclosed, but they are researcher degrees of freedom, all pointing against H-A.
  - In the worktree, `paper/` is untracked and README/CITATION are modified but uncommitted.
