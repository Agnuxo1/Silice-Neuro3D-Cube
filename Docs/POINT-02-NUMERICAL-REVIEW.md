# Numerical milestone inventory — Point 02

Reviewed on 2026-10-06. Scope: documentary reconciliation of existing GLASS-006a,
GLASS-009c, GLASS-009d and GLASS-010 evidence. Current reports, contracts and README
were read from `D:\PROJECTS\Silice-Neuro3D-Cube-work-20261006`; the retained 006a
and 009d JSON snapshots were also inspected locally. No propagation, parameter
search, solver modification or peer-file change was performed for this inventory.
The statements below describe recorded results, not a new independent rerun.

## Current status

| Milestone | Executed and supported | Failed or still limited |
|---|---|---|
| GLASS-006a | Twenty parameter cases; 18 have a mode under the implemented selection rule. Corrected sign gate G1' passes for those 18. G2 passes in 7/18. G3 passes for four eligible WKB pairs, all at core radius 6 micrometres. G4 records radial/BPM core-power difference 0.0149167, below its 0.03 threshold. | Eleven G2 failures remain; two cases have no selected mode. G3 does not cover the radius-10 cases. The original sign error and the approximately 58-second run exceeding its 30-second operational budget remain historical failures. [S1] |
| GLASS-009d | Partial-area detector and subpixel index coverage implemented. Q1 passes for both profiles at the sampled grids. Q2 continuous-profile change is 9.2610e-5; Q3 96-track change is 4.3759e-4 for dx 0.5 to 0.4 micrometres. Q4 passes for the continuous profile. | Q4 fails for 96 tracks: the preceding change is 3.9492e-4, smaller than 4.3759e-4. The contract forbids declaring convergence when this gate fails. Small sampled differences do not establish convergence order or global convergence. Preparation timeouts remain recorded. [S2] |
| GLASS-009c | Both phases were executed with ADI in vacuum. The second phase establishes configuration-specific complex-field error windows; increasing the domain improves the measured error. C4 domain-benefit checks pass. | First-phase B1 and B5 failures remain. Second-phase C1 fails at 0.05 rad in both tested domains and at 0.08 rad in the nominal domain. Isolated boundary reflection by angle, transfer of the result to guided structures and general boundary certification remain open. [S3] |
| GLASS-010 | Six scalar paraxial radial m=0 cases; M1, M2 and M3 pass. All 24 M4 comparisons pass under this new protocol. M7 passes at four propagation distances for one continuous profile; maximum absolute core-power discrepancy is 0.00132198, below 0.01. | M5 and M6 are reported observables, not pass/fail gates. The selected-mode results do not establish full single-mode operation across angular orders or polarizations. Modal interpretation and interference accounting require qualification. This is not a complete rerun of the 006a parameter sweep. [S4] |

## Exact limits that the status page must retain

### Boundary validation is partial and has already been executed

GLASS-009c measures `E = ||A_num - A_an|| / ||A_an||` in the useful region
`r < 40 micrometres`, without aligning away the phase difference. It therefore
does check the complex field in the stated vacuum problem; describing all phase
validation as absent would be inaccurate. Guided-mode phase and coherent-network
validation remain separate pending work.

At dx 0.5 micrometres and normal incidence, the recorded E < 2% window is about
1.4 mm in the 128-micrometre domain; the field error reaches about 10% at 2 mm.
The 256-micrometre domain passes over the full sampled 2 mm, with maximum error
about 0.725%. At 0.02 rad the nominal-domain window is 1.1 mm; at 0.05 rad it is
0.2 mm; at 0.08 rad it is zero. C3 power checks apply only within their recorded
windows: a true flag with a zero-length window supplies no positive propagation
interval. These windows are not universal optical-device limits. [S3]

### GLASS-010 does not erase the eleven GLASS-006a failures

Of its six physical cases, three already passed 006a G2, two previously failed
and one is new. The two repeated failures are `(a,t,dn)=(10,6,-0.005)` and
`(10,12,-0.003)`; the new case is `(15,10,-0.003)`, with lengths in micrometres.
Nine earlier failed cases are not re-examined.

The Re-gamma threshold changes from 1% to the stricter 0.5%, while the loss
threshold remains relative change <10% or absolute change <0.005 dB/cm.
However, grid geometry, mode matching, parameter variations and aggregation
change: 006a uses the range across configurations divided by their mean;
010 compares each variation with the nominal case. The improved results support
the importance of geometric discretization without isolating it as the sole
cause of every earlier failure. [S1, S4]

### Modal dominance is not exclusive modal occupancy

For `(10,6,-0.005)`, the 010 JSON records remainder core power 0.0241238 at 2 mm
and selected-mode/total ratio 0.965447. This satisfies the protocol's dominance
label; it contradicts the narrative claim that the first four cases contain
only the selected mode after 0.5 mm.

The fields add coherently. Their separately calculated powers do not generally
satisfy `P_total = P_mode + P_rest`; an interference term is required.
Keep the stored numbers and describe their scope correctly. Do not present eta
as a certified physical coupling efficiency, or its values above one as energy
generation. The repository does not establish an exact identification with a
Petermann factor. All quoted dB/cm values remain ideal-model predictions. [S4]

## README/status corrections for Point 02

1. Split the combined GLASS-009c/010 row. Label 009c "executed; partial vacuum
   validation; retained failures" and restrict the passing 010 convergence
   statement to its six selected cases and its own M4 protocol.
2. Preserve `7/18` for 006a, with the denominator explained as selected modes
   from 20 parameter cases. Do not describe eleven historical failures as fixed.
3. Preserve the 96-track Q4 failure and the provisional continuous reference;
   do not promote Q2/Q3 success to global convergence.
4. Replace stale "009c next/not started" entries with the executed-partial
   status. Keep isolated reflection and applicability to guided coherent
   structures listed as unresolved.
5. Keep old peer reports unchanged; record the modal wording qualifications
   above in the current status index instead of rewriting historical evidence.
6. Update the README's stale 29-test badge and structure description to the
   51 CPU tests actually verified in Point 01. Retain the Windows/Python and
   CPU-only scope of that new environment verification.

These are documentary corrections only. No proposed remedy for Point 03 or
later research work is implemented or represented as completed here.

## Source paths (relative to repository root)

- **S1:** `experimentos/glass006a_claude/CONTRACT.md`, `ERRATA.md`,
  `resultados.json`, `run006a.py`; `coordinacion/respuestas/GLASS-006a-CLAUDE.md`.
  The corrected sign is `Im gamma > 0` for decay with `A ~ exp(i gamma z)`.
- **S2:** `experimentos/glass009d_claude/CONTRACT.md`, `resultados009d.json`,
  `ERRATA.md`; `coordinacion/respuestas/GLASS-009d-CLAUDE.md`.
- **S3:** `experimentos/glass009c_claude/CONTRACT.md`, `CONTRACT-2.md`,
  `run009c.py`, `resultados009c.json`, `resultados009c2.json`;
  `coordinacion/respuestas/GLASS-009c-CLAUDE.md`.
- **S4:** `experimentos/glass010_claude/CONTRACT.md`, `run010.py`,
  `resultados010_radial.json`, `out/M7.json`;
  `coordinacion/respuestas/GLASS-010-CLAUDE.md`.
- **Presentation inspected:** `README.md`; the earlier retained
  `coordinacion/CHECKPOINT.md` snapshot still contains stale 009c scheduling text.

Source emphasis: the numerical JSON and prospective gate definitions govern the
status; stronger retrospective wording does not override a failed gate or
expand a result beyond its tested model, observable and parameter cases.
