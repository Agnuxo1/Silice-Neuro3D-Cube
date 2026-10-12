# T01 · F1 operational record (2026-10-12)

**Status of T01: OPEN.** F1 (the D16 fine-grid time-convergence run of 2026-10-09) has no recovered final copy. This record states what was searched, what exists and what a replacement run needs. It does not close T01, does not extend the expired resource window of 2026-10-09 and does not create any result.

## What exists

| Item | Location | State |
|---|---|---|
| F1 input package | `resultados/codex/point03_d16_fine_package_20261009/Silice_D16_F1_20261009.zip` with `manifest.json` | Committed; integrity controls in `resultados/codex/point03_d16_fine_*_controls_20261009.json` |
| Last verified count | `coordinacion/tareas/PLAN-22-TAREAS-20261010.md`, row 1 | 96 of 192 fields at 07:45 UTC on 2026-10-09 |
| C1 cloud results (2026-10-08) | `resultados/codex/point03_d16_cloud_recovery_20261008/` | Recovered; the local download `Silice_D16_C1_resultados_20261008.zip` has the same SHA-256 prefix `154c97d008acb69c` as the committed copy |
| M2 R1 results (2026-10-09) | `resultados/codex/point03_m2_ui_transfer_20261009/` | Recovered; not F1 |

## Searches performed on 2026-10-12

1. Repository worktrees on D: (`Silice-Neuro3D-Cube`, `Silice-Neuro3D-Cube-work-20261006`, the audit clone `.cognition/audit/silice-origin-main`) for `point03_d16_fine*` result folders or export manifests. Only the input package and the control records listed above were found.
2. `D:\PROJECTS` and `E:\Proyecto-concursos` (depth 4) for `*d16*fine*`. Only preparation and contract documents in the 2026-10-06 worktree.
3. The titular's download folder for `Silice*`, `d16*`, `point03*`, `fine*`. It holds the C1 package (twice), the M2 R1 package (three copies) and the C1 notebook, but no F1 result archive.
4. The Colab session was not opened: it needs the titular's browser session and credentials, which agents must not use.

## Conclusion

F1 is an operational loss for this closure: the final fields, if they exist, are only in the titular's Colab or Drive session. No count beyond 96/192 is verifiable. The prefix rule of guide §5.1 applies only if a valid prefix is recovered; none was.

## What a replacement needs (guide §5.1, §5.2)

- A **new identifier** (for example `F1R_20261XXX`), its own protocol, and a resource window approved at the time of the run.
- The unchanged D16 contract of §5.2: h = 0.35 µm, 2 mm, ±64 µm, λ = 1550 nm, n₀ = 1.444, contrast 0.003, Padé[3/3] with 32768 steps and Radau[2/3] with 65536 steps, 512-step chunks, the five criteria and the K16 matrix identified by its SHA-256.
- Resumable checkpoints (`tools/resumable_checkpoint.py` or `agentkit.checkpoint`) so that a lost session leaves a verifiable prefix.
- Results downloaded to D: and committed (or archived with a DOI if larger than 10 MB) before the session ends.

## Action for the titular

If the Colab or Drive session still has the F1 outputs, download the result folder to `D:\PROJECTS` and tell the agents. The existing importer (`scripts/import_point03_d16_fine.py`) and auditor (`scripts/audit_point03_d16_fine_local.py`, or `scripts/audit_point03_d16_fine_partial.py` for a prefix) can then be run without changing the contract.
