"""Prospective Point 03 D geometry driver; source/AST review only before freeze.

Install beside point03_union_geometry.py and point03_geometry_reference.py.
No optical solver, propagation, fitting, or adaptive cell selection is used.
All writes are fresh retained evidence. The driver owns full-grid loops and
partial retention, independently of the candidate's cell implementation.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "resultados/codex"
CONTRACT = ROOT / "Docs/POINT-03-GEOMETRY-CONTRACT.md"
CANDIDATE = ROOT / "scripts/point03_union_geometry.py"
REFERENCE = ROOT / "scripts/point03_geometry_reference.py"
TRACKS = ROOT / "src/silice/tracks.py"
STUDY = ROOT / "resultados/codex/point03_refinement_20261006T220909702270Z/manifest.json"
THREADS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")
GRIDS = (256, 320, 400, 500)
INPUTS = ((256, 64), (320, 64), (400, 64), (500, 64), (400, 32), (500, 32))
WIDTH_M = 128e-6
KNOWN_FIXTURES = [
    ("empty", [], None, (-2, 2, -2, 2), 0.0),
    ("filled", [(0, 0, 10)], None, (-.5, .5, -.5, .5), 1.0),
    ("whole_disk", [(0, 0, 1)], None, (-2, 2, -2, 2), math.pi),
    ("half_disk", [(0, 0, 1)], None, (0, 2, -2, 2), math.pi / 2),
    ("quarter_disk", [(0, 0, 1)], None, (0, 2, 0, 2), math.pi / 4),
    ("disjoint_pair", [(-.75, 0, .4), (.75, 0, .4)], None, (-1.5, 1.5, -1.5, 1.5), .32 * math.pi),
    ("overlapping_pair", [(-.5, 0, 1), (.5, 0, 1)], None, (-2, 2, -2, 2), 4 * math.pi / 3 + math.sqrt(3) / 2),
    ("duplicate", [(0, 0, 1), (0, 0, 1)], None, (-2, 2, -2, 2), math.pi),
    ("contained", [(0, 0, 1), (.2, 0, .3)], None, (-2, 2, -2, 2), math.pi),
    ("external_tangent", [(-1, 0, 1), (1, 0, 1)], None, (-2.5, 2.5, -2.5, 2.5), 2 * math.pi),
    ("near_external_overlap", [(-1, 0, 1), (1 - 1e-10, 0, 1)], None, (-2.5, 2.5, -2.5, 2.5), None),
    ("near_external_gap", [(-1, 0, 1), (1 + 1e-10, 0, 1)], None, (-2.5, 2.5, -2.5, 2.5), None),
    ("internal_tangent", [(0, 0, 1), (.5, 0, .5)], None, (-2, 2, -2, 2), math.pi),
    ("triple_overlap", [(-.5, 0, 1), (.5, 0, 1), (0, .6, 1)], None, (-2, 2, -2, 2), None),
    ("hole_three", [(.9, 0, .8), (-.45, .45 * math.sqrt(3), .8), (-.45, -.45 * math.sqrt(3), .8)], None, (-2, 2, -2, 2), None),
    ("annulus_filled", [(0, 0, 3)], {"center": [0, 0], "inner": 1, "outer": 2}, (-3, 3, -3, 3), 3 * math.pi),
    ("annulus_outer_coincident", [(0, 0, 2)], {"center": [0, 0], "inner": 1, "outer": 2}, (-3, 3, -3, 3), 3 * math.pi),
    ("annulus_inner_coincident", [(0, 0, 1)], {"center": [0, 0], "inner": 1, "outer": 2}, (-3, 3, -3, 3), 0.0),
    ("cell_corner_tangent", [(1.5, 1.5, math.sqrt(.5))], None, (-1, 1, -1, 1), 0.0),
    ("wrapped_arc", [(1, 0, 1)], None, (1.5, 2.5, -.5, .5), None),
    ("near_empty_cell", [(0, 0, 1)], None, (1 - 1e-6, 2 - 1e-6, 0, 1), None),
    ("near_full_cell", [(0, 0, .7070)], None, (-.5, .5, -.5, .5), None),
]


def stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "_" + uuid.uuid4().hex[:8]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), "Missing/symlink evidence: " + str(path))
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path):
    def reject(value):
        raise ValueError("Nonfinite JSON: " + value)
    return json.loads(Path(path).read_text(encoding="utf-8"), parse_constant=reject)


def write_json(path, data):
    # Preserve nonfinite failure diagnostics explicitly in strict JSON; raw IEEE
    # array values are retained in NPZ, never converted or silently discarded.
    def safe(value):
        if isinstance(value, float) and not math.isfinite(value):
            return {"nonfinite_float": repr(value)}
        if isinstance(value, dict):
            return {key: safe(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [safe(item) for item in value]
        return value
    serialized = json.dumps(safe(data), indent=2, allow_nan=False) + "\n"
    with Path(path).open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(serialized)


def save_npz(path, np, **arrays):
    with Path(path).open("xb") as handle:
        np.savez_compressed(handle, **arrays)


def tracked_snapshot():
    result = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"],
                            shell=False, capture_output=True, timeout=10)
    require(result.returncode == 0, "Git tracked inventory failed")
    inventory = {}
    for relative in result.stdout.decode("utf-8", "surrogateescape").split("\0"):
        if relative:
            path = ROOT / relative
            require(path.exists(), "Missing tracked file: " + relative)
            if path.is_file() and not path.is_symlink():
                inventory[relative] = sha(path)
    return inventory


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, "Cannot load frozen module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def runtime():
    for name in THREADS:
        os.environ[name] = "1"
    import numpy as np
    import scipy
    import psutil
    require(platform.python_version() == "3.13.7" and np.__version__ == "2.2.6"
            and scipy.__version__ == "1.15.1" and psutil.__version__ == "6.1.1",
            "Use frozen Point 01 CPU dependency versions")
    require(Path(sys.prefix).resolve() == (ROOT / ".venv").resolve(), "Use isolated Point 01 CPU environment")
    require("torch" not in sys.modules and "cupy" not in sys.modules, "GPU library imported")
    return np, scipy, psutil


def guard(psutil, out, deadline):
    require(time.monotonic() < deadline, "Geometry audit wall budget exhausted")
    require(psutil.virtual_memory().available > 1.5 * 1024 ** 3, "Available RAM must exceed 1.5 GiB")
    require(shutil.disk_usage(out).free > 2 * 1024 ** 3, "Free disk must exceed 2 GiB")


def memory_metadata(psutil):
    memory = psutil.Process().memory_info()
    return {"rss_current_bytes": memory.rss, "peak_wset_bytes": getattr(memory, "peak_wset", None),
            "scope": "Windows peak working set if available; RSS is a current sample."}


def verify_manifest(path, expected=None):
    if expected is not None:
        require(sha(path) == expected, "Frozen D manifest changed")
    manifest = read_json(path)
    require(manifest["schema"] == "silice.point03-geometry.manifest.v1", "Unknown D manifest schema")
    require(Path(manifest["source_root"]).resolve() == ROOT and Path(manifest["out_dir"]).is_absolute(),
            "Manifest belongs to another source checkout")
    for name, digest in manifest["frozen_sha256"].items():
        require(sha(name) == digest, "Frozen source/input changed: " + name)
    return manifest


def rect_for(plan, iy, ix):
    # D works on the specified binary64 nominal micrometre grid. SI rounding
    # differences are retained as diagnostics, never claimed byte-identical.
    x, y, half = plan["axis_um"][ix], plan["axis_um"][iy], plan["dx_um"] / 2
    return (x - half, x + half, y - half, y + half)


def selected_cells(np, plan, intersections):
    n, axes = plan["N"], plan["axis_um"]
    pool = [(iy, ix) for iy in range(n) for ix in range(n)
            if 5 <= math.hypot(axes[ix], axes[iy]) <= 13]
    require(len(pool) >= 48, "Insufficient fixed annular cell pool")
    requested = []
    def point_cell(x, y):
        ix = math.floor(x / plan["dx_um"] + n // 2 + .5)
        iy = math.floor(y / plan["dx_um"] + n // 2 + .5)
        require(0 <= ix < n and 0 <= iy < n, "Selection outside fixed domain")
        return iy, ix
    for group, radius in (("inner_angles", 6.0), ("outer_angles", 12.0)):
        for j in range(16):
            angle = 2 * math.pi * j / 16
            point = [radius * math.cos(angle), radius * math.sin(angle)]
            requested.append({"group": group, "rank": j, "point_um": point,
                              "cell": point_cell(*point)})
    unique = {(float(point[0]), float(point[1])) for point in intersections}
    ordered = sorted(unique, key=lambda p: (math.atan2(p[1], p[0]), math.hypot(*p), p[0], p[1]))
    require(len(ordered) >= 8, "Insufficient unique original disk intersections")
    ranks = [(j * (len(ordered) - 1)) // 7 for j in range(8)]
    for rank in ranks:
        point = ordered[rank]
        requested.append({"group": "pair_intersections", "rank": rank,
                          "global_polar_angle_rad": math.atan2(point[1], point[0]),
                          "point_um": point, "cell": point_cell(*point)})
    selected, used, duplicates = [], set(), []
    for item in requested:
        cell = tuple(item["cell"])
        if cell in used:
            duplicates.append(item)
            continue
        used.add(cell)
        selected.append(dict(item, iy=cell[0], ix=cell[1], rect_um=rect_for(plan, *cell)))
    available = [(rank, cell) for rank, cell in enumerate(pool) if cell not in used]
    require(len(available) >= 8, "Insufficient unused cells for fixed random selection")
    rng = np.random.Generator(np.random.PCG64(20261006))
    for available_rank in rng.choice(len(available), size=8, replace=False).tolist():
        rank, cell = available[available_rank]
        item = {"group": "seeded_unused_annular_pool", "rank": rank,
                "unused_pool_rank": available_rank, "cell": cell}
        requested.append(item)
        used.add(cell)
        selected.append(dict(item, iy=cell[0], ix=cell[1], rect_um=rect_for(plan, *cell)))
    for rank, cell in enumerate(pool):
        if len(selected) == 48:
            break
        if cell not in used:
            used.add(cell)
            selected.append({"group": "lexicographic_dedup_fill", "rank": rank,
                             "cell": cell, "iy": cell[0], "ix": cell[1], "rect_um": rect_for(plan, *cell)})
    require(len(selected) == len(used) == 48, "Fixed selection failed to produce 48 distinct cells")
    return {"cells": selected, "requested": requested, "duplicates": duplicates,
            "pool_count": len(pool), "intersection_count": len(ordered),
            "selection_scope": "Chosen before area errors: inner16/outer16,8 evenly ranked unique disk intersections ordered by (global atan2,hypot,x,y); dedup preserving order;8 PCG64 ranks from unused row-major radius[5,13] pool; fill to48 with next unused row-major pool cells. Physical point index=floor(point/dx_um+N//2+0.5)."}


def freeze_study(study, out, np, psutil, deadline):
    require(study == STUDY.resolve(), "D requires the original fixed Stage B study")
    require(len(KNOWN_FIXTURES) == 22, "The complete fixed analytic fixture contract is required")
    b = read_json(study)
    require(b["schema"] == "silice.point03-refinement.manifest.v1"
            and Path(b["source_root"]).resolve() == ROOT, "Wrong Stage B source checkout")
    frozen = dict(b["source_sha256"])
    for path in (study, CONTRACT, CANDIDATE, REFERENCE, TRACKS, Path(__file__).resolve()):
        frozen[str(path.resolve())] = sha(path)
    for name, digest in frozen.items():
        require(sha(name) == digest, "Original/frozen source changed before D preparation: " + name)
    sys.path.insert(0, str(ROOT / "src"))
    tracks = importlib.import_module("silice.tracks")
    require(Path(tracks.__file__).resolve() == TRACKS.resolve(), "Imported another tracks module")
    centres = tracks.track_centres(core_radius_m=6e-6, thickness_m=6e-6,
                                  track_radius_m=1.25e-6, per_ring=32, missing_wedge_rad=0.0)
    centres_m = [[float(x), float(y)] for x, y in centres]
    require(len(centres_m) == 96 and all(math.isfinite(v) for c in centres_m for v in c),
            "Original track_centres did not return 96 finite centres")
    centres_um = [[x * 1e6, y * 1e6] for x, y in centres_m]
    spec = {"disks": [[x, y, 1.25] for x, y in centres_um],
            "annulus": {"center": [0.0, 0.0], "inner": 6.0, "outer": 12.0}}
    # Preserve available original coordinates/spec immediately. Any subsequent
    # selection/reference/preparation failure still leaves these exact inputs.
    (out / "inputs").mkdir()
    grids, produced = [], {}
    centres_path = out / "inputs/centres.json"
    write_json(centres_path, {"schema": "silice.point03-geometry.centres.v1",
                             "centres_m": centres_m, "centres_um": centres_um,
                             "centres_m_hex": [[v.hex() for v in c] for c in centres_m],
                             "centres_um_hex": [[v.hex() for v in c] for c in centres_um],
                             "spec_um": spec,
                             "spec_m": {"disks": [[x, y, 1.25e-6] for x, y in centres_m],
                                        "annulus": {"center": [0.0, 0.0], "inner": 6e-6, "outer": 12e-6}},
                             "source_tracks_sha256": frozen[str(TRACKS.resolve())]})
    centres_sha = sha(centres_path)
    frozen[str(centres_path)] = produced[str(centres_path)] = centres_sha
    imported_sources = {}
    for name, module in list(sys.modules.items()):
        filename = getattr(module, "__file__", None)
        if filename and Path(filename).resolve().is_relative_to((ROOT / "src").resolve()):
            path = Path(filename).resolve()
            imported_sources[name] = {"path": str(path), "sha256": sha(path)}
            frozen[str(path)] = imported_sources[name]["sha256"]
    # Only point intersections for selection; no candidate/reference area calls.
    reference = load_module("point03_geometry_selection_reference", REFERENCE)
    intersections = reference.circle_intersections(spec["disks"], deadline=deadline)
    prepared_inputs = []
    for n, samples in INPUTS:
        matches = [item for item in b["prepared_inputs"] if (item["N"], item["profile_samples"]) == (n, samples)]
        require(len(matches) == 1, "Missing/duplicated original B prepared input")
        item = dict(matches[0])
        require(sha(item["input_npz_path"]) == item["input_npz_sha256"], "B prepared input changed")
        frozen[item["input_npz_path"]] = item["input_npz_sha256"]
        prepared_inputs.append(item)
    for n in GRIDS:
        guard(psutil, out, deadline)
        dx = WIDTH_M / n
        axis = (np.arange(n) - n // 2) * dx
        dx_um = 128.0 / n
        axis_um = (np.arange(n) - n // 2) * dx_um
        axes_path = out / "inputs" / f"axes_n{n}.npz"
        save_npz(axes_path, np, axis_m=axis, axis_um=axis_um)
        digest = sha(axes_path)
        frozen[str(axes_path)] = digest
        produced[str(axes_path)] = digest
        plan = {"N": n, "width_m": WIDTH_M, "dx_m": dx, "dx_um": dx_um,
                "axis_m": axis.tolist(), "axis_um": axis_um.tolist(),
                "max_axis_si_conversion_difference_um": float(np.max(np.abs(axis_um - axis * 1e6))),
                "dx_si_conversion_difference_um": dx_um - dx * 1e6,
                "coordinate_scope": "Nominal D micrometre axes; SI-to-um representation differences recorded. No byte identity between unit representations is claimed.",
                "axis_npz_path": str(axes_path), "axis_npz_sha256": digest}
        plan["reference_selection"] = selected_cells(np, plan, intersections)
        grids.append(plan)
    for name, digest in frozen.items():
        require(sha(name) == digest, "Source/input changed during geometric preparation: " + name)
    require("torch" not in sys.modules and "cupy" not in sys.modules, "GPU library imported")
    manifest = {"schema": "silice.point03-geometry.manifest.v1", "source_root": str(ROOT),
                "out_dir": str(out), "created_utc": datetime.now(timezone.utc).isoformat(),
                "study_path": str(study), "study_sha256": sha(study), "frozen_sha256": frozen,
                "centres_m": centres_m, "centres_um": centres_um,
                "centres_path": str(centres_path), "centres_sha256": centres_sha,
                "centres_m_hex": [[v.hex() for v in c] for c in centres_m],
                "centres_um_hex": [[v.hex() for v in c] for c in centres_um],
                "conversion": "Original track_centres binary64 metres serialized verbatim, then each coordinate multiplied by binary64 1e6; no reconstructed angular/radial centre recipe.",
                "spec_um": spec, "grids": grids, "prepared_inputs": prepared_inputs,
                "spec_m": {"disks": [[x, y, 1.25e-6] for x, y in centres_m],
                           "annulus": {"center": [0.0, 0.0], "inner": 6e-6, "outer": 12e-6}},
                "project_imported_sources": imported_sources,
                "known_fixtures": [{"id": name, "spec_um": {"disks": disks, "annulus": annulus},
                                    "rect_um": rect, "expected_area_um2": expected}
                                   for name, disks, annulus, rect, expected in KNOWN_FIXTURES], "seed": 20261006,
                "cell_fraction_tolerance": 1e-12, "reference_quality_tolerance": 1e-13,
                "raw_fraction_guard": [-1e-12, 1 + 1e-12], "closure_relative_tolerance": 1e-11,
                "global_area_relative_tolerance": 1e-12, "planned_children": 14,
                "reference_cells_per_grid": 48, "reference_batch_size": 24,
                "real_invariance_first_cells": 8, "global_reference_rect_um": [-13.0, 13.0, -13.0, 13.0],
                "total_wall_budget_s": 600, "internal_deadline_s": 35, "parent_timeout_s": 40,
                "scope": "Geometric coverage verification only; original B profiles are diagnostics. No optical propagation, Stage B acceptance change, or later-point authorization."}
    return manifest, produced


def cell_metrics(value, rect, closure_scale):
    area = (rect[1] - rect[0]) * (rect[3] - rect[2])
    raw, fraction = float(value["raw_fraction"]), float(value["fraction"])
    correction = float(value["correction"])
    closure = [float(x) for x in value["boundary_closure_um"]]
    require(area > 0 and all(math.isfinite(x) for x in (raw, fraction, correction, *closure)),
            "Nonfinite/invalid candidate cell result")
    require(-1e-12 <= raw <= 1 + 1e-12, "Raw cell fraction outside endpoint guard")
    expected = min(1.0, max(0.0, raw))
    require(fraction == expected and abs(correction - (fraction - raw)) <= 1e-16,
            "Candidate correction must be endpoint clipping only")
    require(abs(float(value["area_raw_um2"]) / area - raw) <= 1e-12,
            "Raw area/fraction mismatch")
    require(len(closure) == 2 and max(abs(x) for x in closure) <= 1e-11 * closure_scale,
            "Candidate boundary does not close within fixed tolerance")
    contribution = float(value["absolute_contribution_sum_um2"])
    ratio = float(value["cancel_ratio"])
    require(math.isfinite(contribution) and contribution >= 0 and math.isfinite(ratio),
            "Invalid contribution/cancellation diagnostic")
    expected_ratio = abs(float(value["area_raw_um2"])) / contribution if contribution else 1.0
    require(abs(ratio - expected_ratio) <= 1e-12, "Cancellation ratio uses wrong convention")
    return raw, fraction, correction, closure


def private_worker(args):
    started = time.monotonic()
    report = {"schema": "silice.point03-geometry.worker.v1", "status": "failed", "gpu_used": False,
              "audit_manifest_sha256": args.audit_sha, "array_artifacts": []}
    try:
        manifest = verify_manifest(args.audit_manifest, args.audit_sha)
        require(args.out_dir.resolve() == Path(manifest["out_dir"])
                and args.prefix.resolve().is_relative_to(args.out_dir.resolve()), "Worker output escapes frozen study")
        np, scipy, psutil = runtime()
        deadline = started + 35
        guard(psutil, args.out_dir, deadline)
        if args.private_synthetic:
            synthetic_worker(args, manifest, np, psutil, deadline, report)
        elif args.private_grid:
            grid_worker(args, manifest, np, psutil, deadline, report)
        elif args.private_reference:
            reference_worker(args, manifest, np, psutil, deadline, report)
        else:
            global_worker(args, manifest, np, psutil, deadline, report)
        verify_manifest(args.audit_manifest, args.audit_sha)
        guard(psutil, args.out_dir, deadline)
        require("torch" not in sys.modules and "cupy" not in sys.modules, "GPU library imported")
        report.update(sources_and_inputs_unchanged=True, memory=memory_metadata(psutil))
    except (Exception, KeyboardInterrupt) as error:
        report.update(status="failed", error_type=type(error).__name__, error=str(error))
        for key in ("diagnostic", "diagnostics"):
            if hasattr(error, key):
                report["error_" + key] = getattr(error, key)
    if "psutil" in locals():
        report.setdefault("memory", memory_metadata(psutil))
    report["elapsed_s"] = time.monotonic() - started
    write_json(Path(str(args.prefix) + ".json"), report)
    return 0 if report["status"] != "failed" else 1


def synthetic_worker(args, manifest, np, psutil, deadline, report):
    helper = load_module("point03_geometry_candidate", CANDIDATE)
    reference = load_module("point03_geometry_independent_reference", REFERENCE)
    report["fixture_reports"] = []
    raw, fraction = np.full(22, np.nan), np.full(22, np.nan)
    ref_fine, ref_coarse, quality = np.full(22, np.nan), np.full(22, np.nan), np.full(22, np.nan)
    completed = np.zeros(22, dtype=np.uint8)
    try:
        for index, fixture in enumerate(manifest["known_fixtures"]):
            guard(psutil, args.out_dir, deadline - 4)
            spec, rect = fixture["spec_um"], fixture["rect_um"]
            row = {"id": fixture["id"], "spec_um": spec, "rect_um": rect, "state": "RUNNING"}
            report["fixture_reports"].append(row)
            region = helper.UnionRegion(spec)
            try:
                value = region.cell(rect)
                row["candidate"] = value
                raw[index], fraction[index] = float(value["raw_fraction"]), float(value["fraction"])
                cell_metrics(value, rect, min(rect[1] - rect[0], rect[3] - rect[2]))
                parent_area = (rect[1] - rect[0]) * (rect[3] - rect[2])
                expected = fixture["expected_area_um2"]
                if expected is not None:
                    row["known_area_fraction_error"] = abs(raw[index] - expected / parent_area)
                    require(row["known_area_fraction_error"] <= 1e-12, "Known synthetic area mismatch: " + fixture["id"])
                result = reference.cell_reference(spec, rect, deadline=deadline - 4)
                row["reference"] = result
                ref_fine[index], ref_coarse[index], quality[index] = (result["fraction_fine"], result["fraction_coarse"], result["quality_total"])
                row["state"] = "INDETERMINATE_REFERENCE_QUALITY"
                fine = reference_metrics(result, rect)
                row["absolute_fraction_error"] = abs(raw[index] - fine)
                row["state"] = "CANDIDATE_REFERENCE_COMPARISON"
                require(row["absolute_fraction_error"] <= 1e-12, "Synthetic candidate/reference mismatch: " + fixture["id"])
                row["invariances"] = []
                invariance_checks(helper, spec, rect, value, row["invariances"], psutil, args.out_dir, deadline - 4)
                row["state"] = "PASS"
                completed[index] = 1
            finally:
                row["candidate_diagnostics"] = region.diagnostics
        require(len(report["fixture_reports"]) == 22 and np.all(completed == 1), "Incomplete synthetic fixture list")
        report.update(status="synthetic_completed", numeric_valid=True)
    finally:
        path = Path(str(args.prefix) + ".npz")
        save_npz(path, np, raw_fraction=raw, fraction=fraction, reference_fine=ref_fine,
                 reference_coarse=ref_coarse, reference_quality=quality, completed=completed)
        report["array_artifacts"].append({"path": str(path), "sha256": sha(path)})
        report["partial_arrays_retained"] = True


def reference_metrics(result, rect):
    require(tuple(result["rect_um"]) == tuple(rect), "Independent reference used another rectangle")
    area = (rect[1] - rect[0]) * (rect[3] - rect[2])
    fields = ("fraction_fine", "fraction_coarse", "estimated_error_fine", "estimated_error_coarse",
              "stability", "omitted_width_bound", "quality_total", "area_fine_um2", "area_coarse_um2", "rect_area_um2")
    require(all(math.isfinite(float(result[key])) for key in fields), "Nonfinite reference result")
    fine, coarse = float(result["fraction_fine"]), float(result["fraction_coarse"])
    error, omitted = float(result["estimated_error_fine"]), float(result["omitted_width_bound"])
    quality = math.fsum((error, omitted, abs(fine - coarse)))
    require(error >= 0 and float(result["estimated_error_coarse"]) >= 0 and 0 <= omitted <= 1e-14,
            "Invalid reference error/omitted-width diagnostics")
    require(abs(float(result["stability"]) - abs(fine - coarse)) <= 1e-16
            and abs(float(result["quality_total"]) - quality) <= 1e-16, "Reference quality formula mismatch")
    require(result["quality_pass"] is True and quality <= 1e-13
            and float(result["quality_total"]) <= 1e-13 and not result["messages"],
            "Unresolved independent reference: quality/message gate failed")
    require(-1e-12 <= fine <= 1 + 1e-12 and -1e-12 <= coarse <= 1 + 1e-12,
            "Reference coverage outside range")
    require(abs(float(result["rect_area_um2"]) / area - 1) <= 1e-12
            and abs(float(result["area_fine_um2"]) / area - fine) <= 1e-12
            and abs(float(result["area_coarse_um2"]) / area - coarse) <= 1e-12,
            "Reference normalization/area units mismatch")
    return fine


def transformed_spec(spec, point):
    result = {"disks": [[*point(x, y), r] for x, y, r in spec["disks"]], "annulus": None}
    annulus = spec.get("annulus")
    if annulus is not None:
        result["annulus"] = dict(annulus, center=list(point(*annulus["center"])))
    return result


def invariance_checks(helper, spec, rect, baseline, records, psutil, out, deadline):
    width, height = rect[1] - rect[0], rect[3] - rect[2]
    parent_area, baseline_area = width * height, float(baseline["area_raw_um2"])
    reverse = dict(spec, disks=list(reversed(spec["disks"])))
    variants = [("reversed_disk_order", reverse, rect, None)]
    if spec["disks"]:
        duplicate = dict(spec, disks=list(spec["disks"]) + [list(spec["disks"][0])])
        variants.append(("duplicate_first_disk", duplicate, rect, None))
    else:
        records.append({"test": "duplicate_first_disk", "state": "NOT_APPLICABLE_EMPTY"})
    translated = transformed_spec(spec, lambda x, y: (x + 17.25, y - 11.5))
    translated_rect = (rect[0] + 17.25, rect[1] + 17.25, rect[2] - 11.5, rect[3] - 11.5)
    reflected = transformed_spec(spec, lambda x, y: (-x, y))
    reflected_rect = (-rect[1], -rect[0], rect[2], rect[3])
    origin = ((rect[0] + rect[1]) / 2 + width / 7,
              (rect[2] + rect[3]) / 2 - height / 9)
    variants.extend((("translation", translated, translated_rect, None),
                     ("reflection_y_axis", reflected, reflected_rect, None),
                     ("local_origin_offset", spec, rect, origin)))
    for name, variant, variant_rect, variant_origin in variants:
        guard(psutil, out, deadline)
        row = {"test": name, "spec_um": variant, "rect_um": variant_rect,
               "origin_um": variant_origin, "state": "RUNNING"}
        records.append(row)
        region = helper.UnionRegion(variant)
        try:
            value = region.cell(variant_rect, origin=variant_origin)
            row["candidate"] = value
            cell_metrics(value, variant_rect, min(variant_rect[1] - variant_rect[0], variant_rect[3] - variant_rect[2]))
            difference = abs(float(value["area_raw_um2"]) - baseline_area) / parent_area
            row["absolute_fraction_difference"] = difference
            require(difference <= 1e-12, "Candidate invariance failed: " + name)
            row["state"] = "PASS"
        finally:
            row["diagnostics"] = region.diagnostics
    middle_x, middle_y = (rect[0] + rect[1]) / 2, (rect[2] + rect[3]) / 2
    children = [(rect[0], middle_x, rect[2], middle_y), (middle_x, rect[1], rect[2], middle_y),
                (rect[0], middle_x, middle_y, rect[3]), (middle_x, rect[1], middle_y, rect[3])]
    row = {"test": "four_equal_subcells", "state": "RUNNING", "children": []}
    records.append(row)
    region = helper.UnionRegion(spec)
    try:
        for child in children:
            guard(psutil, out, deadline)
            value = region.cell(child)
            row["children"].append({"rect_um": child, "candidate": value})
            cell_metrics(value, child, min(child[1] - child[0], child[3] - child[2]))
        total = math.fsum(float(item["candidate"]["area_raw_um2"]) for item in row["children"])
        row.update(sum_subcell_area_um2=total, parent_area_raw_um2=baseline_area,
                   absolute_fraction_difference=abs(total - baseline_area) / parent_area)
        require(row["absolute_fraction_difference"] <= 1e-12, "Candidate four-subcell additivity failed")
        row["state"] = "PASS"
    finally:
        row["diagnostics"] = region.diagnostics


def proven_support(spec):
    disks = spec["disks"]
    if not disks:
        return None
    bounds = (min(x - r for x, y, r in disks), max(x + r for x, y, r in disks),
              min(y - r for x, y, r in disks), max(y + r for x, y, r in disks))
    annulus = spec.get("annulus")
    if annulus is not None:
        x, y = annulus["center"]
        r = annulus["outer"]
        bounds = (max(bounds[0], x - r), min(bounds[1], x + r),
                  max(bounds[2], y - r), min(bounds[3], y + r))
    return bounds if bounds[0] < bounds[1] and bounds[2] < bounds[3] else None


def grid_worker(args, manifest, np, psutil, deadline, report):
    plan = next(p for p in manifest["grids"] if p["N"] == args.N)
    n, dx = plan["N"], plan["dx_um"]
    raw_fraction = np.full((n, n), np.nan, dtype=np.float64)
    fraction = np.full((n, n), np.nan, dtype=np.float64)
    area_raw = np.full((n, n), np.nan, dtype=np.float64)
    area = np.full((n, n), np.nan, dtype=np.float64)
    closure_array = np.full((n, n, 2), np.nan, dtype=np.float64)
    cell_status = np.zeros((n, n), dtype=np.uint8)
    report.update(N=n, dx_um=dx, active_cell=None, cells_completed=0,
                  raw_endpoint_corrections=[], numeric_valid=False,
                  cell_status_legend={"0": "unprocessed", "1": "support-disjoint exact zero", "2": "candidate evaluated"})
    minimum_ratio, maximum_closure, evaluated = 1.0, 0.0, 0
    try:
        helper = load_module("point03_geometry_candidate", CANDIDATE)
        region = helper.UnionRegion(manifest["spec_um"])
        reported_bounds, bounds = region.support_bounds(), proven_support(manifest["spec_um"])
        require((reported_bounds is None and bounds is None)
                or (reported_bounds is not None and bounds is not None and tuple(reported_bounds) == bounds),
                "Candidate support bounds differ from independent conservative disk/annulus bbox")
        if bounds is not None:
            require(len(bounds) == 4 and all(math.isfinite(float(v)) for v in bounds)
                    and bounds[0] <= bounds[1] and bounds[2] <= bounds[3], "Invalid candidate support bounds")
        report["support_bounds_um"] = bounds
        report["support_scope"] = "Driver-derived conservative disk bounding box intersected with outer-annulus box; helper bounds independently matched. Inner hole does not justify a skip."
        for iy in range(n):
            guard(psutil, args.out_dir, deadline - 4)
            for ix in range(n):
                report["active_cell"] = [iy, ix]
                rect = rect_for(plan, iy, ix)
                rectangle_area = (rect[1] - rect[0]) * (rect[3] - rect[2])
                disjoint = (bounds is None or rect[1] <= bounds[0] or rect[0] >= bounds[1]
                            or rect[3] <= bounds[2] or rect[2] >= bounds[3])
                if disjoint:
                    raw_fraction[iy, ix] = fraction[iy, ix] = area_raw[iy, ix] = area[iy, ix] = 0.0
                    closure_array[iy, ix] = 0.0
                    cell_status[iy, ix] = 1
                else:
                    guard(psutil, args.out_dir, deadline - 4)
                    value = region.cell(rect)
                    # Retain the returned numerical state BEFORE any guard may fail.
                    raw_fraction[iy, ix] = float(value["raw_fraction"])
                    fraction[iy, ix] = float(value["fraction"])
                    area_raw[iy, ix] = float(value["area_raw_um2"])
                    area[iy, ix] = fraction[iy, ix] * rectangle_area
                    closure_array[iy, ix] = value["boundary_closure_um"]
                    raw, clipped, correction, closure = cell_metrics(value, rect,
                                                                     min(rect[1] - rect[0], rect[3] - rect[2]))
                    minimum_ratio = min(minimum_ratio, float(value["cancel_ratio"]))
                    maximum_closure = max(maximum_closure, max(abs(v) for v in closure))
                    if correction:
                        report["raw_endpoint_corrections"].append({"iy": iy, "ix": ix,
                                                                  "raw_fraction": raw, "fraction": clipped,
                                                                  "correction": correction})
                    cell_status[iy, ix] = 2
                    evaluated += 1
                report["cells_completed"] += 1
        report["active_cell"] = None
        report.update(candidate_evaluated_cells=evaluated, support_disjoint_cells=n * n - evaluated,
                      raw_min=float(np.min(raw_fraction)), raw_max=float(np.max(raw_fraction)),
                      fraction_min=float(np.min(fraction)), fraction_max=float(np.max(fraction)),
                      min_cancel_ratio=minimum_ratio, max_boundary_closure_um=maximum_closure,
                      endpoint_correction_count=len(report["raw_endpoint_corrections"]),
                      max_absolute_endpoint_correction=max((abs(item["correction"]) for item in report["raw_endpoint_corrections"]), default=0.0),
                      raw_grid_area_um2=float(np.sum(area_raw)), grid_area_um2=float(np.sum(area)),
                      nominal_raw_fraction_grid_area_um2=float(np.sum(raw_fraction) * dx ** 2),
                      nominal_fraction_grid_area_um2=float(np.sum(fraction) * dx ** 2),
                      diagnostics=region.diagnostics,
                      cancellation_scope="abs(raw area)/sum(abs(boundary contributions)); smaller means stronger cancellation")
        diagnostics = []
        for item in manifest["prepared_inputs"]:
            if item["N"] != n:
                continue
            guard(psutil, args.out_dir, deadline)
            require(sha(item["input_npz_path"]) == item["input_npz_sha256"], "B profile input changed")
            with np.load(item["input_npz_path"], allow_pickle=False) as archive:
                dn = archive["dn"]
            require(dn.shape == (n, n) and dn.dtype == np.dtype("float64") and np.all(np.isfinite(dn)),
                    "Invalid original B profile")
            original_fraction = dn / -.003
            require(np.all((original_fraction >= -1e-12) & (original_fraction <= 1 + 1e-12)),
                    "Original B profile is outside coverage range")
            delta = fraction - original_fraction
            raw_delta = raw_fraction - original_fraction
            diagnostics.append({"N": n, "profile_samples": item["profile_samples"],
                                "input_npz_path": item["input_npz_path"], "input_npz_sha256": item["input_npz_sha256"],
                                "l1_fraction_sum": float(np.sum(np.abs(delta))),
                                "l1_area_um2": float(np.sum(np.abs(delta)) * dx ** 2),
                                "linf_fraction": float(np.max(np.abs(delta))),
                                "signed_area_difference_um2": float(np.sum(delta) * dx ** 2),
                                "original_profile_area_um2": float(np.sum(original_fraction) * dx ** 2),
                                "candidate_profile_area_um2": float(np.sum(fraction) * dx ** 2),
                                "candidate_raw_profile_area_um2": float(np.sum(raw_fraction) * dx ** 2),
                                "raw_l1_area_um2": float(np.sum(np.abs(raw_delta)) * dx ** 2),
                                "raw_linf_fraction": float(np.max(np.abs(raw_delta))),
                                "changed_cells": int(np.count_nonzero(delta)),
                                "scope": "Diagnostic comparison to frozen SS32/64 profile on corresponding nominal grid; no optical field computation or pass threshold."})
        require(len(diagnostics) == (2 if n in (400, 500) else 1), "Missing required frozen B profile comparison")
        report.update(profile_diagnostics=diagnostics, numeric_valid=True, status="grid_completed")
    finally:
        if "region" in locals():
            report["diagnostics"] = region.diagnostics
        report.update(candidate_evaluated_cells=evaluated, min_cancel_ratio=minimum_ratio,
                      max_boundary_closure_um=maximum_closure,
                      endpoint_correction_count=len(report["raw_endpoint_corrections"]),
                      max_absolute_endpoint_correction=max((abs(item["correction"]) for item in report["raw_endpoint_corrections"]), default=0.0))
        path = Path(str(args.prefix) + ".npz")
        save_npz(path, np, raw_fraction=raw_fraction, fraction=fraction,
                 area_raw_um2=area_raw, area_um2=area, boundary_closure_um=closure_array, cell_status=cell_status)
        report["array_artifacts"].append({"path": str(path), "sha256": sha(path)})
        report["partial_arrays_retained"] = True


def reference_worker(args, manifest, np, psutil, deadline, report):
    plan = next(p for p in manifest["grids"] if p["N"] == args.N)
    require(args.grid_report.resolve() == args.out_dir.resolve() / f"grid_n{args.N}.json"
            and sha(args.grid_report) == args.grid_report_sha, "Candidate grid report identity differs")
    grid = read_json(args.grid_report)
    require(grid["status"] == "grid_completed" and grid["numeric_valid"] is True
            and grid["N"] == args.N and grid["audit_manifest_sha256"] == args.audit_sha,
            "Candidate grid not completed in this D attempt")
    require(len(grid["array_artifacts"]) == 1, "Unexpected grid array artifact count")
    artifact = grid["array_artifacts"][0]
    require(sha(artifact["path"]) == artifact["sha256"], "Candidate grid arrays changed before reference")
    with np.load(artifact["path"], allow_pickle=False) as archive:
        saved_raw, saved_fraction, saved_status = archive["raw_fraction"], archive["fraction"], archive["cell_status"]
    require(saved_raw.shape == saved_fraction.shape == saved_status.shape == (args.N, args.N)
            and saved_raw.dtype == saved_fraction.dtype == np.dtype("float64")
            and np.all(np.isfinite(saved_raw)) and np.all(np.isfinite(saved_fraction))
            and np.all(saved_status != 0), "Incomplete/nonfinite saved grid")
    helper = load_module("point03_geometry_candidate", CANDIDATE)
    reference = load_module("point03_geometry_independent_reference", REFERENCE)
    region = helper.UnionRegion(manifest["spec_um"])
    selected = plan["reference_selection"]["cells"][args.batch * 24:(args.batch + 1) * 24]
    require(len(selected) == 24, "Reference batch is not the fixed 24-cell set")
    raw, fraction = np.full(24, np.nan), np.full(24, np.nan)
    repeated_raw = np.full(24, np.nan)
    fine, coarse, quality, errors = (np.full(24, np.nan) for _ in range(4))
    completed, indices = np.zeros(24, dtype=np.uint8), np.empty((24, 2), dtype=np.int64)
    indices[:] = [[cell["iy"], cell["ix"]] for cell in selected]
    report.update(N=args.N, batch=args.batch, reference_records=[], numeric_valid=False,
                  grid_report_path=str(args.grid_report.resolve()), grid_report_sha256=args.grid_report_sha,
                  grid_npz_path=artifact["path"], grid_npz_sha256=artifact["sha256"])
    try:
        for local, selection in enumerate(selected):
            guard(psutil, args.out_dir, deadline - 4)
            iy, ix, rect = selection["iy"], selection["ix"], selection["rect_um"]
            require(tuple(rect) == rect_for(plan, iy, ix), "Frozen selected-cell rectangle differs from grid")
            raw[local], fraction[local] = saved_raw[iy, ix], saved_fraction[iy, ix]
            row = {"selection_index": args.batch * 24 + local, "selection": selection,
                   "saved_raw_fraction": float(raw[local]), "saved_fraction": float(fraction[local]),
                   "state": "RUNNING"}
            report["reference_records"].append(row)
            value = region.cell(rect)
            row["candidate_recalculated"] = value
            repeated_raw[local] = float(value["raw_fraction"])
            cell_metrics(value, rect, min(rect[1] - rect[0], rect[3] - rect[2]))
            row["saved_vs_recalculated_raw_difference"] = abs(float(raw[local]) - repeated_raw[local])
            row["saved_vs_recalculated_fraction_difference"] = abs(float(fraction[local]) - float(value["fraction"]))
            require(max(row["saved_vs_recalculated_raw_difference"], row["saved_vs_recalculated_fraction_difference"]) <= 1e-12,
                    "Saved grid does not agree with repeated candidate cell")
            result = reference.cell_reference(manifest["spec_um"], rect, deadline=deadline - 4)
            row["reference"] = result
            fine[local], coarse[local], quality[local] = result["fraction_fine"], result["fraction_coarse"], result["quality_total"]
            row["state"] = "INDETERMINATE_REFERENCE_QUALITY"
            reference_metrics(result, rect)
            errors[local] = abs(raw[local] - fine[local])
            row["absolute_fraction_error"] = float(errors[local])
            row["state"] = "CANDIDATE_REFERENCE_COMPARISON"
            require(errors[local] <= 1e-12, "Preselected real-cell candidate/reference disagreement")
            if row["selection_index"] < 8:
                row["invariances"] = []
                invariance_checks(helper, manifest["spec_um"], rect, value, row["invariances"],
                                  psutil, args.out_dir, deadline - 4)
            row["state"] = "PASS"
            completed[local] = 1
        require(np.all(completed == 1), "Incomplete frozen reference batch")
        require(sha(args.grid_report) == args.grid_report_sha and sha(artifact["path"]) == artifact["sha256"],
                "Candidate grid evidence changed during independent references")
        report.update(status="reference_completed", numeric_valid=True,
                      max_absolute_fraction_error=float(np.max(errors)), max_reference_quality=float(np.max(quality)))
    finally:
        report["candidate_diagnostics"] = region.diagnostics
        path = Path(str(args.prefix) + ".npz")
        save_npz(path, np, indices=indices, raw_fraction=raw, fraction=fraction,
                 candidate_recalculated_raw_fraction=repeated_raw, reference_fine=fine,
                 reference_coarse=coarse, reference_quality=quality,
                 absolute_fraction_error=errors, completed=completed)
        report["array_artifacts"].append({"path": str(path), "sha256": sha(path)})
        report["partial_arrays_retained"] = True


def global_worker(args, manifest, np, psutil, deadline, report):
    helper = load_module("point03_geometry_candidate", CANDIDATE)
    reference = load_module("point03_geometry_independent_reference", REFERENCE)
    region = helper.UnionRegion(manifest["spec_um"])
    report.update(rect_um=manifest["global_reference_rect_um"], comparison_records=[], numeric_valid=False)
    try:
        guard(psutil, args.out_dir, deadline - 4)
        candidate = region.global_area()
        report["candidate_global"] = candidate
        require(all(math.isfinite(float(candidate[key])) for key in ("area_um2", "area_raw_um2", "cancel_ratio")),
                "Nonfinite candidate global area")
        result = reference.global_reference(manifest["spec_um"], report["rect_um"], deadline=deadline - 4)
        report["reference_global"] = result
        report["assessment_state"] = "INDETERMINATE_REFERENCE_QUALITY"
        reference_metrics(result, report["rect_um"])
        reference_area = float(result["area_fine_um2"])
        require(reference_area > 0, "Nonpositive real global reference area")
        report["assessment_state"] = "GLOBAL_AREA_COMPARISONS"
        def comparison(label, area):
            relative = abs(area - reference_area) / reference_area
            row = {"label": label, "candidate_area_um2": area, "reference_area_um2": reference_area,
                   "relative_error": relative, "state": "PASS" if relative <= 1e-12 else "FAIL"}
            report["comparison_records"].append(row)
            return row["state"] == "PASS"
        passed = comparison("global_oriented_boundary_raw", float(candidate["area_raw_um2"]))
        passed = comparison("global_oriented_boundary_reported", float(candidate["area_um2"])) and passed
        for plan in manifest["grids"]:
            guard(psutil, args.out_dir, deadline - 4)
            path = args.out_dir / f"grid_n{plan['N']}.json"
            grid = read_json(path)
            require(grid["status"] == "grid_completed" and grid["audit_manifest_sha256"] == args.audit_sha,
                    "Global check lacks complete candidate grid")
            artifact = grid["array_artifacts"][0]
            require(sha(artifact["path"]) == artifact["sha256"], "Global grid NPZ changed")
            with np.load(artifact["path"], allow_pickle=False) as archive:
                area_raw, area = archive["area_raw_um2"], archive["area_um2"]
                raw_fraction, fraction, status = archive["raw_fraction"], archive["fraction"], archive["cell_status"]
            require(np.all(np.isfinite(area_raw)) and np.all(np.isfinite(area))
                    and np.all(np.isfinite(raw_fraction)) and np.all(np.isfinite(fraction)) and np.all(status != 0),
                    "Global check encountered partial grid arrays")
            sum_raw, sum_corrected = float(np.sum(area_raw)), float(np.sum(area))
            nominal_raw = float(np.sum(raw_fraction) * plan["dx_um"] ** 2)
            nominal_corrected = float(np.sum(fraction) * plan["dx_um"] ** 2)
            require(abs(sum_raw - grid["raw_grid_area_um2"]) <= 1e-12
                    and abs(sum_corrected - grid["grid_area_um2"]) <= 1e-12
                    and abs(nominal_raw - grid["nominal_raw_fraction_grid_area_um2"]) <= 1e-12
                    and abs(nominal_corrected - grid["nominal_fraction_grid_area_um2"]) <= 1e-12,
                    "Saved grid area differs from report")
            for label, value in (("raw", sum_raw), ("endpoint_corrected", sum_corrected),
                                 ("nominal_raw_fraction", nominal_raw), ("nominal_endpoint_corrected_fraction", nominal_corrected)):
                passed = comparison(f"n{plan['N']}_{label}_grid", value) and passed
            report.setdefault("grid_evidence", []).append({"N": plan["N"], "path": str(path), "sha256": sha(path),
                                                           "npz_path": artifact["path"], "npz_sha256": artifact["sha256"]})
        # Every global comparison is retained before the combined gate is raised.
        require(passed, "Global oriented-boundary/grid area disagrees with independent reference")
        report.update(status="global_completed", numeric_valid=True, assessment_state="PASS")
    finally:
        report["candidate_diagnostics"] = region.diagnostics


def execute(args):
    started = time.monotonic()
    out, attempt_id = args.out_dir.resolve(), stamp()
    report = {"schema": "silice.point03-geometry.execution.v1", "attempt_id": attempt_id,
              "status": "failed", "operational_pass": False, "geometry_pass": False,
              "children": [], "produced_sha256": {}, "grid_reports": [], "reference_reports": [],
              "study_path": str(args.study.resolve()), "gpu_used": False,
              "scope": "Geometry and quadrature only; no optical computation or Stage B acceptance change."}
    attempt_path = out / "attempt.json"
    write_json(attempt_path, {"schema": "silice.point03-geometry.attempt.v1", "attempt_id": attempt_id,
                              "status": "execution_started", "created_utc": datetime.now(timezone.utc).isoformat(),
                              "driver_path": str(Path(__file__).resolve()), "driver_sha256": sha(Path(__file__).resolve()),
                              "total_wall_budget_s": 600, "resume_allowed": False,
                              "scope": "A missing final execution.json indicates an interrupted/unknown-cost attempt; no implicit recovery or reuse."})
    report["produced_sha256"][str(attempt_path)] = sha(attempt_path)
    try:
        report["tracked_sha256_before"] = tracked_snapshot()
        np, scipy, psutil = runtime()
        deadline = started + 600
        guard(psutil, out, deadline)
        manifest, prepared = freeze_study(args.study.resolve(), out, np, psutil, deadline)
        report["produced_sha256"].update(prepared)
        manifest_path = out / "audit_manifest.json"
        write_json(manifest_path, manifest)
        identity = sha(manifest_path)
        report["produced_sha256"][str(manifest_path)] = identity
        report.update(audit_manifest_path=str(manifest_path), audit_manifest_sha256=identity,
                      frozen_sha256_before=manifest["frozen_sha256"],
                      preparation_elapsed_s=time.monotonic() - started,
                      environment={"python": sys.version, "numpy": np.__version__, "scipy": scipy.__version__,
                                   "psutil": psutil.__version__, "threads": {key: os.environ[key] for key in THREADS}})
        verify_manifest(manifest_path, identity)

        def child(mode, prefix, n=None, batch=None, grid_path=None, grid_sha=None):
            guard(psutil, out, deadline)
            require(len(report["children"]) < 14, "Maximum 14 sequential children exceeded")
            require(deadline - time.monotonic() >= 40, "Insufficient attempt budget for another bounded child")
            command = [sys.executable, "-B", "-u", str(Path(__file__).resolve()), mode,
                       "--study", str(args.study.resolve()), "--out-dir", str(out),
                       "--audit-manifest", str(manifest_path), "--audit-sha", identity, "--prefix", str(prefix)]
            if n is not None:
                command += ["--N", str(n)]
            if batch is not None:
                command += ["--batch", str(batch)]
            if grid_path is not None:
                command += ["--grid-report", str(grid_path), "--grid-report-sha", grid_sha]
            entry = {"command": command, "started_elapsed_s": time.monotonic() - started}
            child_started = time.monotonic()
            try:
                run = subprocess.run(command, cwd=ROOT, shell=False, capture_output=True, text=True,
                                     encoding="utf-8", errors="replace", timeout=40)
                stdout, stderr, code = run.stdout, run.stderr, run.returncode
            except subprocess.TimeoutExpired as error:
                def decoded(value):
                    return value.decode("utf-8", "replace") if isinstance(value, bytes) else value or ""
                stdout, stderr, code = decoded(error.stdout), decoded(error.stderr), None
                entry["timed_out"] = True
            except (OSError, KeyboardInterrupt) as error:
                stdout, stderr, code = "", f"{type(error).__name__}: {error}", None
                entry["interrupted_or_launch_error"] = stderr
            entry.update(returncode=code, elapsed_s=time.monotonic() - child_started)
            for label, content in (("stdout", stdout), ("stderr", stderr)):
                path = Path(str(prefix) + "." + label + ".log")
                with path.open("x", encoding="utf-8", newline="\n") as handle:
                    handle.write(content)
                entry[label + "_path"] = str(path)
            report["children"].append(entry)
            # Enroll all available outputs BEFORE the failure gate, including
            # partial arrays and a failed worker report. No failed case is lost.
            for path in sorted(prefix.parent.glob(prefix.name + ".*")):
                if path.is_file() and not path.is_symlink():
                    report["produced_sha256"][str(path)] = sha(path)
            child_path = Path(str(prefix) + ".json")
            result = read_json(child_path) if child_path.is_file() else None
            if result is not None:
                entry.update(worker_report_path=str(child_path), worker_report_sha256=sha(child_path),
                             worker_status=result.get("status"))
                for artifact in result.get("array_artifacts", []):
                    path = Path(artifact["path"]).resolve()
                    require(path.is_relative_to(out) and sha(path) == artifact["sha256"],
                            "Retained worker array identity differs")
                    report["produced_sha256"][str(path)] = artifact["sha256"]
            require(code == 0 and result is not None, "Bounded child failed; its evidence and logs are retained")
            require(result["audit_manifest_sha256"] == identity and result["gpu_used"] is False
                    and result["sources_and_inputs_unchanged"] is True and result.get("numeric_valid") is True,
                    "Worker identity/integrity/numerical completion differs")
            require(0 <= result["elapsed_s"] <= 35, "Worker internal wall deadline exceeded")
            verify_manifest(manifest_path, identity)
            print(json.dumps({"progress": result["status"], "N": n, "batch": batch,
                              "children": len(report["children"])}), flush=True)
            return child_path, result

        synthetic_path, synthetic = child("--private-synthetic", out / "synthetic")
        require(synthetic["status"] == "synthetic_completed", "Synthetic batch not completed")
        report["synthetic_report"] = {"path": str(synthetic_path), "sha256": sha(synthetic_path)}
        grids = {}
        for n in GRIDS:
            path, result = child("--private-grid", out / f"grid_n{n}", n=n)
            require(result["status"] == "grid_completed" and result["N"] == n, "Wrong/incomplete full grid")
            grids[n] = (path, sha(path))
            report["grid_reports"].append({"N": n, "path": str(path), "sha256": sha(path),
                                           "raw_grid_area_um2": result["raw_grid_area_um2"],
                                           "grid_area_um2": result["grid_area_um2"],
                                           "profile_diagnostics": result["profile_diagnostics"]})
        for n in GRIDS:
            grid_path, grid_sha = grids[n]
            for batch in (0, 1):
                path, result = child("--private-reference", out / f"reference_n{n}_batch{batch}",
                                     n=n, batch=batch, grid_path=grid_path, grid_sha=grid_sha)
                require(result["status"] == "reference_completed" and result["N"] == n
                        and result["batch"] == batch, "Wrong/incomplete reference batch")
                report["reference_reports"].append({"N": n, "batch": batch, "path": str(path), "sha256": sha(path),
                                                    "max_absolute_fraction_error": result["max_absolute_fraction_error"],
                                                    "max_reference_quality": result["max_reference_quality"]})
        global_path, global_result = child("--private-global", out / "global")
        require(global_result["status"] == "global_completed", "Independent global checks not completed")
        report["global_report"] = {"path": str(global_path), "sha256": sha(global_path),
                                   "comparisons": global_result["comparison_records"]}
        require(len(report["children"]) == 14 and len(report["reference_reports"]) == 8,
                "The complete predetermined 14-child attempt did not finish")
        guard(psutil, out, deadline)
        verify_manifest(manifest_path, identity)
        report.update(status="completed", operational_pass=True, geometry_pass=True, memory=memory_metadata(psutil))
    except (Exception, KeyboardInterrupt) as error:
        report.update(status="failed", operational_pass=False, geometry_pass=False,
                      error_type=type(error).__name__, error=str(error))
        for key in ("diagnostic", "diagnostics"):
            if hasattr(error, key):
                report["error_" + key] = getattr(error, key)
    try:
        after = tracked_snapshot()
        report["tracked_sha256_after"] = after
        report["tracked_unchanged"] = report.get("tracked_sha256_before") == after
        if not report["tracked_unchanged"]:
            raise ValueError("Tracked source/evidence inventory changed")
        if "manifest" in locals():
            current = {name: sha(name) for name in manifest["frozen_sha256"]}
            report.update(frozen_sha256_after=current, frozen_unchanged=current == manifest["frozen_sha256"])
            require(report["frozen_unchanged"], "Frozen source/input changed")
        # Include preparatory evidence even if freeze/manifest creation failed.
        all_outputs = {str(path.resolve()): sha(path) for path in out.rglob("*") if path.is_file() and not path.is_symlink()}
        expected = report["produced_sha256"]
        current_produced = {name: sha(name) for name in expected}
        report.update(produced_sha256_after=current_produced, produced_unchanged=current_produced == expected,
                      complete_output_sha256=all_outputs)
        require(report["produced_unchanged"], "Recorded output changed before final report")
        if report["operational_pass"]:
            require(all_outputs == expected, "Unlisted output in completed D attempt")
    except (Exception, KeyboardInterrupt) as error:
        report.update(status="failed", operational_pass=False, geometry_pass=False, integrity_error=str(error))
    report["elapsed_s"] = time.monotonic() - started
    report["max_child_elapsed_s"] = max((c["elapsed_s"] for c in report["children"]), default=None)
    if report["elapsed_s"] > 600:
        report.update(status="failed", operational_pass=False, geometry_pass=False,
                      budget_error="Complete D attempt exceeded 600 s including integrity checks")
    report["cost_scope"] = "Observed cost of this complete or failed attempt, including preparation and integrity checks; no comparative performance claim. All attempts use separate directories."
    write_json(out / "execution.json", report)
    print(json.dumps({"status": report["status"], "report": str(out / "execution.json")}), flush=True)
    return 0 if report["geometry_pass"] else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--private-synthetic", action="store_true")
    modes.add_argument("--private-grid", action="store_true")
    modes.add_argument("--private-reference", action="store_true")
    modes.add_argument("--private-global", action="store_true")
    parser.add_argument("--audit-manifest", type=Path)
    parser.add_argument("--audit-sha")
    parser.add_argument("--prefix", type=Path)
    parser.add_argument("--N", type=int, choices=GRIDS)
    parser.add_argument("--batch", type=int, choices=(0, 1))
    parser.add_argument("--grid-report", type=Path)
    parser.add_argument("--grid-report-sha")
    args = parser.parse_args()
    if args.study.resolve() != STUDY.resolve():
        parser.error("--study must identify the original fixed Stage B manifest")
    out = args.out_dir.resolve()
    if not out.is_relative_to(RESULTS.resolve()) or not out.name.startswith("point03_geometry_"):
        parser.error("Use one fresh resultados/codex/point03_geometry_* output directory")
    private = args.private_synthetic or args.private_grid or args.private_reference or args.private_global
    if private:
        if not out.is_dir() or not args.audit_manifest or not args.audit_sha or not args.prefix:
            parser.error("Private workers require existing frozen manifest, identity, output and prefix")
        if (args.private_grid or args.private_reference) and args.N is None:
            parser.error("Grid/reference workers require a fixed --N")
        if args.private_reference and (args.batch is None or not args.grid_report or not args.grid_report_sha):
            parser.error("Reference batches require batch index and retained candidate grid identity")
        return private_worker(args)
    if out.exists():
        parser.error("Output must be fresh: no resumption or overwrites")
    out.mkdir(parents=True, exist_ok=False)
    return execute(args)


if __name__ == "__main__":
    raise SystemExit(main())
