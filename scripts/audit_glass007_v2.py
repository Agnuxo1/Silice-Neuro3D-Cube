"""Read-only audit of retained V2 results and peer009d gates, no wave solve."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(path):
    report = json.loads(path.read_text(encoding="utf-8"))
    if report["status"] != "completed" or not report["sources_unchanged"] or len(report["cases"]) != 13:
        raise ValueError("incomplete/drifted experiment")
    if len({c["name"] for c in report["cases"]}) != 13:
        raise ValueError("duplicate cases")
    reused = []
    for case in report["cases"]:
        source = (ROOT/case["report_path"]).resolve()
        if not source.is_relative_to(ROOT/"resultados/codex") or digest(source) != case["report_sha256"]:
            raise ValueError("case report identity")
        raw = json.loads(source.read_text(encoding="utf-8"))
        if any(case[k] != value for k, value in raw.items()):
            raise ValueError("case values changed in summary")
        if case["hashes_before"] != case["hashes_after"]:
            raise ValueError("case input mutation")
        for relative, sha in case["hashes_before"].items():
            if relative == "scripts/run_glass007_v2.py" and case.get("reused_without_recomputation"):
                continue  # Frozen old runner is explicitly retained in lineage.
            if digest(ROOT/relative) != sha:
                raise ValueError("current case input mismatch")
        balance = abs(case["input_power"]-case["output_power"]
                      -case["material_removed"]-case["boundary_removed"])/case["input_power"]
        if balance >= 1e-10 or not case["balance_gate"]:
            raise ValueError("energy gate")
        if not 0 <= case["weighted_core_fraction_input"] <= case["output_power"]/case["input_power"] + 1e-12:
            raise ValueError("detector passivity")
        if not case["profile_gate"] or case["detector_area_relative_error"] >= 1e-10:
            raise ValueError("profile/detector gate")
        if case.get("reused_without_recomputation"):
            reused.append(case["name"])
    if len(reused) != report["reused_case_count"] or len(reused) != 4:
        raise ValueError("unexpected lineage")
    peer = json.loads((ROOT/"experimentos/glass009d_claude/resultados009d.json").read_text(encoding="utf-8"))
    peer_q4 = {}
    for kind in ("Cd", "T96d"):
        row = peer[kind]
        diff = abs(row["P_dx0p4"]-row["P_dx0p5"])
        previous = abs(row["P_dx0p5"]-row["P_dx0p625"])
        monotonic = previous >= diff
        if (abs(diff-row["diff_04_05"]) > 1e-14 or monotonic != row["Q4_monotone"]
                or not (diff < .005 and diff/abs(row["P_dx0p5"]) < .1) == row["Q23_PASS"]
                or not all(abs(q) < 1e-3 for q in row["Q1"]) == row["Q1_PASS"]):
            raise ValueError("peer saved gate recomputation")
        peer_q4[kind] = monotonic
    if peer_q4["T96d"] or report["peer_Q4_tracks_pass"] or report["boundary_validated"]:
        raise ValueError("unsupported promotion")
    for gate in report["gates"]:
        if "reference" in gate:
            cases = {c["name"]: c for c in report["cases"]}
            ref = cases[gate["reference"]]["weighted_core_fraction_input"]
            candidate = cases[gate["candidate"]]["weighted_core_fraction_input"]
            absolute = abs(ref-candidate)
            expected = ref >= 1e-6 and absolute < .005 and absolute/abs(ref) < .1
            if abs(absolute-gate["absolute"]) > 1e-14 or expected != gate["pass_"]:
                raise ValueError("own refinement gate")
        elif gate["name"].startswith("peer_adi_"):
            name = gate["name"].removeprefix("peer_adi_")
            key = "Cd" if name.startswith("continuous") else "T96d"
            dx = "P_dx0p4" if name.endswith("dx4") else "P_dx0p5"
            case = next(c for c in report["cases"] if c["name"] == name)
            delta = abs(case["weighted_core_fraction_input"]-peer[key][dx])
            if abs(delta-gate["absolute"]) > 1e-14 or (delta < .005) != gate["pass_"]:
                raise ValueError("peer comparison gate")
        elif gate["name"] == "radial_continuous":
            radial = json.loads((ROOT/"experimentos/glass006a_claude/resultados.json").read_text())["G4"]["radial"]
            case = next(c for c in report["cases"] if c["name"] == "continuous")
            delta = abs(case["weighted_core_fraction_input"]-radial)
            if abs(delta-gate["absolute"]) > 1e-14 or (delta < .003) != gate["pass_"]:
                raise ValueError("radial comparison gate")
        else:
            raise ValueError("unrecognized gate")
    if any(child["elapsed_s"] > 30 or child["rc"] != 0 for child in report["children"]):
        raise ValueError("current operational gate")
    return dict(cases=13, reused=len(reused), new_children=len(report["children"]),
                summary_sha256=digest(path), peer_Q4=peer_q4,
                own_gates_pass=report["own_gates_pass"],
                scope="saved gates/lineage only; no full-boundary or physical-fabrication validation")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    target = args.report.resolve()
    if not target.is_relative_to(ROOT/"resultados/codex"):
        parser.error("own report path required")
    print(json.dumps(audit(target)))
