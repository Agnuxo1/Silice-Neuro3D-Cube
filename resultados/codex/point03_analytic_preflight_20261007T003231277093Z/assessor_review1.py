"""Independently assess frozen Point 03 Stage E arrays and evidence.

No propagation, geometry, SciPy or runner module is imported. Exit codes:
0 accepted conditional numerical screens, 2 complete scientific FAIL,
1 invalid/incomplete evidence or an operational failure. The self-checks
exercise scalar assessment logic only and never create optical trajectories.
"""
from __future__ import annotations

import argparse
import ctypes
from datetime import datetime, timezone
import hashlib
import io
import json
import math
import os
from pathlib import Path
import platform
import shutil
import sys
import time


SCHEMA = "silice.point03-analytic.assessment.v1"
RATIO, WIDTH_M, CORE_M = 1.25, 128e-6, 6e-6
GRIDS = (256, 320, 400, 500)
PLAN = [(f"n{n}_geom_z0625", n, .625e-6, 3200, "primary") for n in GRIDS]
PLAN += [(f"n{n}_geom_z125", n, 1.25e-6, 1600, "coarse_control") for n in (400, 500)]
PLAN += [(f"n{n}_geom_z03125", n, .3125e-6, 6400, "fine_control") for n in (400, 500)]
EXPECTED = {row[0]: row for row in PLAN}
THREADS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")
THRESHOLDS = {"minimum_difference_exclusive": 1e-12, "order_disagreement": .20,
              "prediction_fraction": .10, "auxiliary_fraction": .10,
              "individual_auxiliary_max": 2.5e-4, "q_min": 1.8, "q_max": 2.2,
              "safety_factor": 1.25, "total_absolute_max": 1e-3,
              "total_relative_max": .01, "metric_atol": 1e-12,
              "input_power_atol": 1e-12, "detector_area_rtol": 1e-12,
              "raw_final_total_max": 1.001}
B_MANIFEST_SHA = "b09c57d05e190b8fdcc6ad54108e50a05a28570acdc4b82ae12501995c9a0e73"
D_MANIFEST_SHA = "16b64deee8b53b5ed81e3aa15ed01fa533d11032e228b3b20d8b66ce13863512"
D_AUDIT_SHA = "94fb4234b68c0b49f9cc5c6d9c8fd1d8cc31d293818514b9b13ede66eb85a922"
D_GRID_SHA = {
    256: "06223d91e242847e811dfb47b07c6e824096e60d46af606f76504bdc817257be",
    320: "f0ca2b4c3b3ab2bc4fbf6921c12b3d8d9590edd5e98fca99e345ecc896aa5dce",
    400: "c66374c40a35ef0fcf0bad030a315a2bbc959ee6f9a423ced0fe833d220766cf",
    500: "756fe138bb2d8bcc481d258b3101f067cb23d0c2e8e278f4b624e2fe6e17a641"}
SOURCE_PINS = {
    "scripts/point03_sparse_adi.py": "362d4d0fbb56663f0e05fc211cd0c4db031fe20394367c090fea634134ab48bd",
    "experimentos/glass009_claude/adi2d.py": "e4f729bf40a64c545b81f93ab45b282c580349e47612ff20421dea82f1e600fb",
    "experimentos/glass009d_claude/resultados009d.json": "96b5cb7d9fe186b95644e3dfd4f214103db35b655da08d7705acaf33d3feb3ef"}
UPSTREAM_PINS = {
    "B_manifest": ("point03_refinement_20261006T220909702270Z/manifest.json", B_MANIFEST_SHA),
    "C_execution": ("point03_sparse_20261006T223947Z/execution.json", "d8112e1665faf68b55b0b2d5cceccf0344daac0511b1ecf45d849255ade73d71"),
    "C_manifest": ("point03_sparse_20261006T223947Z/audit_manifest.json", "c11722129bc5b1e4f90e0afff1429cce9655d5c2f69841a943a0f02e620db13b"),
    "C_independent": ("point03_sparse_20261006T223947Z/independent_audit.json", "0d2a3578708c1a5bab53a3d4a142a17156ccb10a9388ecddf7be9d7f9e400f72"),
    "D_execution": ("point03_geometry_20261006234649Z/execution.json", "19ed15f1dc1bc6391553033946d216c636507ed2c32ffe690dd7cd32f882227d"),
    "D_manifest": ("point03_geometry_20261006234649Z/audit_manifest.json", D_MANIFEST_SHA),
    "D_independent": ("point03_geometry_20261006234649Z_launch/independent_audit.json", D_AUDIT_SHA)}


class EvidenceError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise EvidenceError(message)


def finite(value, label):
    require(type(value) in (int, float), label + " must be a JSON number")
    try:
        number = float(value)
    except (ValueError, OverflowError) as error:
        raise EvidenceError(label + " is not finite") from error
    require(math.isfinite(number), label + " is not finite")
    return number


def integer(value, label):
    require(type(value) is int, label + " must be an integer, not a boolean")
    return value


def strict_json(raw):
    def constant(value):
        raise EvidenceError("Nonfinite JSON constant: " + value)
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "Duplicate JSON key: " + key)
            result[key] = value
        return result
    def inspect(value):
        if isinstance(value, float):
            require(math.isfinite(value), "Overflowed JSON number")
        elif isinstance(value, dict):
            for child in value.values():
                inspect(child)
        elif isinstance(value, list):
            for child in value:
                inspect(child)
    result = json.loads(raw.decode("utf-8"), parse_constant=constant, object_pairs_hook=pairs)
    require(isinstance(result, dict), "JSON evidence must be an object")
    inspect(result)
    return result


def absolute(value, label="path"):
    require(isinstance(value, str) and value and Path(value).is_absolute(), label + " must be absolute")
    return Path(value).resolve()


class Guard:
    """One-thread assessment with a 31 s work limit and 4 s retention reserve."""
    def __init__(self, output):
        self.started, self.next_resource = time.monotonic(), 0.0
        self.output, self.samples = output, []
    def check(self, full=False):
        now = time.monotonic()
        require(now - self.started < 31, "Assessment work deadline exhausted")
        if not full and now < self.next_resource:
            return
        if os.name == "nt":
            class MemoryStatus(ctypes.Structure):
                _fields_ = [("length", ctypes.c_uint32), ("load", ctypes.c_uint32)] + [
                    (name, ctypes.c_uint64) for name in ("total", "available", "page_total", "page_available",
                                                       "virtual_total", "virtual_available", "extended")]
            state = MemoryStatus()
            state.length = ctypes.sizeof(state)
            require(bool(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(state))), "RAM query failed")
            memory = int(state.available)
        else:
            entries = Path("/proc/meminfo").read_text().splitlines()
            memory = next(int(line.split()[1]) * 1024 for line in entries if line.startswith("MemAvailable:"))
        disk = shutil.disk_usage(self.output.parent).free
        self.samples.append({"elapsed_s": now - self.started, "available_ram_bytes": memory, "free_disk_bytes": disk})
        require(memory > 1.5 * 1024**3 and disk > 2 * 1024**3, "Assessment RAM/disk limit failed")
        self.next_resource = time.monotonic() + 1.0


class Ledger:
    def __init__(self, guard):
        self.guard, self.files = guard, {}
    def _record(self, path, digest, expected):
        require(isinstance(expected, str) and len(expected) == 64
                and all(c in "0123456789abcdef" for c in expected), "Invalid required SHA: " + str(path))
        require(digest == expected, "SHA mismatch: " + str(path))
        require(str(path) not in self.files or self.files[str(path)] == digest, "File changed during assessment: " + str(path))
        self.files[str(path)] = digest
    def hash(self, path, expected, recheck=False):
        path = Path(path).resolve()
        self.guard.check()
        if str(path) in self.files and not recheck:
            self._record(path, self.files[str(path)], expected)
            return
        require(path.is_file() and not path.is_symlink(), "Missing/nonregular evidence: " + str(path))
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(8 * 1024**2), b""):
                digest.update(block)
                self.guard.check()
        self._record(path, digest.hexdigest(), expected)
    def read(self, path, expected=None):
        path = Path(path).resolve()
        self.guard.check()
        require(path.stat().st_size <= 64 * 1024**2, "Unexpectedly large JSON/NPZ read")
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        self._record(path, digest, digest if expected is None else expected)
        self.guard.check()
        return raw
    def json(self, path, expected=None):
        return strict_json(self.read(path, expected))
    def confirm(self):
        for path, digest in list(self.files.items()):
            self.hash(path, digest, recheck=True)


def unique_cases(records, label):
    require(isinstance(records, list) and len(records) == 8, label + " must have exactly eight cases")
    result = {}
    for record in records:
        require(isinstance(record, dict), label + " entry is not an object")
        name = record.get("case_id")
        require(name in EXPECTED and name not in result, label + " has an unexpected/duplicate case")
        result[name] = record
    return result


def validate_spec(record, name):
    _, n, dz, steps, role = EXPECTED[name]
    require(record.get("case_id") == name and record.get("role") == role, "Case ID/role changed: " + name)
    for key, expected in (("N", n), ("steps_target", steps)):
        require(integer(record.get(key), key) == expected, "Case specification changed: " + key)
    for key, expected in (("width_m", WIDTH_M), ("dx_m", WIDTH_M / n), ("dz_m", dz)):
        require(finite(record.get(key), key) == expected, "Case specification changed: " + key)


def observed_order(first, second, ratio):
    if first == 0 or second == 0:
        return None
    value = (math.log(abs(first)) - math.log(abs(second))) / math.log(ratio)
    return value if math.isfinite(value) else None


def first_three_prediction(powers):
    d0, d1 = powers[1] - powers[0], powers[2] - powers[1]
    order = observed_order(d0, d1, RATIO)
    valid = (abs(d0) > 1e-12 and abs(d1) > 1e-12 and d0 * d1 > 0
             and order is not None and order > 0)
    predicted = powers[2] + d1 * math.exp(-order * math.log(RATIO)) if valid else None
    return {"signed_differences": [d0, d1], "observed_order": order,
            "predicted_core_power": predicted, "valid_fit": bool(valid)}


def primary_screen(powers):
    require(len(powers) == 4 and all(math.isfinite(p) for p in powers), "Invalid primary powers")
    differences = [powers[i + 1] - powers[i] for i in range(3)]
    require(all(math.isfinite(d) for d in differences), "Nonfinite primary differences")
    magnitudes = list(map(abs, differences))
    nonzero = all(d > 1e-12 for d in magnitudes)
    signed = nonzero and (all(d > 0 for d in differences) or all(d < 0 for d in differences))
    orders = [observed_order(differences[i], differences[i + 1], RATIO) for i in range(2)]
    positive = all(order is not None and order > 0 for order in orders)
    disagreement = abs(orders[1] - orders[0]) / max(orders) if positive else None
    prediction = first_three_prediction(powers)
    residual = abs(powers[3] - prediction["predicted_core_power"]) if prediction["valid_fit"] else None
    limit = .10 * magnitudes[2]
    gates = {"nonzero_differences": nonzero, "same_signed_differences": signed,
             "positive_finite_observed_orders": positive,
             "observed_order_stability": positive and disagreement <= .20,
             "withheld_finest_grid_prediction": residual is not None and residual <= limit}
    return {"signed_differences": differences, "absolute_differences": magnitudes,
            "candidate_observed_orders": orders, "relative_order_disagreement": disagreement,
            "holdout": dict(prediction, absolute_residual=residual, maximum_residual=limit),
            "gates": gates, "primary_screen_pass": all(gates.values())}


def assess_values(records):
    values = {name: finite(row.get("P_core"), name) for name, row in unique_cases(records, "Measurements").items()}
    require(all(value >= 0 for value in values.values()), "Negative measured core power")
    powers = [values[f"n{n}_geom_z0625"] for n in GRIDS]
    result = primary_screen(powers)
    auxiliary = {}
    factor = 1 + 1.25 / (2**1.8 - 1)
    for n in (400, 500):
        mid = values[f"n{n}_geom_z0625"]
        a, b = values[f"n{n}_geom_z125"] - mid, mid - values[f"n{n}_geom_z03125"]
        require(math.isfinite(a) and math.isfinite(b), "Nonfinite longitudinal contrast")
        q = observed_order(a, b, 2)
        valid = abs(a) > 1e-12 and abs(b) > 1e-12 and a * b > 0 and q is not None and 1.8 <= q <= 2.2
        auxiliary[str(n)] = {"a": a, "b": b, "candidate_q": q, "q_gate_pass": bool(valid),
                             "diagnostic_S_formula": abs(b) * factor,
                             "accepted_S": abs(b) * factor if valid else None}
    aux_valid = all(row["q_gate_pass"] for row in auxiliary.values())
    aux_sum = sum(row["accepted_S"] for row in auxiliary.values()) if aux_valid else None
    aux_limit = .10 * result["absolute_differences"][2]
    individual = aux_valid and all(abs(row["a"]) <= 2.5e-4 and abs(row["b"]) <= 2.5e-4
                                   and row["accepted_S"] <= 2.5e-4 for row in auxiliary.values())
    corners = []
    if aux_valid:
        for s400 in (-1, 1):
            for s500 in (-1, 1):
                perturbed = [*powers[:2], powers[2] + s400 * auxiliary["400"]["accepted_S"],
                             powers[3] + s500 * auxiliary["500"]["accepted_S"]]
                corners.append(dict(primary_screen(perturbed), sign400=s400, sign500=s500, powers=perturbed))
    gates = dict(result["gates"], longitudinal_order_band=aux_valid,
                 individual_auxiliary_components=individual,
                 auxiliary_difference_budget=aux_valid and aux_sum <= aux_limit,
                 auxiliary_corner_robustness=len(corners) == 4 and all(c["primary_screen_pass"] for c in corners))
    prerequisites = all(gates.values())
    candidate = None
    if prerequisites:
        denominator = math.expm1(result["candidate_observed_orders"][1] * math.log(RATIO))
        spatial = 1.25 * result["absolute_differences"][2] / denominator
        total = spatial + auxiliary["500"]["accepted_S"]
        extrapolated = powers[3] + result["signed_differences"][2] / denominator
        require(all(math.isfinite(v) for v in (denominator, spatial, total, extrapolated)) and denominator > 0,
                "Invalid conditional indicator")
        candidate = {"u_space": spatial, "S500": auxiliary["500"]["accepted_S"], "u_total": total,
                     "extrapolated_core_power": extrapolated, "relative_u_total": total / abs(powers[3]) if powers[3] else None}
    gates["absolute_total_indicator"] = candidate is not None and candidate["u_total"] <= 1e-3
    gates["relative_total_indicator"] = candidate is not None and candidate["u_total"] <= .01 * abs(powers[3])
    passed = all(gates.values())
    return dict(result, schema=SCHEMA, status="passed" if passed else "scientific_fail", scientific_pass=passed,
                thresholds=dict(THRESHOLDS), primary_grids=list(GRIDS), primary_core_powers=powers,
                gates=gates, auxiliary=auxiliary, auxiliary_sum_both_grids=aux_sum,
                auxiliary_maximum_sum=aux_limit, auxiliary_sensitivity_corners=corners,
                asymptotic_screening_pass=prerequisites, richardson_candidate=candidate,
                accepted_gci=candidate if passed else None, historical_Q4_replaced=False,
                historical_StageB_replaced=False,
                old_style_Q4_all_adjacent_triples=result["absolute_differences"][2] <= result["absolute_differences"][1] <= result["absolute_differences"][0],
                scope="Conditional local scalar-functional screens only; no certified error bound, full-rectangle robustness, external replication, or physical validation.")


def same_path(value, expected, label):
    require(absolute(value, label) == expected, label + " identifies a different file")


def close(value, expected, label, atol=1e-12):
    error = abs(finite(value, label) - expected)
    require(error <= atol, label + " does not reproduce")
    return error


def hash_map(mapping, ledger, label, root=None):
    require(isinstance(mapping, dict) and bool(mapping), label + " is empty/missing")
    paths = {}
    for name, digest in mapping.items():
        if root is None:
            path = absolute(name, label)
        else:
            require(isinstance(name, str) and name and not Path(name).is_absolute(), "Invalid tracked path")
            path = (root / name).resolve()
            require(path.is_relative_to(root), "Tracked path escapes checkout")
        require(str(path) not in paths, "Duplicate canonical path in " + label)
        ledger.hash(path, digest)
        paths[str(path)] = digest
    return paths


def moment(value, label):
    require(isinstance(value, str), label + " timestamp missing")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(parsed.tzinfo is not None and parsed.utcoffset().total_seconds() == 0, label + " must be UTC")
    return parsed


def open_arrays(np, ledger, path, digest, keys, n, only=True):
    with np.load(io.BytesIO(ledger.read(path, digest)), allow_pickle=False) as archive:
        require(len(archive.files) == len(set(archive.files)), "Duplicate NPZ entries")
        require(set(archive.files) == set(keys) if only else set(keys) <= set(archive.files), "NPZ keys differ")
        arrays = {key: archive[key] for key in keys}
    for key, array in arrays.items():
        dtype = np.dtype("complex128" if key in ("A0", "field") else "uint8" if key == "cell_status" else "float64")
        require(array.shape == (n, n) and array.dtype == dtype and np.all(np.isfinite(array)), "Invalid retained array: " + key)
    return arrays


def audit_manifest(execution_path, ledger):
    execution = ledger.json(execution_path)
    require(execution.get("schema") == "silice.point03-analytic.propagation.v1"
            and execution.get("status") == "completed" and execution.get("operational_pass") is True,
            "All eight new trajectories have not completed operationally")
    manifest_path = absolute(execution.get("manifest_path"))
    identity = execution.get("manifest_sha256")
    manifest = ledger.json(manifest_path, identity)
    require(manifest.get("schema") == "silice.point03-analytic.manifest.v1", "Unknown manifest schema")
    root, out = absolute(manifest.get("source_root")), manifest_path.parent
    require(Path(__file__).resolve() == root / "scripts/assess_point03_analytic.py", "Use the frozen assessor checkout")
    require(out.parent == root / "resultados/codex" and out.name.startswith("point03_analytic_"), "Wrong attempt directory")
    same_path(manifest.get("out_dir"), out, "Manifest output directory")
    same_path(execution.get("out_dir"), out, "Propagation output directory")
    require(execution_path == out / "propagation_execution.json", "Wrong immutable propagation report")
    source_names = ("Docs/POINT-03-ANALYTIC-PROPAGATION-CONTRACT.md", "scripts/assess_point03_analytic.py",
                    "scripts/run_point03_analytic.py", "scripts/point03_sparse_adi.py",
                    "experimentos/glass009_claude/adi2d.py", "Docs/POINT-03-Q4-REFINEMENT-CONTRACT.md",
                    "Docs/POINT-03-SPARSE-ADI-CONTRACT.md", "Docs/POINT-03-GEOMETRY-CONTRACT.md")
    sources = manifest.get("source_sha256")
    require(isinstance(sources, dict) and set(sources) == {str(root / name) for name in source_names}, "Frozen source set differs")
    hash_map(sources, ledger, "Source map")
    require(execution.get("sources_unchanged") is True and execution.get("source_sha256_before") == sources
            and execution.get("source_sha256_after") == sources, "Source snapshots differ")
    tracked = execution.get("tracked_sha256_before")
    require(execution.get("tracked_inputs_unchanged") is True and execution.get("tracked_sha256_after") == tracked
            and execution.get("tracked_changed_paths") == [], "Tracked snapshots differ")
    tracked_paths = hash_map(tracked, ledger, "Tracked inventory", root)
    require(all(tracked_paths.get(path) == digest for path, digest in sources.items()), "A scientific source is not tracked")
    for name, digest in SOURCE_PINS.items():
        path = root / name
        ledger.hash(path, digest)
        require(tracked_paths.get(str(path)) == digest, "Pinned source/history is not in the tracked inventory")
    contract = root / source_names[0]
    same_path(manifest.get("contract_path"), contract, "E contract")
    require(manifest.get("contract_sha256") == sources[str(contract)], "Contract digest differs from frozen sources")
    frozen = manifest.get("frozen_input_sha256")
    require(execution.get("frozen_inputs_unchanged") is True and execution.get("frozen_input_sha256_before") == frozen
            and execution.get("frozen_input_sha256_after") == frozen, "Frozen input snapshots differ")
    frozen_paths = hash_map(frozen, ledger, "Frozen inputs")
    upstream = manifest.get("upstream")
    require(isinstance(upstream, dict) and set(upstream) == set(UPSTREAM_PINS), "Missing/changed upstream study set")
    prior = {}
    for name, (relative, digest) in UPSTREAM_PINS.items():
        path = root / "resultados/codex" / relative
        same_path(upstream[name].get("path"), path, name)
        require(upstream[name].get("sha256") == frozen_paths.get(str(path)) == digest, "Upstream pin changed: " + name)
        prior[name] = ledger.json(path, digest)
    require(prior["B_manifest"].get("schema") == "silice.point03-refinement.manifest.v1", "Unknown B evidence")
    for letter, gate in (("C", "equivalence_pass"), ("D", "geometry_pass")):
        previous = prior[letter + "_execution"]
        require(previous.get("status") == "completed" and previous.get("operational_pass") is True and previous.get(gate) is True,
                "Upstream " + letter + " is not accepted")
        require(prior[letter + "_independent"].get("status") == "PASS"
                and previous.get("audit_manifest_sha256") == UPSTREAM_PINS[letter + "_manifest"][1], "Upstream audit linkage differs")
    history_path = root / "experimentos/glass009d_claude/resultados009d.json"
    history_sha = SOURCE_PINS[history_path.relative_to(root).as_posix()]
    same_path(manifest.get("historical_Q4_path"), history_path, "Historical Q4")
    require(manifest.get("historical_Q4_sha256") == frozen_paths.get(str(history_path))
            == prior["B_manifest"].get("source_sha256", {}).get(str(history_path)) == history_sha, "Historical identity differs")
    old = ledger.json(history_path, history_sha).get("T96d", {})
    old_p = [finite(old.get(key), key) for key in ("P_dx0p625", "P_dx0p5", "P_dx0p4")]
    old_d = [old_p[i + 1] - old_p[i] for i in range(2)]
    require(old.get("Q4_monotone") is False and not (abs(old_d[1]) <= abs(old_d[0])), "Historical Q4 FAIL changed")
    physics = manifest.get("physics", {})
    for key, value in {"width_m": WIDTH_M, "wavelength_m": 1550e-9, "n_ref": 1.444, "z_m": .002,
                       "dn_track": -.003, "core_radius_m": CORE_M}.items():
        require(finite(physics.get(key), key) == value, "Changed optical model: " + key)
    require(physics.get("array_axis") == "(arange(N)-N//2)*dx_m", "Changed grid convention")
    plans = unique_cases(manifest.get("case_plan"), "Manifest")
    require(list(plans) == list(EXPECTED), "Execution order changed")
    for name, plan in plans.items():
        validate_spec(plan, name)
        require(plan.get("profile_kind") == "accepted_D_analytic", "Changed index profile family")
    for key, expected in (("total_wall_budget_s", 3600), ("propagation_chunk_steps", 200), ("propagation_chunk_count", 144)):
        require(integer(manifest.get(key), key) == expected, "Execution budget/plan changed")
    require(execution.get("completed_chunk_count") == 144 and execution.get("gpu_used") is False
            and execution.get("resume_allowed") is False and 0 <= finite(execution.get("elapsed_s"), "Propagation time") < 3600,
            "Propagation completion/resource metadata differs")
    environment = manifest.get("environment", {})
    require(environment == execution.get("environment"), "Environment records differ")
    for key, value in {"python": "3.13.7", "numpy": "2.2.6", "scipy": "1.15.1", "psutil": "6.1.1"}.items():
        require(environment.get(key) == value, "CPU environment changed: " + key)
    require(environment.get("threads") == {key: "1" for key in THREADS}, "Numerical thread settings differ")
    produced = hash_map(execution.get("produced_sha256"), ledger, "Produced output inventory")
    require(all(Path(path).is_relative_to(out) for path in produced) and str(execution_path) not in produced,
            "Produced outputs escape attempt or create a hash cycle")
    return {"execution": execution, "manifest": manifest, "manifest_path": manifest_path, "identity": identity,
            "root": root, "out": out, "sources": sources, "frozen": frozen_paths, "produced": produced,
            "plans": plans, "prior": prior, "tracked_count": len(tracked),
            "historical": {"path": str(history_path), "sha256": history_sha, "T96d_core_powers": old_p,
                           "signed_differences": old_d, "stored_Q4": False, "recomputed_Q4": False,
                           "scope": "Current bytes checked; current hashes do not retrospectively authenticate execution."}}


def audit_inputs(context, np, ledger):
    manifest, prior, out = (context[key] for key in ("manifest", "prior", "out"))
    entries = manifest.get("prepared_inputs")
    require(isinstance(entries, list) and len(entries) == 4, "Exactly four prepared inputs required")
    d_grids = prior["D_manifest"].get("grids", [])
    require(len(d_grids) == 4 and {row.get("N") for row in d_grids} == set(GRIDS), "D grid specifications differ")
    spec = prior["D_manifest"].get("spec_um", {})
    require(len(spec.get("disks", [])) == 96 and all(row[2] == 1.25 for row in spec["disks"])
            and spec.get("annulus") == {"center": [0.0, 0.0], "inner": 6.0, "outer": 12.0}, "Accepted D geometry differs")
    inputs, summaries = {}, []
    for row in entries:
        ledger.guard.check()
        n = integer(row.get("N"), "Prepared N")
        require(n in GRIDS and n not in inputs, "Unexpected/duplicate prepared grid")
        path, digest = out / "inputs" / f"n{n}_geom.npz", row.get("input_npz_sha256")
        same_path(row.get("input_npz_path"), path, "Prepared input")
        require(context["frozen"].get(str(path)) == digest, "New input is not frozen")
        arrays = open_arrays(np, ledger, path, digest, ("A0", "dn", "sigma", "weights"), n)
        expected_hashes = {key: hashlib.sha256(array.tobytes(order="C")).hexdigest() for key, array in arrays.items()}
        require(row.get("array_sha256") == expected_hashes, "Per-array byte hashes differ")
        b_matches = [item for item in prior["B_manifest"]["prepared_inputs"] if item["N"] == n and item["profile_samples"] == 64]
        d_matches = [item for item in prior["D_execution"]["grid_reports"] if item["N"] == n]
        require(len(b_matches) == len(d_matches) == 1, "Upstream grid/input linkage is ambiguous")
        b_row, d_link = b_matches[0], d_matches[0]
        same_path(row.get("B_input_npz_path"), absolute(b_row["input_npz_path"]), "B SS64 source")
        require(row.get("B_input_npz_sha256") == b_row["input_npz_sha256"], "B input hash differs")
        same_path(row.get("D_grid_report_path"), absolute(d_link["path"]), "D grid report")
        require(row.get("D_grid_report_sha256") == d_link["sha256"], "D grid report hash differs")
        d_report = ledger.json(absolute(d_link["path"]), d_link["sha256"])
        require(d_report.get("status") == "grid_completed" and d_report.get("numeric_valid") is True
                and d_report.get("N") == n and d_report.get("cells_completed") == n*n
                and d_report.get("dx_um") == 128.0/n, "Accepted D grid is incomplete or changed")
        artifact = [item for item in d_report.get("array_artifacts", []) if item.get("sha256") == D_GRID_SHA[n]]
        require(len(artifact) == 1 and row.get("D_grid_npz_sha256") == D_GRID_SHA[n]
                and row.get("D_fraction_key") == "fraction", "D coverage pin changed")
        same_path(row.get("D_grid_npz_path"), absolute(artifact[0]["path"]), "Accepted D coverage")
        for role, original, original_sha in (("B", absolute(b_row["input_npz_path"]), b_row["input_npz_sha256"]),
                                             ("D", absolute(artifact[0]["path"]), D_GRID_SHA[n])):
            copied = out / "upstream_copies" / f"n{n}_{role}.npz"
            same_path(row.get(role + "_copy_path"), copied, role + " retained copy")
            require(row.get(role + "_copy_sha256") == context["frozen"].get(str(copied))
                    == context["frozen"].get(str(original)) == original_sha, "Source/copy is not frozen identically")
            ledger.hash(copied, original_sha)
            ledger.hash(original, original_sha)
        b_arrays = open_arrays(np, ledger, absolute(row["B_copy_path"]), row["B_copy_sha256"],
                               ("A0", "dn", "sigma", "weights"), n)
        for key in ("A0", "sigma", "weights"):
            require(arrays[key].tobytes(order="C") == b_arrays[key].tobytes(order="C"), "Unchanged B array differs: " + key)
        require(row.get("upstream_unchanged_array_sha256") == {key: expected_hashes[key] for key in ("A0", "sigma", "weights")},
                "Unchanged-array hash record differs")
        d_arrays = open_arrays(np, ledger, absolute(row["D_copy_path"]), D_GRID_SHA[n],
                               ("fraction", "raw_fraction", "cell_status"), n, only=False)
        fraction, raw = d_arrays["fraction"], d_arrays["raw_fraction"]
        require(np.all((d_arrays["cell_status"] == 1) | (d_arrays["cell_status"] == 2))
                and np.all((fraction >= 0) & (fraction <= 1)) and np.all((raw >= -1e-12) & (raw <= 1+1e-12))
                and np.array_equal(fraction, np.clip(raw, 0, 1)), "D endpoint correction/completion differs")
        require(arrays["dn"].tobytes(order="C") == (-.003*fraction).tobytes(order="C"), "Index is not the exact prescribed D product")
        correction_count = int(np.count_nonzero(fraction - raw))
        correction_max = float(np.max(np.abs(fraction - raw)))
        require(row.get("raw_endpoint_correction_count") == d_report.get("endpoint_correction_count") == correction_count
                and row.get("raw_endpoint_correction_max") == d_report.get("max_absolute_endpoint_correction") == correction_max,
                "Endpoint correction diagnostics differ")
        grid = next(item for item in d_grids if item["N"] == n)
        dx = WIDTH_M / n
        require(grid.get("width_m") == WIDTH_M and grid.get("dx_m") == dx and grid.get("dx_um") == 128.0/n
                and np.asarray(grid.get("axis_m"), dtype=np.float64).tobytes()
                == ((np.arange(n)-n//2)*dx).tobytes(), "D/B cell-axis convention differs")
        require(row.get("D_grid_identity") == {"N": n, "dx_um": 128.0/n, "axis": "(arange(N)-N//2)*dx"}, "D identity record differs")
        require(np.all(arrays["sigma"] >= 0) and np.all((arrays["weights"] >= 0) & (arrays["weights"] <= 1)), "Nonpassive absorber/detector")
        with np.errstate(over="raise", invalid="raise", divide="raise"):
            pin = float(np.sum(np.abs(arrays["A0"])**2)*dx**2)
            area = float(np.sum(arrays["weights"])*dx**2)
        require(math.isfinite(pin) and abs(pin-1) <= 1e-12 and math.isfinite(area)
                and abs(area/(math.pi*CORE_M**2)-1) <= 1e-12, "Input power/detector area failed")
        inputs[n] = {"path": path, "sha256": digest, "weights": arrays["weights"], "P_in": pin, "core_area_m2": area}
        summaries.append({"N": n, "input_npz_path": str(path), "input_npz_sha256": digest,
                          "P_in": pin, "core_area_m2": area, "unchanged_B_array_bytes": True,
                          "prescribed_D_index_bytes": True, "array_sha256": expected_hashes,
                          "endpoint_correction_count": correction_count, "maximum_endpoint_correction": correction_max})
    for plan in context["plans"].values():
        same_path(plan.get("input_npz_path"), inputs[plan["N"]]["path"], "Case input")
        require(plan.get("input_npz_sha256") == inputs[plan["N"]]["sha256"], "Case does not reuse its frozen input")
    return inputs, summaries


def numeric_report(row, initial, actual=None, final=False):
    pin, area = initial["P_in"], initial["core_area_m2"]
    raw = finite(row.get("raw_total_power"), "Raw total") if actual is None else actual["raw_total_power"]
    core = finite(row.get("P_core"), "Core power") if actual is None else actual["P_core"]
    require(math.isfinite(raw) and math.isfinite(core) and raw >= 0 and 0 <= core <= raw/pin+1e-12,
            "Power/detector validity screen failed")
    require(not final or raw <= 1.001, "Raw final total exceeds 1.001")
    metrics = {"P_in": pin, "input_power": pin, "P0": pin, "raw_total_power": raw,
               "output_power": raw, "P_final": raw, "P_total": raw/pin,
               "P_core": core, "core_power_analytic_input": core, "core_area_m2": area}
    errors = {key: close(row.get(key), value, key) for key, value in metrics.items()}
    require(abs(finite(row.get("core_area_m2"), "Core area")/area-1) <= 1e-12, "Reported detector area differs")
    return metrics, errors


def audit_factors(metadata, n, np, permutation_hashes):
    require(isinstance(metadata, dict) and metadata.get("backend") == "scipy.sparse.linalg.splu"
            and metadata.get("numpy_version") == "2.2.6" and metadata.get("scipy_version") == "1.15.1"
            and metadata.get("options") == {"permc_spec": "NATURAL", "diag_pivot_thresh": 0.0, "Equil": False},
            "Sparse factor implementation/options differ")
    factors = metadata.get("factors")
    require(isinstance(factors, list) and len(factors) == 2, "Expected two factors per chunk")
    for index, factor in enumerate(factors):
        values = {"factor_index": index, "line_count": n, "line_size": n, "matrix_order": n*n,
                  "matrix_nnz": 3*n*n-2*n, "expected_matrix_nnz": 3*n*n-2*n, "solve_calls": 200}
        for key, expected in values.items():
            require(integer(factor.get(key), key) == expected, "Sparse factor structure/solve count differs")
        for key in ("perm_r", "perm_c"):
            permutation = factor.get(key, {})
            dtype = permutation.get("dtype")
            require(dtype in ("int32", "int64") and permutation.get("identity") is True
                    and permutation.get("nonidentity_entries") == 0 and permutation.get("length") == n*n,
                    "Sparse permutation is not identity")
            pair = (n, dtype)
            if pair not in permutation_hashes:
                permutation_hashes[pair] = hashlib.sha256(np.arange(n*n, dtype=np.dtype(dtype)).tobytes()).hexdigest()
            require(permutation.get("sha256") == permutation_hashes[pair], "Recorded identity permutation hash differs")


def audit_cases(context, inputs, np, ledger, progress):
    execution, out, identity = (context[key] for key in ("execution", "out", "identity"))
    references = unique_cases(execution.get("case_reports"), "Completed cases")
    require(list(references) == list(EXPECTED), "Completed cases are reordered")
    require({path.name for path in (out / "cases").iterdir()} == set(EXPECTED), "Unexpected case directory/evidence")
    children = execution.get("children")
    require(isinstance(children, list) and len(children) == 144, "Exactly 144 successful chunks required")
    seen, case_data, permutation_hashes, child_index = set(), {}, {}, 0
    measures = progress["completed_case_audits"] = []
    manifest_time = moment(context["manifest"].get("created_utc"), "Manifest")
    previous_end, previous_time = 0.0, manifest_time
    expected_outputs = {str(out / "attempt.json"), str(context["manifest_path"])}
    expected_outputs.update(path for path in context["frozen"] if Path(path).is_relative_to(out))
    for name, n, dz, steps, role in PLAN:
        ledger.guard.check()
        initial, reference = inputs[n], references[name]
        folder, case_path = out / "cases" / name, out / "cases" / name / "case.json"
        same_path(reference.get("path"), case_path, "Completed case report")
        require(context["produced"].get(str(case_path)) == reference.get("sha256"), "Case is absent from output inventory")
        case = ledger.json(case_path, reference.get("sha256"))
        require(case.get("schema") == "silice.point03-analytic.case.v1" and case.get("status") == "completed"
                and case.get("numeric_pass") is True, "Case is not complete")
        validate_spec(case, name)
        links = case.get("checkpoint_reports")
        require(isinstance(links, list) and len(links) == steps//200, "Wrong checkpoint count for " + name)
        previous_path, previous_sha, last, case_elapsed = None, None, None, 0.0
        folder_outputs = {str(case_path)}
        for sequence, link in enumerate(links):
            checkpoint_path = absolute(link.get("path"), "Checkpoint")
            digest = link.get("sha256")
            require(checkpoint_path.parent == folder and checkpoint_path.name.startswith("chunk_")
                    and checkpoint_path.suffix == ".json" and str(checkpoint_path) not in seen, "Duplicate/misplaced checkpoint")
            seen.add(str(checkpoint_path))
            require(context["produced"].get(str(checkpoint_path)) == digest, "Checkpoint is not enrolled in outputs")
            checkpoint = ledger.json(checkpoint_path, digest)
            require(checkpoint.get("schema") == "silice.point03-analytic.checkpoint.v1"
                    and checkpoint.get("status") == "checkpoint_completed", "Incomplete checkpoint in chain")
            validate_spec(checkpoint, name)
            require(checkpoint.get("profile_kind") == "accepted_D_analytic" and checkpoint.get("manifest_sha256") == identity
                    and checkpoint.get("numeric_valid") is True and checkpoint.get("sources_unchanged") is True
                    and checkpoint.get("input_unchanged") is True and checkpoint.get("gpu_used") is False
                    and checkpoint.get("dtype") == "complex128", "Checkpoint model/validity identity differs")
            require(checkpoint.get("source_sha256_before") == context["sources"]
                    and checkpoint.get("source_sha256_after") == context["sources"], "Checkpoint source snapshots differ")
            same_path(checkpoint.get("input_npz_path"), initial["path"], "Checkpoint input")
            require(checkpoint.get("input_npz_sha256") == initial["sha256"], "Checkpoint input hash differs")
            start, done = 200*sequence, 200*(sequence+1)
            for key, value in (("steps_start", start), ("steps_done", done), ("steps_completed", done)):
                require(integer(checkpoint.get(key), key) == value, "Gap/wrong steps in checkpoint chain")
            require(checkpoint.get("previous_checkpoint_path") == (str(previous_path) if previous_path else None)
                    and checkpoint.get("previous_checkpoint_sha256") == previous_sha, "Checkpoint predecessor identity differs")
            npz_path = checkpoint_path.with_suffix(".npz")
            same_path(checkpoint.get("npz_path"), npz_path, "Checkpoint field")
            same_path(checkpoint.get("final_npz_path"), npz_path, "Checkpoint field alias")
            require(checkpoint.get("npz_sha256") == checkpoint.get("final_npz_sha256")
                    == context["produced"].get(str(npz_path)), "Checkpoint field digest differs")
            ledger.hash(npz_path, checkpoint.get("npz_sha256"))
            numeric_report(checkpoint, initial, final=done == steps)
            audit_factors(checkpoint.get("factor_metadata"), n, np, permutation_hashes)
            require(0 <= finite(checkpoint.get("elapsed_s"), "Worker elapsed") <= 35, "Worker deadline exceeded")
            child = children[child_index]
            require(child.get("case_id") == name and integer(child.get("steps_start"), "Child start") == start
                    and integer(child.get("steps_done"), "Child end") == done and child.get("returncode") == 0
                    and not child.get("timed_out") and not child.get("interrupted_or_launch_error"), "Child sequence/status differs")
            for prefix in ("checkpoint", "worker_report"):
                same_path(child.get(prefix + "_path"), checkpoint_path, "Child report")
                require(child.get(prefix + "_sha256") == digest, "Child report hash differs")
            prefix = checkpoint_path.with_suffix("")
            command = [sys.executable, "-B", "-u", str(context["root"] / "scripts/run_point03_analytic.py"), "--worker",
                       "--manifest", str(context["manifest_path"]), "--manifest-sha", identity,
                       "--case-id", name, "--steps-start", str(start), "--prefix", str(prefix)]
            if previous_path is not None:
                command.extend(("--previous", str(previous_path)))
            require(child.get("command") == command, "Child launch differs from prescribed chain")
            started, elapsed = finite(child.get("started_elapsed_s"), "Child start time"), finite(child.get("elapsed_s"), "Child duration")
            started_utc = moment(child.get("started_utc"), "Child")
            require(started >= previous_end and 0 <= elapsed <= 40 and started_utc >= previous_time
                    and moment(checkpoint.get("created_utc"), "Worker") >= started_utc, "Sequential child chronology/budget differs")
            previous_end, previous_time = started+elapsed, started_utc
            case_elapsed += elapsed
            for label in ("stdout", "stderr"):
                log_path = Path(str(prefix) + "." + label + ".log")
                same_path(child.get(label + "_path"), log_path, "Raw child log")
                require(child.get(label + "_sha256") == context["produced"].get(str(log_path)), "Raw log is not enrolled")
                ledger.hash(log_path, child.get(label + "_sha256"))
                folder_outputs.add(str(log_path))
            folder_outputs.update((str(checkpoint_path), str(npz_path)))
            previous_path, previous_sha, last = checkpoint_path, digest, checkpoint
            child_index += 1
            progress["checkpoint_chains_verified"] = child_index
        same_path(case.get("last_checkpoint_path"), previous_path, "Last checkpoint")
        require(case.get("last_checkpoint_sha256") == previous_sha, "Last checkpoint digest differs")
        require(all(case.get(key) == value for key, value in last.items() if key not in ("schema", "status")),
                "Final case metadata differs from its last checkpoint")
        final_path, final_sha = absolute(case.get("final_npz_path")), case.get("final_npz_sha256")
        field = open_arrays(np, ledger, final_path, final_sha, ("field",), n)["field"]
        with np.errstate(over="raise", invalid="raise", divide="raise"):
            intensity = np.abs(field)**2
            raw = float(np.sum(intensity)*(WIDTH_M/n)**2)
            core = float(np.sum(initial["weights"]*intensity)*(WIDTH_M/n)**2/initial["P_in"])
        metrics, errors = numeric_report(case, initial, {"raw_total_power": raw, "P_core": core}, final=True)
        require({str(path.resolve()) for path in folder.rglob("*") if path.is_file()} == folder_outputs,
                "Disconnected/unlisted case evidence exists")
        expected_outputs.update(folder_outputs)
        measures.append(dict(metrics, case_id=name, N=n, role=role, dz_m=dz, steps_completed=steps,
                             case_path=str(case_path), case_sha256=reference["sha256"],
                             input_npz_path=str(initial["path"]), input_npz_sha256=initial["sha256"],
                             final_npz_path=str(final_path), final_npz_sha256=final_sha,
                             checkpoint_count=len(links), sum_child_elapsed_s=case_elapsed, metric_absolute_errors=errors))
        case_data[name] = (case, reference)
    require(child_index == len(seen) == 144 and previous_end <= finite(execution.get("elapsed_s"), "Propagation elapsed"),
            "Incomplete chain count/end chronology")
    return measures, case_data, expected_outputs


def audit_prediction(context, case_data, measures, ledger):
    execution, out, identity = (context[key] for key in ("execution", "out", "identity"))
    path, digest = out / "prediction.json", execution.get("prediction_sha256")
    same_path(execution.get("prediction_path"), path, "Frozen prediction")
    require(context["produced"].get(str(path)) == digest, "Prediction is not enrolled in outputs")
    record = ledger.json(path, digest)
    require(record.get("schema") == "silice.point03-analytic.prediction.v1" and record.get("manifest_sha256") == identity
            and integer(record.get("completed_chunk_count"), "Prediction chunk count") == 48, "Wrong prediction identity/position")
    same_path(record.get("manifest_path"), context["manifest_path"], "Prediction manifest")
    rows = record.get("first_three_case_reports")
    require(isinstance(rows, list) and len(rows) == 3, "Prediction did not use exactly three cases")
    for index, row in enumerate(rows):
        name = PLAN[index][0]
        case, reference = case_data[name]
        require(row.get("case_id") == name and row.get("path") == reference["path"]
                and row.get("sha256") == reference["sha256"], "Prediction uses different case evidence")
        for key in ("input_npz_path", "input_npz_sha256", "final_npz_path", "final_npz_sha256", "P_core"):
            require(row.get(key) == case.get(key), "Prediction case input/field/power differs")
        close(row.get("P_core"), measures[index]["P_core"], "Prediction input power")
    prediction = first_three_prediction([row["P_core"] for row in measures[:3]])
    differences = record.get("signed_differences")
    require(isinstance(differences, list) and len(differences) == 2, "Prediction differences missing")
    for actual, expected in zip(differences, prediction["signed_differences"]):
        close(actual, expected, "Prediction difference")
    require(record.get("valid_fit") is prediction["valid_fit"] and isinstance(record.get("invalid_reasons"), list)
            and bool(record["invalid_reasons"]) is not prediction["valid_fit"], "Frozen prediction validity differs")
    if prediction["valid_fit"]:
        close(record.get("observed_order"), prediction["observed_order"], "Frozen order")
        close(record.get("predicted_core_power"), prediction["predicted_core_power"], "Frozen fourth-grid prediction")
    else:
        require(record.get("predicted_core_power") is None, "Invalid prediction must be null")
        if record.get("observed_order") is not None:
            require(prediction["observed_order"] is not None, "Unexpected finite diagnostic order")
            close(record["observed_order"], prediction["observed_order"], "Diagnostic prediction order")
    children = execution["children"]
    previous, withheld = children[47], children[48]
    elapsed = finite(record.get("parent_elapsed_s"), "Prediction elapsed")
    saved_time = moment(record.get("created_utc"), "Prediction")
    require(elapsed >= previous["started_elapsed_s"]+previous["elapsed_s"]
            and elapsed < withheld["started_elapsed_s"] and saved_time < moment(withheld["started_utc"], "First N500")
            and saved_time >= moment(previous["started_utc"], "Last pre-prediction child"), "Prediction is not prospective")
    require(all(elapsed < child["started_elapsed_s"] and saved_time < moment(child["started_utc"], "N500 child")
                for child in children if child["case_id"].startswith("n500_")), "N500 propagation precedes prediction")
    return dict(prediction, path=str(path), sha256=digest, created_utc=record["created_utc"], parent_elapsed_s=elapsed,
                completed_chunk_count=48, chronology_verified=True, scope="Arithmetic and retained chronology; no external replication.")


def audit_evidence(execution_path, ledger, progress):
    progress["phase"] = "frozen_manifest_and_inventories"
    context = audit_manifest(execution_path, ledger)
    require(ledger.guard.output.parent == context["out"], "Assessment must remain in its attempt directory")
    for key in THREADS:
        os.environ[key] = "1"
    import numpy as np
    from importlib.metadata import version
    require(platform.python_version() == "3.13.7" and np.__version__ == "2.2.6"
            and version("scipy") == "1.15.1" and version("psutil") == "6.1.1", "Actual Point 01 environment differs")
    require(Path(sys.prefix).resolve() == context["root"] / ".venv", "Use the isolated Point 01 environment")
    require(not any(key == prefix or key.startswith(prefix + ".") for key in sys.modules
                    for prefix in ("scipy", "torch", "cupy", "silice")), "Assessor imported an excluded implementation")
    progress["phase"] = "independent_input_arrays"
    inputs, input_summaries = audit_inputs(context, np, ledger)
    progress["input_audits"] = input_summaries
    progress["phase"] = "checkpoint_chains_and_final_arrays"
    measures, case_data, expected_outputs = audit_cases(context, inputs, np, ledger, progress)
    progress["phase"] = "prospective_prediction"
    prediction = audit_prediction(context, case_data, measures, ledger)
    expected_outputs.add(prediction["path"])
    require(set(context["produced"]) == expected_outputs, "Disconnected/missing attempt evidence in produced inventory")
    attempt = ledger.json(context["out"] / "attempt.json", context["produced"][str(context["out"] / "attempt.json")])
    require(attempt.get("schema") == "silice.point03-analytic.attempt.v1" and attempt.get("total_wall_budget_s") == 3600
            and integer(attempt.get("pid"), "Attempt PID") > 0, "Attempt journal is missing/invalid")
    require(moment(attempt.get("created_utc"), "Attempt") <= moment(context["manifest"].get("created_utc"), "Manifest"),
            "Attempt journal follows preparation")
    actual_outputs = {str(path.resolve()) for path in context["out"].rglob("*") if path.is_file()}
    allowed_live = {str(execution_path), str(ledger.guard.output), str(context["out"] / "assessment.stdout.log"),
                    str(context["out"] / "assessment.stderr.log")}
    require(actual_outputs - allowed_live == expected_outputs, "Unlisted output appeared after propagation inventory")
    progress["phase"] = "scientific_screens"
    scientific = assess_values(measures)
    scientific["gates"].update(E1_complete_frozen_evidence=True, E2_numerical_validity=True,
                                E3_independent_retained_array_recomputation=True)
    progress["phase"] = "final_byte_identity_check"
    ledger.confirm()
    ledger.guard.check(full=True)
    progress["phase"] = "completed"
    return dict(scientific, status="completed", operational_pass=True, integrity_pass=True,
                manifest_path=str(context["manifest_path"]), manifest_sha256=context["identity"],
                propagation_execution_path=str(execution_path), propagation_execution_sha256=ledger.files[str(execution_path)],
                independent_measurements=measures, input_audits=input_summaries, frozen_prediction=prediction,
                historical_Q4=context["historical"], tracked_files_verified=context["tracked_count"],
                complete_checkpoint_chains=8, checkpoint_reports_verified=144, final_fields_decompressed=8,
                intermediate_field_verification="All 144 NPZ byte hashes and linked reports; only the eight final arrays independently decompressed.",
                environment={"python": platform.python_version(), "numpy": np.__version__,
                             "threads": {key: os.environ[key] for key in THREADS},
                             "scipy_imported": False, "propagation_implementation_imported": False, "gpu_used": False},
                longitudinal_scope="One observed q at each of N400/N500 is a local quadratic-predominance screen, not proof of an asymptotic regime; leading functional error may cancel.",
                geometry_scope="Accepted D area evidence fixes the profile bytes. It does not supply a geometry-to-power uncertainty bound or prove zero geometry error.",
                historical_StageB_scope="The new experiment does not replace the retained Stage B FAIL; original inputs and manifest remain pinned.")


def self_check():
    """Pure scalar logic checks: these data are not optical simulations."""
    checks = []
    factor = 1 + 1.25/(2**1.8-1)
    def analytic(base=.3, coefficient=.0032, z_coefficient=1e-6):
        return [{"case_id": name, "P_core": base+coefficient*(128/n)**2+z_coefficient*(dz*1e6)**2}
                for name, n, dz, _, _ in PLAN]
    def controlled(primary, b=1e-7, a=None):
        values = {PLAN[i][0]: value for i, value in enumerate(primary)}
        for n, value in ((400, primary[2]), (500, primary[3])):
            values[f"n{n}_geom_z125"] = value+(4*b if a is None else a)
            values[f"n{n}_geom_z03125"] = value-b
        return [{"case_id": name, "P_core": values[name]} for name in EXPECTED]
    def rejected(label, records, gate):
        result = assess_values(records)
        passed = result["scientific_pass"] is False and result["accepted_gci"] is None and result["gates"][gate] is False
        checks.append({"name": label, "pass": passed, "failed_gate": gate})
        return result
    passing = assess_values(analytic())
    accepted = passing["accepted_gci"]
    checks.append({"name": "separable_spatial_and_longitudinal_order_two", "pass": passing["scientific_pass"] is True
                   and accepted is not None and abs(accepted["u_space"]-.000262144) <= 2e-12
                   and abs(accepted["extrapolated_core_power"]-(.3+1e-6*.625**2)) <= 2e-12
                   and all(abs(row["candidate_q"]-2) < 1e-8 for row in passing["auxiliary"].values()),
                   "expected_extrapolation_scope": "Spatial continuum at fixed primary dz, not simultaneous dz=0."})
    primary = passing["primary_core_powers"]
    rejected("oscillatory_spatial_differences", controlled([.33, .331, .3305, .3309]), "same_signed_differences")
    rejected("negative_observed_spatial_order", controlled([.3, .301, .303, .307]), "positive_finite_observed_orders")
    rejected("unstable_positive_spatial_orders", controlled([.3, .301, .30164, .30184]), "observed_order_stability")
    withheld = rejected("withheld_grid_residual", controlled([*primary[:3], primary[3]+1.1e-5]), "withheld_finest_grid_prediction")
    checks[-1]["pass"] = checks[-1]["pass"] and withheld["gates"]["observed_order_stability"]
    for label, a, b in (("longitudinal_order_outside_band", 1e-7, 1e-7),
                         ("oscillatory_longitudinal_differences", -4e-7, 1e-7),
                         ("unresolvable_longitudinal_differences", 4e-15, 1e-15)):
        result = rejected(label, controlled(primary, b=b, a=a), "longitudinal_order_band")
        checks[-1]["pass"] = checks[-1]["pass"] and all(row["accepted_S"] is None for row in result["auxiliary"].values())
    budget = rejected("combined_auxiliary_budget", controlled(primary, b=1e-5), "auxiliary_difference_budget")
    checks[-1]["pass"] = checks[-1]["pass"] and budget["gates"]["individual_auxiliary_components"]
    corner = rejected("corners_can_fail_inside_sum_budget", controlled(primary, b=4e-6/factor), "auxiliary_corner_robustness")
    checks[-1]["pass"] = checks[-1]["pass"] and corner["gates"]["auxiliary_difference_budget"]
    for label, records, gate in (("final_absolute_target", analytic(coefficient=.032), "absolute_total_indicator"),
                                  ("final_relative_target", analytic(base=.01), "relative_total_indicator")):
        result = rejected(label, records, gate)
        checks[-1]["pass"] = checks[-1]["pass"] and result["asymptotic_screening_pass"] and result["richardson_candidate"] is not None
    invalid = [("missing_case", analytic()[:-1]), ("duplicate_case", [*analytic()[:-1], analytic()[0]])]
    for number, label in ((float("nan"), "nonfinite_nan"), (float("inf"), "nonfinite_infinity")):
        values = analytic()
        values[0]["P_core"] = number
        invalid.append((label, values))
    for label, values in invalid:
        try:
            assess_values(values)
        except EvidenceError:
            checks.append({"name": label, "pass": True, "accepted_gci": None})
        else:
            checks.append({"name": label, "pass": False})
    for label, raw in (("json_overflow", b'{"value":1e999}'), ("json_duplicate_key", b'{"value":1,"value":2}')):
        try:
            strict_json(raw)
        except EvidenceError:
            checks.append({"name": label, "pass": True})
        else:
            checks.append({"name": label, "pass": False})
    return {"checks": checks, "self_check_pass": all(row["pass"] for row in checks),
            "checks_count": len(checks), "physical_propagations": 0,
            "scope": "Analytic scalar fixtures and evidence-parser logic only; no solver, geometry, files or experimental data generated."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--execution", type=Path)
    mode.add_argument("--self-check", action="store_true")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    output = args.out.resolve()
    if output.exists() or not output.parent.is_dir():
        parser.error("Output must be a fresh file in an existing directory")
    guard, progress = Guard(output), {}
    ledger = Ledger(guard)
    report = {"schema": SCHEMA, "created_utc": datetime.now(timezone.utc).isoformat(), "status": "failed",
              "operational_pass": False, "scientific_pass": None, "accepted_gci": None,
              "historical_Q4_replaced": False, "historical_StageB_replaced": False}
    code = 1
    try:
        guard.check(full=True)
        for key in THREADS:
            os.environ[key] = "1"
        if args.self_check:
            report.update(self_check(), status="completed", operational_pass=True)
            code = 0 if report["self_check_pass"] else 1
        else:
            report.update(audit_evidence(args.execution.resolve(), ledger, progress))
            code = 0 if report["scientific_pass"] else 2
        guard.check(full=True)
    except (Exception, KeyboardInterrupt) as error:
        report.update(status="failed", operational_pass=False, scientific_pass=None, integrity_pass=False,
                      accepted_gci=None, error_type=type(error).__name__, error=str(error))
        code = 1
    report.update(progress=progress, files_verified=ledger.files, files_verified_count=len(ledger.files),
                  resource_samples=guard.samples, elapsed_s=time.monotonic()-guard.started,
                  resource_scope="Sampled available RAM/disk; 31 s work deadline, 4 s retention reserve, 40 s outer timeout.",
                  assessor_path=str(Path(__file__).resolve()),
                  assessor_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    if report["elapsed_s"] >= 35:
        report.update(status="failed", operational_pass=False, scientific_pass=None, accepted_gci=None,
                      retention_deadline_exceeded=True)
        code = 1
    payload = json.dumps(report, indent=2, allow_nan=False)+"\n"
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(payload)
    print(json.dumps({"status": report["status"], "operational_pass": report["operational_pass"],
                      "scientific_pass": report["scientific_pass"], "assessment_path": str(output)}), flush=True)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
