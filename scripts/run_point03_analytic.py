"""Prospective Stage E propagation of frozen analytic-coverage inputs.

This is a newly traced runner, not a recovery of the unavailable earlier draft.
The accepted ADI and sparse helper remain byte-identical. No propagation occurs
on import. Freeze and review this file before any scientific execution.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
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
SCRIPT = ROOT / "scripts/run_point03_analytic.py"
ASSESSOR = ROOT / "scripts/assess_point03_analytic.py"
RESULTS = ROOT / "resultados/codex"
CONTRACT = ROOT / "Docs/POINT-03-ANALYTIC-PROPAGATION-CONTRACT.md"
CONTRACT_SHA = "be0b3639bcfd463e49dd0fa1d433b5a6bb4f585fd66471c28ce12b6c54287d41"
ASSESSOR_SHA = "18f99c958e8766e57322ec637942c004a11aa7a4e2ae688b4f1a005f7964590a"
THREADS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")
WIDTH, CORE = 128e-6, 6e-6
PLAN = [(f"n{n}_geom_z0625", n, .625e-6, 3200, "primary") for n in (256, 320, 400, 500)]
PLAN += [(f"n{n}_geom_z125", n, 1.25e-6, 1600, "coarse_control") for n in (400, 500)]
PLAN += [(f"n{n}_geom_z03125", n, .3125e-6, 6400, "fine_control") for n in (400, 500)]
SOURCE_NAMES = ("Docs/POINT-03-ANALYTIC-PROPAGATION-CONTRACT.md",
                "scripts/assess_point03_analytic.py", "scripts/run_point03_analytic.py",
                "scripts/point03_sparse_adi.py", "experimentos/glass009_claude/adi2d.py",
                "Docs/POINT-03-Q4-REFINEMENT-CONTRACT.md",
                "Docs/POINT-03-SPARSE-ADI-CONTRACT.md", "Docs/POINT-03-GEOMETRY-CONTRACT.md")
SOURCE_PINS = {
    "scripts/point03_sparse_adi.py": "362d4d0fbb56663f0e05fc211cd0c4db031fe20394367c090fea634134ab48bd",
    "experimentos/glass009_claude/adi2d.py": "e4f729bf40a64c545b81f93ab45b282c580349e47612ff20421dea82f1e600fb",
    "experimentos/glass009d_claude/resultados009d.json": "96b5cb7d9fe186b95644e3dfd4f214103db35b655da08d7705acaf33d3feb3ef"}
UPSTREAM = {
    "B_manifest": ("point03_refinement_20261006T220909702270Z/manifest.json",
                   "b09c57d05e190b8fdcc6ad54108e50a05a28570acdc4b82ae12501995c9a0e73"),
    "C_execution": ("point03_sparse_20261006T223947Z/execution.json",
                    "d8112e1665faf68b55b0b2d5cceccf0344daac0511b1ecf45d849255ade73d71"),
    "C_manifest": ("point03_sparse_20261006T223947Z/audit_manifest.json",
                   "c11722129bc5b1e4f90e0afff1429cce9655d5c2f69841a943a0f02e620db13b"),
    "C_independent": ("point03_sparse_20261006T223947Z/independent_audit.json",
                      "0d2a3578708c1a5bab53a3d4a142a17156ccb10a9388ecddf7be9d7f9e400f72"),
    "D_execution": ("point03_geometry_20261006234649Z/execution.json",
                    "19ed15f1dc1bc6391553033946d216c636507ed2c32ffe690dd7cd32f882227d"),
    "D_manifest": ("point03_geometry_20261006234649Z/audit_manifest.json",
                   "16b64deee8b53b5ed81e3aa15ed01fa533d11032e228b3b20d8b66ce13863512"),
    "D_independent": ("point03_geometry_20261006234649Z_launch/independent_audit.json",
                      "94fb4234b68c0b49f9cc5c6d9c8fd1d8cc31d293818514b9b13ede66eb85a922")}
D_SHA = {
    256: "06223d91e242847e811dfb47b07c6e824096e60d46af606f76504bdc817257be",
    320: "f0ca2b4c3b3ab2bc4fbf6921c12b3d8d9590edd5e98fca99e345ecc896aa5dce",
    400: "c66374c40a35ef0fcf0bad030a315a2bbc959ee6f9a423ced0fe833d220766cf",
    500: "756fe138bb2d8bcc481d258b3101f067cb23d0c2e8e278f4b624e2fe6e17a641"}
DEADLINE = None


class DiagnosticError(ValueError):
    def __init__(self, message, diagnostic):
        super().__init__(message)
        self.diagnostic = diagnostic


def utc():
    return datetime.now(timezone.utc).isoformat()


def stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "_" + uuid.uuid4().hex[:8]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def clock(reserve=0):
    require(DEADLINE is None or time.monotonic() < DEADLINE-reserve, "Attempt/worker deadline exhausted")


def sha(path, bounded=True):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), "Missing/nonregular file: " + str(path))
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024**2), b""):
            digest.update(block)
            if bounded:
                clock()
    return digest.hexdigest()


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "Duplicate JSON key")
            result[key] = value
        return result
    def reject(value):
        raise ValueError("Nonfinite JSON constant: " + value)
    value = json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=pairs,
                       parse_constant=reject)
    require(isinstance(value, dict), "Expected a JSON object")
    return value


def json_safe(value):
    if isinstance(value, float) and not math.isfinite(value):
        return {"nonfinite_value": repr(value)}
    if isinstance(value, dict):
        return {str(key): json_safe(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(child) for child in value]
    return value


def write_json(path, value):
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(json_safe(value), indent=2, allow_nan=False) + "\n")


def save_arrays(np, path, **arrays):
    with Path(path).open("xb") as stream:
        np.savez_compressed(stream, **arrays)


def source_snapshot():
    result = {str(ROOT / name): sha(ROOT / name) for name in SOURCE_NAMES}
    for name, digest in SOURCE_PINS.items():
        require(sha(ROOT / name) == digest, "Immutable source/history changed: " + name)
    require(result[str(CONTRACT)] == CONTRACT_SHA and result[str(ASSESSOR)] == ASSESSOR_SHA,
            "Frozen contract/assessor changed")
    return result


def tracked_snapshot():
    clock()
    child = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"],
                           capture_output=True, timeout=10, check=True, shell=False)
    result = {}
    for raw in child.stdout.split(b"\0"):
        if not raw:
            continue
        name = raw.decode("utf-8")
        path = ROOT / name
        require(path.resolve().is_relative_to(ROOT), "Tracked path escapes checkout")
        require(path.exists(), "Tracked file is missing: " + name)
        if path.is_file():
            require(not path.is_symlink(), "Tracked symlink is unsupported")
            result[name] = sha(path)
    require(result, "Empty tracked inventory")
    return result


def check_hashes(mapping):
    for path, digest in mapping.items():
        require(sha(path) == digest, "Retained bytes changed: " + path)


def inventory(out):
    return {str(path.resolve()): sha(path) for path in sorted(out.rglob("*")) if path.is_file()}


def copy_exact(source, target, digest):
    require(sha(source) == digest, "Upstream file SHA differs")
    with Path(source).open("rb") as src, Path(target).open("xb") as dst:
        for block in iter(lambda: src.read(1024**2), b""):
            dst.write(block)
            clock()
    require(sha(target) == digest and sha(source) == digest, "Copy/source identity failed")


def module_from(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def runtime(backend=False):
    for key in THREADS:
        os.environ[key] = "1"
    require(Path(sys.prefix).resolve() == ROOT / ".venv", "Use the Point 01 isolated interpreter")
    require(platform.python_version() == "3.13.7" and sys.platform == "win32"
            and sys.maxsize > 2**32, "Expected Windows x64 CPython 3.13.7")
    import numpy as np
    import scipy
    import psutil
    versions = {"python": platform.python_version(), "numpy": np.__version__,
                "scipy": scipy.__version__, "psutil": psutil.__version__,
                "threads": {key: os.environ[key] for key in THREADS}}
    require([versions[key] for key in ("numpy", "scipy", "psutil")] ==
            ["2.2.6", "1.15.1", "6.1.1"], "Point 01 versions differ")
    require(not any(name == prefix or name.startswith(prefix+".") for name in sys.modules
                    for prefix in ("torch", "cupy")), "GPU implementation imported")
    stepper = None
    if backend:
        adi = module_from(ROOT / "experimentos/glass009_claude/adi2d.py", "point03_frozen_adi")
        sparse = module_from(ROOT / "scripts/point03_sparse_adi.py", "point03_frozen_sparse")
        stepper = sparse.make_sparse_stepper(adi.Stepper)
        require(all(getattr(stepper, name) is getattr(adi.Stepper, name)
                    for name in ("__init__", "_lap", "step")), "Original ADI methods changed")
    return np, psutil, versions, stepper


def guard(psutil, out, reserve=0):
    clock(reserve)
    available = int(psutil.virtual_memory().available)
    disk = int(shutil.disk_usage(out).free)
    sample = {"available_ram_bytes": available, "free_disk_bytes": disk,
              "minimum_ram_exclusive_bytes": 1.5*1024**3, "minimum_disk_exclusive_bytes": 2*1024**3}
    if not (available > 1.5*1024**3 and disk > 2*1024**3):
        raise DiagnosticError("RAM/disk guard failed", sample)
    clock(reserve)
    return sample


def memory(psutil):
    state = psutil.Process().memory_info()
    result = {"rss_bytes": int(state.rss), "rss_scope": "Current process resident set"}
    if hasattr(state, "peak_wset"):
        result.update(peak_working_set_bytes=int(state.peak_wset), peak_scope="Windows peak working set")
    return result


def arrays_from(np, path, n, keys, exact=True):
    with np.load(path, allow_pickle=False) as archive:
        require(len(archive.files) == len(set(archive.files)), "Duplicate NPZ keys")
        require(set(archive.files) == set(keys) if exact else set(keys) <= set(archive.files),
                "Unexpected NPZ keys")
        arrays = {key: archive[key] for key in keys}
    for key, array in arrays.items():
        dtype = "complex128" if key in ("A0", "field") else "uint8" if key == "cell_status" else "float64"
        require(array.shape == (n, n) and array.dtype == np.dtype(dtype) and np.all(np.isfinite(array)),
                "Invalid retained array: " + key)
    return arrays


def array_hashes(arrays):
    return {key: hashlib.sha256(value.tobytes(order="C")).hexdigest() for key, value in arrays.items()}


def metrics(np, field, inputs, n, final=False):
    dx = WIDTH/n
    diagnostic = {"field_shape": list(field.shape), "field_dtype": str(field.dtype),
                  "expected_N": n, "final_power_ceiling_applicable": final}
    valid_field = field.shape == (n, n) and field.dtype == np.dtype("complex128")
    diagnostic["field_finite"] = bool(np.all(np.isfinite(field)))
    if not valid_field or not diagnostic["field_finite"]:
        raise DiagnosticError("Invalid propagated field", diagnostic)
    diagnostic["passive_input_valid"] = bool(np.all(inputs["sigma"] >= 0)
        and np.all((inputs["weights"] >= 0) & (inputs["weights"] <= 1))
        and np.all((inputs["dn"] >= -.003) & (inputs["dn"] <= 0)))
    if not diagnostic["passive_input_valid"]:
        raise DiagnosticError("Invalid passive input", diagnostic)
    try:
        with np.errstate(over="raise", invalid="raise", divide="raise"):
            pin = float(np.sum(np.abs(inputs["A0"])**2)*dx**2)
            diagnostic["P_in"] = pin
            area = float(np.sum(inputs["weights"])*dx**2)
            diagnostic["core_area_m2"] = area
            intensity = np.abs(field)**2
            total = float(np.sum(intensity)*dx**2)
            diagnostic["raw_total_power"] = total
            core = float(np.sum(inputs["weights"]*intensity)*dx**2/pin)
            diagnostic["P_core"] = core
    except (Exception, KeyboardInterrupt) as error:
        raise DiagnosticError("Power computation failed: "+str(error), diagnostic) from error
    diagnostic.update(input_power_error=abs(pin-1), detector_area_relative_error=abs(area/(math.pi*CORE**2)-1))
    if not (all(math.isfinite(value) for value in (pin, area, total, core))
            and abs(pin-1) <= 1e-12 and abs(area/(math.pi*CORE**2)-1) <= 1e-12):
        raise DiagnosticError("Input normalization/detector area/finite power failed", diagnostic)
    if not (total >= 0 and 0 <= core <= total/pin+1e-12 and (not final or total <= 1.001)):
        raise DiagnosticError("Power validity failed", diagnostic)
    return {"P_in": pin, "input_power": pin, "P0": pin, "raw_total_power": total,
            "output_power": total, "P_final": total, "P_total": total/pin,
            "P_core": core, "core_power_analytic_input": core, "core_area_m2": area,
            "numeric_valid": True}

def factor_valid(metadata, n, calls):
    require(metadata.get("backend") == "scipy.sparse.linalg.splu"
            and metadata.get("numpy_version") == "2.2.6" and metadata.get("scipy_version") == "1.15.1"
            and metadata.get("options") == {"permc_spec": "NATURAL", "diag_pivot_thresh": 0.0, "Equil": False},
            "Sparse options/implementation changed")
    factors = metadata.get("factors")
    require(isinstance(factors, list) and len(factors) == 2, "Expected two sparse factors")
    for index, factor in enumerate(factors):
        expected = {"factor_index": index, "line_count": n, "line_size": n, "matrix_order": n*n,
                    "matrix_nnz": 3*n*n-2*n, "expected_matrix_nnz": 3*n*n-2*n, "solve_calls": calls}
        require(all(factor.get(key) == value for key, value in expected.items()), "Sparse structure/solve count differs")
        for key in ("perm_r", "perm_c"):
            value = factor.get(key, {})
            require(value.get("identity") is True and value.get("nonidentity_entries") == 0
                    and value.get("length") == n*n and value.get("dtype") in ("int32", "int64"),
                    "Sparse permutation rejected")


def prepare(out, np, psutil, environment, sources, report):
    frozen, prior, descriptors = {}, {}, {}
    report["preparation"] = {"prepared_inputs": [], "upstream": descriptors}
    for name, (relative, digest) in UPSTREAM.items():
        path = RESULTS / relative
        require(sha(path) == digest, "Upstream pin changed: " + name)
        frozen[str(path)] = digest
        descriptors[name] = {"path": str(path), "sha256": digest}
        prior[name] = read_json(path)
    require(prior["B_manifest"].get("schema") == "silice.point03-refinement.manifest.v1", "Unknown B manifest")
    for letter, gate in (("C", "equivalence_pass"), ("D", "geometry_pass")):
        previous = prior[letter+"_execution"]
        require(previous.get("status") == "completed" and previous.get("operational_pass") is True
                and previous.get(gate) is True and prior[letter+"_independent"].get("status") == "PASS"
                and previous.get("audit_manifest_sha256") == UPSTREAM[letter+"_manifest"][1],
                "Upstream acceptance/linkage changed: " + letter)
    history = ROOT / "experimentos/glass009d_claude/resultados009d.json"
    history_sha = SOURCE_PINS[history.relative_to(ROOT).as_posix()]
    require(sha(history) == prior["B_manifest"]["source_sha256"].get(str(history)) == history_sha,
            "Historical Q4 identity changed")
    frozen[str(history)] = history_sha
    old = read_json(history)["T96d"]
    old_p = [old[key] for key in ("P_dx0p625", "P_dx0p5", "P_dx0p4")]
    require(old.get("Q4_monotone") is False
            and not abs(old_p[2]-old_p[1]) <= abs(old_p[1]-old_p[0]), "Historical Q4 FAIL changed")
    geometry = prior["D_manifest"].get("spec_um", {})
    require(len(geometry.get("disks", [])) == 96 and all(row[2] == 1.25 for row in geometry["disks"])
            and geometry.get("annulus") == {"center": [0.0, 0.0], "inner": 6.0, "outer": 12.0},
            "Accepted D geometry changed")
    grids = prior["D_manifest"].get("grids", [])
    require(len(grids) == 4 and {grid["N"] for grid in grids} == {256, 320, 400, 500}, "D grids differ")
    (out / "inputs").mkdir()
    (out / "upstream_copies").mkdir()
    prepared = report["preparation"]["prepared_inputs"]
    report["preparation"]["frozen_input_sha256"] = frozen
    for n in (256, 320, 400, 500):
        guard(psutil, out, 50)
        b_rows = [row for row in prior["B_manifest"]["prepared_inputs"]
                  if row["N"] == n and row["profile_samples"] == 64]
        d_links = [row for row in prior["D_execution"]["grid_reports"] if row["N"] == n]
        require(len(b_rows) == len(d_links) == 1, "Ambiguous B/D input linkage")
        b, link = b_rows[0], d_links[0]
        b_path, b_sha = Path(b["input_npz_path"]).resolve(), b["input_npz_sha256"]
        d_report_path = Path(link["path"]).resolve()
        require(sha(d_report_path) == link["sha256"], "D grid report bytes changed")
        frozen[str(d_report_path)] = link["sha256"]
        d_report = read_json(d_report_path)
        artifacts = [item for item in d_report.get("array_artifacts", []) if item.get("sha256") == D_SHA[n]]
        require(len(artifacts) == 1, "Accepted D array is ambiguous")
        d_path = Path(artifacts[0]["path"]).resolve()
        row = {"N": n, "B_input_npz_path": str(b_path), "B_input_npz_sha256": b_sha,
               "D_grid_report_path": str(d_report_path), "D_grid_report_sha256": link["sha256"],
               "D_grid_npz_path": str(d_path), "D_grid_npz_sha256": D_SHA[n], "D_fraction_key": "fraction"}
        prepared.append(row)
        # Preserve upstream bytes before numeric validity checks can reject them.
        for role, original, digest in (("B", b_path, b_sha), ("D", d_path, D_SHA[n])):
            copied = out / "upstream_copies" / f"n{n}_{role}.npz"
            row[role+"_copy_path"], row[role+"_copy_sha256"] = str(copied), digest
            copy_exact(original, copied, digest)
            frozen[str(original)] = frozen[str(copied)] = digest
        require(d_report.get("status") == "grid_completed" and d_report.get("numeric_valid") is True
                and d_report.get("N") == n and d_report.get("cells_completed") == n*n
                and d_report.get("dx_um") == 128.0/n, "D grid incomplete or changed")
        grid = next(item for item in grids if item["N"] == n)
        identity_keys = ("N", "width_m", "dx_m", "dx_um", "axis_m", "axis_um",
                         "max_axis_si_conversion_difference_um", "dx_si_conversion_difference_um", "coordinate_scope")
        row["D_grid_identity"] = {key: grid[key] for key in identity_keys}
        axis_m, axis_um = np.asarray(grid["axis_m"], dtype=np.float64), np.asarray(grid["axis_um"], dtype=np.float64)
        require(grid["width_m"] == WIDTH and grid["dx_m"] == WIDTH/n and grid["dx_um"] == 128.0/n
                and axis_m.shape == axis_um.shape == (n,)
                and axis_m.tobytes() == ((np.arange(n)-n//2)*(WIDTH/n)).tobytes()
                and axis_um.tobytes() == ((np.arange(n)-n//2)*(128.0/n)).tobytes(), "D/B axes differ")
        inputs = arrays_from(np, row["B_copy_path"], n, ("A0", "dn", "sigma", "weights"))
        original_hashes = {key: digest for key, digest in array_hashes(inputs).items() if key != "dn"}
        d_arrays = arrays_from(np, row["D_copy_path"], n, ("fraction", "raw_fraction", "cell_status"), exact=False)
        fraction, raw = d_arrays["fraction"], d_arrays["raw_fraction"]
        row["raw_endpoint_correction_count"] = int(np.count_nonzero(fraction-raw))
        row["raw_endpoint_correction_max"] = float(np.max(np.abs(fraction-raw)))
        require(np.all((d_arrays["cell_status"] == 1) | (d_arrays["cell_status"] == 2))
                and np.all((fraction >= 0) & (fraction <= 1))
                and np.all((raw >= -1e-12) & (raw <= 1+1e-12))
                and np.array_equal(fraction, np.clip(raw, 0, 1)), "D correction/completion invalid")
        require(row["raw_endpoint_correction_count"] == d_report["endpoint_correction_count"]
                and row["raw_endpoint_correction_max"] == d_report["max_absolute_endpoint_correction"],
                "D correction diagnostics differ")
        inputs["dn"] = -.003*fraction
        path = out / "inputs" / f"n{n}_geom.npz"
        row["input_npz_path"] = str(path)
        save_arrays(np, path, **inputs)
        row["input_npz_sha256"] = sha(path)
        frozen[str(path)] = row["input_npz_sha256"]
        retained = arrays_from(np, path, n, ("A0", "dn", "sigma", "weights"))
        row["array_sha256"] = array_hashes(retained)
        row["upstream_unchanged_array_sha256"] = original_hashes
        require(all(retained[key].tobytes(order="C") == inputs[key].tobytes(order="C")
                    for key in retained), "Prepared array bytes differ")
        require(all(row["array_sha256"][key] == original_hashes[key] for key in original_hashes),
                "A0/sigma/weights changed")
        row["input_metrics"] = metrics(np, retained["A0"], retained, n)
    plans = []
    for name, n, dz, steps, role in PLAN:
        row = next(item for item in prepared if item["N"] == n)
        plans.append({"case_id": name, "N": n, "width_m": WIDTH, "dx_m": WIDTH/n,
                      "dz_m": dz, "steps_target": steps, "role": role,
                      "profile_kind": "accepted_D_analytic",
                      "input_npz_path": row["input_npz_path"], "input_npz_sha256": row["input_npz_sha256"]})
    check_hashes(frozen)
    manifest = {"schema": "silice.point03-analytic.manifest.v1", "created_utc": utc(),
                "source_root": str(ROOT), "out_dir": str(out), "source_sha256": sources,
                "contract_path": str(CONTRACT), "contract_sha256": CONTRACT_SHA,
                "upstream": descriptors, "historical_Q4_path": str(history), "historical_Q4_sha256": history_sha,
                "prepared_inputs": prepared, "case_plan": plans, "frozen_input_sha256": frozen,
                "environment": environment, "physics": {"width_m": WIDTH, "wavelength_m": 1550e-9,
                "n_ref": 1.444, "z_m": .002, "dn_track": -.003, "core_radius_m": CORE,
                "array_axis": "(arange(N)-N//2)*dx_m"}, "total_wall_budget_s": 3600,
                "propagation_chunk_steps": 200, "propagation_chunk_count": 144,
                "resource_schedule": "Full guard at child entry/exit and every 20 steps; cheap clock before each step",
                "implementation_lineage": "New v2 draft after unavailable prior source; not a byte recovery"}
    path = out / "manifest.json"
    write_json(path, manifest)
    return path, sha(path), manifest


def verify_manifest(path, digest):
    path = Path(path).resolve()
    require(sha(path) == digest, "Manifest changed")
    manifest = read_json(path)
    require(manifest.get("schema") == "silice.point03-analytic.manifest.v1"
            and manifest.get("source_root") == str(ROOT) and manifest.get("out_dir") == str(path.parent)
            and path.parent.parent == RESULTS and path.parent.name.startswith("point03_analytic_"),
            "Invalid attempt manifest")
    require(source_snapshot() == manifest["source_sha256"], "Frozen sources changed")
    plans = manifest["case_plan"]
    require(len(plans) == 8, "Wrong case count")
    for row, (name, n, dz, steps, role) in zip(plans, PLAN):
        expected = {"case_id": name, "N": n, "width_m": WIDTH, "dx_m": WIDTH/n,
                    "dz_m": dz, "steps_target": steps, "role": role, "profile_kind": "accepted_D_analytic"}
        require(all(row.get(key) == value for key, value in expected.items()), "Frozen plan changed")
        prepared = [item for item in manifest["prepared_inputs"] if item["N"] == n]
        require(len(prepared) == 1 and row["input_npz_path"] == prepared[0]["input_npz_path"]
                and row["input_npz_sha256"] == prepared[0]["input_npz_sha256"], "Case input reuse differs")
    return manifest


def worker(args):
    global DEADLINE
    started = time.monotonic()
    DEADLINE = started+31
    prefix = args.prefix.resolve()
    path = Path(str(prefix)+".json")
    report = {"schema": "silice.point03-analytic.checkpoint.v1", "status": "failed",
              "created_utc": utc(), "gpu_used": False, "dtype": "complex128",
              "manifest_sha256": args.manifest_sha, "steps_start": args.steps_start,
              "steps_done": args.steps_start, "steps_completed": args.steps_start,
              "previous_checkpoint_path": str(args.previous.resolve()) if args.previous else None,
              "previous_checkpoint_sha256": None}
    field, np, psutil, instance, inputs = None, None, None, None, None
    try:
        require(Path(__file__).resolve() == SCRIPT, "Run the frozen checkout runner")
        manifest = verify_manifest(args.manifest, args.manifest_sha)
        matches = [row for row in manifest["case_plan"] if row["case_id"] == args.case_id]
        require(len(matches) == 1, "Unknown case")
        case = matches[0]
        report.update(case)
        require(prefix.parent == args.manifest.resolve().parent / "cases" / args.case_id
                and prefix.name.startswith("chunk_") and not path.exists(), "Invalid/fresh checkpoint prefix")
        report["source_sha256_before"] = source_snapshot()
        require(sha(case["input_npz_path"]) == case["input_npz_sha256"], "Input changed")
        np, psutil, environment, stepper = runtime(backend=True)
        require(environment == manifest["environment"], "Child environment changed")
        report["resource_entry"] = guard(psutil, prefix.parent)
        inputs = arrays_from(np, case["input_npz_path"], case["N"], ("A0", "dn", "sigma", "weights"))
        field = inputs["A0"].copy()
        start = args.steps_start
        require(type(start) is int and start >= 0 and start % 200 == 0
                and start+200 <= case["steps_target"], "Invalid chunk step interval")
        if args.previous:
            previous = args.previous.resolve()
            require(previous.parent == prefix.parent and previous.suffix == ".json", "Wrong previous checkpoint")
            report["previous_checkpoint_sha256"] = sha(previous)
            prior = read_json(previous)
            require(prior.get("status") == "checkpoint_completed" and prior.get("manifest_sha256") == args.manifest_sha
                    and prior.get("case_id") == args.case_id and prior.get("steps_done") == start
                    and prior.get("numeric_valid") is True and prior.get("input_npz_sha256") == case["input_npz_sha256"]
                    and prior.get("sources_unchanged") is True and prior.get("input_unchanged") is True,
                    "Invalid previous checkpoint identity")
            previous_npz = previous.with_suffix(".npz")
            require(prior.get("npz_path") == str(previous_npz) and sha(previous_npz) == prior.get("npz_sha256"),
                    "Previous field identity differs")
            field = arrays_from(np, previous_npz, case["N"], ("field",))["field"]
        else:
            require(start == 0, "First checkpoint must start from frozen input")
        report.update(metrics(np, field, inputs, case["N"]))
        setup = time.monotonic()
        instance = stepper(inputs["dn"], inputs["sigma"], case["dx_m"], case["dz_m"])
        report["setup_elapsed_s"] = time.monotonic()-setup
        factor_valid(instance.sparse_metadata(), case["N"], 0)
        propagation = time.monotonic()
        for offset in range(200):
            clock()
            if offset % 20 == 0:
                guard(psutil, prefix.parent)
            field = instance.step(field)
            report["steps_done"] = report["steps_completed"] = start+offset+1
        report["propagation_elapsed_s"] = time.monotonic()-propagation
        factor_valid(instance.sparse_metadata(), case["N"], 200)
        report.update(metrics(np, field, inputs, case["N"], final=report["steps_done"] == case["steps_target"]))
        report["status"] = "checkpoint_completed"
    except (Exception, KeyboardInterrupt) as error:
        report.update(status="failed", numeric_valid=False, error_type=type(error).__name__, error=str(error))
        if hasattr(error, "diagnostic"):
            report["failure_diagnostic"] = error.diagnostic
            if hasattr(error, "permutation_arrays"):
                report["rejected_factor_diagnostic"] = error.diagnostic
        if hasattr(error, "permutation_arrays") and np is not None:
            try:
                rejected = Path(str(prefix)+".rejected.npz")
                save_arrays(np, rejected, **error.permutation_arrays)
                report.update(rejected_permutation_path=str(rejected), rejected_permutation_sha256=sha(rejected, bounded=False))
            except (Exception, KeyboardInterrupt) as retain_error:
                report["rejected_permutation_retention_error"] = str(retain_error)
    finally:
        DEADLINE = started+35
        # Each failure keeps its latest available unaltered field; no retry/resume.
        try:
            if field is not None and np is not None:
                npz = Path(str(prefix)+".npz")
                save_arrays(np, npz, field=field)
                digest = sha(npz, bounded=False)
                report.update(npz_path=str(npz), npz_sha256=digest,
                              final_npz_path=str(npz), final_npz_sha256=digest)
            if instance is not None:
                report["factor_metadata"] = instance.sparse_metadata()
            after = source_snapshot()
            report["source_sha256_after"] = after
            report["sources_unchanged"] = after == report.get("source_sha256_before")
            report["input_unchanged"] = sha(report["input_npz_path"]) == report["input_npz_sha256"]
            require(report["sources_unchanged"] and report["input_unchanged"], "Child provenance changed")
            if psutil is not None:
                report["resource_exit"] = guard(psutil, prefix.parent)
                report.update(memory(psutil))
            require(report["steps_done"] == args.steps_start+200, "Partial chunk cannot be accepted")
            require(time.monotonic()-started < 35, "Worker retention deadline exceeded")
        except (Exception, KeyboardInterrupt) as error:
            report.update(status="failed", numeric_valid=False, retention_or_integrity_error=str(error))
            if hasattr(error, "diagnostic"):
                report["retention_or_integrity_diagnostic"] = error.diagnostic
        report["elapsed_s"] = time.monotonic()-started
        if report["elapsed_s"] >= 35:
            report.update(status="failed", numeric_valid=False, retention_deadline_exceeded=True)
        write_json(path, report)
    print(json.dumps({"case_id": args.case_id, "status": report["status"],
                      "steps_done": report["steps_done"]}), flush=True)
    return 0 if report["status"] == "checkpoint_completed" else 1


def prediction(out, manifest_path, manifest_sha, case_reports, children, started):
    require(len(case_reports) == 3 and len(children) == 48, "Prediction must follow exactly 48 chunks")
    rows = []
    for index, reference in enumerate(case_reports):
        require(reference["case_id"] == PLAN[index][0] and sha(reference["path"]) == reference["sha256"],
                "Prediction cases changed")
        case = read_json(reference["path"])
        rows.append({key: case[key] for key in ("case_id", "P_core", "input_npz_path",
                    "input_npz_sha256", "final_npz_path", "final_npz_sha256")} |
                    {"path": reference["path"], "sha256": reference["sha256"]})
    p = [row["P_core"] for row in rows]
    differences = [p[1]-p[0], p[2]-p[1]]
    order, predicted, reasons = None, None, []
    if not all(math.isfinite(value) and abs(value) > 1e-12 for value in differences):
        reasons.append("Unresolvable or nonfinite first-three differences")
    if differences[0]*differences[1] <= 0:
        reasons.append("First-three differences do not have the same sign")
    if not reasons:
        order = (math.log(abs(differences[0]))-math.log(abs(differences[1])))/math.log(1.25)
        if not math.isfinite(order) or order <= 0:
            reasons.append("Observed order is not finite and positive")
            if not math.isfinite(order):
                order = None
        else:
            predicted = p[2]+differences[1]*math.exp(-order*math.log(1.25))
            if not math.isfinite(predicted):
                reasons.append("Nonfinite predicted power")
                predicted = None
    record = {"schema": "silice.point03-analytic.prediction.v1", "created_utc": utc(),
              "manifest_path": str(manifest_path), "manifest_sha256": manifest_sha,
              "parent_elapsed_s": time.monotonic()-started, "completed_chunk_count": 48,
              "first_three_case_reports": rows, "signed_differences": differences,
              "observed_order": order, "predicted_core_power": predicted,
              "valid_fit": not reasons, "invalid_reasons": reasons,
              "scope": "Frozen first-three arithmetic before every new N500 trajectory"}
    path = out / "prediction.json"
    write_json(path, record)
    return path, sha(path)


def child_run(command, prefix, started, entry):
    require(DEADLINE-time.monotonic() > 40, "Insufficient remaining hard-timeout budget")
    entry.update(command=command, started_utc=utc(), started_elapsed_s=time.monotonic()-started)
    began = time.monotonic()
    stdout, stderr = Path(str(prefix)+".stdout.log"), Path(str(prefix)+".stderr.log")
    entry.update(stdout_path=str(stdout), stderr_path=str(stderr), returncode=None)
    try:
        with stdout.open("xb", buffering=0) as out_stream, stderr.open("xb", buffering=0) as err_stream:
            result = subprocess.run(command, cwd=ROOT, stdout=out_stream, stderr=err_stream,
                                    timeout=min(40, DEADLINE-time.monotonic()), shell=False)
        entry["returncode"] = result.returncode
    except subprocess.TimeoutExpired as error:
        entry.update(timed_out=True, error=str(error))
    except (Exception, KeyboardInterrupt) as error:
        entry.update(interrupted_or_launch_error=True, error_type=type(error).__name__, error=str(error))
    finally:
        entry["elapsed_s"] = time.monotonic()-began
        for label, path in (("stdout", stdout), ("stderr", stderr)):
            if path.is_file():
                entry[label+"_sha256"] = sha(path, bounded=False)
    return entry


def final_integrity(report, manifest, sources_before, tracked_before):
    if sources_before is not None:
        after = source_snapshot()
        report.update(source_sha256_after=after, sources_unchanged=after == sources_before)
        require(report["sources_unchanged"], "Sources changed")
    if tracked_before is not None:
        after = tracked_snapshot()
        changed = sorted(name for name in set(tracked_before) | set(after)
                         if tracked_before.get(name) != after.get(name))
        report.update(tracked_sha256_after=after, tracked_changed_paths=changed,
                      tracked_inputs_unchanged=not changed)
        require(not changed, "Tracked bytes changed")
    if manifest is not None:
        check_hashes(manifest["frozen_input_sha256"])
        report.update(frozen_input_sha256_after=manifest["frozen_input_sha256"], frozen_inputs_unchanged=True)


def run(out):
    global DEADLINE
    started = time.monotonic()
    DEADLINE = started+3600
    out = out.resolve()
    require(out.parent == RESULTS and out.name.startswith("point03_analytic_"), "Output must be a direct fresh codex child")
    out.mkdir(exist_ok=False)
    report = {"schema": "silice.point03-analytic.execution.v1", "status": "failed",
              "operational_pass": False, "scientific_pass": None, "science_pass": None,
              "created_utc": utc(), "out_dir": str(out), "source_root": str(ROOT),
              "children": [], "case_reports": [], "completed_chunk_count": 0,
              "gpu_used": False, "resume_allowed": False, "total_wall_budget_s": 3600,
              "implementation_lineage": "New reviewed v2 after prior draft became inaccessible"}
    np, psutil, manifest, propagation, sources_before, tracked_before = None, None, None, None, None, None
    try:
        write_json(out / "attempt.json", {"schema": "silice.point03-analytic.attempt.v1",
                   "created_utc": report["created_utc"], "pid": os.getpid(), "total_wall_budget_s": 3600,
                   "resume_allowed": False, "runner_path": str(Path(__file__).resolve())})
        require(Path(__file__).resolve() == SCRIPT, "Freeze this draft at the contracted runner path before use")
        sources_before, tracked_before = source_snapshot(), tracked_snapshot()
        report.update(source_sha256_before=sources_before, tracked_sha256_before=tracked_before)
        require(all(tracked_before.get(Path(path).relative_to(ROOT).as_posix()) == digest
                    for path, digest in sources_before.items()), "Every source must be tracked before propagation")
        np, psutil, environment, unused = runtime()
        report["environment"] = environment
        report["resource_entry"] = guard(psutil, out, 50)
        manifest_path, identity, manifest = prepare(out, np, psutil, environment, sources_before, report)
        report.update(manifest_path=str(manifest_path), manifest_sha256=identity,
                      frozen_input_sha256_before=manifest["frozen_input_sha256"],
                      preparation_elapsed_s=time.monotonic()-started)
        cases = out / "cases"
        cases.mkdir()
        for index, case in enumerate(manifest["case_plan"]):
            if index == 3:
                pred_path, pred_sha = prediction(out, manifest_path, identity,
                                                report["case_reports"], report["children"], started)
                report.update(prediction_path=str(pred_path), prediction_sha256=pred_sha)
            folder = cases / case["case_id"]
            folder.mkdir()
            checkpoints, previous, previous_sha, last = [], None, None, None
            for steps_start in range(0, case["steps_target"], 200):
                guard(psutil, out, 50)
                require(DEADLINE-time.monotonic() > 90, "Reserve 40 s child plus 50 s assessment/retention")
                verify_manifest(manifest_path, identity)
                if case["N"] == 500:
                    require(sha(report["prediction_path"]) == report["prediction_sha256"],
                            "Frozen prediction changed before N500")
                prefix = folder / ("chunk_"+stamp())
                command = [sys.executable, "-B", "-u", str(SCRIPT), "--worker",
                           "--manifest", str(manifest_path), "--manifest-sha", identity,
                           "--case-id", case["case_id"], "--steps-start", str(steps_start), "--prefix", str(prefix)]
                if previous is not None:
                    command += ["--previous", str(previous)]
                entry = {"case_id": case["case_id"], "steps_start": steps_start}
                report["children"].append(entry)
                child_run(command, prefix, started, entry)
                checkpoint_path = prefix.with_suffix(".json")
                if checkpoint_path.is_file():
                    digest = sha(checkpoint_path)
                    entry.update(checkpoint_path=str(checkpoint_path), checkpoint_sha256=digest,
                                 worker_report_path=str(checkpoint_path), worker_report_sha256=digest)
                    last = read_json(checkpoint_path)
                    entry["steps_done"] = last.get("steps_done")
                require(entry.get("returncode") == 0 and not entry.get("timed_out")
                        and not entry.get("interrupted_or_launch_error") and last is not None,
                        "Propagation child failed; partial evidence retained; no resume")
                require(last.get("status") == "checkpoint_completed" and last.get("numeric_valid") is True
                        and last.get("case_id") == case["case_id"] and last.get("manifest_sha256") == identity
                        and last.get("steps_start") == steps_start and last.get("steps_done") == steps_start+200
                        and last.get("steps_completed") == steps_start+200 and last.get("elapsed_s", 36) <= 35
                        and last.get("sources_unchanged") is True and last.get("input_unchanged") is True
                        and last.get("gpu_used") is False, "Invalid child completion")
                require(last.get("previous_checkpoint_path") == (str(previous) if previous else None)
                        and last.get("previous_checkpoint_sha256") == previous_sha
                        and last.get("input_npz_path") == case["input_npz_path"]
                        and last.get("input_npz_sha256") == case["input_npz_sha256"], "Checkpoint chain/input differs")
                require(last.get("npz_path") == str(prefix.with_suffix(".npz"))
                        and sha(last["npz_path"]) == last.get("npz_sha256") == last.get("final_npz_sha256"),
                        "Checkpoint field SHA differs")
                factor_valid(last["factor_metadata"], case["N"], 200)
                previous, previous_sha = checkpoint_path, digest
                checkpoints.append({"path": str(previous), "sha256": previous_sha})
                report["completed_chunk_count"] += 1
                print(f"{case['case_id']} steps {steps_start+200}/{case['steps_target']}", flush=True)
            require(last["steps_done"] == case["steps_target"] and sha(previous) == previous_sha,
                    "Final checkpoint identity/completion differs")
            case_report = dict(last)
            case_report.update(schema="silice.point03-analytic.case.v1", status="completed", numeric_pass=True,
                               last_checkpoint_path=str(previous), last_checkpoint_sha256=previous_sha,
                               checkpoint_reports=checkpoints)
            case_path = folder / "case.json"
            write_json(case_path, case_report)
            report["case_reports"].append({"case_id": case["case_id"], "path": str(case_path), "sha256": sha(case_path)})
            print(f"{case['case_id']} completed P_core={last['P_core']:.17g}", flush=True)
        require(len(report["case_reports"]) == 8 and report["completed_chunk_count"] == 144, "Incomplete attempt")
        final_integrity(report, manifest, sources_before, tracked_before)
        propagation = dict(report)
        propagation.update(schema="silice.point03-analytic.propagation.v1", status="completed",
                           operational_pass=True, elapsed_s=time.monotonic()-started, produced_sha256=inventory(out))
        propagation_path = out / "propagation_execution.json"
        write_json(propagation_path, propagation)
        report.update(propagation_execution_path=str(propagation_path), propagation_execution_sha256=sha(propagation_path))
        guard(psutil, out, 45)
        assessment = out / "assessment.json"
        assessment_child = {}
        report["assessment_child"] = assessment_child
        child_run([sys.executable, "-B", "-u", str(ASSESSOR), "--execution", str(propagation_path),
                   "--out", str(assessment)], out / "assessment", started, assessment_child)
        if assessment.is_file():
            report.update(assessment_path=str(assessment), assessment_sha256=sha(assessment))
        require(assessment_child.get("returncode") in (0, 2) and not assessment_child.get("timed_out")
                and not assessment_child.get("interrupted_or_launch_error") and assessment.is_file(),
                "Independent assessment failed operationally")
        verdict = read_json(assessment)
        require(verdict.get("schema") == "silice.point03-analytic.assessment.v1"
                and verdict.get("status") == "completed" and verdict.get("operational_pass") is True
                and type(verdict.get("scientific_pass")) is bool
                and assessment_child["returncode"] == (0 if verdict["scientific_pass"] else 2),
                "Assessment completion/verdict differs")
        report.update(status="completed", operational_pass=True,
                      scientific_pass=verdict["scientific_pass"], science_pass=verdict["scientific_pass"])
    except (Exception, KeyboardInterrupt) as error:
        report.update(status="failed", operational_pass=False, error_type=type(error).__name__, error=str(error))
        if hasattr(error, "diagnostic"):
            report["failure_diagnostic"] = error.diagnostic
    finally:
        # Each block is independent: a failed provenance check cannot skip inventory retention.
        try:
            final_integrity(report, manifest, sources_before, tracked_before)
            if propagation is not None:
                check_hashes(propagation["produced_sha256"])
            for label in ("propagation_execution", "assessment"):
                if label+"_path" in report:
                    require(sha(report[label+"_path"]) == report[label+"_sha256"], "Final report-link bytes changed")
            for child in report["children"] + ([report["assessment_child"]] if "assessment_child" in report else []):
                for label in ("stdout", "stderr"):
                    if label+"_sha256" in child:
                        require(sha(child[label+"_path"]) == child[label+"_sha256"], "Retained log bytes changed")
            if psutil is not None:
                report["resource_exit"] = guard(psutil, out)
                report.update(memory(psutil))
        except (Exception, KeyboardInterrupt) as error:
            report.update(status="failed", operational_pass=False, final_integrity_error=str(error))
            if hasattr(error, "diagnostic"):
                report["final_failure_diagnostic"] = error.diagnostic
        try:
            # Hash even after the work deadline, record any extra retention time as failure.
            retention_started = time.monotonic()
            retained = {str(path.resolve()): sha(path, bounded=False)
                        for path in sorted(out.rglob("*")) if path.is_file()}
            report["produced_sha256"] = retained
            report["final_inventory_retention_s"] = time.monotonic()-retention_started
            if report["operational_pass"]:
                extra = {report["propagation_execution_path"], report["assessment_path"],
                         str(out / "assessment.stdout.log"), str(out / "assessment.stderr.log")}
                require(set(retained) == set(propagation["produced_sha256"]) | extra,
                        "Unexpected/missing final retained outputs")
        except (Exception, KeyboardInterrupt) as error:
            report.update(status="failed", operational_pass=False, final_inventory_error=str(error))
        report["elapsed_s"] = time.monotonic()-started
        if report["elapsed_s"] >= 3600:
            report.update(status="failed", operational_pass=False, total_budget_exceeded=True)
        if not report["operational_pass"]:
            report.update(scientific_pass=None, science_pass=None)
        report["scope"] = "Fixed-model prospective Stage E only; scientific verdict comes exclusively from the independent assessor"
        write_json(out / "execution.json", report)
    print(json.dumps({"status": report["status"], "operational_pass": report["operational_pass"],
                      "science_pass": report["science_pass"], "out_dir": str(out)}), flush=True)
    return (0 if report["science_pass"] else 2) if report["operational_pass"] else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--manifest", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--manifest-sha", help=argparse.SUPPRESS)
    parser.add_argument("--case-id", help=argparse.SUPPRESS)
    parser.add_argument("--steps-start", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--prefix", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--previous", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        if args.out_dir is not None or any(value is None for value in
                (args.manifest, args.manifest_sha, args.case_id, args.steps_start, args.prefix)):
            parser.error("Private worker requires a complete contracted chunk specification")
        return worker(args)
    if any(value is not None for value in
           (args.manifest, args.manifest_sha, args.case_id, args.steps_start, args.prefix, args.previous)):
        parser.error("Private arguments require --worker")
    return run(args.out_dir if args.out_dir else RESULTS / ("point03_analytic_"+stamp()))


if __name__ == "__main__":
    raise SystemExit(main())
