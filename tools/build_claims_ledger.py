"""Build, validate and render the project claims ledger (guide v2 section 41.3).

Every public statement about the project should come from this ledger. The
script hashes each evidence file at build time, validates the ledger with
agentkit.claims and renders the Markdown table only if the ledger is
consistent. Output paths must be new; earlier ledgers are kept as history.

Usage (from the repository root):
  python -B tools/build_claims_ledger.py --stage final \
      --out Docs/CIERRE-20261012/CLAIMS-LEDGER-<tag>.json --table Docs/CIERRE-20261012/CLAIMS-TABLE-<tag>.md
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agentkit.claims import render_table, validate  # noqa: E402
from agentkit.evidence import sha256_file  # noqa: E402

CLAUDE = "Claude (project agent, Anthropic)"
DEFAULT_HOW = "Recorded result document; see the file for protocol, data and limits."


def ev(kind: str, path: str, produced_by: str = CLAUDE, how: str = DEFAULT_HOW, **extra) -> dict:
    item = {"kind": kind, "path": path, "sha256": sha256_file(ROOT / path),
            "produced_by": produced_by, "how": how}
    item.update(extra)
    return item


def task_requires() -> dict:
    out = {}
    for name in ("tasks.json", "tasks_v2.json"):
        for task in json.loads((ROOT / "agentkit" / name).read_text(encoding="utf-8"))["tasks"]:
            out[task["id"]] = task["requires"]
    return out


def task(tid, scope, status, statement, falsifier, evidence=(), limitations="", next_action="", **extra):
    claim = {"id": tid, "scope": scope, "status": status, "statement": statement,
             "falsifier": falsifier, "evidence": list(evidence), "limitations": limitations,
             "next_action": next_action, "depends_on": REQUIRES.get(tid, [])}
    claim.update(extra)
    return claim


REQUIRES = task_requires()


def claims_baseline() -> list[dict]:
    sim = "simulation"
    return [
        task("T01", "numerical_wave_model", "OPEN",
             "D16 (Q4) spatial convergence of the T96 waveguide model is established, including the F1 fine-grid run, the S16 reserved prediction and a domain study.",
             "F1 unrecoverable without a registered replacement run, or any registered temporal/spatial criterion fails.",
             [ev(sim, "experimentos/glass009d_claude/RESULTADOS-T96-Q4-AUDITORIA.md")],
             "F1 final copy not recovered (last verified count 96/192 fields); the ADI audit retained the historical Q4 and did not close D16.",
             "Operational loss declaration for F1 and a new registered run with a current resource window."),
        task("T02", "numerical_wave_model", "PARTIAL",
             "The modal sweep of the 20 GLASS-006a geometries selects modes with justified residuals and tracked branches.",
             "A selected mode fails its residual or branch tracking, or a 'no mode' case is presented as absence of a physical mode.",
             [ev(sim, "experimentos/glass006a_claude/RESULTADOS-BARRIDO-MODAL.md")],
             "18 cases selected, 2 without selection; P-B4 judged with a declared relative criterion (the absolute one fails by units).",
             "Adjoint modes and eigenvalue condition for leaky cases; publish 'no candidate passed this rule' for the two cases."),
        task("T03", "numerical_wave_model", "PARTIAL",
             "Field, phase, detector and boundary have a joint validity domain for the guide and coupler geometries of the network.",
             "Registered field/phase/return thresholds fail in the common observation region.",
             [ev(sim, "experimentos/frontera_claude/RESULTADOS-ABSORBENTE.md"),
              ev(sim, "experimentos/frontera_claude/RESULTADOS-ABSORBENTE-FASE.md")],
             "1D PML law |r| = R0^sin(theta) holds; vacuum validation of the 009c absorber failed its threshold; guided joint field/phase pending.",
             "New registered study with fixed observation window (guide section 7 targets)."),
        task("T04", "numerical_wave_model", "PARTIAL",
             "Coherent modal decomposition with the cross term and a biorthogonal basis is applied to the leaky GLASS-010 modes.",
             "Balance error or biorthogonality error above registered tolerance on solver data.",
             [ev(sim, "experimentos/glass010_claude/RESULTADOS-DESCOMPOSICION-V2.md")],
             "Exact in the orthonormal and synthetic nonnormal cases; eta > 1 diagnosed as bilinear projection without cross term.",
             "Apply agentkit.numerics.coherent_decomposition with adjoint modes to the retained GLASS-010 fields."),
        task("T05", "measured_material", "BLOCKED",
             "Index profile and geometry of written traces in the actual SK-1310/silica samples are measured with uncertainties.",
             "Measured profile outside the modeled tolerance band.",
             [ev(sim, "Docs/T5-ESTADO-20261011.md")],
             "Ideal budget only; SK1310 article full text (DOI 10.1016/j.optmat.2025.116651) not obtained; no samples.",
             "Laboratory metrology after T13; obtain the article through an authorized route."),
        task("T06", "numerical_wave_model", "PARTIAL",
             "An independent vectorial solver reproduces the HE11/TE01/TM01/HE21 indices and losses of the trench geometry with error below the TE/TM splitting.",
             "Independent method disagrees beyond its error budget, or its error is not below 3e-6 in n_eff.",
             [ev(sim, "experimentos/vectorial_claude/RESULTADOS-VECTORIAL-GEOMETRIA.md")],
             "Layer solver validated for step fibre n_eff; scalar FD error 4.2e-6 is of the order of the 3e-6 TE/TM splitting.",
             "Nedelec FEM or high-precision shooting method as independent contrast."),
        task("T07", "numerical_wave_model", "PARTIAL",
             "The two-guide coupler transfer (complex, with phase) is validated against an independent method on the same profiles.",
             "Transfer mismatch beyond the registered tolerance without phase fitting.",
             [ev(sim, "experimentos/acoplador_claude/CONTRATO-acoplador.md")],
             "GLASS-006b pilot used Gaussian ports; dx and Gaussian-reduction failures retained; modal ports pending.",
             "Modal-port BPM versus CMT contrast at d = 14 and 16 um."),
        task("T08", "numerical_wave_model", "PARTIAL",
             "Bends, crossings and 3D routes have a design envelope (radius, gap, angle, loss, crosstalk, phase error).",
             "Reserved radius or gap prediction outside the envelope.",
             [ev(sim, "experimentos/acoplo_claude/RESULTADOS-ACOPLO.md"),
              ev(sim, "experimentos/curvas_claude/RESULTADOS-curvas-r4.md")],
             "Parallel-guide coupling in model (H-T8-1 fails, H-T8-2 holds); crossing loss unknown (decisive for H-B, see T25).",
             "Simulate and then measure fs-written crossings (T14)."),
        task("T09", "physical_component", "BLOCKED",
             "Deep writing and face-to-face registration errors are measured on fabricated coupons.",
             "Measured registration error above the T07/T10 phase and coupling budget.",
             [ev(sim, "Docs/PROTOCOLOS-BLOQUEADOS-22-TAREAS.md")],
             "Protocol only; no machine or samples.", "Laboratory partner (T28 dossier)."),
        task("T10", "physical_component", "PARTIAL",
             "Phase stability and control meet the registered mean, tail and drift criteria.",
             "H10b fails (95th-percentile ratio 1.68) or measured drift exceeds the control range.",
             [ev(sim, "experimentos/fase_claude/RESULTADOS-FASE.md")],
             "Model only: H10a and H10c hold, H10b fails. A 95th-percentile claim needs >= 59 independent realizations (Wilks 95/95).",
             "Measure phase drift and correlation on fabricated parts."),
        task("T11", "fabricable_design", "PARTIAL",
             "The compiler maps a trained function to a validated, fabricable geometry with reconstructed transfer.",
             "C2 remains failed or the exported geometry fails re-simulation.",
             [ev(sim, "experimentos/compilador_claude/RESULTADOS-COMPILADOR.md")],
             "C1 holds; C2 fails (1.3e-2 to 1.7e-2 vs 5e-3); C3 in 28/36 realizations = 77.8 % (exact 95 % CI 60.8 % to 89.9 %). Geometry export not done.",
             "Geometry export with a calibrated component library; re-simulate."),
        task("T12", "numerical_neural_model", "FAIL",
             "Network F3-b meets its registered hypotheses H-F1 and H-F2.",
             "Registered criteria H-F1 or H-F2 not met.",
             [ev(sim, "Docs/T12-CIERRE-Y-BLOQUEADOS-20261011.md")],
             "Preregistered negative. Majority-class baseline is 52.5 % on the imbalanced test set; the electronic reference did not converge; kit v1 |cos| MZM did not converge (guide v2 section 44).",
             "New registered experiment with converged, gain-matched baselines and balanced metrics."),
        task("T13", "physical_device", "BLOCKED",
             "Calibration coupons and a small network are fabricated, identified and accepted for measurement.",
             "Fabricated parts fail inspection.",
             [ev(sim, "Docs/PROTOCOLOS-BLOQUEADOS-22-TAREAS.md")],
             "No fabrication access.", "T28 fabrication dossier; titular decides on a partner."),
        task("T14", "physical_component", "BLOCKED",
             "Calibrated optical measurements (cutback, transfer matrix, modes) exist for fabricated parts.",
             "Not applicable until data exist.",
             [ev(sim, "Docs/F2-PROTOCOLO-MEDIDA.md")],
             "Protocol frozen; no samples or instruments.", "Blind cutback with custodian (agentkit.blind) once samples exist."),
        task("T15", "physical_system", "BLOCKED",
             "An integrated optical-electronic-control system runs repeatable end-to-end inference.",
             "End-to-end runs fail or drift beyond specification.", [],
             "No hardware.", "After T13 and T14."),
        task("T16", "independent_evaluation", "PARTIAL",
             "A reserved independent task is evaluated once against converged, comparable baselines.",
             "H-D2 remains failed or baselines are not converged and gain-matched.",
             [ev(sim, "experimentos/f3_red_pequena/RESULTADOS-DIGITS.md")],
             "H-D1 and H-D3 hold; H-D2 fails (B = 0.4074 vs 0.90). Digits 0-3 were already used: development control only.",
             "New reserved dataset with a custodian; gain-matched references."),
        task("T17", "physical_system_measurement", "BLOCKED",
             "Whole-system energy and latency are measured against references at equal accuracy.",
             "Measured energy per correct inference not better than the reference.", [],
             "No system. T24 provides only a parametric kill test.", "After T15."),
        task("T18", "physical_system_measurement", "PARTIAL",
             "Scaling law and between-device reproducibility are measured.",
             "Between-device variation exceeds the registered tolerance.",
             [ev("software_test", "resultados/agent/kit_validation_windows_20261012/project_check_windows.txt",
                 how="python -B scripts/check.py on Windows 10, CPython 3.13.7 (51/51)")],
             "Software portability only (CI Windows + Linux); no physical repeatability.", "Multiple chips and lots after T13."),
        task("T19", "scientific_claim", "OPEN",
             "The project has an original contribution verified against the literature.",
             "A verified prior record covers the claimed contribution.",
             [ev(sim, "Docs/NOVEDAD-ESTADO-20261011.md")],
             "No original contribution is established; multilayer 3D fs network in glass (LAMP, 2026) and telecom depressed-cladding (SK1310, 2025) have precedents.",
             "T26 search with verified identifiers; then a narrow, testable claim (T20)."),
        task("T20", "scientific_claim", "OPEN",
             "A single central claim with a decisive, registered test is chosen and supported or refuted by evidence.",
             "The decisive test refutes the chosen claim.",
             [ev(sim, "Docs/CONTRIBUCION-CENTRAL-T20.md")],
             "H1 registered without measurement; its five ambiguities must be amended before measuring.",
             "Choose the headline after T24-T27 (decision record)."),
        task("T21", "external_replication", "BLOCKED",
             "An independent team reproduces the central numerical result from the archived inputs.",
             "The independent rerun disagrees beyond the declared uncertainty.", [],
             "Agreement among project AI agents does not count; no license yet (titular decision).",
             "Reproduction package; license decision by the titular."),
        task("T22", "observed_impact", "OPEN_OBSERVATION",
             "Third parties use, reproduce or build on the results.",
             "No third-party record after a stated observation period.", [],
             "Cannot be produced in a session.", "Keep a dated, verifiable impact log."),
        task("T23", "software", "PASS",
             "The integrity tools of kit v2 (git-anchored preregistration, blind analysis, claims ledger, decision statistics) pass their 29 tests on Windows 10 with the pinned environment, and the 32 kit v1 tests also pass.",
             "Any kit test fails on a supported platform, or a documented attack on prereg/blind/claims succeeds.",
             [ev("software_test", "resultados/agent/kit_validation_windows_20261012/test_v2_windows.txt",
                 how="python -B -m unittest agentkit.test_v2 -v; Windows 10, CPython 3.13.7, NumPy 2.2.6, SciPy 1.15.1, one BLAS thread"),
              ev("software_test", "resultados/agent/kit_validation_windows_20261012/test_v1_windows.txt",
                 how="python -B -m unittest discover -s tests -p test_agentkit.py -v (guide extraction layout)")],
             "Software scope only; the residual prereg limit (a protocol first committed after the data) remains.",
             "Linux confirmation through the agentkit CI workflow."),
        task("T24", "numerical_model", "OPEN",
             "Kill test of H-A: with sourced parameters, the optimistic optoelectronic budget beats a modern digital INT8 reference per MAC at 8 bits.",
             "Optimistic advantage factor versus the modern reference < 1 at N = 64, 8 bits, 1 GS/s.",
             [ev("decision_record", "experimentos/t24_energia_claude/PROTOCOL-T24.json", how="Preregistered protocol, commitment e640f9f")],
             "Protocol registered; parameters being gathered under frozen rules.", "Run after the parameter files are committed."),
        task("T25", "numerical_model", "PASS",
             "In the ideal-algebra model: Clements depth is N and triangular depth 2N - 3 for N = 3..16 (bound N - 1); a planar butterfly layout needs N(N - 1 - log2 N)/2 crossings with 18 on the worst path at N = 16; the butterfly DFT accumulates less splitter error than Clements.",
             "Any of the 7 registered computational criteria fails on rerun.",
             [ev(sim, "resultados/agent/t25_scaling_20261012/results.json",
                 how="python -B experimentos/t25_escalado_claude/run_t25.py (protocol T25 r2, commitment ff1c449)"),
              ev(sim, "resultados/agent/prereg/T25r2_audit.json", how="agentkit.prereg audit --query-server --require-published")],
             "Model only; planar crossing count is an upper-bound layout; crosstalk and geometry not modeled; attempt 1 crashed (retained).",
             "Use with the T26 crossing-loss value (rule I1) in the T20 decision."),
        task("T26", "novelty", "OPEN",
             "State-of-the-art benchmark for H1 and H-B with identifier-verified records.",
             "Fewer than 8 verified records or any unverifiable identifier in the table.",
             [ev("decision_record", "experimentos/t26_estado_arte_claude/PROTOCOL-T26.json", how="Preregistered protocol, commitment e640f9f")],
             "Search running under the frozen strategy.", "Verify identifiers and write the report."),
        task("T27", "numerical_model", "OPEN",
             "Model part of H-C: in-situ recalibration brings the 95/95 upper bound of the infidelity of an N = 8 Clements mesh (sigma 0.02 rad, correlation 0.8) to <= 1e-3 with a median improvement >= 10.",
             "Either registered criterion fails at the primary point.",
             [ev("decision_record", "experimentos/t27_calibracion_claude/PROTOCOL-T27.json", how="Preregistered protocol, commitment 1407c62")],
             "Running.", "Report and audit."),
        task("T28", "fabricable_design", "OPEN",
             "A fabrication and collaboration dossier specifies coupons, chips, measurements and data policy.",
             "The dossier omits a quantity needed by the decisive test.", [],
             "To be written in this closure.", "Write Docs/CIERRE-20261012/T28-FABRICATION-DOSSIER.md."),
        task("T29", "decision", "OPEN",
             "The titular decided on intellectual property and disclosure before new public results.",
             "New results published without a recorded decision.", [],
             "Pending record.", "Record the titular's instruction of 2026-10-12."),
        task("T30", "review", "OPEN",
             "An adversarial review and pre-mortem of the central claim were performed and answered in writing.",
             "Objections unanswered or claim not revised.", [],
             "Pending.", "Red-team review after the T20 decision; external human review remains required."),
    ]


def claims_hypotheses() -> list[dict]:
    return [
        {"id": "C-T19-a", "scope": "novelty", "status": "WITHDRAWN",
         "statement": "A multilayer 3D network written by fs laser in glass is new.",
         "falsifier": "A published prior fs-written multilayer 3D photonic network in glass.",
         "withdrawal_reason": "Cao et al., Nat. Commun. 17, 5476 (2026), DOI 10.1038/s41467-026-72316-9 (LAMP), fs-written in borosilicate.",
         "evidence": [], "limitations": "", "next_action": "Narrower variants only (silica, multi-face registration)."},
        {"id": "C-T19-c", "scope": "novelty", "status": "WITHDRAWN",
         "statement": "The project shows the first fs-written depressed-cladding trench waveguide at 1550 nm.",
         "falsifier": "A prior telecom-band depressed-cladding fs waveguide.",
         "withdrawal_reason": "Zhou et al., Optical Materials 159, 116651 (2025), DOI 10.1016/j.optmat.2025.116651 (SK1310, telecom band).",
         "evidence": [], "limitations": "", "next_action": "Own blind cutback with coupling and propagation separated (H1)."},
        {"id": "C-T20-H1", "scope": "physical_component", "status": "OPEN",
         "statement": "A trench waveguide (core n = 1.444, trench delta n = -0.005, t = 12 um, a = 6 um), written by fs laser in silica, has a total propagation loss <= 0.3 dB/cm at 1550 nm.",
         "falsifier": "Lower bound of the 95 % CI above 0.3 dB/cm (registered F1).",
         "evidence": [ev("decision_record", "Docs/CONTRIBUCION-CENTRAL-T20.md", how="Registered 2026-10-10")],
         "limitations": "Mode, excitation and a single decision rule not yet declared; threshold far above 0.07 dB/cm reported at 1550 nm (Tan et al. 2022).",
         "next_action": "Dated amendment (T26) before any measurement."},
    ]


def build(stage: str) -> dict:
    claims = claims_baseline() + claims_hypotheses()
    if stage == "final":
        from build_claims_final import update  # noqa: E402  (written after results exist)
        claims = update(claims, ev, task)
    return {"schema": 1, "project_agents": ["Claude", "Codex", "JEV"],
            "stage": stage, "built": "2026-10-12", "claims": claims}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("baseline", "final"), required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--table", type=Path, required=True)
    args = parser.parse_args()
    out = args.out if args.out.is_absolute() else ROOT / args.out
    table = args.table if args.table.is_absolute() else ROOT / args.table
    if out.exists() or table.exists():
        raise FileExistsError("Ledger and table paths must be new")
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    ledger = build(args.stage)
    problems = validate(ledger, ROOT)
    out.write_text(json.dumps(ledger, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    if problems:
        print(json.dumps({"consistent": False, "problems": problems}, indent=1, ensure_ascii=False))
        raise SystemExit(2)
    table.write_text(render_table(ledger), encoding="utf-8", newline="\n")
    counts = {}
    for claim in ledger["claims"]:
        counts[claim["status"]] = counts.get(claim["status"], 0) + 1
    print(json.dumps({"consistent": True, "claims": len(ledger["claims"]), "by_status": counts}))


if __name__ == "__main__":
    main()
