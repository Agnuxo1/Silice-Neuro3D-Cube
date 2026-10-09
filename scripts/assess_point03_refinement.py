"""Independently audit Stage B evidence and apply the prospective Q4 gates.

This program never propagates a field or imports the refinement runner.  An
operationally complete study may return 2 because its scientific gates fail.
Richardson indicators are conditional numerical estimates, not error bounds or
statistical confidence intervals.  Historical GLASS-009d Q4 remains unchanged.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
import math
import os
from pathlib import Path
import sys
import time


SCHEMA = "silice.point03-refinement.assessment.v1"
RATIO = 1.25
WIDTH_M = 128e-6
CORE_RADIUS_M = 6e-6
THRESHOLDS = {
    "minimum_absolute_difference_exclusive": 1e-12,
    "maximum_relative_order_disagreement": 0.20,
    "holdout_fraction_of_last_difference": 0.10,
    "auxiliary_fraction_of_last_difference": 0.10,
    "maximum_individual_auxiliary_component": 2.5e-4,
    "gci_safety_factor": 1.25,
    "maximum_total_indicator_absolute": 1e-3,
    "maximum_total_indicator_relative": 0.01,
    "metric_recomputation_absolute_tolerance": 1e-12,
    "initial_power_absolute_tolerance": 1e-12,
    "detector_area_relative_tolerance": 1e-12,
    "maximum_final_total_power": 1.001,
}
PLAN = [(f"n{n}_ss64_z125", n, 64, 1.25e-6, 1600)
        for n in (256, 320, 400, 500)]
PLAN += [(f"n{n}_ss32_z125", n, 32, 1.25e-6, 1600) for n in (400, 500)]
PLAN += [(f"n{n}_ss64_z0625", n, 64, .625e-6, 3200) for n in (400, 500)]
EXPECTED = {row[0]: row for row in PLAN}
INPUT_PAIRS = {(n, 64) for n in (256, 320, 400, 500)} | {(400, 32), (500, 32)}
THREADS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")
UNSPECIFIED = object()


class EvidenceError(ValueError):
    """Missing, inconsistent, mutated, or numerically invalid evidence."""


def require(condition, message):
    if not condition:
        raise EvidenceError(message)


def finite(value, label):
    require(type(value) in (int, float), label + " must be a JSON number.")
    try:
        result = float(value)
    except (OverflowError, ValueError) as error:
        raise EvidenceError(label + " is not a finite number.") from error
    require(math.isfinite(result), label + " must be finite.")
    return result


def integer(value, label):
    require(type(value) is int, label + " must be an integer, not a boolean.")
    return value


def strict_json(raw):
    def reject_constant(value):
        raise EvidenceError("Nonfinite JSON constant: " + value)

    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "Duplicate JSON key: " + key)
            result[key] = value
        return result

    def inspect(value):
        if isinstance(value, float):
            require(math.isfinite(value), "Overflowed or nonfinite JSON number.")
        elif isinstance(value, dict):
            for child in value.values():
                inspect(child)
        elif isinstance(value, list):
            for child in value:
                inspect(child)

    result = json.loads(raw.decode("utf-8"), parse_constant=reject_constant,
                        object_pairs_hook=unique_pairs)
    require(isinstance(result, dict), "JSON evidence must be an object.")
    inspect(result)
    return result


def absolute_path(value, label):
    require(isinstance(value, str) and value, label + " must be a path string.")
    path = Path(value)
    require(path.is_absolute(), label + " must be absolute on this platform.")
    return path.resolve()


class Ledger:
    """Hash the bytes actually read, then confirm that they remain unchanged."""
    def __init__(self):
        self.files = {}

    def read(self, path, expected=UNSPECIFIED):
        path = Path(path).resolve()
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if expected is not UNSPECIFIED:
            require(isinstance(expected, str) and len(expected) == 64
                    and all(c in "0123456789abcdef" for c in expected),
                    "Invalid SHA-256 for " + str(path))
            require(digest == expected, "SHA-256 mismatch: " + str(path))
        if str(path) in self.files:
            require(self.files[str(path)] == digest, "File changed while reading: " + str(path))
        self.files[str(path)] = digest
        return raw

    def json(self, path, expected=UNSPECIFIED):
        return strict_json(self.read(path, expected))

    def confirm(self):
        for path, expected in list(self.files.items()):
            self.read(path, expected)


def validate_spec(record, name):
    require(name in EXPECTED, "Unexpected case: " + str(name))
    _, n, samples, dz, steps = EXPECTED[name]
    require(record.get("case_id") == name, "Case identifier mismatch.")
    for key, expected in (("N", n), ("profile_samples", samples), ("steps_target", steps)):
        require(integer(record.get(key), name + "." + key) == expected,
                name + ": changed " + key)
    for key, expected in (("width_m", WIDTH_M), ("dx_m", WIDTH_M / n), ("dz_m", dz)):
        require(finite(record.get(key), name + "." + key) == expected,
                name + ": changed " + key)


def unique_by_id(records, label):
    require(isinstance(records, list) and len(records) == 8, label + " must contain exactly eight cases.")
    result = {}
    for record in records:
        require(isinstance(record, dict), label + " entry must be an object.")
        name = record.get("case_id")
        require(isinstance(name, str) and name in EXPECTED, label + ": unknown case identifier.")
        require(name not in result, label + ": duplicated case identifier " + name)
        result[name] = record
    require(set(result) == set(EXPECTED), label + " is incomplete.")
    return result


def primary_screen(powers):
    """B4-B5, shared by observed data and the four prescribed sensitivity corners."""
    differences = [powers[i + 1] - powers[i] for i in range(3)]
    require(all(math.isfinite(d) for d in differences), "Nonfinite power differences.")
    magnitudes = [abs(d) for d in differences]
    nonzero = all(d > THRESHOLDS["minimum_absolute_difference_exclusive"] for d in magnitudes)
    same_sign = nonzero and (all(d > 0 for d in differences) or all(d < 0 for d in differences))
    orders = [None, None]
    for i in range(2):
        if magnitudes[i] > 0 and magnitudes[i + 1] > 0:
            candidate = (math.log(magnitudes[i]) - math.log(magnitudes[i + 1])) / math.log(RATIO)
            if math.isfinite(candidate):
                orders[i] = candidate
    positive = all(p is not None and p > 0 for p in orders)
    order_disagreement = abs(orders[1] - orders[0]) / max(orders) if positive else None
    order_stable = positive and order_disagreement <= THRESHOLDS["maximum_relative_order_disagreement"]
    predicted = residual = None
    if orders[0] is not None and orders[0] > 0:
        # Fit only N=256,320,400. The N=500 observation is excluded from this fit.
        predicted = powers[2] + differences[1] * math.exp(-orders[0] * math.log(RATIO))
        residual = abs(powers[3] - predicted)
    holdout_limit = THRESHOLDS["holdout_fraction_of_last_difference"] * magnitudes[2]
    holdout_pass = residual is not None and math.isfinite(residual) and residual <= holdout_limit
    gates = {"nonzero_differences": nonzero,
             "same_signed_differences": same_sign,
             "positive_finite_observed_orders": positive,
             "observed_order_stability": order_stable,
             "withheld_finest_grid_prediction": holdout_pass}
    return {"signed_differences": differences, "absolute_differences": magnitudes,
            "candidate_observed_orders": orders, "relative_order_disagreement": order_disagreement,
            "holdout": {"fit_grids": [256, 320, 400], "withheld_grid": 500,
                        "predicted_core_power": predicted, "absolute_residual": residual,
                        "maximum_residual": holdout_limit}, "gates": gates,
            "primary_screen_pass": all(gates.values())}


def assess_values(records):
    """Apply frozen gates to eight independently measured core powers."""
    entries = unique_by_id(records, "Measured values")
    values = {name: finite(row.get("P_core"), name + ".P_core")
              for name, row in entries.items()}
    require(all(value >= 0 for value in values.values()), "Core powers must be nonnegative.")
    powers = [values[f"n{n}_ss64_z125"] for n in (256, 320, 400, 500)]
    primary = primary_screen(powers)
    differences, magnitudes = primary["signed_differences"], primary["absolute_differences"]
    orders = primary["candidate_observed_orders"]
    auxiliary = {}
    for n in (400, 500):
        profile = abs(values[f"n{n}_ss32_z125"] - values[f"n{n}_ss64_z125"])
        longitudinal = abs(values[f"n{n}_ss64_z0625"] - values[f"n{n}_ss64_z125"])
        auxiliary[str(n)] = {"profile_component": profile, "longitudinal_component": longitudinal,
                             "sum": profile + longitudinal}
    require(all(math.isfinite(v) for row in auxiliary.values() for v in row.values()),
            "Nonfinite auxiliary differences.")
    individual_pass = all(row[key] <= THRESHOLDS["maximum_individual_auxiliary_component"]
                          for row in auxiliary.values() for key in ("profile_component", "longitudinal_component"))
    auxiliary_sum = auxiliary["400"]["sum"] + auxiliary["500"]["sum"]
    auxiliary_limit = THRESHOLDS["auxiliary_fraction_of_last_difference"] * magnitudes[2]
    corners = []
    for sign400 in (-1, 1):
        for sign500 in (-1, 1):
            perturbed = [powers[0], powers[1], powers[2] + sign400 * auxiliary["400"]["sum"],
                         powers[3] + sign500 * auxiliary["500"]["sum"]]
            screen = primary_screen(perturbed)
            corners.append(dict(screen, sign400=sign400, sign500=sign500,
                                P400=perturbed[2], P500=perturbed[3]))
    gates = dict(primary["gates"], individual_auxiliary_components=individual_pass,
                 auxiliary_difference_budget=auxiliary_sum <= auxiliary_limit,
                 auxiliary_corner_robustness=all(corner["primary_screen_pass"] for corner in corners))
    guards_pass = all(gates.values())
    richardson = None
    if guards_pass:
        denominator = math.expm1(orders[1] * math.log(RATIO))
        require(math.isfinite(denominator) and denominator > 0, "Invalid Richardson denominator.")
        spatial = THRESHOLDS["gci_safety_factor"] * magnitudes[2] / denominator
        total = spatial + auxiliary["500"]["sum"]
        extrapolated = powers[3] + differences[2] / denominator
        require(all(math.isfinite(v) for v in (spatial, total, extrapolated)), "Nonfinite Richardson estimate.")
        richardson = {"observed_order": orders[1], "extrapolated_core_power": extrapolated,
                      "u_space": spatial, "S500": auxiliary["500"]["sum"], "u_total": total,
                      "relative_u_total": total / abs(powers[3]) if powers[3] else None,
                      "interpretation": "Conditional Richardson/GCI-style numerical indicator; not a rigorous bound or confidence interval."}
    gates["absolute_total_indicator"] = richardson is not None and richardson["u_total"] <= THRESHOLDS["maximum_total_indicator_absolute"]
    gates["relative_total_indicator"] = (richardson is not None
                                          and richardson["u_total"] <= THRESHOLDS["maximum_total_indicator_relative"] * abs(powers[3]))
    passed = all(gates.values())
    return {"scientific_pass": passed, "status": "passed" if passed else "scientific_fail",
            "thresholds": dict(THRESHOLDS), "refinement_ratio": RATIO,
            "primary_grids": [256, 320, 400, 500], "primary_core_powers": powers,
            "signed_differences": differences, "absolute_differences": magnitudes,
            "candidate_observed_orders": orders, "relative_order_disagreement": primary["relative_order_disagreement"],
            "holdout": primary["holdout"],
            "auxiliary": auxiliary, "auxiliary_sum_both_grids": auxiliary_sum,
            "auxiliary_maximum_sum": auxiliary_limit, "gates": gates,
            "auxiliary_sensitivity_corners": corners,
            "auxiliary_sensitivity_scope": "B4-B5 checked at four prescribed corners with the two coarsest powers fixed; not a certified uncertainty in observed order or a proof over the full perturbation interval.",
            "asymptotic_screening_pass": guards_pass,
            "richardson_candidate": richardson, "accepted_gci": richardson if passed else None,
            "old_style_absolute_difference_nonincreasing": [magnitudes[1] <= magnitudes[0], magnitudes[2] <= magnitudes[1]],
            "old_style_Q4_all_adjacent_triples": magnitudes[2] <= magnitudes[1] <= magnitudes[0],
            "historical_Q4_replaced": False,
            "scope": "Only this fixed-width, scalar-ADI, analytic-detector refinement series. No global convergence, independent experimental replication, or hardware claim."}


def audit_evidence(execution_path, ledger):
    execution_path = Path(execution_path).resolve()
    execution = ledger.json(execution_path)
    require(execution.get("schema") == "silice.point03-refinement.execution.v1", "Unknown execution schema.")
    require(execution.get("status") == "completed" and execution.get("operational_pass") is True,
            "The eight-case execution has not completed operationally.")
    manifest_path = absolute_path(execution.get("manifest_path"), "manifest_path")
    identity = execution.get("manifest_sha256")
    manifest = ledger.json(manifest_path, identity)
    require(manifest.get("schema") == "silice.point03-refinement.manifest.v1", "Unknown manifest schema.")
    root = absolute_path(manifest.get("source_root"), "source_root")
    require(Path(__file__).resolve() == root / "scripts/assess_point03_refinement.py",
            "Assessment must use the assessor from the frozen source checkout.")
    required_sources = [root / "Docs/POINT-03-Q4-REFINEMENT-CONTRACT.md",
                        root / "experimentos/glass009d_claude/resultados009d.json",
                        root / "scripts/run_point03_refinement.py", Path(__file__).resolve(),
                        root / "experimentos/glass009_claude/adi2d.py", root / "src/silice/coverage.py",
                        root / "src/silice/tracks.py", root / "src/silice/bpm.py"]
    sources = manifest.get("source_sha256")
    require(isinstance(sources, dict) and set(sources) == {str(p.resolve()) for p in required_sources},
            "Frozen source set is incomplete or differs from the contract.")
    for path, digest in sources.items():
        ledger.read(absolute_path(path, "source path"), digest)
    require(execution.get("sources_unchanged") is True
            and execution.get("source_sha256_before") == sources
            and execution.get("source_sha256_after") == sources, "Execution source identities differ.")
    tracked = execution.get("tracked_sha256_before")
    require(isinstance(tracked, dict) and bool(tracked)
            and execution.get("tracked_sha256_after") == tracked
            and execution.get("tracked_inputs_unchanged") is True
            and execution.get("tracked_changed_paths") == [], "Tracked-file integrity snapshots are missing or unequal.")
    for relative, digest in tracked.items():
        require(isinstance(relative, str) and bool(relative) and not Path(relative).is_absolute(),
                "Tracked-file key must be relative to the source checkout.")
        path = (root / relative).resolve()
        require(path.is_relative_to(root), "Tracked-file key escapes the source checkout.")
        ledger.read(path, digest)
    for source in required_sources:
        relative = source.relative_to(root).as_posix()
        require(tracked.get(relative) == sources[str(source.resolve())], "A frozen source is absent from the tracked-file snapshot.")
    for prefix, expected in (("contract", required_sources[0]), ("historical_Q4", required_sources[1])):
        path = absolute_path(manifest.get(prefix + "_path"), prefix + "_path")
        require(path == expected.resolve(), prefix + " points to the wrong file.")
        require(manifest.get(prefix + "_sha256") == sources[str(path)], prefix + " digest differs from source map.")
    physics = manifest.get("physics", {})
    expected_physics = {"wavelength_m": 1550e-9, "n_reference": 1.444, "delta_n": -.003,
                        "waist_m": 6e-6, "core_radius_m": 6e-6, "thickness_m": 6e-6,
                        "track_radius_m": 1.25e-6, "tracks": 96, "smax_per_m": 4e4, "sigma_frac": .2}
    for key, value in expected_physics.items():
        require(finite(physics.get(key), "physics." + key) == value, "Changed physical parameter: " + key)
    history = ledger.json(required_sources[1], manifest["historical_Q4_sha256"])
    t96 = history.get("T96d", {})
    old_powers = [finite(t96.get(key), "historical " + key) for key in ("P_dx0p625", "P_dx0p5", "P_dx0p4")]
    old_differences = [old_powers[i + 1] - old_powers[i] for i in range(2)]
    old_q4 = abs(old_differences[1]) <= abs(old_differences[0])
    require(t96.get("Q4_monotone") is False and old_q4 is False,
            "Historical T96d Q4 failure must remain recorded and independently recoverable.")
    historical = {"path": str(required_sources[1]), "sha256": manifest["historical_Q4_sha256"],
                  "T96d_core_powers": old_powers, "signed_differences": old_differences,
                  "stored_Q4": False, "recomputed_Q4": old_q4,
                  "scope": "Current bytes checked; current hashes do not retrospectively authenticate historical execution."}
    plans = unique_by_id(manifest.get("case_plan"), "Manifest plan")
    for name, case in plans.items():
        validate_spec(case, name)
    prepared = manifest.get("prepared_inputs")
    require(isinstance(prepared, list) and len(prepared) == 6, "Exactly six prepared inputs are required.")
    inputs = {}
    for item in prepared:
        pair = (integer(item.get("N"), "prepared N"), integer(item.get("profile_samples"), "prepared samples"))
        require(pair in INPUT_PAIRS and pair not in inputs, "Unexpected or duplicate prepared-input pair.")
        path = absolute_path(item.get("input_npz_path"), "input_npz_path")
        require(path == manifest_path.parent / "inputs" / f"n{pair[0]}_ss{pair[1]}.npz", "Prepared input is outside its declared group.")
        inputs[pair] = (path, item.get("input_npz_sha256"))
    require(set(inputs) == INPUT_PAIRS, "Prepared-input pairs are incomplete.")
    for name, plan in plans.items():
        expected = inputs[(plan["N"], plan["profile_samples"])]
        actual = (absolute_path(plan.get("input_npz_path"), name + " input"), plan.get("input_npz_sha256"))
        require(actual == expected, "Case does not reuse its prescribed prepared input: " + name)
    for variable in THREADS:
        os.environ[variable] = "1"
    import numpy as np
    require("torch" not in sys.modules and "cupy" not in sys.modules, "Assessor must use CPU NumPy only.")
    cached = {}
    input_summaries = []
    for (n, samples), (path, digest) in inputs.items():
        with np.load(io.BytesIO(ledger.read(path, digest)), allow_pickle=False) as archive:
            require(set(archive.files) == {"A0", "dn", "sigma", "weights"}, "Unexpected prepared-input NPZ keys.")
            arrays = {key: archive[key] for key in archive.files}
        for key, array in arrays.items():
            require(array.shape == (n, n) and np.all(np.isfinite(array)), "Invalid input array: " + key)
            expected_dtype = np.dtype("complex128" if key == "A0" else "float64")
            require(array.dtype == expected_dtype, "Unexpected input dtype: " + key)
        require(np.all((arrays["dn"] >= -.003) & (arrays["dn"] <= 0)), "Index profile is outside the fixed passive model.")
        require(np.all(arrays["sigma"] >= 0), "Absorber contains negative damping.")
        require(np.all((arrays["weights"] >= 0) & (arrays["weights"] <= 1)), "Analytic detector has nonpassive weights.")
        dx = WIDTH_M / n
        with np.errstate(over="raise", invalid="raise", divide="raise"):
            p0 = float(np.sum(np.abs(arrays["A0"])**2) * dx**2)
            area = float(np.sum(arrays["weights"]) * dx**2)
        require(math.isfinite(p0) and abs(p0 - 1) <= THRESHOLDS["initial_power_absolute_tolerance"], "Input power is not normalized to one.")
        area_error = abs(area / (math.pi * CORE_RADIUS_M**2) - 1)
        require(math.isfinite(area_error) and area_error <= THRESHOLDS["detector_area_relative_tolerance"], "Analytic detector area is inaccurate.")
        cached[(n, samples)] = (arrays, p0, area)
        input_summaries.append({"N": n, "profile_samples": samples, "path": str(path), "sha256": digest,
                                "P0": p0, "core_area_m2": area, "relative_area_error": area_error})
    # At a given grid, changing index supersampling must not change the other arrays.
    for n in (400, 500):
        for key in ("A0", "sigma", "weights"):
            require(np.array_equal(cached[(n, 32)][0][key], cached[(n, 64)][0][key]),
                    "Profile control also changed " + key + " at N=" + str(n))
    references = unique_by_id(execution.get("case_reports"), "Execution case reports")
    measurements = []
    for name, n, samples, dz, steps in PLAN:
        reference = references[name]
        case_path = absolute_path(reference.get("path"), name + " case report")
        require(case_path == manifest_path.parent / "cases" / name / "case.json", "Case report location differs from plan.")
        case = ledger.json(case_path, reference.get("sha256"))
        require(case.get("schema") == "silice.point03-refinement.case.v1" and case.get("status") == "completed", "Case is not completed: " + name)
        validate_spec(case, name)
        require(case.get("manifest_sha256") == identity, "Case belongs to a different manifest: " + name)
        for key in ("numeric_valid", "numeric_pass", "sources_unchanged", "input_unchanged"):
            require(case.get(key) is True, name + " lacks a successful " + key)
        require(case.get("gpu_used") is False and case.get("dtype") == "complex128", "Case backend or dtype is outside the CPU contract.")
        for key in ("steps_done", "steps_completed"):
            require(integer(case.get(key), name + "." + key) == steps, "Case did not complete all prescribed steps.")
        expected_input = inputs[(n, samples)]
        actual_input = (absolute_path(case.get("input_npz_path"), name + " input"), case.get("input_npz_sha256"))
        require(actual_input == expected_input, "Case input identity differs from the manifest.")
        final_path = absolute_path(case.get("final_npz_path"), name + " final NPZ")
        require(final_path.is_relative_to(case_path.parent) and final_path.suffix == ".npz", "Final field is outside its own case directory.")
        with np.load(io.BytesIO(ledger.read(final_path, case.get("final_npz_sha256"))), allow_pickle=False) as archive:
            require(archive.files == ["field"], "Final NPZ must contain only field.")
            field = archive["field"]
        require(field.shape == (n, n) and field.dtype == np.dtype("complex128") and np.all(np.isfinite(field)), "Invalid retained final field.")
        arrays, p0, area = cached[(n, samples)]
        with np.errstate(over="raise", invalid="raise", divide="raise"):
            intensity = np.abs(field)**2
            total = float(np.sum(intensity) * (WIDTH_M / n)**2)
            core = float(np.sum(arrays["weights"] * intensity) * (WIDTH_M / n)**2 / p0)
        require(all(math.isfinite(v) for v in (total, core)), "Nonfinite recalculated final metrics.")
        require(0 <= total <= THRESHOLDS["maximum_final_total_power"], "Final total power exceeds the fixed numerical guard.")
        require(0 <= core <= total / p0 + 1e-12, "Core detector power is outside the passive range.")
        recalculated = {"P0": p0, "P_final": total, "P_core": core,
                        "input_power": p0, "output_power": total, "core_power_analytic_input": core}
        errors = {}
        for key, value in recalculated.items():
            errors[key] = abs(finite(case.get(key), name + "." + key) - value)
            require(errors[key] <= THRESHOLDS["metric_recomputation_absolute_tolerance"], "Reported field metric does not reproduce: " + name + "." + key)
        reported_area = finite(case.get("core_area_m2"), name + ".core_area_m2")
        require(abs(reported_area / area - 1) <= THRESHOLDS["detector_area_relative_tolerance"], "Reported area does not reproduce.")
        last_path = absolute_path(case.get("last_checkpoint_path"), name + " last checkpoint")
        require(last_path.parent == case_path.parent, "Last checkpoint is outside its case.")
        last = ledger.json(last_path, case.get("last_checkpoint_sha256"))
        require(last.get("schema") == "silice.point03-refinement.checkpoint.v1"
                and last.get("status") == "checkpoint_completed", "Last checkpoint is not valid.")
        for key in ("case_id", "manifest_sha256", "input_npz_sha256", "final_npz_path", "final_npz_sha256", "steps_done", "steps_completed"):
            require(last.get(key) == case.get(key), "Final case differs from its checkpoint: " + key)
        measurements.append({"case_id": name, "N": n, "profile_samples": samples,
                             "dz_m": dz, "steps_completed": steps, "case_path": str(case_path),
                             "case_sha256": reference["sha256"], "input_npz_sha256": expected_input[1],
                             "final_npz_path": str(final_path), "final_npz_sha256": case["final_npz_sha256"],
                             "P0": p0, "P_final": total, "P_core": core,
                             "maximum_metric_absolute_error": max(errors.values())})
    result = assess_values(measurements)
    ledger.confirm()
    result.update(schema=SCHEMA, operational_pass=True, execution_path=str(execution_path),
                  execution_sha256=ledger.files[str(execution_path)], manifest_path=str(manifest_path),
                  manifest_sha256=identity, historical_Q4=historical, prepared_inputs=input_summaries,
                  cases=measurements, verified_file_sha256=dict(ledger.files), integrity_pass=True,
                  tracked_files_verified=len(tracked), tracked_inputs_unchanged=True,
                  independence="Separate assessment code and NPZ recomputation; not an external peer or experimental replication.")
    return result


def synthetic_records(powers, auxiliary_offset=0):
    values = {f"n{n}_ss64_z125": power for n, power in zip((256, 320, 400, 500), powers)}
    for n in (400, 500):
        for suffix in ("ss32_z125", "ss64_z0625"):
            values[f"n{n}_{suffix}"] = values[f"n{n}_ss64_z125"] + auxiliary_offset
    return [{"case_id": name, "P_core": value} for name, value in values.items()]


def self_check():
    """Six synthetic rejection/acceptance groups; no physical propagation."""
    checks = []
    known = [.3 + .0008 / RATIO**(2 * i) for i in range(4)]

    def record(name, condition, details):
        checks.append({"name": name, "passed": bool(condition), "details": details})

    good = assess_values(synthetic_records(known))
    oversized = assess_values(synthetic_records([.3 + .008 / RATIO**(2 * i) for i in range(4)]))
    good_condition = (good["scientific_pass"] and good["accepted_gci"] is not None
                      and all(abs(p - 2) < 1e-10 for p in good["candidate_observed_orders"])
                      and abs(good["accepted_gci"]["extrapolated_core_power"] - .3) < 1e-12
                      and abs(good["accepted_gci"]["u_space"] - .000262144) < 1e-12
                      and oversized["asymptotic_screening_pass"] and not oversized["scientific_pass"]
                      and oversized["accepted_gci"] is None)
    record("known_second_order_and_error_target", good_condition,
           {"observed_orders": good["candidate_observed_orders"], "accepted_gci": good["accepted_gci"],
            "oversized_error_target_rejected": oversized["accepted_gci"] is None})
    oscillatory = assess_values(synthetic_records([.33, .331, .3305, .3309]))
    record("oscillatory_differences_rejected", not oscillatory["gates"]["same_signed_differences"]
           and oscillatory["accepted_gci"] is None and not oscillatory["scientific_pass"], oscillatory["gates"])
    nonpositive = assess_values(synthetic_records([.30, .301, .303, .306]))
    constant = assess_values(synthetic_records([.3, .3, .3, .3]))
    record("nonpositive_order_rejected", not nonpositive["gates"]["positive_finite_observed_orders"]
           and nonpositive["accepted_gci"] is None and constant["old_style_Q4_all_adjacent_triples"]
           and not constant["gates"]["nonzero_differences"] and constant["accepted_gci"] is None,
           {"observed_orders": nonpositive["candidate_observed_orders"],
            "constant_sequence_diagnostic_Q4_true_but_asymptotic_claim_rejected": constant["accepted_gci"] is None})
    off = list(known)
    off[3] += 1.1e-5
    holdout = assess_values(synthetic_records(off))
    record("withheld_grid_failure_rejected", holdout["gates"]["observed_order_stability"]
           and not holdout["gates"]["withheld_finest_grid_prediction"] and holdout["accepted_gci"] is None,
           holdout["holdout"])
    dominated = assess_values(synthetic_records(known, auxiliary_offset=1e-4))
    corner_sensitive = assess_values(synthetic_records(known, auxiliary_offset=2e-6))
    record("auxiliary_contamination_rejected", dominated["gates"]["individual_auxiliary_components"]
           and not dominated["gates"]["auxiliary_difference_budget"] and dominated["accepted_gci"] is None,
           {"sum": dominated["auxiliary_sum_both_grids"], "limit": dominated["auxiliary_maximum_sum"]})
    checks[-1]["passed"] = (checks[-1]["passed"] and corner_sensitive["gates"]["auxiliary_difference_budget"]
                            and not corner_sensitive["gates"]["auxiliary_corner_robustness"]
                            and corner_sensitive["accepted_gci"] is None)
    checks[-1]["details"]["within_budget_but_corner_sensitive_rejected"] = not corner_sensitive["gates"]["auxiliary_corner_robustness"]
    invalid = []
    for label, bad in (("nan", math.nan), ("positive_infinity", math.inf), ("negative_infinity", -math.inf)):
        rows = synthetic_records(known)
        rows[0]["P_core"] = bad
        try:
            assess_values(rows)
        except EvidenceError:
            invalid.append(label)
    for label, rows in (("missing_case", synthetic_records(known)[:-1]),
                        ("duplicate_case", synthetic_records(known)[:-1] + [synthetic_records(known)[0]])):
        try:
            assess_values(rows)
        except EvidenceError:
            invalid.append(label)
    for label, raw in (("json_overflow", b'{"x":1e999}'), ("json_nan", b'{"x":NaN}'),
                       ("json_duplicate_key", b'{"x":1,"x":2}')):
        try:
            strict_json(raw)
        except EvidenceError:
            invalid.append(label)
    try:
        Ledger().read(Path(__file__), None)
    except EvidenceError:
        invalid.append("missing_required_sha256")
    record("nonfinite_or_incomplete_evidence_rejected", len(invalid) == 9, {"rejected_inputs": invalid})
    passed = len(checks) == 6 and all(check["passed"] for check in checks)
    return {"schema": "silice.point03-refinement.self-check.v1", "status": "passed" if passed else "failed",
            "self_check_pass": passed, "checks_count": len(checks), "checks": checks,
            "thresholds": dict(THRESHOLDS), "physical_propagations": 0,
            "scope": "Synthetic assessment logic checks only; not scientific evidence for convergence."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--execution", type=Path)
    modes.add_argument("--self-check", action="store_true")
    parser.add_argument("--out", type=Path, required=True, help="New JSON file; existing evidence is never overwritten.")
    args = parser.parse_args()
    destination = args.out.resolve()
    if destination.exists() or not destination.parent.is_dir():
        parser.error("--out must name a new file in an existing directory.")
    started = time.monotonic()
    ledger = Ledger()
    try:
        result = self_check() if args.self_check else audit_evidence(args.execution, ledger)
        code = (0 if result["self_check_pass"] else 1) if args.self_check else (0 if result["scientific_pass"] else 2)
    except Exception as error:
        result = {"schema": SCHEMA, "status": "invalid_evidence", "operational_pass": False,
                  "scientific_pass": False, "accepted_gci": None, "integrity_pass": False,
                  "error_type": type(error).__name__, "error": str(error),
                  "files_read_sha256": dict(ledger.files), "historical_Q4_replaced": False}
        code = 1
    result["created_utc"] = datetime.now(timezone.utc).isoformat()
    result["elapsed_s"] = time.monotonic() - started
    result["assessor_path"] = str(Path(__file__).resolve())
    result["assessor_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    with destination.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps({"status": result["status"], "report": str(destination), "exit_code": code}))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
