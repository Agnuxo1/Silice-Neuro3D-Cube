"""Local execution record for the Point 03 Stage B preparation, no propagation."""
from pathlib import Path
from datetime import datetime, timezone
import ast
import hashlib
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
import sys
import time

ROOT = Path(r"D:\PROJECTS\Silice-Neuro3D-Cube-work-20261006")
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
OUT = ROOT / "resultados/codex" / ("point03_preflight_" + STAMP)
OUT.mkdir(parents=True, exist_ok=False)
REFINEMENT = ROOT / "resultados/codex" / ("point03_refinement_" + STAMP)
START = time.monotonic()
REPORT = {"schema": "silice.point03-preflight.v1", "status": "running", "children": [], "propagations": 0}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, check=True, timeout=30)


def run(label, arguments):
    command = [sys.executable, "-B", "-u", *map(str, arguments)]
    begin = time.monotonic()
    child = {"label": label, "command": command}
    try:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=40)
        child["returncode"] = result.returncode
        stdout, stderr = result.stdout, result.stderr
    except subprocess.TimeoutExpired as error:
        child.update(returncode=None, timed_out=True)
        stdout, stderr = error.stdout or b"", error.stderr or b""
    for name, raw in (("stdout", stdout), ("stderr", stderr)):
        path = OUT / (label + "." + name + ".log")
        with path.open("xb") as handle:
            handle.write(raw)
        child[name + "_path"] = str(path)
        child[name + "_sha256"] = sha(path)
    child["elapsed_s"] = time.monotonic() - begin
    REPORT["children"].append(child)
    if child["returncode"] != 0:
        raise RuntimeError(label + " failed; retained logs identify the reason.")


try:
    for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS"):
        os.environ[name] = "1"
    import numpy as np
    import psutil
    assert Path(sys.executable).resolve() == (ROOT / ".venv/Scripts/python.exe").resolve()
    assert Path(sys.prefix).resolve() == (ROOT / ".venv").resolve()
    assert platform.python_version() == "3.13.7"
    versions = {name: importlib.metadata.version(name) for name in ("numpy", "scipy", "psutil")}
    assert versions == {"numpy": "2.2.6", "scipy": "1.15.1", "psutil": "6.1.1"}
    assert Path(np.__file__).resolve().is_relative_to((ROOT / ".venv").resolve())
    assert "torch" not in sys.modules and "cupy" not in sys.modules
    assert psutil.virtual_memory().available > 1.5 * 1024**3
    assert shutil.disk_usage(ROOT).free > 2 * 1024**3
    REPORT["environment"] = dict(versions, python=platform.python_version(), executable=sys.executable,
                                 prefix=sys.prefix, numpy_file=np.__file__, platform=platform.platform())
    REPORT["available_ram_before_bytes"] = psutil.virtual_memory().available
    assert git("branch", "--show-current").stdout.decode().strip() == "codex/scientific-closure-20261006"
    assert not git("diff", "--cached", "--name-only").stdout.strip(), "Unexpected staged files."
    targets = ["scripts/run_point03_refinement.py", "scripts/assess_point03_refinement.py",
               "Docs/POINT-03-Q4-REFINEMENT-CONTRACT.md"]
    for name in targets[:2]:
        ast.parse((ROOT / name).read_text(encoding="utf-8"))
    git("add", "--", *targets)
    git("diff", "--cached", "--check")
    commit = git("commit", "-m", "Implement bounded Point 03 refinement and independent acceptance checks")
    (OUT / "source_commit.log").write_bytes(commit.stdout + commit.stderr)
    REPORT["source_commit"] = git("rev-parse", "HEAD").stdout.decode().strip()
    REPORT["source_sha256"] = {name: sha(ROOT / name) for name in targets}
    assert not git("diff", "--name-only").stdout.strip(), "Unexpected tracked working changes."
    detector_report = ROOT / "resultados/codex/point03_detector_20261006T215200970875Z/summary.json"
    detector = json.loads(detector_report.read_text(encoding="utf-8"))
    REPORT["historical_array_current_hashes"] = {}
    for row in detector["records"]:
        digest = sha(row["source"])
        assert digest == row["sha256"], row["source"]
        REPORT["historical_array_current_hashes"][row["source"]] = digest
    run("assessor_self_check", [ROOT / targets[1], "--self-check", "--out", OUT / "assessor_self_check.json"])
    checks = json.loads((OUT / "assessor_self_check.json").read_text(encoding="utf-8"))
    assert checks["self_check_pass"] and checks["checks_count"] == 6
    run("regression_suite", [ROOT / "scripts/check.py", "--report", OUT / "regression_suite.json"])
    run("prepare_inputs", [ROOT / targets[0], "--prepare", "--out-dir", REFINEMENT])
    manifest_path = REFINEMENT / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert len(manifest["prepared_inputs"]) == 6 and len(manifest["case_plan"]) == 8
    summaries = []
    for item in manifest["prepared_inputs"]:
        assert sha(item["input_npz_path"]) == item["input_npz_sha256"]
        n = item["N"]
        dx = 128e-6 / n
        with np.load(item["input_npz_path"], allow_pickle=False) as archive:
            initial, dn, sigma, weights = [archive[name] for name in ("A0", "dn", "sigma", "weights")]
        assert all(a.shape == (n,n) and np.isfinite(a).all() for a in (initial,dn,sigma,weights))
        p0 = float(np.sum(abs(initial)**2) * dx**2)
        area_relative_error = abs(float(np.sum(weights) * dx**2) / (np.pi * (6e-6)**2) - 1)
        assert abs(p0 - 1) <= 1e-12 and area_relative_error <= 1e-12
        assert np.min(dn) >= -.003 and np.max(dn) == 0 and np.min(sigma) >= 0
        summaries.append(dict(item, input_power=p0, detector_area_relative_error=area_relative_error,
                              modified_area_m2=float(np.sum(-dn/.003)*dx**2), maximum_sigma=float(np.max(sigma))))
    REPORT.update(status="passed", prepared_inputs=summaries, manifest_path=str(manifest_path),
                  manifest_sha256=sha(manifest_path), available_ram_after_bytes=psutil.virtual_memory().available,
                  gpu_initialized=False)
except Exception as error:
    REPORT.update(status="failed", error_type=type(error).__name__, error=str(error))
REPORT["elapsed_s"] = time.monotonic() - START
script_copy = OUT / "preflight_orchestrator.py"
script_copy.write_bytes(Path(__file__).read_bytes())
REPORT["orchestrator_sha256"] = sha(script_copy)
report_path = OUT / "preflight.json"
with report_path.open("x", encoding="utf-8", newline="\n") as handle:
    json.dump(REPORT, handle, indent=2, allow_nan=False)
    handle.write("\n")
print(json.dumps({"status": REPORT["status"], "report": str(report_path),
                  "source_commit": REPORT.get("source_commit"), "manifest": REPORT.get("manifest_path"),
                  "error": REPORT.get("error"), "elapsed_s": REPORT["elapsed_s"]}))
raise SystemExit(0 if REPORT["status"] == "passed" else 1)
