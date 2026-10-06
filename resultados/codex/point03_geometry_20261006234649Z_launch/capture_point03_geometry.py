"""Summarize retained, audited Stage D evidence; never evaluate geometry."""
from pathlib import Path
import hashlib
import json
import sys


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


out = Path(sys.argv[1]).resolve()
launch = Path(str(out) + "_launch")
execution = read(out / "execution.json")
manifest = read(out / "audit_manifest.json")
audit = read(launch / "independent_audit.json")
assert execution["geometry_pass"] and execution["operational_pass"]
assert audit["status"] == "PASS" and not any(audit["errors"].values())
global_report = read(out / "global.json")
grids = []
for n in (256, 320, 400, 500):
    g = read(out / f"grid_n{n}.json")
    keep = ("N", "dx_um", "status", "elapsed_s", "cells_completed",
            "candidate_evaluated_cells", "raw_min", "raw_max", "fraction_min",
            "fraction_max", "max_boundary_closure_um", "endpoint_correction_count",
            "max_absolute_endpoint_correction", "raw_grid_area_um2", "grid_area_um2",
            "nominal_raw_fraction_grid_area_um2", "nominal_fraction_grid_area_um2",
            "profile_diagnostics", "resource_check_schedule", "array_artifacts")
    row = {key: g[key] for key in keep}
    row["unrepresentable_events"] = g["diagnostics"]["unrepresentable_events"]
    grids.append(row)
references = [r for n in (256, 320, 400, 500) for batch in (0, 1)
              for r in read(out / f"reference_n{n}_batch{batch}.json")["reference_records"]]
synthetic = read(out / "synthetic.json")["fixture_reports"]
summary = {
    "schema": "silice.point03-geometry.compact.v1",
    "scope": "Retained-data summary after independent audit. Geometry only; Point 03 remains open.",
    "out_dir": str(out), "manifest_sha256": sha(out / "audit_manifest.json"),
    "execution_sha256": sha(out / "execution.json"),
    "independent_audit_sha256": sha(launch / "independent_audit.json"),
    "source_commit": "da6a8d63a6dae4c057a5a8863fece0925c4462b1",
    "source_commit_basis": "Root recorded the clean freeze commit immediately before this fourth attempt; scientific source hashes are independently retained in the manifest.",
    "environment": execution["environment"],
    "elapsed_s": execution["elapsed_s"], "max_child_elapsed_s": execution["max_child_elapsed_s"],
    "children": len(execution["children"]),
    "child_costs": [{key: c.get(key) for key in ("mode", "N", "batch", "elapsed_s", "returncode")} for c in execution["children"]],
    "tracked_file_count": len(execution["tracked_sha256_before"]),
    "tracked_unchanged": execution["tracked_unchanged"],
    "frozen_unchanged": execution["frozen_unchanged"],
    "produced_unchanged": execution["produced_unchanged"],
    "audit_counts": audit["counts"], "audit_errors": audit["errors"],
    "synthetic_max_absolute_fraction_error": max(r["absolute_fraction_error"] for r in synthetic),
    "synthetic_max_reference_quality": max(r["reference"]["quality_total"] for r in synthetic),
    "reference_max_absolute_fraction_error": max(r["absolute_fraction_error"] for r in references),
    "reference_max_quality": max(r["reference"]["quality_total"] for r in references),
    "global_reference": {key: global_report["reference_global"][key] for key in
                         ("area_fine_um2", "area_coarse_um2", "quality_total", "quality_pass")},
    "global_comparisons": global_report["comparison_records"], "grids": grids,
    "frozen_sha256": manifest["frozen_sha256"],
}
target = launch / "compact_result.json"
with target.open("x", encoding="utf-8", newline="\n") as handle:
    json.dump(summary, handle, indent=2, allow_nan=False)
    handle.write("\n")
print(json.dumps(summary, indent=2, allow_nan=False))
print("COMPACT_SHA256 " + sha(target))
