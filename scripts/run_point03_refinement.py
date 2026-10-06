"""Frozen eight-case ADI refinement with immutable inputs and bounded checkpoints."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
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
CONTRACT = ROOT / "Docs/POINT-03-Q4-REFINEMENT-CONTRACT.md"
HISTORY = ROOT / "experimentos/glass009d_claude/resultados009d.json"
THREADS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")
PLAN = [(f"n{n}_ss64_z125", n, 64, 1.25e-6, 1600) for n in (256, 320, 400, 500)]
PLAN += [(f"n{n}_ss32_z125", n, 32, 1.25e-6, 1600) for n in (400, 500)]
PLAN += [(f"n{n}_ss64_z0625", n, 64, .625e-6, 3200) for n in (400, 500)]


def stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "_" + uuid.uuid4().hex[:8]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, data):
    with Path(path).open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=2, allow_nan=False)
        handle.write("\n")


def read_json(path):
    def reject(value):
        raise ValueError("Nonfinite JSON value: " + value)
    return json.loads(Path(path).read_text(encoding="utf-8"), parse_constant=reject)


def save_npz(path, np, **arrays):
    with Path(path).open("xb") as handle:
        np.savez_compressed(handle, **arrays)


def sources():
    paths = [CONTRACT, HISTORY, Path(__file__).resolve(), ROOT / "scripts/assess_point03_refinement.py",
             ROOT / "experimentos/glass009_claude/adi2d.py", ROOT / "src/silice/coverage.py",
             ROOT / "src/silice/tracks.py", ROOT / "src/silice/bpm.py"]
    return {str(path.resolve()): sha(path) for path in paths}


def tracked_snapshot():
    """Hash tracked regular files once per attempt boundary, not per chunk."""
    run = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"], shell=False,
                         capture_output=True, timeout=10)
    if run.returncode:
        raise RuntimeError("Git tracked inventory failed: " + run.stderr.decode("utf-8", "replace"))
    snapshot = {}
    for relative in run.stdout.decode("utf-8", "surrogateescape").split("\0"):
        if not relative:
            continue
        path = ROOT / relative
        if not path.exists():
            raise FileNotFoundError("Tracked input is missing: " + relative)
        if path.is_file() and not path.is_symlink():
            snapshot[relative] = sha(path)
    return snapshot


def runtime():
    for name in THREADS:
        os.environ[name] = "1"
    import numpy as np
    import psutil
    sys.path.insert(0, str(ROOT / "src"))
    from silice import coverage, tracks
    for module, relative in ((coverage, "src/silice/coverage.py"), (tracks, "src/silice/tracks.py")):
        if Path(module.__file__).resolve() != (ROOT / relative).resolve():
            raise RuntimeError("Research helper imported from the wrong source checkout.")
    spec = importlib.util.spec_from_file_location("point03_frozen_adi", ROOT / "experimentos/glass009_claude/adi2d.py")
    adi = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adi)  # Definitions only; never import the peer's writer.
    if "torch" in sys.modules or "cupy" in sys.modules:
        raise RuntimeError("A GPU library was imported into the CPU refinement.")
    return np, psutil, coverage, tracks, adi


def guard(psutil, directory, deadline):
    if time.monotonic() >= deadline:
        raise TimeoutError("CPU refinement time budget exhausted.")
    if psutil.virtual_memory().available <= 1.5 * 1024**3:
        raise RuntimeError("More than 1.5 GiB available RAM is required.")
    if shutil.disk_usage(directory).free <= 2 * 1024**3:
        raise RuntimeError("More than 2 GiB free disk is required.")


class AuditGrid:
    """Opt-in contract grid; does not modify the historical CellGrid bounds."""
    def __init__(self, np, n):
        if n not in (256, 320, 400, 500):
            raise ValueError("Grid is outside the frozen Stage B plan.")
        self.np, self.points, self.width_m = np, n, 128e-6
        self.dx_m = self.width_m / n

    def coordinates(self):
        axis = (self.np.arange(self.points) - self.points // 2) * self.dx_m
        return self.np.meshgrid(axis, axis, indexing="xy")


def validate_manifest(path, expected_sha=None):
    path = Path(path).resolve()
    if not path.is_relative_to(RESULTS.resolve()):
        raise ValueError("Manifest is outside own results.")
    digest = sha(path)
    if expected_sha and digest != expected_sha:
        raise ValueError("Manifest identity changed.")
    manifest = read_json(path)
    if manifest.get("schema") != "silice.point03-refinement.manifest.v1":
        raise ValueError("Unknown refinement manifest schema.")
    if manifest["source_sha256"] != sources():
        raise ValueError("A frozen source, contract, assessor, or historical report changed.")
    expected = [(name, n, ss, dz, steps) for name, n, ss, dz, steps in PLAN]
    actual = [(c["case_id"], c["N"], c["profile_samples"], c["dz_m"], c["steps_target"]) for c in manifest["case_plan"]]
    if actual != expected:
        raise ValueError("Case plan differs from the frozen eight cases.")
    pairs = [(item["N"], item["profile_samples"]) for item in manifest["prepared_inputs"]]
    if sorted(pairs) != sorted([(n, 64) for n in (256, 320, 400, 500)] + [(400, 32), (500, 32)]):
        raise ValueError("The six prepared-input groups differ from the contract.")
    for item in manifest["prepared_inputs"]:
        if sha(item["input_npz_path"]) != item["input_npz_sha256"]:
            raise ValueError("Prepared input changed.")
    for case in manifest["case_plan"]:
        if case["width_m"] != 128e-6 or case["dx_m"] != 128e-6 / case["N"]:
            raise ValueError("Case geometry differs from the fixed physical domain.")
        if sha(case["input_npz_path"]) != case["input_npz_sha256"]:
            raise ValueError("Case input identity differs.")
        item = next(p for p in manifest["prepared_inputs"] if (p["N"], p["profile_samples"]) == (case["N"], case["profile_samples"]))
        if (case["input_npz_path"], case["input_npz_sha256"]) != (item["input_npz_path"], item["input_npz_sha256"]):
            raise ValueError("Longitudinal controls must reuse the identical prepared input.")
    return manifest, digest


def prepare(out):
    started = time.monotonic()
    report = {"schema": "silice.point03-refinement.prepare.v1", "status": "running"}
    try:
        np, psutil, coverage, tracks, adi = runtime()
        before = sources()
        report["source_sha256_before"] = before
        guard(psutil, out, started + 35)
        (out / "inputs").mkdir()
        prepared = []
        report["prepared_inputs"] = prepared
        for n, samples in ((256, 64), (320, 64), (400, 64), (500, 64), (400, 32), (500, 32)):
            report["active_prepared_input"] = f"n{n}_ss{samples}"
            guard(psutil, out, started + 35)
            grid = AuditGrid(np, n)
            centres = tracks.track_centres(per_ring=32)
            dn = -.003 * coverage.union_coverage(grid, centres, samples=samples, deadline=started + 35)
            weights = coverage.circle_coverage(grid, 6e-6)
            sigma = adi.sigma_map(n, grid.dx_m, smax=4e4, frac=.2)
            initial = adi.gaussian(n, grid.dx_m, 6e-6)
            path = out / "inputs" / f"n{n}_ss{samples}.npz"
            save_npz(path, np, A0=initial, dn=dn, sigma=sigma, weights=weights)
            prepared.append({"N": n, "profile_samples": samples, "input_npz_path": str(path), "input_npz_sha256": sha(path)})
        cases = []
        for name, n, samples, dz, steps in PLAN:
            item = next(p for p in prepared if p["N"] == n and p["profile_samples"] == samples)
            cases.append(dict(item, case_id=name, width_m=128e-6, dx_m=128e-6 / n,
                              dz_m=dz, steps_target=steps))
        if sources() != before:
            raise ValueError("Source mutation during input preparation.")
        manifest = {"schema": "silice.point03-refinement.manifest.v1", "source_root": str(ROOT.resolve()),
                    "created_utc": datetime.now(timezone.utc).isoformat(), "source_sha256": before,
                    "contract_path": str(CONTRACT), "contract_sha256": sha(CONTRACT),
                    "historical_Q4_path": str(HISTORY), "historical_Q4_sha256": sha(HISTORY),
                    "case_plan": cases, "prepared_inputs": prepared, "total_wall_budget_s": 1800,
                    "preparation_elapsed_s": time.monotonic() - started,
                    "physics": {"wavelength_m": 1550e-9, "n_reference": 1.444, "delta_n": -.003,
                                "waist_m": 6e-6, "core_radius_m": 6e-6, "thickness_m": 6e-6,
                                "track_radius_m": 1.25e-6, "tracks": 96, "smax_per_m": 4e4, "sigma_frac": .2},
                    "environment": {"python": platform.python_version(), "platform": platform.platform(),
                                    "executable": sys.executable, "numpy": np.__version__,
                                    "psutil": importlib.metadata.version("psutil"),
                                    "threads": {name: os.environ[name] for name in THREADS}},
                    "scope": "Scalar paraxial ADI; no fitting, output normalization, or global convergence certification."}
        guard(psutil, out, started + 35)
        write_json(out / "manifest.json", manifest)
        report.update(status="prepared", manifest_path=str(out / "manifest.json"), manifest_sha256=sha(out / "manifest.json"))
    except Exception as error:
        report.update(status="failed", error_type=type(error).__name__, error=str(error))
    report["elapsed_s"] = time.monotonic() - started
    write_json(out / ("preparation_" + stamp() + ".json"), report)
    print(json.dumps(report))
    return 0 if report["status"] == "prepared" else 1


def input_arrays(np, case):
    with np.load(case["input_npz_path"], allow_pickle=False) as archive:
        arrays = {name: archive[name] for name in ("A0", "dn", "sigma", "weights")}
    if any(a.shape != (case["N"], case["N"]) or not np.all(np.isfinite(a)) for a in arrays.values()):
        raise ValueError("Prepared arrays have invalid shapes or values.")
    if arrays["A0"].dtype != np.dtype("complex128"):
        raise ValueError("Initial field is not complex128.")
    if any(arrays[key].dtype != np.dtype("float64") for key in ("dn", "sigma", "weights")):
        raise ValueError("Index, absorber, and detector arrays must be real float64.")
    if not np.all((arrays["dn"] >= -.003) & (arrays["dn"] <= 0)) or np.any(arrays["sigma"] < 0):
        raise ValueError("Prepared profile or absorber is outside the passive fixed model.")
    return arrays


def metrics(np, arrays, field, case):
    if field.shape != (case["N"], case["N"]) or field.dtype != np.dtype("complex128") or not np.all(np.isfinite(field)):
        raise ValueError("Checkpoint field is invalid.")
    dx = case["dx_m"]
    p0 = float((np.abs(arrays["A0"])**2).sum() * dx**2)
    total = float((np.abs(field)**2).sum() * dx**2)
    core = float((arrays["weights"] * np.abs(field)**2).sum() * dx**2 / p0)
    area = float(arrays["weights"].sum() * dx**2)
    if not all(math.isfinite(v) for v in (p0, total, core, area)):
        raise ValueError("Nonfinite field metrics.")
    valid = (abs(p0 - 1) <= 1e-12 and abs(area / (math.pi * (6e-6)**2) - 1) <= 1e-12
             and np.all((arrays["weights"] >= 0) & (arrays["weights"] <= 1))
             and 0 <= core <= total / p0 + 1e-12)
    return dict(input_power=p0, output_power=total, core_power_analytic_input=core,
                P0=p0, P_final=total, P_core=core, core_area_m2=area, numeric_valid=bool(valid))


def latest_checkpoint(case, folder, manifest_sha):
    previous, digest, steps = None, None, 0
    candidates = []
    for path in folder.glob("chunk_*.json"):
        data = read_json(path)
        if data.get("status") != "checkpoint_completed":
            continue  # Explicitly retained failed attempts are never used as states.
        candidates.append((data["steps_done"], path, data))
    for done, path, data in sorted(candidates):
        if (data["case_id"] != case["case_id"] or data["manifest_sha256"] != manifest_sha
                or data["input_npz_sha256"] != case["input_npz_sha256"] or data["steps_start"] != steps
                or data["previous_checkpoint_sha256"] != digest or not steps < done <= min(steps + 200, case["steps_target"])
                or sha(data["final_npz_path"]) != data["final_npz_sha256"]):
            raise ValueError("Checkpoint identity, sequence, or field hash is invalid.")
        previous, digest, steps = path, sha(path), done
    return previous, digest, steps


def worker(args):
    started = time.monotonic()
    report = {"status": "failed", "case_id": args.case_id}
    prefix = args.prefix.resolve()
    try:
        manifest, identity = validate_manifest(args.manifest, args.manifest_sha)
        case = next(c for c in manifest["case_plan"] if c["case_id"] == args.case_id)
        if not prefix.is_relative_to(args.manifest.resolve().parent / "cases" / args.case_id):
            raise ValueError("Worker output is outside its own case directory.")
        np, psutil, _, _, adi = runtime()
        if (manifest["environment"]["numpy"] != np.__version__
                or manifest["environment"]["python"] != platform.python_version()
                or manifest["environment"]["psutil"] != importlib.metadata.version("psutil")):
            raise ValueError("Runtime versions differ from input preparation.")
        guard(psutil, prefix.parent, started + 35)
        arrays = input_arrays(np, case)
        steps = 0
        previous_sha = None
        field = arrays["A0"].copy()
        if args.checkpoint:
            old = read_json(args.checkpoint)
            previous_sha = sha(args.checkpoint)
            if old["manifest_sha256"] != identity or old["case_id"] != args.case_id or old["input_npz_sha256"] != case["input_npz_sha256"]:
                raise ValueError("Worker parent checkpoint identity differs.")
            if sha(old["final_npz_path"]) != old["final_npz_sha256"]:
                raise ValueError("Parent field changed.")
            with np.load(old["final_npz_path"], allow_pickle=False) as archive:
                field = archive["field"]
            steps = old["steps_done"]
        measured = metrics(np, arrays, field, case)
        if not measured["numeric_valid"] or not 0 <= steps < case["steps_target"]:
            raise ValueError("Invalid starting state or completed case passed to worker.")
        stepper = adi.Stepper(arrays["dn"], arrays["sigma"], case["dx_m"], case["dz_m"])
        initial_step = steps
        propagation_start = time.monotonic()
        while steps < min(initial_step + 200, case["steps_target"]) and time.monotonic() < started + 31:
            guard(psutil, prefix.parent, started + 35)
            field = stepper.step(field)
            steps += 1
        if steps == initial_step:
            raise TimeoutError("No progress before the checkpoint deadline.")
        propagation_s = time.monotonic() - propagation_start
        npz = Path(str(prefix) + ".npz")
        save_npz(npz, np, field=field)  # Retain the field even if a subsequent numeric guard fails.
        report.update(steps_start=initial_step, steps_done=steps, manifest_sha256=identity,
                      final_npz_path=str(npz), final_npz_sha256=sha(npz))
        measured = metrics(np, arrays, field, case)
        if steps == case["steps_target"]:
            measured["numeric_valid"] = measured["numeric_valid"] and measured["output_power"] <= 1.001
        if not measured["numeric_valid"]:
            report.update(measured)
            raise ValueError("Checkpoint violates frozen numerical invariants.")
        guard(psutil, prefix.parent, started + 35)
        validate_manifest(args.manifest, identity)
        guard(psutil, prefix.parent, started + 35)
        memory = psutil.Process().memory_info()
        report = dict(case, **measured, schema="silice.point03-refinement.checkpoint.v1", status="checkpoint_completed",
                      steps_start=initial_step, steps_done=steps, steps_completed=steps,
                      manifest_sha256=identity, previous_checkpoint_sha256=previous_sha,
                      previous_checkpoint_path=str(args.checkpoint) if args.checkpoint else None,
                      final_npz_path=str(npz), final_npz_sha256=sha(npz), gpu_used=False, dtype="complex128",
                      sources_unchanged=True, input_unchanged=True,
                      propagation_s=propagation_s, rss_current_bytes=memory.rss,
                      peak_wset_bytes=getattr(memory, "peak_wset", None),
                      memory_scope="Windows peak working set if available; otherwise RSS is a current sample, not a peak.")
    except Exception as error:
        report.update(status="failed", error_type=type(error).__name__, error=str(error))
    report["elapsed_s"] = time.monotonic() - started
    write_json(Path(str(prefix) + ".json"), report)
    print(json.dumps({"status": report["status"], "report": str(prefix) + ".json"}))
    return 0 if report["status"] == "checkpoint_completed" else 1


def execute(args):
    started = time.monotonic()
    out = args.manifest.resolve().parent
    attempt = stamp()
    report = {"schema": "silice.point03-refinement.execution.v1", "status": "running", "operational_pass": False,
              "manifest_path": str(args.manifest.resolve()), "case_reports": [], "children": [], "attempt_id": attempt}
    marker = out / ("attempt_" + attempt + ".json")
    write_json(marker, {"schema": "silice.point03-refinement.attempt.v1", "attempt_id": attempt,
                        "manifest_path": str(args.manifest.resolve()), "started_utc": datetime.now(timezone.utc).isoformat(),
                        "pid": os.getpid(), "cost_state": "Unknown until the matching execution report is complete."})
    report["attempt_marker_path"] = str(marker)
    report["attempt_marker_sha256"] = sha(marker)
    try:
        orphaned = [str(path) for path in out.glob("attempt_*.json") if path != marker
                    and not (out / path.name.replace("attempt_", "execution_", 1)).exists()]
        if orphaned:
            report["unclosed_attempts"] = orphaned
            raise RuntimeError("Prior attempt cost is unknown after a hard interruption; explicit recovery is required before any propagation. The 1800 s budget is not reset.")
        report["tracked_sha256_before"] = tracked_snapshot()
        manifest, identity = validate_manifest(args.manifest)
        report["manifest_sha256"] = identity
        report["source_sha256_before"] = sources()
        np, psutil, _, _, _ = runtime()
        prior = sum(read_json(p)["elapsed_s"] for p in out.glob("execution_*.json"))
        report["prior_attempt_elapsed_s"] = prior
        deadline = started + 1800 - prior - manifest["preparation_elapsed_s"]
        guard(psutil, out, deadline)
        for case in manifest["case_plan"]:
            folder = out / "cases" / case["case_id"]
            folder.mkdir(parents=True, exist_ok=True)
            final = folder / "case.json"
            if not args.resume and (final.exists() or any(folder.glob("chunk_*"))):
                raise ValueError("Existing case evidence requires --resume; nothing will be overwritten.")
            if final.exists():
                old = read_json(final)
                if (old["status"] != "completed" or old["manifest_sha256"] != identity or old["case_id"] != case["case_id"]
                        or old["input_npz_sha256"] != case["input_npz_sha256"] or sha(old["final_npz_path"]) != old["final_npz_sha256"]):
                    raise ValueError("Completed case cannot be verified for reuse.")
                if any(old[key] != value for key, value in case.items()) or old["steps_done"] != case["steps_target"]:
                    raise ValueError("Completed case parameters or step count differ from the plan.")
                latest, latest_sha, done = latest_checkpoint(case, folder, identity)
                if (done != case["steps_target"] or latest is None
                        or str(latest) != old["last_checkpoint_path"] or latest_sha != old["last_checkpoint_sha256"]):
                    raise ValueError("Completed case's final checkpoint pointer or chain is invalid.")
                checkpoint = read_json(latest)
                if (checkpoint["final_npz_path"] != old["final_npz_path"]
                        or checkpoint["final_npz_sha256"] != old["final_npz_sha256"]):
                    raise ValueError("Final case field differs from the verified checkpoint chain.")
                with np.load(old["final_npz_path"], allow_pickle=False) as archive:
                    measured = metrics(np, input_arrays(np, case), archive["field"], case)
                if (not old["numeric_valid"] or not measured["numeric_valid"] or measured["output_power"] > 1.001
                        or any(abs(measured[key] - old[key]) > 1e-12 for key in ("input_power", "output_power", "core_power_analytic_input"))):
                    raise ValueError("Completed case's retained field no longer validates its numeric report.")
            else:
                while True:
                    previous, previous_sha, steps = latest_checkpoint(case, folder, identity)
                    if steps == case["steps_target"]:
                        data = read_json(previous)
                        data.update(schema="silice.point03-refinement.case.v1", status="completed", numeric_pass=data["numeric_valid"],
                                    last_checkpoint_path=str(previous), last_checkpoint_sha256=previous_sha)
                        write_json(final, data)  # Parent commits one final case report, exactly once.
                        break
                    guard(psutil, out, deadline)
                    if deadline - time.monotonic() < 40:
                        raise TimeoutError("Insufficient total wall budget to launch another bounded child.")
                    prefix = folder / ("chunk_" + stamp())
                    command = [sys.executable, "-B", "-u", str(Path(__file__).resolve()), "--worker",
                               "--manifest", str(args.manifest.resolve()), "--manifest-sha", identity,
                               "--case-id", case["case_id"], "--prefix", str(prefix)]
                    if previous:
                        command += ["--checkpoint", str(previous)]
                    child_started = time.monotonic()
                    child = {"case_id": case["case_id"], "steps_start": steps, "command": command}
                    try:
                        run = subprocess.run(command, cwd=ROOT, shell=False, capture_output=True, text=True,
                                             encoding="utf-8", errors="replace", timeout=40)
                        stdout, stderr = run.stdout, run.stderr
                        child["returncode"] = run.returncode
                    except subprocess.TimeoutExpired as error:
                        def decoded(value):
                            return value.decode("utf-8", "replace") if isinstance(value, bytes) else value or ""
                        stdout, stderr = decoded(error.stdout), decoded(error.stderr)
                        child.update(returncode=None, timed_out=True)
                    except OSError as error:
                        stdout, stderr = "", f"{type(error).__name__}: {error}"
                        child.update(returncode=None, launch_error=stderr)
                    except KeyboardInterrupt:
                        stdout, stderr = "", "Interrupted during subprocess.run; the library terminates its own child. Partial captured output may be unavailable."
                        child.update(returncode=None, interrupted=True)
                    child["elapsed_s"] = time.monotonic() - child_started
                    for label, text in (("stdout", stdout), ("stderr", stderr)):
                        path = Path(str(prefix) + "." + label + ".log")
                        with path.open("x", encoding="utf-8", newline="\n") as handle:
                            handle.write(text)
                        child[label + "_path"] = str(path)
                    report["children"].append(child)
                    if child["returncode"] != 0:
                        if child.get("interrupted"):
                            raise KeyboardInterrupt("Worker launch interrupted; evidence and elapsed attempt cost are retained.")
                        raise RuntimeError("Child failed operationally; its outputs and logs are retained for --resume.")
                    validate_manifest(args.manifest, identity)
                    completed_chunk = read_json(Path(str(prefix) + ".json"))
                    print(json.dumps({"progress": "chunk", "case_id": case["case_id"],
                                      "steps_done": completed_chunk["steps_done"], "steps_target": case["steps_target"],
                                      "elapsed_s": child["elapsed_s"]}), flush=True)
            report["case_reports"].append({"case_id": case["case_id"], "path": str(final), "sha256": sha(final)})
            completed_case = read_json(final)
            print(json.dumps({"progress": "case_completed", "case_id": case["case_id"],
                              "steps_done": completed_case["steps_done"],
                              "P_core": completed_case["core_power_analytic_input"]}), flush=True)
        validate_manifest(args.manifest, identity)
        report.update(status="completed", operational_pass=len(report["case_reports"]) == 8)
    except (Exception, KeyboardInterrupt) as error:
        report.update(status="failed", error_type=type(error).__name__, error=str(error))
    try:
        report["source_sha256_after"] = sources()
        report["sources_unchanged"] = report.get("source_sha256_before") == report["source_sha256_after"]
        if not report["sources_unchanged"]:
            report.update(status="failed", operational_pass=False, integrity_error="Frozen sources changed.")
    except Exception as error:
        report.update(status="failed", operational_pass=False, integrity_error=str(error))
    try:
        report["tracked_sha256_after"] = tracked_snapshot()
        before = report.get("tracked_sha256_before", {})
        after = report["tracked_sha256_after"]
        report["tracked_inputs_unchanged"] = report.get("tracked_sha256_before") == after
        report["tracked_changed_paths"] = sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
        if not report["tracked_inputs_unchanged"]:
            report.update(status="failed", operational_pass=False, tracked_integrity_error="Tracked inputs changed during execution.")
    except Exception as error:
        report.update(status="failed", operational_pass=False, tracked_integrity_error=f"{type(error).__name__}: {error}")
    report["elapsed_s"] = time.monotonic() - started
    write_json(out / ("execution_" + attempt + ".json"), report)
    print(json.dumps({"status": report["status"], "operational_pass": report["operational_pass"],
                      "report": str(out / ("execution_" + attempt + ".json"))}))
    return 0 if report["operational_pass"] else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    for mode in ("prepare", "run", "resume", "worker"):
        modes.add_argument("--" + mode, action="store_true")
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--manifest-sha")
    parser.add_argument("--case-id")
    parser.add_argument("--prefix", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    args = parser.parse_args()
    if args.prepare:
        out = args.out_dir.resolve() if args.out_dir else RESULTS.resolve() / ("point03_refinement_" + stamp())
        if not out.is_relative_to(RESULTS.resolve()) or out.exists():
            parser.error("A fresh output directory under resultados/codex is required.")
        out.mkdir(parents=True, exist_ok=False)
        return prepare(out)
    if not args.manifest or not args.manifest.is_file():
        parser.error("An existing prepared --manifest is required.")
    if not args.manifest.resolve().is_relative_to(RESULTS.resolve()):
        parser.error("Manifest must remain under resultados/codex.")
    if args.worker:
        if not args.case_id or not args.prefix or not args.manifest_sha:
            parser.error("Private worker requires case identity, prefix, and frozen manifest SHA.")
        return worker(args)
    return execute(args)


if __name__ == "__main__":
    raise SystemExit(main())
