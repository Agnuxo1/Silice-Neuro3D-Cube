# GLASS-006b pilot v1 — contract before measurements

Question: does a two-intact-core ideal depressed-index geometry transfer
coherent fields reproducibly, and is a two-Gaussian Galerkin reduction adequate?
Local prospective registration: this contract and implementation committed
before any propagation of these cases. No external preregistration service,
IPFS record or paper publication claimed. Results tables remain TBD here.

Model: same frozen scalar paraxial FFT BPM and cell coverage as007V2.
Assumed lambda1550nm/n0=1.444; two cores a6um/t6um/dn=-.005,
centres(+/-D/2,0). D14um near, D32um far. Modified region is the UNION of
outer disks MINUS BOTH cores. Near geometry explicitly carves the overlapping
cladding to leave both cores intact: coupling-region hypothesis, not two
unchanged isolated fibres or a fabrication recipe.16x16midpoint index
coverage,32x32independent area refinement; analytic core/pixel detectors.

Launch/readout basis: amplitude Gaussians waist6um, symmetric Gram inverse
square root. Two orthonormal ports; NOT eigenmodes. Input norm1 only at
launch. No output/step renormalization. Save complex input/output/basis,
index/detectors in NPZ; port amplitudes, core powers/input, total power,
projection residual and numerical sponge loss are separate observables.

Reduction: H=Q^dagger[laplacian/(2beta0)+k0dn]Q using same spectral operator.
Predict c(z)=exp(iHz)c(0), no fitted kappa, phases or attenuation. This
Hermitian two-Gaussian approximation omits leakage outside its basis and
sponge. Report residual generator. Its failure does not refute optical
coupling; success is not true modal CMT validation.

Nine frozen deterministic cases, seed0 (no random sampling):
near_left/near_right/near_coherent:256^2/128um/z1mm/400steps;
coherent input=(qL+i*qR)/sqrt2. far_left and vacuum_left same grid/z/steps;
near_half:256^2/128um/z0.5mm/200steps;
near_dz:256^2/128um/z1mm/500steps;
near_coarse:192^2/128um/z1mm/400steps;
near_wide:256^2/(128*256/192)um/z1mm/400steps (same dx as coarse).
Vacuum sets dn0 but keeps both detectors and same near launch basis.

Acceptance, prospective, distinct scopes:
- operational: all9 outputs retained, child<=30s, unchanged source hashes;
  every child1thread, internal28sdeadline; freeRAM>=1GiB AFTER256MiB reserve;
- geometry: each detector area error<1e-10, fully core cells dn0,
  no additive double-index, modified-area16vs32relative<1e-3;
- conservation: balance<1e-10, basis orthogonality<1e-12;
- linearity: coherent full output relative L2 error<1e-10 against the
  two independently propagated columns; mirror symmetry/reciprocity of
  Gaussian projected transfer entries absolute<1e-8;
- refinements: projected amplitudes and both core powers abs change<.005
  for nominal vs coarse, nominal vs dz, coarse vs wide independently;
- reduction hypothesis: complex Gaussian-port error<.05 for both basis
  inputs near at1mm and near_left at0.5mm. Failure threshold>=.05;
  report separately, NEVER include a fitted phase or renormalized output.
Transfer effect near-vs-far-vs-vacuum is exploratory: no efficacy threshold
or claim of advantage. No combined convergence/absorber/Maxwell guarantee.

Peer009c concerns ADI, not our frozen FFT sponge; do not transplant its
angular thresholds as validated FFT limits. Pilot <=1mm/no tilted launch;
Gaussian angular spectrum still present. Peer010 eigenvalue loss is not a
calibrated Gaussian input efficiency and does not fix the coupler model.

Relevant primary context (not parameter recipes or matched benchmarks):
- https://pmc.ncbi.nlm.nih.gov/articles/PMC7019769/ : depressed-cladding
  couplers with modified interaction region, Tm:YAG/810nm, NOT silica1550nm.
- https://opg.optica.org/josaa/abstract.cfm?uri=josaa-11-3-963 : CMT review;
  Gaussian projection below must not be labelled isolated guided modes.
No literature-wide novelty/SOTA claim. Next independent test: Claude ADI
on these exact retained index/basis arrays, core powers AND complex ports.
JEV securityblocked, no retry; local fallback. No GPU/install/push/merge.
