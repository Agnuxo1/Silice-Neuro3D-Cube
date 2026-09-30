# GLASS-006b refinement v2 — new prospective experiment

Motivation observed in retained v1: nine cases completed, coherent linearity
and symmetry PASS, dz/domain PASS, coarse dx FAIL (.0065447984>.005),
two-Gaussian reduction FAIL (.1628325>.05 at1mm). No thresholds changed.
The old numeric_pass and reduction_pass remain FALSE forever.

Freeze this document and wrapper in a local commit before new propagation.
Three new cases, near_left/near_right/near_coherent at320^2/128um/dx0.4um,
z1mm/400steps; SAME ideal D14/a6/t6/dn-.005 geometry,16/32coverage, basis,
old frozen coupler.py, BPM, coverage and pilot run_case. All costs included.
No fitted phases, kappa, attenuation or post-propagation normalization.

Parent read-only: resultados/codex/glass006b_pilot_v1.json and its9NPZs.
Before/after hashes include parent/new wrapper/new contract and old sources.
New outputs use a fresh prefix, three children1thread/internal28s/parent30s;
RAM>=1GiB after256MiBreserve, noGPU. No original case repeated.

Gates: nine original per-case profile/conservation metrics remain retained;
new per-case geometry/balance/basis gates identical. Field linearity relative
L2<1e-10 and projected symmetry/reciprocity abs<1e-8 on the new grid.
Each new case compared with its NOMINAL256^2 counterpart: both projected
complex amplitudes AND both core powers absolute change<.005. Report every
case, not just left. A PASS is fine-grid pair stability, NOT proof of global
convergence or repair of historical coarse gate.
Gaussian reduction error<.05 still tested/reported separately. Independent
ADI and true guided/quasi-mode CMT remain pending. Record null/failing
results; no extra refinement until a different prospective contract.
JEV securityblocked/local fallback, no external preregistration claimed.
