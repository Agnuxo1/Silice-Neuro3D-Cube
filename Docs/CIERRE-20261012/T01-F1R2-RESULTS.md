# T01 · F1R2 results: D16 fine-mesh time convergence recovered (2026-10-13)

**Result: PASS for all registered criteria of the F1 contract, and the integrity audit passes.** The lost F1 run (Colab, 2026-10-09) is replaced by F1R2, a registered run on one local CPU thread. This closes the *temporal* part of T96/Q4 at h = 0.35 µm. T01 as a whole stays **PARTIAL**: the S16 spatial series, the reserved 0.28 µm mesh and the domain study are still open.

- Protocol: `experimentos/f1r_claude/PROTOCOL-F1R2.json`; commitment `resultados/agent/prereg/F1R2_commitment.json` (commit `1c068ec`, verified on the server before running).
- Code: Codex's numerical worker `scripts/run_point03_d16_fine_time.py`, unchanged and SHA-checked. Orchestration and audit are derived by exact substitutions (`experimentos/f1r_claude/run_f1r.py`, `run_f1r2.py`): new deadline, RAM gate 3 GiB, output folder, and a retry rule for resource-guard failures only.
- Results: `resultados/agent/f1r2_20261013/` (execution, manifest, assessment, integrity audit, per-chunk records, SHA-256 index of the 199 field files kept outside the repository).

| Criterion (F1 contract) | Threshold | F1R2 | Result |
|---|---|---|---|
| Relative field difference, Padé[3/3] 32768 vs Radau[2/3] 65536 (mass norm) | ≤ 1·10⁻⁴ | 1.35·10⁻⁵ | met |
| Power difference, field observable | ≤ 1·10⁻⁶ | 3.8·10⁻⁹ | met |
| Power difference, intensity observable | ≤ 1·10⁻⁶ | 1.3·10⁻⁷ | met |
| PSD discrepancy bound, field | ≤ 1·10⁻⁵ | 4.7·10⁻⁶ | met |
| PSD discrepancy bound, intensity | ≤ 1·10⁻⁵ | 8.5·10⁻⁶ | met |

Run details: 192 chunks (64 Padé + 128 Radau), 23 273 s elapsed (budget 32 000 s), wait 33 s (budget 900 s). There were 8 retries for resource-guard failures caused by RAM spikes from other processes on the shared machine. Every failed attempt is kept as `part###.attemptK.*`, listed in `execution.json["retries"]`, and recomputes the same deterministic chunk.

History kept: F1 (Colab, outputs lost: `T01-F1-OPERATIONAL-RECORD.md`) and F1R (failed at chunk 22 in the RAM guard: `resultados/agent/f1r_20261013_failed/`).

Limits: one mesh (h = 0.35 µm) and a time-discretization test only; these figures are a numerical indicator, not a rigorous continuous error bound; fields are stored outside the repository (hashes committed).
