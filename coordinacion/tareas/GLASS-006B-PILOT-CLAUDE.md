# Claude — independent contrast of Codex's actual two-core pilot

Codex now delivers geometry/fields, not just a task list. Read
Docs/GLASS-006B-PILOT-CONTRACT.md, Docs/GLASS-006B-REFINEMENT-CONTRACT.md
and results. Old BPM/coverage frozen; nearD14/farD32/a6/t6/dn-.005/lambda1550nm.
The near cladding is union of outer circles excluding BOTH cores: intentional
carved interaction region, not two unchanged isolated annuli. Gaussian
ports Gram-orthogonalized, NOT guided eigenmodes. No output normalization.

All nine original cases complete. Retain dxFAIL .0065448>.005 and Gaussian
GalerkinFAIL .1628325>.05; no fitted phase/attenuation/kappa. Three finer
cases are a NEW contract, not replacement of original failures.

Please do ONE bounded retained independent contrast first: near_left at
dx0.5um/z1mm/dz2.5um, then near_coherent if safe. Import only NPZ arrays
(allow_pickle=False) from resultados/codex/glass006b_pilot_v1__NAME.npz:
input/output/delta_n/detectors/basis/generator/dx_m/width_m/length_m.
Verify SHA against its corresponding JSON, retain hashes before/after.
Use your ADI in YOUR folder, exact supplied dn/input; recompute complex
<q_i,A> with dx² and core powers/input using the supplied weights.
Freeze field/port/core tolerances before running. Do not align away phase,
renormalize power or replace optical propagation with the retained matrix.
Different sponges explicit; at1mm still no global boundary certificate.
If disagreement, determine whether phase/discretization/domain/profile.
Then propose TRUE coupled/quasi-mode basis and leakage-aware CMT; a
failure of our Gaussian reduction is not a failure of physical coupling.
No need to repeat all12 fields or pause your discrete-cladding search.

Acuse009c/010: read sources/contracts/data.009c is ADI vacuum, not FFT
or arbitrary guided radiation; reflection coefficient remains unmeasured.
010 loss arithmetic agrees, but M4 now uses0.5% vs previous006a1%, and
node layout/stencil changed too: radius-only causal attribution requires
matched-factor control. Bilinear non-Hermitian mode overlap is not bounded
like a Hermitian correlation. Power of mode + rest omits interference:
Ptotal=Pmode+Prest+2Re<mode,rest>. From retained010 at2mm cross terms
are -0.01725 for(10,12,-.003), +0.04411 for(15,10,-.003); include them
before interpreting a ratio>0.9 as exclusive modal content.
Do not change old gates; retain script/data/costs and a reply on the board.
CPU1thread/30s perchild; noGPU window; JEVblocked/localfallback.
