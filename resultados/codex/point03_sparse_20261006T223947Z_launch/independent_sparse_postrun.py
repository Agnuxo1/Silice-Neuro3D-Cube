#!/usr/bin/env python3
"""Independent retained-evidence audit AFTER Point 03 Stage C has finished.

Reads JSON/source/NPZ evidence and uses NumPy arithmetic only. It never imports
the ADI, sparse helper, driver, SciPy, or psutil, and never solves or propagates.
Success writes one fresh JSON exclusively. Failure writes no certificate and
prints a JSON diagnostic to stderr. Run outside the tracked source inventory.
"""
import argparse
import ast
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time

CASES = {"n256_ss64_z125": 256, "n500_ss64_z125": 500}
THREADS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")
TOL = 1e-12
HELPER_SHA = "362d4d0fbb56663f0e05fc211cd0c4db031fe20394367c090fea634134ab48bd"
DRIVER_SHA = "96e5251f2ac3ef16dd83e7dc1b08f3bb3c2e5256c63732972c6b1cbed7690da5"
CONTRACT_SHA = "59629e1689a91b181e7cdad617d16e4e62ebafd0762174e72c62d7dcb2da5a60"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), "Missing/symlink file: " + str(path))
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pairs(items):
    result = {}
    for key, value in items:
        require(key not in result, "Duplicate JSON key: " + key)
        result[key] = value
    return result


def read_json(path):
    with Path(path).open("r", encoding="utf-8") as handle:
        result = json.load(handle, object_pairs_hook=pairs,
                           parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    require(isinstance(result, dict), "JSON root must be an object: " + str(path))
    return result


def number(value, name):
    require(type(value) in (float, int) and math.isfinite(value), "Invalid number: " + name)
    return float(value)


def integer(value, name):
    require(type(value) is int, "Expected integer: " + name)
    return value


def agree(recorded, actual, name, tolerance=TOL):
    require(abs(number(recorded, name) - actual) <= tolerance,
            "Recomputed value disagrees: " + name)


class Auditor:
    def __init__(self, out, output, np):
        self.out, self.output, self.np = out, output, np
        self.observed = {}
        self.worker_paths = set()
        self.referenced_outputs = set()
        self.worker_memory = []
        self.factor_count = 0
        self.max_record_error = 0.0

    def file(self, path, expected=None, output=False):
        path = Path(path)
        require(path.is_absolute(), "Evidence path must be absolute: " + str(path))
        path = path.resolve()
        if output:
            require(path.is_relative_to(self.out), "Output escapes C directory: " + str(path))
        actual = sha(path)
        if expected is not None:
            require(actual == expected, "SHA256 mismatch: " + str(path))
        old = self.observed.setdefault(str(path), actual)
        require(old == actual, "Evidence changed during independent audit: " + str(path))
        return path

    def json(self, path, expected=None, output=False):
        return read_json(self.file(path, expected, output))

    def arrays(self, path, expected, keys, output=False):
        path = self.file(path, expected, output)
        if output:
            self.referenced_outputs.add(path)
        with self.np.load(path, allow_pickle=False) as archive:
            require(set(archive.files) == set(keys), "Unexpected NPZ keys: " + str(path))
            result = {key: archive[key] for key in keys}
        return result

    def array(self, array, n, complex_field, name):
        np = self.np
        require(array.shape == (n, n), "Wrong shape: " + name)
        require(array.dtype == np.dtype("complex128" if complex_field else "float64"),
                "Wrong dtype: " + name)
        require(bool(np.all(np.isfinite(array))), "Nonfinite array: " + name)

    def power(self, field, dx):
        return float(self.np.sum(self.np.abs(field) ** 2) * dx * dx)

    def core(self, field, weights, dx, p0):
        return float(self.np.sum(weights * self.np.abs(field) ** 2) * dx ** 2 / p0)

    def difference(self, actual, reference):
        np = self.np
        require(actual.shape == reference.shape and actual.dtype == reference.dtype == np.dtype("complex128"),
                "Incompatible raw complex fields")
        require(bool(np.all(np.isfinite(actual))) and bool(np.all(np.isfinite(reference))),
                "Nonfinite raw complex field")
        denominator_l2 = float(np.linalg.norm(reference.ravel()))
        denominator_linf = float(np.max(np.abs(reference)))
        require(denominator_l2 > 0 and denominator_linf > 0, "Zero reference field norm")
        delta = actual - reference
        return {"relative_l2": float(np.linalg.norm(delta.ravel()) / denominator_l2),
                "relative_linf": float(np.max(np.abs(delta)) / denominator_linf)}

    def compare_record(self, record, values, label):
        for key, actual in values.items():
            error = abs(number(record[key], label + "." + key) - actual)
            self.max_record_error = max(self.max_record_error, error)
            require(error <= TOL, "Recorded metric differs from retained arrays: " + label + "." + key)

    def memory(self, record):
        current = integer(record["rss_current_bytes"], "rss_current_bytes")
        require(current > 0, "Nonpositive current RSS")
        peak = record["peak_wset_bytes"]
        if peak is not None:
            require(integer(peak, "peak_wset_bytes") >= current, "Peak working set below current RSS")
        require(isinstance(record["scope"], str) and "current" in record["scope"], "Missing memory scope")
        return {"rss_current_bytes": current, "peak_wset_bytes": peak}

    def metadata(self, record, n, steps):
        np = self.np
        require(record["backend"] == "scipy.sparse.linalg.splu", "Wrong factor backend")
        require(record["numpy_version"] == "2.2.6" and record["scipy_version"] == "1.15.1",
                "Wrong factor dependency versions")
        require(record["options"] == {"permc_spec": "NATURAL", "diag_pivot_thresh": 0.0, "Equil": False},
                "Wrong sparse factor options")
        factors = record["factors"]
        require(len(factors) == 2, "Expected x/y factor metadata")
        for index, factor in enumerate(factors):
            require(factor["factor_index"] == index and factor["line_count"] == factor["line_size"] == n
                    and factor["matrix_order"] == n * n, "Factor dimensions differ")
            require(factor["matrix_nnz"] == factor["expected_matrix_nnz"] == 3 * n * n - 2 * n,
                    "Wrong sparse matrix nonzero count")
            require(integer(factor["solve_calls"], "solve_calls") == steps, "Factor solve count differs")
            for key in ("L_nnz", "U_nnz", "matrix_csc_bytes", "factor_export_csc_bytes"):
                require(integer(factor[key], key) > 0, "Invalid factor storage count")
            for key in ("assembly_s", "factorization_s", "setup_elapsed_s", "solve_elapsed_s"):
                require(number(factor[key], key) >= 0, "Negative factor timing")
            require("excludes" in factor["storage_scope"], "Factor storage scope must exclude native overhead")
            for key in ("perm_r", "perm_c"):
                permutation = factor[key]
                require(permutation["length"] == n * n and permutation["identity"] is True
                        and permutation["nonidentity_entries"] == 0, "Nonidentity permutation recorded")
                require(permutation["dtype"] in ("int32", "int64"), "Unexpected permutation dtype")
                identity = np.arange(n * n, dtype=np.dtype(permutation["dtype"]))
                digest = hashlib.sha256(identity.tobytes(order="C")).hexdigest()
                require(digest == permutation["sha256"], "Permutation identity hash differs")
            self.factor_count += 1

    def worker(self, path, digest, status):
        path = self.file(path, digest, True)
        require(path not in self.worker_paths, "Worker report reused")
        self.worker_paths.add(path)
        self.referenced_outputs.add(path)
        report = read_json(path)
        require(report["schema"] == "silice.point03-sparse.worker.v1" and report["status"] == status,
                "Worker did not complete expected evidence stage")
        require(report["audit_manifest_sha256"] == self.manifest_sha
                and report["sources_and_inputs_unchanged"] is True and report["gpu_used"] is False,
                "Worker identity/integrity/CPU flag differs")
        require(0 <= number(report["elapsed_s"], "worker elapsed_s") <= 35, "Worker internal deadline exceeded")
        self.worker_memory.append(self.memory(report["memory"]))
        return report

    def dense(self, dn, sigma, dx, dz, axis):
        # Independent algebraic assembly, no solve/factorization/ADI call.
        np = self.np
        n, h = dn.shape[0], dz / 2
        k0 = 2 * math.pi / 1550e-9
        beta0 = k0 * 1.444
        c = 1j / (2 * beta0 * dx * dx)
        diagonal = 1 + 2 * h * c - h * (1j * k0 * dn - sigma) / 2
        matrix = np.zeros((n * n, n * n), dtype=np.complex128)
        for line in range(n):
            for position in range(n):
                j = line * n + position
                iy, ix = (line, position) if axis == "x" else (position, line)
                matrix[j, j] = diagonal[iy, ix]
                if position > 0:
                    matrix[j, j - 1] = -h * c
                if position + 1 < n:
                    matrix[j, j + 1] = -h * c
        return matrix

    def small(self, entry):
        np = self.np
        n = integer(entry["N"], "small N")
        require(n in (8, 11), "Unknown small grid")
        report = self.worker(entry["path"], entry["sha256"], "small_completed")
        profile = report["small_profile"]
        dx, dz = ((.5e-6, 1.25e-6) if n == 8 else (.256e-6, .625e-6))
        require(profile["N"] == n and profile["seed"] == 20261006
                and profile["dx_m"] == dx and profile["dz_m"] == dz, "Small profile differs")
        artifacts = {Path(a["path"]).resolve(): a["sha256"] for a in report["array_artifacts"]}
        require(len(artifacts) == len(report["array_artifacts"]) == 11, "Small artifact inventory differs")
        expected_names = {f"small_n{n}_inputs.npz", f"small_n{n}_dense.npz"}
        expected_names |= {f"small_n{n}_{axis}_{label}.npz" for axis in ("x", "y")
                           for label in ("random", "impulse_before_cut", "impulse_after_cut")}
        expected_names |= {f"small_n{n}_steps{step}.npz" for step in (1, 16, 64)}
        require(set(artifacts) == {self.out / name for name in expected_names}, "Unexpected small evidence paths")
        def load(name, keys):
            path = self.out / name
            return self.arrays(path, artifacts[path], keys, True)
        inputs = load(f"small_n{n}_inputs.npz", ("dn", "sigma", "rhs"))
        for key in inputs:
            self.array(inputs[key], n, key == "rhs", "small " + key)
        rng = np.random.Generator(np.random.PCG64(20261006))
        expected_dn = rng.uniform(-.003, 0, (n, n)).astype(np.float64)
        expected_sigma = rng.uniform(0, 4e4, (n, n)).astype(np.float64)
        expected_rhs = (rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))).astype(np.complex128)
        expected_rhs /= math.sqrt(float(np.sum(np.abs(expected_rhs) ** 2) * dx ** 2))
        require(np.array_equal(inputs["dn"], expected_dn) and np.array_equal(inputs["sigma"], expected_sigma)
                and np.array_equal(inputs["rhs"], expected_rhs), "Small seeded retained inputs differ")
        p0 = self.power(inputs["rhs"], dx)
        require(abs(p0 - 1) <= TOL, "Small initial power differs")
        agree(profile["input_power"], p0, "small input power")
        retained = load(f"small_n{n}_dense.npz", ("dense_x", "dense_y"))
        require(len(report["matrix_checks"]) == 2 and len(report["checks"]) == 9, "Wrong C1/C2 evidence count")
        rows = {}
        for row in report["checks"]:
            require(row["N"] == n, "Small check N differs")
            key = (row["axis"], row["rhs"]) if "axis" in row else ("steps", row["steps"])
            require(key not in rows, "Duplicate small check")
            rows[key] = row
        matrices = {row["axis"]: row for row in report["matrix_checks"]}
        require(set(matrices) == {"x", "y"}, "Wrong C1 matrix axes")
        c1, c2 = [], []
        for axis in ("x", "y"):
            matrix = self.dense(inputs["dn"], inputs["sigma"], dx, dz, axis)
            require(retained["dense_" + axis].dtype == np.dtype("complex128")
                    and np.array_equal(retained["dense_" + axis], matrix), "Retained dense operator differs")
            cuts = range(n - 1, n * n - 1, n)
            require(np.count_nonzero(matrix) == 3 * n * n - 2 * n
                    and all(matrix[j, j + 1] == matrix[j + 1, j] == 0 for j in cuts),
                    "Independent dense operator has cross-line coupling")
            mr = matrices[axis]
            require(mr["N"] == n and mr["exact_dense_match"] is True
                    and mr["matrix_nnz"] == 3 * n * n - 2 * n
                    and mr["line_cuts"] == n - 1 and mr["cross_block_connections"] == 0,
                    "Recorded sparse matrix assertion differs")
            for label in ("random", "impulse_before_cut", "impulse_after_cut"):
                arrays = load(f"small_n{n}_{axis}_{label}.npz", ("rhs", "sparse_field", "original_field"))
                for key, array in arrays.items():
                    self.array(array, n, True, "C1 " + key)
                expected = inputs["rhs"].copy() if axis == "x" else inputs["rhs"].T.copy()
                if label != "random":
                    expected.fill(0)
                    index = n - 1 if label == "impulse_before_cut" else n
                    expected.flat[index] = 1 / dx
                require(np.array_equal(arrays["rhs"], expected), "C1 retained right-hand side differs")
                actual, original = arrays["sparse_field"], arrays["original_field"]
                values = self.difference(actual, original)
                vector, solution = expected.ravel(), actual.ravel()
                denominator = np.linalg.norm(matrix, ord=np.inf) * np.linalg.norm(solution, ord=np.inf)
                denominator += np.linalg.norm(vector, ord=np.inf)
                require(denominator > 0, "Zero C1 residual denominator")
                residual = float(np.linalg.norm(matrix @ solution - vector, ord=np.inf) / denominator)
                leakage = 0.0
                if label != "random":
                    other = actual.copy()
                    other[index // n, :] = 0
                    leakage = float(np.max(np.abs(other)))
                values.update(residual_infinity_normalized=residual, cross_block_leakage=leakage)
                self.compare_record(rows[(axis, label)], values, f"C1 N{n} {axis} {label}")
                require(values["relative_l2"] <= TOL and residual <= 1e-13 and leakage == 0,
                        "Independent C1 equivalence/residual/isolation failed")
                c1.append(dict(axis=axis, rhs=label, **values, state="PASS"))
        for step in (1, 16, 64):
            arrays = load(f"small_n{n}_steps{step}.npz", ("sparse_field", "original_field"))
            for key, array in arrays.items():
                self.array(array, n, True, "C2 " + key)
            values = self.difference(arrays["sparse_field"], arrays["original_field"])
            values["absolute_power_difference"] = abs(self.power(arrays["sparse_field"], dx)
                                                       - self.power(arrays["original_field"], dx))
            self.compare_record(rows[("steps", step)], values, f"C2 N{n} steps{step}")
            require(values["relative_l2"] <= TOL and values["absolute_power_difference"] <= TOL,
                    "Independent C2 retained trajectory equivalence failed")
            c2.append(dict(steps=step, **values, state="PASS"))
        require(len(report["factor_metadata"]) == 1 and report["factor_metadata"][0]["N"] == n,
                "Small factor metadata identity differs")
        self.metadata(report["factor_metadata"][0]["metadata"], n, 67)
        return {"N": n, "state": "PASS", "C1": c1, "C2": c2,
                "scope": "Retained solve/trajectory pairs and algebraic residuals; no propagation replay. Sparse-vs-dense exact match is a frozen worker assertion, not a retained sparse matrix."}

    def reproduction(self, case, entry, bmanifest):
        np = self.np
        name, n = case["case_id"], case["N"]
        require(CASES.get(name) == n, "Unexpected C reference case")
        required_plan = {"N": n, "profile_samples": 64, "steps_target": 1600,
                         "width_m": 128e-6, "dx_m": 128e-6 / n, "dz_m": 1.25e-6}
        require(all(case[k] == v for k, v in required_plan.items()), "Fixed C3 plan differs")
        plans = [p for p in bmanifest["case_plan"] if p["case_id"] == name]
        require(len(plans) == 1, "B reference plan missing/duplicated")
        plan = plans[0]
        require(all(case[k] == v for k, v in plan.items()), "C plan is not the original B plan")
        reference_case_path = self.study.parent / "cases" / name / "case.json"
        require(Path(case["reference_case_path"]).resolve() == reference_case_path, "B case path differs")
        bref = self.json(case["reference_case_path"], case["reference_case_sha256"])
        require(bref["status"] == "completed" and bref["numeric_valid"] is True
                and bref["manifest_sha256"] == self.manifest["study_sha256"]
                and bref["steps_done"] == 1600, "B reference not completed at exactly 1600 steps")
        require(all(bref[k] == case[k] for k in ("input_npz_path", "input_npz_sha256")), "B input differs")
        require(bref["final_npz_path"] == case["reference_npz_path"]
                and bref["final_npz_sha256"] == case["reference_npz_sha256"], "B final field differs")
        for path, digest in ((case["reference_case_path"], case["reference_case_sha256"]),
                             (case["input_npz_path"], case["input_npz_sha256"]),
                             (case["reference_npz_path"], case["reference_npz_sha256"])):
            require(self.manifest["frozen_sha256"].get(str(Path(path).resolve())) == digest,
                    "B case/input/reference missing from frozen inventory")
        inputs = self.arrays(case["input_npz_path"], case["input_npz_sha256"], ("A0", "dn", "sigma", "weights"))
        for key, array in inputs.items():
            self.array(array, n, key == "A0", "C3 input " + key)
        require(bool(np.all((inputs["dn"] >= -.003) & (inputs["dn"] <= 0)))
                and bool(np.all(inputs["sigma"] >= 0)), "C3 passive profile differs")
        weights, dx = inputs["weights"], case["dx_m"]
        require(bool(np.all((weights >= 0) & (weights <= 1))), "Detector weights outside [0,1]")
        p0 = self.power(inputs["A0"], dx)
        area = float(np.sum(weights) * dx ** 2)
        require(abs(p0 - 1) <= TOL and abs(area / (math.pi * (6e-6) ** 2) - 1) <= TOL,
                "Frozen initial power/detector area failed")
        reference = self.arrays(case["reference_npz_path"], case["reference_npz_sha256"], ("field",))["field"]
        self.array(reference, n, True, "B original final field")
        require(entry["case_id"] == name, "Final case report identity differs")
        path, digest, expected_done = Path(entry["path"]).resolve(), entry["sha256"], 1600
        chain, final_report, final_field = [], None, None
        while True:
            report = self.worker(path, digest, "checkpoint_completed")
            require(path.parent == self.out / name, "Checkpoint outside its case directory")
            start = integer(report["steps_start"], "steps_start")
            done = integer(report["steps_done"], "steps_done")
            require(report["case_id"] == name and report["input_npz_sha256"] == case["input_npz_sha256"]
                    and done == expected_done and 0 <= start < done <= 1600 and done - start <= 200,
                    "Disconnected/out-of-order/nonprogressing/oversized checkpoint")
            field_path = Path(report["npz_path"]).resolve()
            require(field_path == path.with_suffix(".npz"), "Checkpoint NPZ does not share report prefix")
            field = self.arrays(field_path, report["npz_sha256"], ("field",), True)["field"]
            self.array(field, n, True, "C checkpoint field")
            total, core = self.power(field, dx), self.core(field, weights, dx, p0)
            self.compare_record(report, {"input_power": p0, "output_power": total,
                                         "core_power_analytic_input": core, "core_area_m2": area}, name + " checkpoint")
            require(0 <= core <= total / p0 + TOL, "Checkpoint detector invariants failed")
            require(0 <= number(report["propagation_s"], "propagation_s") <= report["elapsed_s"],
                    "Invalid propagation timing")
            self.metadata(report["factor_metadata"], n, done - start)
            chain.append({"path": str(path), "sha256": digest, "steps_start": start,
                          "steps_done": done, "npz_path": str(field_path), "npz_sha256": report["npz_sha256"]})
            if final_report is None:
                final_report, final_field = report, field
            elif "comparison" in report:
                raise ValueError("Comparison present before final 1600-step checkpoint")
            previous = report["previous_checkpoint_path"]
            previous_sha = report["previous_checkpoint_sha256"]
            if start == 0:
                require(previous is None and previous_sha is None, "Initial checkpoint has a parent")
                break
            require(previous is not None and previous_sha is not None, "Noninitial checkpoint missing parent")
            expected_done, path, digest = start, Path(previous).resolve(), previous_sha
        completed = set()
        for candidate in (self.out / name).glob("*.json"):
            record = self.json(candidate, output=True)
            require(record.get("status") == "checkpoint_completed", "Unexpected failed/noncheckpoint case evidence")
            completed.add(candidate.resolve())
        require(completed == {Path(link["path"]) for link in chain}, "Extra completed disconnected checkpoint(s)")
        values = self.difference(final_field, reference)
        sparse_total, reference_total = self.power(final_field, dx), self.power(reference, dx)
        sparse_core = self.core(final_field, weights, dx, p0)
        reference_core = self.core(reference, weights, dx, p0)
        values.update(input_power=p0, sparse_total=sparse_total, reference_total=reference_total,
                      sparse_core=sparse_core, reference_core=reference_core,
                      absolute_total_difference=abs(sparse_total - reference_total),
                      absolute_core_difference=abs(sparse_core - reference_core))
        self.compare_record(final_report["comparison"], values, name + " final worker")
        self.compare_record(entry["comparison"], values, name + " execution summary")
        require(values["relative_l2"] <= TOL and values["relative_linf"] <= TOL
                and values["absolute_total_difference"] <= TOL and values["absolute_core_difference"] <= TOL,
                "C3 raw complex/full-power/core-power equivalence failed")
        require(0 <= sparse_total <= 1.001 and 0 <= reference_total <= 1.001
                and 0 <= reference_core <= reference_total / p0 + TOL, "C3 final power guard failed")
        return {"case_id": name, "state": "PASS", "steps_done": 1600,
                "checkpoint_count": len(chain), "shorter_chunks": sum(link["steps_done"] - link["steps_start"] < 200 for link in chain),
                "chain_forward": list(reversed(chain)), "comparison": values,
                "reference_case_path": str(reference_case_path), "reference_case_sha256": case["reference_case_sha256"],
                "reference_npz_path": case["reference_npz_path"], "reference_npz_sha256": case["reference_npz_sha256"],
                "core_area_m2": area}

    def run(self):
        np = self.np
        require(np.__version__ == "2.2.6", "Independent auditor requires NumPy 2.2.6")
        execution_path, manifest_path = self.out / "execution.json", self.out / "audit_manifest.json"
        execution = self.json(execution_path, output=True)
        auditor_path = self.file(Path(__file__).resolve())
        self.manifest_sha = sha(manifest_path)
        self.manifest = self.json(manifest_path, self.manifest_sha, True)
        manifest = self.manifest
        require(execution["schema"] == "silice.point03-sparse.execution.v1"
                and manifest["schema"] == "silice.point03-sparse.manifest.v1", "Unknown C evidence schema")
        require(execution["status"] == "completed" and execution["operational_pass"] is True
                and execution["equivalence_pass"] is True, "Stage C did not finish successfully")
        require(Path(manifest["out_dir"]).resolve() == self.out
                and Path(execution["audit_manifest_path"]).resolve() == manifest_path
                and execution["audit_manifest_sha256"] == self.manifest_sha, "C manifest identity differs")
        limits = {"total_wall_budget_s": 600, "max_steps_per_child": 200, "internal_deadline_s": 35,
                  "parent_timeout_s": 40, "field_tolerance": TOL, "power_tolerance": TOL,
                  "residual_tolerance": 1e-13, "seed": 20261006}
        require(all(manifest[k] == v for k, v in limits.items()), "Frozen C contract limits differ")
        self.study = self.file(manifest["study_path"], manifest["study_sha256"])
        require(Path(execution["study_path"]).resolve() == self.study, "Execution points to another B study")
        bmanifest = read_json(self.study)
        require(bmanifest["schema"] == "silice.point03-refinement.manifest.v1", "Unknown B manifest schema")
        root = Path(bmanifest["source_root"])
        require(root.is_absolute() and root.is_dir(), "Invalid B source root")
        root = root.resolve()
        require(self.study == root / "resultados/codex/point03_refinement_20261006T220909702270Z/manifest.json",
                "Reference study is not the contracted original B study")
        frozen = manifest["frozen_sha256"]
        require(execution["frozen_sha256_before"] == execution["frozen_sha256_after"] == frozen
                and execution["frozen_unchanged"] is True, "Frozen before/after inventory differs")
        for name, digest in frozen.items():
            self.file(name, digest)
        require(all(frozen.get(name) == digest for name, digest in bmanifest["source_sha256"].items()),
                "Original B source hashes not retained")
        helper = root / "scripts/point03_sparse_adi.py"
        driver = root / "scripts/audit_point03_sparse_adi.py"
        original = root / "experimentos/glass009_claude/adi2d.py"
        contract = root / "Docs/POINT-03-SPARSE-ADI-CONTRACT.md"
        for path in (helper, driver, original, contract, self.study):
            require(str(path) in frozen, "Required source/contract missing from frozen inventory")
        require(frozen[str(helper)] == HELPER_SHA and frozen[str(driver)] == DRIVER_SHA
                and frozen[str(contract)] == CONTRACT_SHA,
                "Helper/driver/contract differ from frozen Stage C commit 005dae057df0a264ad8372be905d24644715373a")
        # Parse only: never import or evaluate a source expression.
        tree = ast.parse(original.read_text(encoding="utf-8-sig"), filename=str(original))
        constants = {target.id: node.value.value for node in tree.body if isinstance(node, ast.Assign)
                     and isinstance(node.value, ast.Constant) for target in node.targets if isinstance(target, ast.Name)}
        require(constants.get("lam") == 1550e-9 and constants.get("n0") == 1.444,
                "ADI physical constants differ from independent dense formula")
        before, after = execution["tracked_sha256_before"], execution["tracked_sha256_after"]
        require(before == after and execution["tracked_inputs_unchanged"] is True and len(before) > 0,
                "Declared tracked before/after inventory differs")
        for name, digest in before.items():
            relative = Path(name)
            require(not relative.is_absolute() and ".." not in relative.parts, "Tracked path escapes source root")
            self.file(root / relative, digest)
        for path in (helper, driver, original, contract):
            relative_name = path.relative_to(root).as_posix()
            require(before.get(relative_name) == frozen[str(path)], "Required source missing from declared tracked list")
        environment = execution["environment"]
        require(environment["numpy"] == "2.2.6" and environment["scipy"] == "1.15.1"
                and environment["psutil"] == "6.1.1" and environment["python"].startswith("3.13.7"),
                "Execution dependency versions differ")
        require(environment["threads"] == {key: "1" for key in THREADS}, "Execution thread isolation differs")
        produced = execution["produced_sha256"]
        require(produced == execution["produced_sha256_after"] and execution["produced_unchanged"] is True,
                "Produced before/after inventory differs")
        require(str(manifest_path) in produced and produced[str(manifest_path)] == self.manifest_sha,
                "Manifest absent from produced inventory")
        inventory = set()
        for name, digest in produced.items():
            path = self.file(name, digest, True)
            require(path not in inventory, "Aliased output inventory path")
            inventory.add(path)
        actual_inventory = set()
        for path in self.out.rglob("*"):
            require(not path.is_symlink(), "Symlink in C output tree")
            if path.is_file():
                actual_inventory.add(path.resolve())
        # Explicitly named summaries created by the orchestrator AFTER C ended.
        # They are auxiliary, never inputs to a numerical/hash/pass decision.
        allowed_auxiliary = {self.out / "compact_result.json", self.out / "summarize_orchestrator.py"}
        auxiliary = actual_inventory & allowed_auxiliary
        auxiliary_sha256 = {}
        for path in sorted(auxiliary):
            self.file(path, output=True)
            auxiliary_sha256[str(path)] = self.observed[str(path)]
        require(actual_inventory == inventory | {execution_path} | auxiliary,
                "Unlisted/missing C output file(s) outside explicitly allowed postrun auxiliaries")
        small_entries = execution["small_reports"]
        require(len(small_entries) == 2 and {entry["N"] for entry in small_entries} == {8, 11},
                "Expected both C1/C2 small cases")
        small = [self.small(entry) for entry in small_entries]
        require(len(manifest["cases"]) == len(execution["case_reports"]) == 2, "Expected exactly two C3 cases")
        case_entries = {entry["case_id"]: entry for entry in execution["case_reports"]}
        require(set(case_entries) == set(CASES)
                and {case["case_id"] for case in manifest["cases"]} == set(CASES), "C3 case identities differ")
        cases = [self.reproduction(case, case_entries[case["case_id"]], bmanifest) for case in manifest["cases"]]
        children = execution["children"]
        require(len(children) == len(self.worker_paths), "Children do not match retained worker reports")
        child_reports = set()
        previous_end, max_child = 0.0, 0.0
        for child in children:
            require(child["returncode"] == 0 and not child.get("timed_out", False)
                    and not child.get("interrupted_or_launch_error"), "Child timeout/failure/interruption")
            elapsed = number(child["elapsed_s"], "child elapsed_s")
            start = number(child["started_elapsed_s"], "child started_elapsed_s")
            require(0 <= elapsed <= 40 and start >= previous_end - 1e-6, "Child timeout or overlapping execution")
            previous_end, max_child = start + elapsed, max(max_child, elapsed)
            argv = child["command"]
            require(isinstance(argv, list) and argv.count("--prefix") == 1, "Invalid child command evidence")
            prefix = Path(argv[argv.index("--prefix") + 1]).resolve()
            child_report = Path(str(prefix) + ".json")
            require(child_report in self.worker_paths and child_report not in child_reports,
                    "Child prefix does not uniquely identify a retained worker")
            child_reports.add(child_report)
            child_record = read_json(child_report)
            require(number(child_record["elapsed_s"], "worker elapsed_s") <= elapsed + 1e-3,
                    "Worker duration exceeds parent observed child duration")
            for option, value in (("--out-dir", str(self.out)), ("--audit-manifest", str(manifest_path)),
                                  ("--audit-sha", self.manifest_sha), ("--study", str(self.study))):
                require(argv.count(option) == 1 and argv[argv.index(option) + 1] == value,
                        "Child command audit identity differs: " + option)
            require(len(argv) > 3 and Path(argv[3]).resolve() == driver, "Child invoked another driver")
            if child_record["status"] == "small_completed":
                require("--private-small" in argv and argv.count("--small-n") == 1
                        and int(argv[argv.index("--small-n") + 1]) == child_record["small_profile"]["N"],
                        "Small child mode/grid differs")
            else:
                require("--private-reproduce" in argv and argv.count("--case-id") == 1
                        and argv[argv.index("--case-id") + 1] == child_record["case_id"], "C3 child mode/case differs")
                predecessor = child_record["previous_checkpoint_path"]
                if predecessor is None:
                    require("--checkpoint" not in argv, "Initial child command has checkpoint")
                else:
                    require(argv.count("--checkpoint") == 1 and argv[argv.index("--checkpoint") + 1] == predecessor,
                            "Child command predecessor differs from chain")
            for label in ("stdout", "stderr"):
                path = Path(child[label + "_path"]).resolve()
                require(path == Path(str(prefix) + "." + label + ".log") and path in inventory,
                        "Missing child log identity")
                self.referenced_outputs.add(path)
        require(inventory == self.referenced_outputs | {manifest_path},
                "Produced inventory contains output unconnected to validated workers/chains")
        total_elapsed = number(execution["elapsed_s"], "execution elapsed_s")
        require(0 <= total_elapsed <= 600 and total_elapsed >= previous_end - 1e-6,
                "Execution wall budget invalid/exceeded")
        parent_memory = self.memory(execution["memory"])
        checkpoint_count = sum(case["checkpoint_count"] for case in cases)
        require(checkpoint_count >= 16, "Fewer than eight <=200-step chunks per 1600-step case")
        require(self.factor_count == 2 * len(children), "Factor metadata count differs from sequential children")
        # Complete second read detects evidence modification during this audit.
        for name, digest in self.observed.items():
            require(sha(name) == digest, "Evidence changed before certificate write: " + name)
        require({p.resolve() for p in self.out.rglob("*") if p.is_file()} == actual_inventory,
                "Output inventory changed during independent audit")
        peaks = [record["peak_wset_bytes"] for record in self.worker_memory + [parent_memory]
                 if record["peak_wset_bytes"] is not None]
        return {"schema": "silice.point03-sparse.independent-postrun.v1", "status": "PASS",
                "independent_equivalence_pass": True, "out_dir": str(self.out), "source_root": str(root),
                "audit_manifest_sha256": self.manifest_sha, "execution_sha256": self.observed[str(execution_path)],
                "auditor_sha256": self.observed[str(auditor_path)], "numpy_version": np.__version__,
                "C1_C2": small, "C3": cases, "raw_complex_fields": True,
                "phase_alignment": False, "output_renormalization": False,
                "field_tolerance": TOL, "power_tolerance": TOL, "residual_tolerance": 1e-13,
                "max_recorded_metric_recalculation_error": self.max_record_error,
                "integrity": {"frozen_file_count": len(frozen), "declared_tracked_file_count": len(before),
                              "produced_file_count": len(inventory), "all_observed_sha256": dict(self.observed),
                              "postrun_auxiliary_sha256": auxiliary_sha256,
                              "postrun_auxiliary_unchanged": True,
                              "scope": "Exact equality of declared before/after tracked inventory, current file hashes, frozen inputs/sources, and complete C output file listing. Only compact_result.json and summarize_orchestrator.py are allowed as postrun auxiliaries; neither supplies scientific evidence. Git index membership is not rediscovered; the recorded driver inventory defines the tracked set."},
                "operations": {"children": len(children), "checkpoint_children": checkpoint_count,
                               "nominal_checkpoint_children": 16, "shorter_valid_chunks": sum(c["shorter_chunks"] for c in cases),
                               "sequential_recorded": True, "max_child_elapsed_s": max_child,
                               "parent_timeout_s": 40, "internal_deadline_s": 35,
                               "execution_elapsed_s": total_elapsed, "wall_budget_s": 600,
                               "gpu_used": False,
                               "gpu_scope": "All completed worker CPU/GPU flags checked; frozen CPU-only sparse backend and versions checked. No independent hardware activity trace is retained.",
                               "timing_scope": "Recorded costs including the original driver integrity checks; not a comparative speedup benchmark or independent replay."},
                "memory": {"parent": parent_memory,
                           "maximum_reported_current_rss_bytes": max(m["rss_current_bytes"] for m in self.worker_memory + [parent_memory]),
                           "maximum_reported_peak_wset_bytes": max(peaks) if peaks else None,
                           "scope": "RSS values are per-process current samples. Windows working-set peaks are reported only when available; they are not aggregate study memory or native LU allocation totals. Available-RAM/free-disk guards have no retained numerical telemetry."},
                "permutations": {"factors_checked": self.factor_count, "nonidentity_recorded": 0,
                                 "identity_hashes_verified": True,
                                 "scope": "Recorded row/column identity arrays checked by independently constructed identity hashes. Successful raw permutation arrays/native LU objects are not retained; C1 residuals and raw C1/C2/C3 fields provide separate numerical checks."},
                "scientific_scope": "Solver equivalence on these frozen cases only. This does not establish spatial/temporal convergence, validate Stage B acceptance, certify physical accuracy, or authorize a later stage."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    out, output = args.out_dir.resolve(), args.output.resolve()
    if not out.is_dir():
        parser.error("--out-dir must be an existing, finished Stage C evidence directory")
    if output.exists():
        parser.error("--output must be fresh; this audit never replaces a file")
    if not output.parent.is_dir():
        parser.error("--output parent directory must already exist")
    # Thread settings affect only this independent NumPy arithmetic process.
    for name in THREADS:
        os.environ[name] = "1"
    started = time.monotonic()
    created = False
    try:
        import numpy as np
        result = Auditor(out, output, np).run()
        result["independent_audit_elapsed_s"] = time.monotonic() - started
        # No certificate exists on a failed audit; create exclusively only after PASS.
        serialized = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
        with output.open("x", encoding="utf-8", newline="\n") as handle:
            created = True
            handle.write(serialized)
        print(json.dumps({"status": "PASS", "output": str(output), "sha256": sha(output)}, allow_nan=False))
        return 0
    except (Exception, KeyboardInterrupt) as error:
        cleanup_error = None
        if created:
            try:
                output.unlink()
            except OSError as cleanup:
                cleanup_error = str(cleanup)
        print(json.dumps({"status": "FAIL", "error_type": type(error).__name__, "error": str(error),
                          "certificate_written": False, "partial_output_cleanup_error": cleanup_error},
                         allow_nan=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
