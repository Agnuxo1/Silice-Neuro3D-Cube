"""Read-only detector diagnosis on six archived ADI fields; no propagation."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
THREADS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")
TARGETS = {"Cd": (.36341858760421314, .36308954401493865, .3631821542545893),
           "T96d": (.33263167400842963, .33223675582032003, .33267434735736884)}
GRIDS = (("6", 205, .625 * 1e-6, "P_dx0p625"), ("5", 256, .5 * 1e-6, "P_dx0p5"),
         ("4", 320, .4 * 1e-6, "P_dx0p4"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(paths):
    return {str(path): sha(path) for path in paths}


def tracked(deadline):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("Total 40 s audit deadline reached during source inventory.")
    run = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"], shell=False,
                         capture_output=True, timeout=min(10, remaining))
    if run.returncode:
        raise RuntimeError("Git inventory failed: " + run.stderr.decode("utf-8", "replace"))
    return inventory([ROOT / name for name in run.stdout.decode("utf-8", "surrogateescape").split("\0") if name])


def guard(deadline, psutil):
    if time.monotonic() >= deadline:
        raise TimeoutError("Total 40 s audit deadline reached.")
    available = psutil.virtual_memory().available
    if available <= 1.5 * 1024**3:
        raise RuntimeError("Detector audit requires more than 1.5 GiB available RAM.")
    return available


def midpoint_weights(np, n, dx, samples, deadline):
    """Legacy strict-radius midpoint detector; allocate only the circle ROI."""
    if time.monotonic() >= deadline:
        raise TimeoutError("Detector construction deadline reached.")
    axis = (np.arange(n) - n // 2) * dx
    indices = np.flatnonzero(np.abs(axis) <= 6e-6 + dx)
    offsets = (np.arange(samples) + .5) / samples - .5
    fine = (axis[indices, None] + offsets * dx).reshape(-1)
    occupied = fine[:, None]**2 + fine[None, :]**2 < (6e-6)**2
    small = occupied.reshape(len(indices), samples, len(indices), samples).sum(axis=(1, 3)) / samples**2
    weights = np.zeros((n, n), dtype=np.float64)
    weights[np.ix_(indices, indices)] = small
    return weights


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-main", type=Path, default=Path("D:/PROJECTS/Silice-Neuro3D-Cube"))
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--contract", type=Path, default=ROOT / "Docs/POINT-03-DETECTOR-AUDIT-CONTRACT.md")
    args = parser.parse_args()
    started = time.monotonic()
    deadline = started + 40
    parent = (ROOT / "resultados/codex").resolve()
    default_out = parent / ("point03_detector_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
    out = args.out_dir.resolve() if args.out_dir else default_out
    invalid_out = not out.is_relative_to(parent) or out.exists()
    if invalid_out:
        out = default_out  # Preserve a failure report without touching the rejected destination.
    out.mkdir(parents=True, exist_ok=False)
    report = {"schema": "silice.point03-detector.v1", "status": "running", "records": [], "diagnostics": {},
              "scope": "Same saved fields, detector quadrature only; no propagation, fitting, or normalization.",
              "provenance_limit": "Current hashes identify files available now; they do not retroactively authenticate historical execution.",
              "input_power": 1.0, "gates": {name: False for name in ("D1", "D2", "D3", "D4", "D5")},
              "started_utc": datetime.now(timezone.utc).isoformat(), "output_directory": str(out)}
    inputs = []
    sources = []
    try:
        if invalid_out:
            raise ValueError("Requested output already exists or lies outside resultados/codex; fresh failure report retained.")
        for name in THREADS:
            os.environ[name] = "1"
        import numpy as np
        import psutil
        sys.path.insert(0, str(ROOT / "src"))
        from silice.coverage import CellGrid, circle_coverage
        if Path(circle_coverage.__code__.co_filename).resolve() != (ROOT / "src/silice/coverage.py").resolve():
            raise RuntimeError("Analytic detector was not imported from the frozen source checkout.")
        legacy_path = args.source_main.resolve() / "experimentos/glass009d_claude/resultados009d.json"
        sources = [Path(__file__).resolve(), args.contract.resolve(), legacy_path,
                   ROOT / "src/silice/coverage.py", ROOT / "src/silice/tracks.py", ROOT / "src/silice/bpm.py"]
        inputs = [args.source_main.resolve() / "experimentos/glass009d_claude/out" / f"state_{kind}_dx{tag}.npy"
                  for kind in TARGETS for tag, _, _, _ in GRIDS]
        report["tracked_sha256_before"] = tracked(deadline)
        report["source_sha256_before"] = inventory(sources)
        report["input_sha256_before"] = inventory(inputs)
        report["host"] = {"platform": platform.platform(), "python": platform.python_version(), "executable": sys.executable,
                          "packages": {name: importlib.metadata.version(name) for name in ("numpy", "psutil")},
                          "threads": {name: os.environ[name] for name in THREADS}}
        report["available_ram_before_bytes"] = guard(deadline, psutil)
        legacy = json.loads(legacy_path.read_text(encoding="utf-8"))
        for kind, targets in TARGETS.items():
            for index, (tag, n, dx, legacy_key) in enumerate(GRIDS):
                report["active_input"] = f"state_{kind}_dx{tag}.npy"
                guard(deadline, psutil)
                if legacy[kind][legacy_key] != targets[index]:
                    raise ValueError("Retained legacy target differs from the frozen contract.")
                original = args.source_main.resolve() / "experimentos/glass009d_claude/out" / report["active_input"]
                copied = out / original.name
                payload = original.read_bytes()
                if hashlib.sha256(payload).hexdigest() != report["input_sha256_before"][str(original)]:
                    raise ValueError("Original input changed before its byte copy.")
                with copied.open("xb") as handle:
                    handle.write(payload)
                field = np.load(copied, allow_pickle=False)
                if field.shape != (n, n) or field.dtype != np.dtype("complex128") or not np.all(np.isfinite(field)):
                    raise ValueError("Archived array has invalid shape, dtype, or nonfinite values.")
                total = float((np.abs(field)**2).sum() * dx * dx)
                if not math.isfinite(total) or total <= 0:
                    raise ValueError("Archived array has nonfinite or zero total field power.")
                row = {"kind": kind, "N": n, "dx_m": dx, "width_m": n * dx, "source": str(original),
                       "byte_copy": str(copied), "sha256": sha(copied), "total_power": total, "detectors": {}}
                report["records"].append(row)
                for detector in ("SSR16", "SSR32", "SSR64", "analytic"):
                    guard(deadline, psutil)
                    weights = (circle_coverage(CellGrid(n, n * dx), 6e-6) if detector == "analytic"
                               else midpoint_weights(np, n, dx, int(detector[3:]), deadline))
                    power = float((weights * np.abs(field)**2).sum() * dx * dx)
                    area_error = float(weights.sum() * dx * dx / (math.pi * (6e-6)**2) - 1)
                    if not math.isfinite(power) or not math.isfinite(area_error):
                        raise ValueError("Detector produced nonfinite measurements.")
                    row["detectors"][detector] = {"power": power, "area_relative_error_signed": area_error,
                                                   "area_relative_error": abs(area_error),
                                                   "passivity_pass": 0 <= power <= total + 1e-12}
                row["legacy_target"] = targets[index]
                row["legacy_absolute_error"] = abs(row["detectors"]["SSR16"]["power"] - targets[index])
                row["historical_interpretation_eligible"] = row["legacy_absolute_error"] <= 1e-12
        for kind in TARGETS:
            rows = [row for row in report["records"] if row["kind"] == kind]
            report["diagnostics"][kind] = {}
            for detector in ("SSR16", "SSR32", "SSR64", "analytic"):
                powers = [row["detectors"][detector]["power"] for row in rows]
                signed = [powers[1] - powers[0], powers[2] - powers[1]]
                report["diagnostics"][kind][detector] = {"powers_coarse_to_fine": powers,
                    "signed_successive_differences": signed, "absolute_successive_differences": list(map(abs, signed)),
                    "historical_interpretation_eligible": all(row["historical_interpretation_eligible"] for row in rows),
                    "Q4_monotone_diagnostic": abs(signed[0]) >= abs(signed[1])}
        report["gates"]["D2"] = all(row["legacy_absolute_error"] <= 1e-12 for row in report["records"])
        report["gates"]["D3"] = all(row["detectors"]["analytic"]["area_relative_error"] <= 1e-12
            and all(value["passivity_pass"] for value in row["detectors"].values()) for row in report["records"])
        report["gates"]["D4"] = len(report["diagnostics"]) == 2 and all(len(d) == 4 for d in report["diagnostics"].values())
        report["available_ram_after_bytes"] = guard(deadline, psutil)
        report["gpu_initialized"] = "torch" in sys.modules or "cupy" in sys.modules
        if report["gpu_initialized"]:
            raise RuntimeError("GPU library imported into a CPU-only diagnosis.")
        report["status"] = "completed"
    except Exception as error:
        report.update(status="failed", error_type=type(error).__name__, error=str(error))
    finally:
        try:
            report["input_sha256_after"] = inventory(inputs)
            report["source_sha256_after"] = inventory(sources)
            report["tracked_sha256_after"] = tracked(deadline)
            unchanged = (report.get("tracked_sha256_before") == report["tracked_sha256_after"]
                         and report.get("source_sha256_before") == report["source_sha256_after"])
            copies = all(Path(row["byte_copy"]).is_file() and sha(Path(row["byte_copy"])) == row["sha256"]
                         == report["input_sha256_before"][row["source"]] for row in report["records"])
            report["gates"]["D1"] = len(report["records"]) == 6 and copies and report.get("input_sha256_before") == report["input_sha256_after"]
            report["gates"]["D5"] = unchanged and time.monotonic() < deadline and report.get("gpu_initialized") is False
        except Exception as error:
            report["integrity_error"] = f"{type(error).__name__}: {error}"
        report["elapsed_s"] = time.monotonic() - started
        report["scope_limits"] = {"historical_Q4_failure_erased": False, "global_convergence_certified": False,
                                  "cause_isolated": False, "independent_propagation_performed": False}
        report["status"] = "passed" if report["status"] == "completed" and all(report["gates"].values()) else "failed"
        with (out / "summary.json").open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(report, handle, indent=2, allow_nan=False)
            handle.write("\n")
    print(json.dumps({"status": report["status"], "gates": report["gates"], "report": str(out / "summary.json")}))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
