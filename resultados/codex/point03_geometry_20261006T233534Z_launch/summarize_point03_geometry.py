#!/usr/bin/env python3
"""Read-only retained-data summary AFTER Point 03 D, including failed attempts.

No scientific module is imported and no geometry or quadrature is evaluated.
Only files, JSON, hashes and NumPy arithmetic on retained arrays are used.
The fresh summary is written outside the original execution evidence tree.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import sys


def sha(path):
    with Path(path).open("rb") as handle:
        digest = hashlib.sha256()
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate JSON key: " + key)
            result[key] = value
        return result
    def reject(value):
        raise ValueError("Nonfinite JSON: " + value)
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=pairs, parse_constant=reject)


class Audit:
    def __init__(self, out, np):
        self.out, self.np, self.observed = out, np, {}
        self.errors = {"integrity": [], "completion": [], "science": []}
        self.data = {"grids": [], "references": [], "synthetic": [], "global_comparisons": []}
        self.count = {"grids": 0, "reference_rows": 0, "resolved_references": 0, "synthetic_rows": 0,
                      "invariance_suites": 0, "global_comparisons": 0}

    def need(self, condition, label, kind="science"):
        if not bool(condition) and label not in self.errors[kind]:
            self.errors[kind].append(label)

    def close(self, actual, recorded, label, tol=1e-12):
        self.need(math.isfinite(float(recorded)) and abs(actual - float(recorded)) <= tol, label)

    def file(self, path, expected=None):
        path = Path(path).resolve()
        if not path.is_file() or path.is_symlink():
            raise ValueError("Missing/symlink file: " + str(path))
        current = sha(path)
        self.need(expected is None or current == expected, "SHA mismatch: " + str(path), "integrity")
        self.need(self.observed.setdefault(str(path), current) == current, "File changed during summary: " + str(path), "integrity")
        return path

    def attempt(self, label, function, kind="completion"):
        try:
            return function()
        except Exception as error:
            self.errors[kind].append(f"{label}: {type(error).__name__}: {error}")
            return None

    def report(self, name):
        value = read(self.file(self.out / (name + ".json")))
        self.need(value["schema"] == "silice.point03-geometry.worker.v1"
                  and value["audit_manifest_sha256"] == self.identity, name + " worker identity", "integrity")
        self.need(value["status"] == name.split("_")[0] + "_completed", name + " worker incomplete", "completion")
        self.need(value["gpu_used"] is False, name + " reported CPU flag", "integrity")
        if value["status"] != "failed": self.need(value.get("sources_and_inputs_unchanged") is True, name + " source flag", "integrity")
        self.need(0 <= value["elapsed_s"] <= 35, name + " internal deadline", "completion")
        return value

    def arrays(self, report):
        self.need(len(report["array_artifacts"]) == 1, "Expected one retained NPZ per numerical worker", "integrity")
        artifact = report["array_artifacts"][0]
        path = self.file(artifact["path"], artifact["sha256"])
        self.need(path.is_relative_to(self.out), "Worker NPZ outside execution tree", "integrity")
        with self.np.load(path, allow_pickle=False) as archive:
            return {key: archive[key] for key in archive.files}

    def cell(self, value, rect, label):
        area = (rect[1] - rect[0]) * (rect[3] - rect[2])
        raw, clipped, raw_area = float(value["raw_fraction"]), float(value["fraction"]), float(value["area_raw_um2"])
        closure = [float(x) for x in value["boundary_closure_um"]]
        self.need(area > 0 and all(math.isfinite(v) for v in (raw, clipped, raw_area, *closure)), label + " finite")
        self.need(-1e-12 <= raw <= 1 + 1e-12 and clipped == min(1.0, max(0.0, raw)), label + " range/clipping")
        self.close(raw_area / area, raw, label + " raw normalization")
        self.close(clipped - raw, value["correction"], label + " correction", 1e-16)
        self.need(len(closure) == 2 and max(abs(v) for v in closure) <= 1e-11 * min(rect[1] - rect[0], rect[3] - rect[2]), label + " closure")
        contribution = float(value["absolute_contribution_sum_um2"])
        self.need(contribution >= 0 and math.isfinite(contribution), label + " contributions")
        self.close(abs(raw_area) / contribution if contribution else 1.0, value["cancel_ratio"], label + " cancel convention")
        return raw, clipped, raw_area, area

    def reference(self, result, rect, label):
        fine, coarse = float(result["fraction_fine"]), float(result["fraction_coarse"])
        error, omitted = float(result["estimated_error_fine"]), float(result["omitted_width_bound"])
        quality = math.fsum((error, omitted, abs(fine - coarse)))
        self.need(tuple(result["rect_um"]) == tuple(rect), label + " reference rectangle")
        self.close(quality, result["quality_total"], label + " quality formula", 1e-16)
        self.close(abs(fine - coarse), result["stability"], label + " stability", 1e-16)
        valid = (all(math.isfinite(v) for v in (fine, coarse, error, omitted, quality))
                 and error >= 0 and float(result["estimated_error_coarse"]) >= 0
                 and 0 <= omitted <= 1e-14 and quality <= 1e-13 and not result["messages"])
        self.need(valid and result["quality_pass"] is True, label + " unresolved reference quality")
        area = (rect[1] - rect[0]) * (rect[3] - rect[2])
        self.close(float(result["area_fine_um2"]) / area, fine, label + " reference area")
        self.close(float(result["area_coarse_um2"]) / area, coarse, label + " coarse area")
        self.close(float(result["rect_area_um2"]) / area, 1.0, label + " reference normalization")
        for mode, fraction in (("coarse", coarse), ("fine", fine)):
            records = result["diagnostics"][mode]["intervals"]
            self.close(math.fsum(float(r["value"]) for r in records), fraction, label + " normalized " + mode + " interval sum", 1e-16)
            self.close(math.fsum(float(r["estimated_error"]) for r in records), result["estimated_error_" + mode], label + " normalized " + mode + " error sum", 1e-16)
            self.need(all(0 <= r["u_lower"] < r["u_upper"] <= 1 and r["estimated_error"] >= 0 for r in records), label + " normalized interval diagnostics")
        return fine, coarse, quality, valid

    def invariants(self, records, baseline, rect, spec, label):
        width, height = rect[1] - rect[0], rect[3] - rect[2]
        area, base = width * height, float(baseline["area_raw_um2"])
        def mapped(point):
            result = {"disks": [[*point(x, y), r] for x, y, r in spec["disks"]], "annulus": None}
            if spec.get("annulus") is not None: result["annulus"] = dict(spec["annulus"], center=list(point(*spec["annulus"]["center"])))
            return result
        variants = {"reversed_disk_order": (dict(spec, disks=list(reversed(spec["disks"]))), tuple(rect), None),
                    "translation": (mapped(lambda x, y: (x + 17.25, y - 11.5)), (rect[0] + 17.25, rect[1] + 17.25, rect[2] - 11.5, rect[3] - 11.5), None),
                    "reflection_y_axis": (mapped(lambda x, y: (-x, y)), (-rect[1], -rect[0], rect[2], rect[3]), None),
                    "local_origin_offset": (spec, tuple(rect), [(rect[0] + rect[1]) / 2 + width / 7, (rect[2] + rect[3]) / 2 - height / 9])}
        if spec["disks"]: variants["duplicate_first_disk"] = (dict(spec, disks=list(spec["disks"]) + [list(spec["disks"][0])]), tuple(rect), None)
        expected = {"reversed_disk_order", "duplicate_first_disk", "translation", "reflection_y_axis", "local_origin_offset", "four_equal_subcells"}
        self.need(len(records) == 6 and {row["test"] for row in records} == expected, label + " invariant set")
        for row in records:
            test = row["test"]
            if test == "duplicate_first_disk" and not spec["disks"]:
                self.need(row["state"] == "NOT_APPLICABLE_EMPTY", label + " empty duplicate state")
                continue
            if test == "four_equal_subcells":
                self.need(len(row["children"]) == 4, label + " four subcells")
                mx, my = (rect[0] + rect[1]) / 2, (rect[2] + rect[3]) / 2
                expected_rects = [(rect[0], mx, rect[2], my), (mx, rect[1], rect[2], my), (rect[0], mx, my, rect[3]), (mx, rect[1], my, rect[3])]
                values = [self.cell(child["candidate"], child["rect_um"], label + " subcell")[2] for child in row["children"]]
                self.need([tuple(c["rect_um"]) for c in row["children"]] == expected_rects, label + " subcell partition")
                changed = math.fsum(values)
                self.close(changed, row["sum_subcell_area_um2"], label + " subcell sum")
            else:
                expected_spec, expected_rect, expected_origin = variants[test]
                self.need(row["spec_um"] == expected_spec and tuple(row["rect_um"]) == expected_rect
                          and row["origin_um"] == expected_origin, label + " " + test + " actual transformation", "integrity")
                changed = self.cell(row["candidate"], row["rect_um"], label + " " + test)[2]
            delta = abs(changed - base) / area
            self.close(delta, row["absolute_fraction_difference"], label + " " + test + " recorded difference")
            self.need(delta <= 1e-12 and row["state"] == "PASS", label + " " + test + " invariant")
        self.count["invariance_suites"] += 1

    def grid(self, plan):
        np, n, dx = self.np, plan["N"], plan["dx_um"]
        report = self.report(f"grid_n{n}"); arrays = self.arrays(report)
        expected = {"raw_fraction", "fraction", "area_raw_um2", "area_um2", "boundary_closure_um", "cell_status"}
        self.need(set(arrays) == expected, f"N{n} grid NPZ keys", "integrity")
        raw, clipped, a0, a1, closure, status = (arrays[key] for key in ("raw_fraction", "fraction", "area_raw_um2", "area_um2", "boundary_closure_um", "cell_status"))
        self.need(all(x.shape == (n, n) and x.dtype == np.dtype("float64") for x in (raw, clipped, a0, a1))
                  and closure.shape == (n, n, 2) and closure.dtype == np.dtype("float64")
                  and status.shape == (n, n) and status.dtype == np.dtype("uint8"), f"N{n} grid shape/dtype")
        axis = (np.arange(n) - n // 2) * (128.0 / n)
        self.need(dx == 128.0 / n and plan["dx_m"] == 128e-6 / n and plan["axis_um"] == axis.tolist(), f"N{n} nominal grid")
        widths = (axis + dx / 2) - (axis - dx / 2); areas = widths[:, None] * widths[None, :]
        disks, annulus = self.manifest["spec_um"]["disks"], self.manifest["spec_um"]["annulus"]
        bbox = (min(x - r for x, y, r in disks), max(x + r for x, y, r in disks), min(y - r for x, y, r in disks), max(y + r for x, y, r in disks))
        if annulus is not None:
            x, y = annulus["center"]; r = annulus["outer"]
            bbox = (max(bbox[0], x - r), min(bbox[1], x + r), max(bbox[2], y - r), min(bbox[3], y + r))
        self.need(tuple(report["support_bounds_um"]) == bbox, f"N{n} independent support bbox", "integrity")
        low, high = axis - dx / 2, axis + dx / 2
        disjoint = (high[None, :] <= bbox[0]) | (low[None, :] >= bbox[1]) | (high[:, None] <= bbox[2]) | (low[:, None] >= bbox[3])
        outside = status == 1
        self.need(np.all(disjoint[outside]) and all(np.all(x[outside] == 0) for x in (raw, clipped, a0, a1, closure)), f"N{n} status1 proven disjoint zeros")
        finite = np.isfinite(raw) & np.isfinite(clipped) & np.isfinite(a0) & np.isfinite(a1) & np.all(np.isfinite(closure), axis=2)
        complete = bool(np.all(finite) and np.all((status == 1) | (status == 2)))
        self.need(complete and report.get("numeric_valid") is True, f"N{n} grid incomplete", "completion")
        self.need(report["cells_completed"] == int(np.sum(status != 0)) and report["candidate_evaluated_cells"] == int(np.sum(status == 2)), f"N{n} completion/evaluation counts")
        if "support_disjoint_cells" in report: self.need(report["support_disjoint_cells"] == int(np.sum(outside)), f"N{n} disjoint count")
        processed = finite & (status != 0)
        maximum = float(np.max(np.abs(closure[processed]))) if np.any(processed) else 0.0
        self.close(maximum, report["max_boundary_closure_um"], f"N{n} recorded max processed closure")
        available = np.isfinite(raw); self.need(np.all((raw[available] >= -1e-12) & (raw[available] <= 1 + 1e-12)), f"N{n} raw range")
        self.need(np.array_equal(clipped[finite], np.clip(raw[finite], 0, 1)), f"N{n} endpoint clipping")
        self.need(np.all(np.abs(a0[finite] / areas[finite] - raw[finite]) <= 1e-12) and np.all(np.abs(a1[finite] / areas[finite] - clipped[finite]) <= 1e-12), f"N{n} cell area normalization")
        self.need(np.all(np.max(np.abs(closure[finite]), axis=1) <= (1e-11 * np.minimum(widths[:, None], widths[None, :]))[finite]), f"N{n} cell closures")
        corrected = finite & (clipped != raw); logs = report["raw_endpoint_corrections"]
        self.need({(row["iy"], row["ix"]) for row in logs} == set(zip(*np.nonzero(corrected))) and len(logs) == int(np.sum(corrected)), f"N{n} clipping list")
        for row in logs:
            iy, ix = row["iy"], row["ix"]
            for key, value in (("raw_fraction", raw[iy, ix]), ("fraction", clipped[iy, ix]), ("correction", clipped[iy, ix] - raw[iy, ix])):
                self.close(float(value), row[key], f"N{n} clipping {key}", 1e-16)
        self.need(report["endpoint_correction_count"] == int(np.sum(corrected)), f"N{n} clipping count")
        max_correction = float(np.max(np.abs((clipped - raw)[finite]))) if np.any(finite) else 0.0
        self.close(max_correction, report["max_absolute_endpoint_correction"], f"N{n} clipping maximum")
        sums = {"raw_grid_area_um2": float(np.sum(a0)), "grid_area_um2": float(np.sum(a1)),
                "nominal_raw_fraction_grid_area_um2": float(np.sum(raw) * dx ** 2), "nominal_fraction_grid_area_um2": float(np.sum(clipped) * dx ** 2)} if complete else {}
        for key, value in sums.items(): self.close(value, report[key], f"N{n} {key}")
        self.data["grids"].append({"N": n, "complete": complete, "finite_cells": int(np.sum(finite)), "completed_cells": int(np.sum(status != 0)),
                                   "max_closure_um": float(np.max(np.abs(closure[finite]))) if np.any(finite) else None, "correction_count": len(logs), "integrals": sums})
        self.count["grids"] += int(complete)
        self.grid_arrays[n] = arrays; self.integrals[n] = sums
        selection = plan["reference_selection"]["cells"]
        self.need(len(selection) == len({(s["iy"], s["ix"]) for s in selection}) == 48, f"N{n} frozen selection48")
        for item in selection:
            iy, ix = item["iy"], item["ix"]
            rect = (axis[ix] - dx / 2, axis[ix] + dx / 2, axis[iy] - dx / 2, axis[iy] + dx / 2)
            self.need(0 <= iy < n and 0 <= ix < n and tuple(item["rect_um"]) == rect, f"N{n} frozen selected rectangle")
            if "point_um" in item: self.need((iy, ix) == tuple(math.floor(p / dx + n // 2 + .5) for p in reversed(item["point_um"])), f"N{n} selected point index")

    def refs(self, plan, batch):
        np, n = self.np, plan["N"]
        report = self.report(f"reference_n{n}_batch{batch}"); arrays = self.arrays(report)
        expected = {"indices", "raw_fraction", "fraction", "candidate_recalculated_raw_fraction", "reference_fine", "reference_coarse", "reference_quality", "absolute_fraction_error", "completed"}
        self.need(set(arrays) == expected and arrays["indices"].shape == (24, 2) and arrays["indices"].dtype == np.dtype("int64")
                  and arrays["completed"].shape == (24,) and arrays["completed"].dtype == np.dtype("uint8")
                  and all(arrays[k].shape == (24,) and arrays[k].dtype == np.dtype("float64") for k in expected - {"indices", "completed"}), f"N{n} batch{batch} NPZ schema", "integrity")
        selected = plan["reference_selection"]["cells"][batch * 24:(batch + 1) * 24]
        self.need(len(report["reference_records"]) == 24 and np.all(arrays["completed"] == 1), f"N{n} batch{batch} incomplete", "completion")
        self.need(np.array_equal(arrays["indices"], np.array([[s["iy"], s["ix"]] for s in selected])), f"N{n} fixed batch indices", "integrity")
        errors, qualities = [], []
        for local, row in enumerate(report["reference_records"]):
            label = f"N{n} batch{batch} cell{local}"; item = selected[local]; self.count["reference_rows"] += 1
            self.need(row["selection"] == item and row["selection_index"] == batch * 24 + local, label + " selection identity", "integrity")
            rect, iy, ix = item["rect_um"], item["iy"], item["ix"]
            raw, clipped, _, _ = self.cell(row["candidate_recalculated"], rect, label)
            saved = self.grid_arrays[n]; base_raw, base_clipped = float(saved["raw_fraction"][iy, ix]), float(saved["fraction"][iy, ix])
            self.close(base_raw, row["saved_raw_fraction"], label + " saved raw"); self.close(base_clipped, row["saved_fraction"], label + " saved fraction")
            self.need(abs(raw - base_raw) <= 1e-12 and abs(clipped - base_clipped) <= 1e-12, label + " repeat candidate")
            fine, coarse, quality, valid = self.reference(row["reference"], rect, label)
            delta = abs(base_raw - fine); self.count["resolved_references"] += int(valid)
            if valid: self.need(delta <= 1e-12, label + " conditional reference agreement")
            for key, value in (("raw_fraction", base_raw), ("fraction", base_clipped), ("candidate_recalculated_raw_fraction", raw), ("reference_fine", fine), ("reference_coarse", coarse), ("reference_quality", quality), ("absolute_fraction_error", delta)):
                self.close(value, arrays[key][local], label + " NPZ " + key, 1e-16)
            if "absolute_fraction_error" in row: self.close(delta, row["absolute_fraction_error"], label + " recorded error", 1e-16)
            if row["selection_index"] < 8: self.invariants(row["invariances"], row["candidate_recalculated"], rect, self.manifest["spec_um"], label)
            self.need(row["state"] == "PASS", label + " incomplete state", "completion")
            if valid: errors.append(delta); qualities.append(quality)
        self.data["references"].append({"N": n, "batch": batch, "available_rows": len(report["reference_records"]), "resolved_rows": len(errors),
                                        "max_resolved_absolute_error": max(errors, default=None), "max_resolved_quality": max(qualities, default=None)})

    def synthetic(self):
        report = self.report("synthetic"); arrays = self.arrays(report); fixtures = self.manifest["known_fixtures"]
        expected = {"raw_fraction", "fraction", "reference_fine", "reference_coarse", "reference_quality", "completed"}
        self.need(set(arrays) == expected and arrays["completed"].shape == (22,) and arrays["completed"].dtype == self.np.dtype("uint8")
                  and all(arrays[k].shape == (22,) and arrays[k].dtype == self.np.dtype("float64") for k in expected - {"completed"}), "Synthetic NPZ schema", "integrity")
        self.need(len(fixtures) == len(report["fixture_reports"]) == 22 and self.np.all(arrays["completed"] == 1), "Synthetic22 incomplete", "completion")
        for index, row in enumerate(report["fixture_reports"]):
            fixture = fixtures[index]; label = "Synthetic " + fixture["id"]; self.count["synthetic_rows"] += 1
            self.need(row["id"] == fixture["id"] and row["spec_um"] == fixture["spec_um"] and row["rect_um"] == fixture["rect_um"], label + " frozen case", "integrity")
            raw, clipped, _, area = self.cell(row["candidate"], row["rect_um"], label)
            if fixture["expected_area_um2"] is not None: self.need(abs(raw - fixture["expected_area_um2"] / area) <= 1e-12, label + " known area")
            fine, coarse, quality, valid = self.reference(row["reference"], row["rect_um"], label)
            if valid: self.need(abs(raw - fine) <= 1e-12, label + " conditional independent reference")
            self.data["synthetic"].append({"id": fixture["id"], "recorded_state": row["state"],
                                           "reference_quality_resolved": valid, "available_absolute_fraction_difference": abs(raw - fine),
                                           "reference_quality": quality, "accepted_comparison": valid and abs(raw - fine) <= 1e-12})
            for key, value in (("raw_fraction", raw), ("fraction", clipped), ("reference_fine", fine), ("reference_coarse", coarse), ("reference_quality", quality)):
                self.close(value, arrays[key][index], label + " NPZ " + key, 1e-16)
            if "invariances" in row: self.invariants(row["invariances"], row["candidate"], row["rect_um"], fixture["spec_um"], label)
            else: self.need(False, label + " invariant suite not evaluated", "completion")
            self.need(row["state"] == "PASS", label + " unfinished", "completion")

    def global_check(self):
        report = self.report("global"); result = report["reference_global"]
        self.reference(result, [-13.0, 13.0, -13.0, 13.0], "Global"); reference = float(result["area_fine_um2"])
        self.need(reference > 0, "Global reference positive")
        values = {"global_oriented_boundary_raw": float(report["candidate_global"]["area_raw_um2"]), "global_oriented_boundary_reported": float(report["candidate_global"]["area_um2"])}
        keys = ("raw", "endpoint_corrected", "nominal_raw_fraction", "nominal_endpoint_corrected_fraction")
        sum_keys = ("raw_grid_area_um2", "grid_area_um2", "nominal_raw_fraction_grid_area_um2", "nominal_fraction_grid_area_um2")
        for n, sums in self.integrals.items(): values.update({f"n{n}_{label}_grid": sums[key] for label, key in zip(keys, sum_keys)})
        rows = report["comparison_records"]; self.need(len(rows) == 18 and {r["label"] for r in rows} == set(values), "Global18 comparison set", "completion")
        for row in rows:
            actual = values[row["label"]]; error = abs(actual - reference) / reference
            for key, value in (("candidate_area_um2", actual), ("reference_area_um2", reference), ("relative_error", error)): self.close(value, row[key], "Global recorded " + row["label"] + " " + key)
            self.need(error <= 1e-12 and row["state"] == "PASS", "Global area " + row["label"])
            self.data["global_comparisons"].append({"label": row["label"], "relative_error": error})
            self.count["global_comparisons"] += 1

    def run(self):
        self.execution = self.attempt("execution", lambda: read(self.file(self.out / "execution.json"))) or {}
        execution = self.execution; self.manifest = self.attempt("manifest", lambda: read(self.file(self.out / "audit_manifest.json", execution.get("audit_manifest_sha256"))))
        self.identity = self.observed.get(str(self.out / "audit_manifest.json")); self.grid_arrays, self.integrals = {}, {}
        self.need(self.np.__version__ == "2.2.6", "Auditor NumPy2.2.6", "integrity")
        self.need(execution.get("schema") == "silice.point03-geometry.execution.v1" and execution.get("status") == "completed" and execution.get("geometry_pass") is True and execution.get("operational_pass") is True, "Original execution did not pass completely", "completion")
        if self.manifest:
            manifest = self.manifest; root = Path(manifest["source_root"]).resolve()
            self.need(manifest["schema"] == "silice.point03-geometry.manifest.v1" and Path(manifest["out_dir"]).resolve() == self.out and manifest["seed"] == 20261006, "Frozen manifest identity", "integrity")
            for name, digest in manifest["frozen_sha256"].items(): self.attempt("Frozen hash " + name, lambda n=name, d=digest: self.file(n, d), "integrity")
            self.need(execution.get("frozen_sha256_before") == execution.get("frozen_sha256_after") == manifest["frozen_sha256"], "Frozen before/after equality", "integrity")
            before, after = execution.get("tracked_sha256_before", {}), execution.get("tracked_sha256_after", {})
            self.need(bool(before) and before == after, "Tracked inventory equality", "integrity")
            for name, digest in before.items(): self.attempt("Tracked hash " + name, lambda n=name, d=digest: self.file(root / n, d), "integrity")
            self.data["tracked_file_count"] = len(before)
            self.attempt("synthetic", self.synthetic)
            for plan in manifest["grids"]: self.attempt("grid " + str(plan["N"]), lambda p=plan: self.grid(p))
            for plan in manifest["grids"]:
                for batch in (0, 1): self.attempt(f"reference {plan['N']}/{batch}", lambda p=plan, b=batch: self.refs(p, b))
            self.attempt("global", self.global_check)
        children = execution.get("children", []); self.need(len(children) == 14, "All14 children required", "completion")
        previous_end = 0.0
        for child in children:
            self.need(child.get("returncode") == 0 and not child.get("timed_out") and not child.get("interrupted_or_launch_error"), "Child failure/timeout", "completion")
            self.need(0 <= child["elapsed_s"] <= 40 and child["started_elapsed_s"] >= previous_end - 1e-6, "Sequential child40 deadline", "completion")
            previous_end = child["started_elapsed_s"] + child["elapsed_s"]
            for key in ("worker_report_path", "stdout_path", "stderr_path"):
                if key in child: self.attempt("Child evidence", lambda p=child[key]: self.file(p, child.get("worker_report_sha256") if key == "worker_report_path" else None))
        self.need(0 <= execution.get("elapsed_s", -1) <= 600 and execution.get("elapsed_s", -1) >= previous_end - 1e-6, "Attempt600 budget", "completion")
        produced = execution.get("produced_sha256", {}); complete = execution.get("complete_output_sha256", {})
        self.need(bool(produced) and produced == execution.get("produced_sha256_after"), "Produced before/after equality", "integrity")
        for name, digest in complete.items(): self.attempt("Output hash", lambda n=name, d=digest: self.file(n, d), "integrity")
        self.need(set(complete) | {str(self.out / "execution.json")} == {str(p.resolve()) for p in self.out.rglob("*") if p.is_file()}, "Complete output listing", "integrity")
        if execution.get("status") == "completed": self.need(produced == complete, "Complete produced inventory", "integrity")
        for name, digest in self.observed.items(): self.attempt("Rehash " + name, lambda n=name, d=digest: self.file(n, d), "integrity")
        expected = {"grids": 4, "reference_rows": 192, "resolved_references": 192, "synthetic_rows": 22, "invariance_suites": 54, "global_comparisons": 18}
        self.need(self.count == expected, "Complete scientific evidence counts", "completion")
        return {"schema": "silice.point03-geometry.readonly-postrun.v1", "status": "PASS" if not any(self.errors.values()) else "FAIL",
                "out_dir": str(self.out), "driver_status": execution.get("status"), "driver_error": execution.get("error"),
                "elapsed_s": execution.get("elapsed_s"), "children": len(children), "max_child_elapsed_s": max((c["elapsed_s"] for c in children), default=None),
                "counts": self.count, "expected_counts": expected, "errors": self.errors, "data": self.data,
                "observed_sha256": self.observed, "auditor_sha256": sha(Path(__file__).resolve()),
                "scope": "Retained-file arithmetic/integrity audit, including partial attempts. No geometry/quadrature replay or scientific-module import. A PASS requires all evidence and means agreement accepted under the frozen gates, not a mathematical certificate. An unresolved reference is not accepted agreement. Tracked membership is the declared before/after Git inventory, not a rediscovered index. Current-file hash mismatches do not alone establish mutation during the original run. No physical-accuracy/convergence or optical-error inference."}


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--out", type=Path, required=True); parser.add_argument("--output", type=Path)
    args = parser.parse_args(); out = args.out.resolve()
    output = args.output.resolve() if args.output else out.parent / (out.name + "_postrun_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".json")
    if not out.is_dir() or output.exists() or output.is_relative_to(out) or not output.parent.is_dir(): parser.error("Existing evidence directory and fresh summary outside its tree are required")
    for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS"): os.environ[name] = "1"
    import numpy as np
    audit = Audit(out, np); result = audit.run()
    with output.open("x", encoding="utf-8", newline="\n") as handle: json.dump(result, handle, indent=2, allow_nan=False); handle.write("\n")
    print(f"{result['status']} | driver={result['driver_status']} | children={result['children']}/14 | elapsed={result['elapsed_s']} s | max_child={result['max_child_elapsed_s']} s")
    print("Evidence counts: " + json.dumps(result["counts"])); print("Driver error: " + str(result["driver_error"]))
    for kind, errors in result["errors"].items():
        print(f"{kind}: {len(errors)} findings")
        for error in errors[:12]: print("  " + error)
    print("Fresh summary: " + str(output) + " | SHA256 " + sha(output))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
