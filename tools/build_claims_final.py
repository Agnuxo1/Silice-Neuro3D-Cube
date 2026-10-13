"""Final-stage updates for tools/build_claims_ledger.py (closure of 2026-10-13).

Each update replaces a baseline claim by its state after the registered tests
T24-T27, T20D, the T30 review and
F1R2 (T01), plus the license decision, CI evidence (T23) and the partner
list (T28) of 2026-10-13 (ledger 20261013b). Statements are scoped to their evidence.
"""
from __future__ import annotations

CLAUDE = "Claude (project agent, Anthropic)"
SEARCH = "Search agent (Claude, project agent) under the frozen T26 protocol; decisive values re-read by Claude"


def update(claims: list[dict], ev, task) -> list[dict]:
    lit, sim = "literature_search", "simulation"
    by_id = {c["id"]: i for i, c in enumerate(claims)}

    def put(claim: dict) -> None:
        if claim["id"] in by_id:
            claims[by_id[claim["id"]]] = claim
        else:
            by_id[claim["id"]] = len(claims)
            claims.append(claim)

    t26_evidence = [
        ev(lit, "resultados/agent/t26_sota_20261012/records.json", produced_by=SEARCH,
           how="Frozen search strategy (PROTOCOL-T26.json, commitment e640f9f); 41 queries, 31 records"),
        ev(lit, "resultados/agent/t26_sota_20261012/verification.json",
           how="experimentos/t26_estado_arte_claude/verify_refs.py against Crossref and arXiv (31/31)"),
        ev(lit, "Docs/CIERRE-20261012/T26-STATE-OF-THE-ART.md", how="Report with second-reader checks of R1 and R4"),
        ev("review_record", "resultados/agent/prereg/T26_audit.json", how="agentkit.prereg audit --query-server --require-published")]
    t24_evidence = [
        ev(sim, "resultados/agent/t24_energy_20261012/budget.json",
           how="python -B experimentos/t24_energia_claude/run_t24.py after the parameter files were frozen (fb78678)"),
        ev(sim, "resultados/agent/t24_energy_20261012/sources_verification.json", how="verify_refs.py, 22/22 DOIs"),
        ev("review_record", "resultados/agent/prereg/T24_audit.json", how="agentkit.prereg audit (criterion fails, integrity passes)")]
    t25_evidence = [
        ev(sim, "resultados/agent/t25_scaling_20261012/results.json",
           how="python -B experimentos/t25_escalado_claude/run_t25.py (protocol T25 r2, commitment ff1c449)")]
    t27_evidence = [
        ev(sim, "resultados/agent/t27_calibration_20261012/results.json",
           how="python -B experimentos/t27_calibracion_claude/run_t27.py (commitment 1407c62)"),
        ev("review_record", "resultados/agent/prereg/T27_audit.json", how="agentkit.prereg audit --query-server --require-published")]
    t20d_evidence = [
        ev(sim, "resultados/agent/t20_trench_width_20261013/results.json",
           how="python -B experimentos/t20_diseno_claude/run_trench_width.py (commitment ba039e0)")]

    put(task("T01", "numerical_wave_model", "PARTIAL",
             "D16 (Q4) spatial convergence of the T96 waveguide model is established, including the F1 fine-grid run, the S16 reserved prediction and a domain study.",
             "F1 unrecoverable without a registered replacement run, or any registered temporal/spatial criterion fails.",
             [ev(sim, "experimentos/glass009d_claude/RESULTADOS-T96-Q4-AUDITORIA.md"),
              ev("decision_record", "Docs/CIERRE-20261012/T01-F1-OPERATIONAL-RECORD.md", how="Search record of 2026-10-12"),
              ev(sim, "resultados/agent/f1r2_20261013/integrity_audit.json",
                 how="python -B run_f1r2.py run, then audit (commitment 1c068ec; Codex's worker unchanged, SHA-checked; one CPU thread, 23273 s of 32000 s)"),
              ev(sim, "Docs/CIERRE-20261012/T01-F1R2-RESULTS.md", how="Result report of F1R2"),
              ev("review_record", "resultados/agent/prereg/F1R2_audit.json", how="agentkit.prereg audit --query-server --require-published")],
             "F1 recovered by F1R2: all five registered F1 criteria met at h = 0.35 um (relative field difference 1.35e-5 <= 1e-4; power differences 3.8e-9 and 1.3e-7 <= 1e-6; PSD bounds 4.7e-6 and 8.5e-6 <= 1e-5), integrity audit PASS, 8 resource-guard retries kept; F1R (failed at chunk 22) retained. Time discretization at one mesh only; not a continuous error bound; fields kept outside the repository (hashes committed).",
             "Register the K16 spatial series and the S16 reserved prediction before generating h = 0.28 um; domain study."))
    put(task("T19", "scientific_claim", "OPEN",
             "The project has an original contribution verified against the literature.",
             "A verified prior record covers the claimed contribution.",
             t26_evidence[:3],
             "After T26 no original contribution is established: 3D multilayer fs networks (2026), crossing-free 3D Fourier circuits (2016), programmable fs meshes at 1550 nm (2024) exist. A depressed-cladding loss at 1550 nm was not verified in any record (Zhou 2025 unread).",
             "Read Zhou et al. 2025; the trench-loss test (H1-SOTA) is the only candidate for an original measured result."))
    put(task("T20", "scientific_claim", "PARTIAL",
             "A single central claim with a decisive test is chosen and supported or refuted by evidence.",
             "The decisive test refutes the chosen claim.",
             [ev("decision_record", "Docs/CIERRE-20261012/T20-DECISION.md", how="Decision after T24-T27 with JEV advice (provenance=jev)")],
             "Central claim C-T20-DELIMIT chosen and supported numerically (PASS in numerical scope); the next physical decisive test (H1-SOTA) needs samples.",
             "Fabrication partner (T28) and blind cut-back (T14)."))
    put(task("T24", "numerical_model", "FAIL",
             "Kill test of H-A: with sourced parameters, the optimistic optoelectronic budget beats a modern digital INT8 reference per MAC at 8 bits (N = 64, 1 GS/s).",
             "Optimistic advantage factor versus the modern reference < 1 at the registered point.",
             t24_evidence,
             "Registered negative: optimistic advantage 1.6e-4 (modern, 3 nm INT8) and 2.3e-3 (45 nm, 2014). Mesh realization of a dense layer only.",
             "None for H-A; other architectures need their own protocol."))
    put(task("T25", "numerical_model", "PASS",
             "In the ideal-algebra model: Clements depth is N and triangular depth 2N - 3 for N = 3..16 (bound N - 1); a planar butterfly layout needs N(N - 1 - log2 N)/2 crossings with 18 on the worst path at N = 16; the butterfly DFT accumulates less splitter error than Clements.",
             "Any of the 7 registered computational criteria fails on rerun.",
             t25_evidence + [ev("review_record", "resultados/agent/prereg/T25r2_audit.json", how="agentkit.prereg audit --query-server --require-published")],
             "Model only; planar crossing count is an upper-bound layout; attempt 1 crashed (retained).",
             "Measure crossing and 3D-transition losses (T08, T14)."))
    put(task("T26", "novelty", "PARTIAL",
             "State-of-the-art benchmark for H1 and H-B: 31 identifier-verified records; lowest verified loss at 1550 nm in fused silica 0.06 +/- 0.02 dB/cm (cut-back); lowest verified crossing loss <= 0.01 dB at 80 deg.",
             "An unverifiable identifier in the table, fewer than 8 verified records, or a decisive value contradicted by its source.",
             t26_evidence,
             "Registered review criteria met (audit PASS, see C-T26-SOTA); task closure is blocked by its declared dependency T19 (agentkit/tasks_v2.json). Search by one agent; only the two decisive values were re-read by a second reader.",
             "Re-read Zhou et al. 2025 and Tan et al. 2022 full texts."))
    put({"id": "C-T26-SOTA", "scope": "novelty", "status": "PASS",
         "statement": "Verified state of the art (T26): lowest verified fs-written single-mode loss in fused silica at 1550 nm 0.06 +/- 0.02 dB/cm by cut-back (Ackermann et al. 2025); lowest verified crossing loss <= 0.01 dB at 80 deg (Djogo et al. 2026); 3D fs-written Fourier circuits (2016) and a 3D multilayer photonic neural network in glass (2026) exist.",
         "falsifier": "A decisive value contradicted by its primary source, or an identifier that does not resolve.",
         "evidence": t26_evidence, "limitations": "Absence of a record in this search does not prove absence in the literature.",
         "next_action": "Keep the table current before any priority statement."})
    put(task("T27", "numerical_model", "PARTIAL",
             "Model part of H-C: in-situ recalibration brings the 95/95 upper bound of the infidelity of an N = 8 Clements mesh (sigma 0.02 rad, 80 % shared variance) from 1.5e-2 to 1.3e-4 (threshold 1e-3; median improvement >= 10).",
             "Either registered criterion fails at the primary point on rerun.",
             t27_evidence,
             "Registered model criteria met (audit PASS, see C-HC-model); the task asks for measured error models, which do not exist, and it depends on T12 (FAIL). Fails at sigma 0.05 rad with independent errors (2.3e-3); 8-bit DAC floor about 2e-4.",
             "Measured splitter errors and a measured calibration loop on a fabricated mesh."))
    put(task("T23", "software", "PASS",
             "The integrity tools of kit v2 (git-anchored preregistration, blind analysis, claims ledger, decision statistics) pass their 29 tests and the 32 kit v1 tests pass, on Windows 10 with the pinned environment and in CI on windows-2022 and ubuntu-24.04.",
             "Any kit test fails on a supported platform, or a documented attack on prereg/blind/claims succeeds.",
             [ev("software_test", "resultados/agent/kit_validation_windows_20261012/test_v2_windows.txt",
                 how="python -B -m unittest agentkit.test_v2 -v; Windows 10, CPython 3.13.7, NumPy 2.2.6, SciPy 1.15.1, one BLAS thread"),
              ev("software_test", "resultados/agent/kit_validation_windows_20261012/test_v1_windows.txt",
                 how="python -B -m unittest discover -s tests -p test_agentkit.py -v (guide extraction layout)"),
              ev("software_test", "resultados/agent/kit_validation_ci_20261012/ci_run_38312740345.txt",
                 produced_by="GitHub Actions (workflow agentkit.yml), log retrieved by Claude",
                 how="Run 38312740345 at 48566e4: kit byte-identical to the guide, 32 + 29 tests on windows-2022 and ubuntu-24.04, CPython 3.13.7, hash-checked pinned dependencies")],
             "Software scope only; the residual prereg limit (a protocol first committed after the data) remains.",
             "External timestamp for confirmatory commitments."))
    put(task("T28", "fabricable_design", "PARTIAL",
             "A fabrication and collaboration dossier specifies coupons, chips, measurements, blind analysis and data policy.",
             "The dossier omits a quantity needed by the decisive test.",
             [ev("decision_record", "Docs/CIERRE-20261012/T28-FABRICATION-DOSSIER.md", how="Dossier of 2026-10-12; no laboratory contacted"),
              ev("decision_record", "Docs/CIERRE-20261012/LAB-PARTNERS-20261013.md",
                 how="Candidate partner list of 2026-10-13: 23 candidates scored 1-5 from public sources, 34 DOIs re-fetched from Crossref; nobody contacted"),
              ev("decision_record", "resultados/agent/partners_20261013/partners.json", how="Machine-readable candidate table behind LAB-PARTNERS-20261013.md")],
             "Not reviewed by a laboratory; recipe left to the partner; no candidate scored 5/5.",
             "Titular authorizes a contact (draft emails in LAB-PARTNERS-20261013.md); partner review."))
    put(task("T29", "decision", "PASS",
             "The titular decided on disclosure before new public results: open publication ordered on 2026-10-12, no patent protection requested.",
             "New results published without a recorded titular decision.",
             [ev("decision_record", "Docs/CIERRE-20261012/T29-DISCLOSURE-DECISION.md",
                 produced_by="Francisco Angulo de Lafuente (titular), recorded by Claude", how="Chat instruction of 2026-10-12, quoted verbatim")],
             "Not legal advice; license decided on 2026-10-13 (Apache-2.0, separate claim C-LICENSE).", "None."))
    put(task("T30", "review", "PARTIAL",
             "An adversarial review and pre-mortem of the central claim were performed and answered in writing.",
             "Objections left unanswered or the claim not revised where an objection holds.",
             [ev("review_record", "Docs/CIERRE-20261012/T30-REDTEAM-RESPONSE.md",
                 how="Independent AI red-team report and point-by-point response")],
             "Internal AI review only; the guide requires external human reviewers as well.",
             "External human review of the manuscript (titular authorization)."))

    put({"id": "C-T20-DELIMIT", "scope": "numerical_model", "status": "PASS",
         "statement": "C-T20-DELIMIT v2 (revised after T30). For fs-laser-written waveguide meshes in glass with the component values found: (a) 3D connectivity can save at most one layer of a universal mesh of two-mode elements (bound N - 1 for even N, N for odd N; planar rectangular N; cylindrical 3D N - 1); (b) at N = 64 and 8 bits the converters and modulators alone cost about 72 fJ per MAC, 1.4-4.5 times a 3 nm INT8 macro, independently of the optical core; with the single cited MZI stage loss (0.35 dB) in a 2N-stage SVD mesh the layer needs 0.10 nJ per MAC and would beat a 45 nm MAC only at <= 0.13 dB per stage; (c) crossings alone do not decide a 3D advantage: 11 worst-path crossings at N = 16 cost at most about 0.11 dB at the only verified crossing loss, while the same source reports 0.4-0.5 dB per S-bend.",
         "falsifier": "(a) a mesh of two-mode elements dense in U(N) with fewer layers than stated; (b) verified 8-bit converter plus modulator energies per MAC below the digital reference at N = 64, or a measured fs MZI stage loss making the full layer competitive; (c) a measured net worst-path advantage of a 3D over a planar butterfly of at least 0.4 dB at N = 16.",
         "evidence": t25_evidence + t24_evidence[:1] + t26_evidence[:2] + [
             ev("review_record", "Docs/CIERRE-20261012/T30-REDTEAM-REPORT.md",
                produced_by="Independent AI reviewer (Claude Opus subagent, read-only), 2026-10-13",
                how="Adversarial review with independent recomputation; scripts in resultados/agent/t30_redteam_20261013/")],
         "depends_on": ["T25"],
         "limitations": "Model and literature only; the 440x/6300x full-layer figures rest on one 2020 borosilicate stage-loss value and the SVD realization (chosen after the T24 commitment); crossing loss is an upper bound at 80 deg; first wording superseded (T20-DECISION.md).",
         "next_action": "Measure per-stage MZI loss and series crossings / 3D transitions in fs-written silica (T28 coupons F and B); external human review."})
    put({"id": "C-HA-energy", "scope": "numerical_model", "status": "WITHDRAWN",
         "statement": "A passive optical layer in silica with its electronics needs less energy per MAC than a cited digital reference at equal precision.",
         "falsifier": "Optimistic advantage < 1 in the registered T24 budget.",
         "withdrawal_reason": "T24 registered negative. Robust reason: it fails against the 3 nm INT8 reference even for a lossless optical core (converter floor 1.4-4.5x). The registered kill against the 45 nm reference depends on the mesh stage loss (<= 0.13 dB per stage would reverse it).",
         "evidence": t24_evidence[:1], "limitations": "", "next_action": "None."})
    put({"id": "C-HB-crossings", "scope": "scientific_claim", "status": "OPEN",
         "statement": "For structured transforms with N >= 64, 3D routing removes planar crossings and gives a measurable net loss advantage.",
         "falsifier": "Measured per-crossing loss times worst-path crossings below 0.4 dB at the target N, or 3D transitions costing more than the crossings they remove.",
         "evidence": t25_evidence + t26_evidence[:1],
         "limitations": "Secondary (rule I1 recomputed with free output order: N >= 64, at the edge of the rule); S-bends of 0.4-0.5 dB may cancel the gain; precedent of 3D FFT circuits (Crespi et al. 2016); crossing loss known only as an upper bound.",
         "next_action": "Series-crossing and 3D-overpass coupons (T28 coupon B)."})
    put({"id": "C-HC-model", "scope": "numerical_model", "status": "PASS",
         "statement": "In a model (N <= 8, sigma <= 0.02 rad, ideal transfer-matrix access), in-situ recalibration absorbs correlated splitter errors of 0.02 rad in an 8-mode Clements mesh to a 95/95 infidelity bound of 1.3e-4.",
         "falsifier": "Rerun of T27 fails a registered criterion at the primary point.",
         "evidence": t27_evidence[:1],
         "limitations": "Model only; established practice for fs meshes; not a novelty claim.",
         "next_action": "Physical part in T10/T14/T15."})
    put({"id": "C-T20-H1-A", "scope": "physical_component", "status": "OPEN",
         "statement": "Amended H1 (A1): the HE11 total propagation loss of the trench guide (t = 12 um) at 1550 nm is <= 0.3 dB/cm, judged by the three-zone rule with floor 0.044044 dB/cm (recomputed for the measured profile).",
         "falsifier": "Lower bound of the 95 % CI above 0.3 dB/cm (FALSIFIED) or upper bound below the floor (MODEL_CONTROL_FAIL).",
         "evidence": [ev("decision_record", "Docs/CIERRE-20261012/H1-AMENDMENT-A1-20261013.md", how="Dated amendment before any measurement")],
         "limitations": "Feasibility threshold, not state of the art.", "next_action": "Blind cut-back (T14) after fabrication (T13)."})
    put({"id": "C-T20-H1-SOTA", "scope": "physical_component", "status": "OPEN",
         "statement": "H1-SOTA: the HE11 total propagation loss at 1550 nm of a trench guide with t = 16 um (ideal leakage 0.0020 dB/cm) is <= 0.06 dB/cm, under the same rule.",
         "falsifier": "Lower bound of the 95 % CI above 0.06 dB/cm.",
         "evidence": t20d_evidence + [ev("decision_record", "Docs/CIERRE-20261012/H1-AMENDMENT-A1-20261013.md", how="Dated amendment before any measurement")],
         "limitations": "Needs a margin of hundredths of dB/cm: tens of chips if sigma between chips is 0.02-0.05 dB/cm (T28 table).",
         "next_action": "Pilot of 3 chips to estimate sigma; then the registered number of chips."})
    put({"id": "C-LICENSE", "scope": "decision", "status": "PASS",
         "statement": "The repository has a license chosen by the titular: Apache License 2.0 for the whole repository (code, documents, figures, animations and data), with a NOTICE file.",
         "falsifier": "No license file after the titular's decision, or a license file different from the recorded decision.",
         "evidence": [ev("decision_record", "Docs/CIERRE-20261012/LICENSE-DECISION-20261013.md",
                         produced_by="Francisco Angulo de Lafuente (titular), recorded by Claude",
                         how="Chat instruction of 2026-10-13, quoted verbatim; LICENSE body hash checked against GitHub's Apache-2.0 text")],
         "limitations": "Not legal advice; the earlier CC-BY-4.0 proposal for documents and data (Docs/LICENCIA-PROPUESTA.md) is not applied; cited third-party works are not covered.",
         "next_action": "None."})
    for cid in ("C-T20-H1",):
        if cid in by_id:
            claims[by_id[cid]]["status"] = "WITHDRAWN"
            claims[by_id[cid]]["withdrawal_reason"] = "Superseded by amendment A1 (C-T20-H1-A and C-T20-H1-SOTA), dated 2026-10-13 before any measurement."
    return claims
