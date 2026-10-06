"""Verify the pinned CPU environment and retain expected scientific failures."""
from __future__ import annotations

import argparse
import ast
import contextlib
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import io
import json
import math
import os
from pathlib import Path
import platform
import struct
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {"numpy": "2.2.6", "scipy": "1.15.1", "psutil": "6.1.1",
            "setuptools": "82.0.1", "pip": "25.3", "wheel": "0.45.1"}
THREAD_NAMES = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write("\n")


def cpu_environment() -> dict[str, str]:
    result = os.environ.copy()
    result.update({name: "1" for name in THREAD_NAMES})
    result.update(PYTHONDONTWRITEBYTECODE="1", PIP_DISABLE_PIP_VERSION_CHECK="1")
    result.pop("PYTHONPATH", None)
    result.pop("PYTHONHOME", None)
    return result


def capture(command: list[str], label: str, report_dir: Path, timeout: int = 40) -> dict:
    started = time.monotonic()
    result = {"command": command, "cwd": str(ROOT), "timeout_s": timeout}
    try:
        run = subprocess.run(command, cwd=ROOT, env=cpu_environment(), shell=False,
                             capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=timeout)
        result.update(returncode=run.returncode, stdout=run.stdout, stderr=run.stderr,
                      timed_out=False)
    except subprocess.TimeoutExpired as error:
        def decoded(value):
            return value.decode("utf-8", "replace") if isinstance(value, bytes) else value or ""
        result.update(returncode=None, stdout=decoded(error.stdout), stderr=decoded(error.stderr),
                      timed_out=True, error="Process exceeded its time budget.")
    except OSError as error:
        result.update(returncode=None, stdout="", stderr="", timed_out=False,
                      error=f"{type(error).__name__}: {error}")
    result["elapsed_s"] = time.monotonic() - started
    for stream in ("stdout", "stderr"):
        path = report_dir / f"{label}.{stream}.log"
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(result[stream])
        result[f"{stream}_path"] = str(path)
    return result


def git_bytes(arguments: list[str]) -> bytes:
    run = subprocess.run(["git", "-C", str(ROOT), *arguments], shell=False,
                         capture_output=True, timeout=40)
    if run.returncode:
        raise RuntimeError("Git source inventory failed: " + run.stderr.decode("utf-8", "replace"))
    return run.stdout


def tracked_hashes() -> dict[str, str]:
    names = git_bytes(["ls-files", "-z"]).decode("utf-8", "surrogateescape").split("\0")
    result = {}
    for relative in names:
        if not relative:
            continue
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError("Tracked input is missing: " + relative)
        result[relative] = digest(path)
    return result


def strict_json(path: Path) -> dict:
    def reject(value):
        raise ValueError("Nonfinite JSON constant: " + value)
    value = json.loads(path.read_text(encoding="utf-8"), parse_constant=reject)
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object: " + str(path))
    return value


def stdout_json(result: dict) -> dict:
    lines = [line for line in result["stdout"].splitlines() if line.strip()]
    if not lines:
        raise ValueError("The process produced no JSON summary.")
    data = json.loads(lines[-1])
    if not isinstance(data, dict):
        raise ValueError("The stdout summary is not an object.")
    return data


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def check_suite(result: dict, output: Path, expected: int) -> dict:
    data = strict_json(output)
    methods = sum(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                  and node.name.startswith("test_")
                  for path in (ROOT / "tests").glob("test_*.py")
                  for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"), str(path))))
    require(data.get("schema") == "silice.cpu-tests.v1", "Unexpected test report schema.")
    require(result["returncode"] == 0 and not result["timed_out"], "CPU unit-test process failed.")
    require(data.get("tests_run") == expected and data.get("tests_expected") == expected
            and methods == expected, "The test count does not match the frozen environment contract.")
    require(data.get("successful") is True and data.get("failures") == []
            and data.get("errors") == [] and data.get("skipped") == [],
            "Tests failed, could not be collected, or were skipped.")
    require(data.get("gpu_initialized") is False, "The suite did not certify its CPU-only invariant.")
    require(Path(data.get("source_root", "")).resolve() == ROOT.resolve(), "Test source root differs.")
    return {"tests_run": expected, "test_methods_in_source": methods, "skipped": 0,
            "gpu_initialized": False, "report": str(output), "report_sha256": digest(output)}


def check_cmt(result: dict, output: Path) -> dict:
    data = strict_json(output)
    require(result["returncode"] == 0 and not result["timed_out"], "CMT audit process failed.")
    require(data.get("experiment") == "GLASS-004-v1" and data.get("gpu_used") is False,
            "CMT report has an unexpected identity or backend scope.")
    require(data.get("peer_unchanged") is True
            and bool(data.get("source_hashes_before"))
            and data.get("source_hashes_before") == data.get("source_hashes_after"),
            "CMT peer inputs changed.")
    require(data.get("gate_nominal") is True and data.get("gate_controls") is True,
            "CMT nominal or negative controls failed.")
    require(data["nominal_bright_relative"] < 1e-4
            and data["independent_vs_cmt_max_field"] < 1e-12
            and set(data["controls"]) == {"phase_pi", "coupler_off"}
            and all(value > .1 for value in data["controls"].values()),
            "CMT saved gates disagree with their measured values.")
    require(math.isclose(data["loss_power"], data["loss_expected"], abs_tol=1e-12, rel_tol=1e-12),
            "CMT loss control differs from expected power attenuation.")
    return {"status": "completed_pass", "report": str(output), "report_sha256": digest(output),
            "scope": "Ideal CMT and hypothetical seeded noise; no fabrication certification."}


def check_historical_v2(result: dict) -> dict:
    require(result["returncode"] == 0 and not result["timed_out"], "Historical V2 audit failed.")
    data = stdout_json(result)
    require(data.get("cases") == 13 and data.get("reused") == 4 and data.get("new_children") == 9,
            "Historical V2 lineage differs from the retained experiment.")
    require(data.get("own_gates_pass") is True and data.get("peer_Q4") == {"Cd": True, "T96d": False},
            "Historical V2 gates or retained Q4 failure changed.")
    path = ROOT / "resultados/codex/glass007_v2_run3.json"
    require(data.get("summary_sha256") == digest(path), "Historical V2 report identity differs.")
    raw = strict_json(path)
    require(raw.get("boundary_validated") is False and raw.get("combined_convergence_certified") is False,
            "Historical report claims unsupported boundary/global convergence.")
    require(data.get("scope") == "saved gates/lineage only; no full-boundary or physical-fabrication validation",
            "Historical auditor scope changed.")
    return data


def check_expected_bpm_failure(result: dict, output: Path) -> dict:
    data = strict_json(output)
    require(result["returncode"] == 2 and not result["timed_out"],
            "Expected scientific FAIL requires return code 2, not an operational failure.")
    require(data.get("experiment") == "GLASS-003-v2" and data.get("gpu_used") is False,
            "Unexpected BPM experiment identity.")
    cases = data.get("cases", [])
    contrasts = (-.001, -.003, -.005)
    names = ("nominal", "domain144", "domain192", "dz", "dx")
    expected_keys = {(contrast, name) for contrast in contrasts for name in names}
    actual_keys = [(case.get("delta_n"), case.get("name")) for case in cases]
    require(len(cases) == 15 and len(set(actual_keys)) == 15 and set(actual_keys) == expected_keys,
            "BPM report is incomplete or contains unexpected cases.")
    indexed = dict(zip(actual_keys, cases))
    for case in cases:
        require(case.get("backend") == "scalar_paraxial_cpu_ssfm", "Unexpected BPM backend.")
        require(case.get("status", "completed") in ("completed", "success"), "BPM case failed operationally.")
        numeric = ("input_power", "output_power", "material_removed", "boundary_removed",
                   "balance_relative", "core_power_fraction_input", "dx_m", "dz_m")
        require(all(isinstance(case.get(key), (int, float)) and not isinstance(case[key], bool)
                    and math.isfinite(case[key]) for key in numeric), "Invalid BPM numeric row.")
        require(case["input_power"] > 0 and case["output_power"] >= 0
                and case["dx_m"] > 0 and case["dz_m"] > 0, "Invalid BPM power/grid row.")
        balance = abs(case["input_power"] - case["output_power"]
                      - case["material_removed"] - case["boundary_removed"]) / case["input_power"]
        require(balance < 1e-10 and math.isclose(balance, case["balance_relative"], abs_tol=1e-14),
                "BPM power balance is incoherent.")
        require(0 <= case["core_power_fraction_input"] <= case["output_power"] / case["input_power"] + 1e-12,
                "BPM detector violates passivity.")
    comparisons = {"domain144to192": ("domain144", "domain192"), "dz": ("nominal", "dz"),
                   "dx": ("nominal", "dx")}
    gates = data.get("gates", [])
    keys = [(gate.get("delta_n"), gate.get("name")) for gate in gates]
    require(len(gates) == 9 and len(set(keys)) == 9
            and set(keys) == {(contrast, name) for contrast in contrasts for name in comparisons},
            "BPM convergence comparisons are incomplete.")
    recomputed = []
    for gate in gates:
        before, after = comparisons[gate["name"]]
        reference = indexed[gate["delta_n"], before]["core_power_fraction_input"]
        candidate = indexed[gate["delta_n"], after]["core_power_fraction_input"]
        absolute = abs(candidate - reference)
        relative = absolute / abs(reference) if reference else None
        passed = reference >= 1e-6 and absolute < .005 and relative < .1
        require(math.isclose(gate["absolute"], absolute, abs_tol=1e-14, rel_tol=1e-12)
                and gate["gate"] is passed, "BPM convergence gate does not match its cases.")
        require((relative is None and gate.get("relative") is None)
                or (relative is not None and math.isclose(gate["relative"], relative, abs_tol=1e-14, rel_tol=1e-12)),
                "BPM relative error is incoherent.")
        recomputed.append(passed)
    require(data.get("gate_balance") is True and data.get("gate_partial_refinements") is False
            and not all(recomputed) and data.get("combined_convergence_certified") is False,
            "Expected retained scientific FAIL was not reproduced.")
    for relative, sha in data.get("sha256", {}).items():
        path = (ROOT / relative).resolve()
        require(path.is_relative_to(ROOT.resolve()) and digest(path) == sha, "BPM source hash mismatch.")
    require(bool(data.get("sha256")), "BPM report has no source provenance.")
    return {"status": "expected_scientific_fail_reproduced", "returncode": 2, "cases": 15,
            "gate_balance": True, "gate_partial_refinements": False,
            "combined_convergence_certified": False, "report": str(output),
            "report_sha256": digest(output)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-dir", type=Path)
    parser.add_argument("--lock", type=Path, default=ROOT / "requirements/cpu-win-py313.lock")
    parser.add_argument("--expected-tests", type=int, default=51)
    args = parser.parse_args()
    if args.report_dir:
        report_dir = args.report_dir.resolve()
        if not report_dir.is_relative_to((ROOT / "resultados/codex").resolve()):
            parser.error("Reports must remain below resultados/codex.")
        report_dir.mkdir(parents=True, exist_ok=True)
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        report_dir = ROOT / "resultados/codex" / f"env_{stamp}_{uuid.uuid4().hex[:8]}"
        report_dir.mkdir(parents=True, exist_ok=False)
    if (report_dir / "verification.json").exists():
        parser.error("A fresh verification report is required; never overwrite evidence.")
    report = {"schema": "silice.cpu-environment.v1", "status": "running", "steps": [],
              "started_utc": datetime.now(timezone.utc).isoformat(), "source_root": str(ROOT.resolve()),
              "scope": "CPU environment reproduction; expected scientific failures are retained.",
              "gpu_initialized": False}
    started = time.monotonic()
    try:
        report["tracked_sha256_before"] = tracked_hashes()
        report["git_head"] = git_bytes(["rev-parse", "HEAD"]).decode().strip()
        for name in THREAD_NAMES:
            os.environ[name] = "1"
        report["platform"] = {"system": platform.system(), "release": platform.release(),
                              "version": platform.version(), "machine": platform.machine(),
                              "pointer_bits": struct.calcsize("P") * 8,
                              "python": platform.python_version(), "implementation": platform.python_implementation(),
                              "executable": sys.executable, "prefix": sys.prefix, "base_prefix": sys.base_prefix}
        require(sys.platform == "win32" and platform.release() == "10"
                and platform.machine().lower() in ("amd64", "x86_64")
                and struct.calcsize("P") == 8 and platform.python_implementation() == "CPython"
                and platform.python_version() == "3.13.7", "The interpreter differs from the pinned Windows CPU environment.")
        require(sys.prefix != sys.base_prefix, "Verification must run in an isolated virtual environment.")
        report["packages"] = {name: importlib.metadata.version(name) for name in EXPECTED}
        require(report["packages"] == EXPECTED, "Installed package versions differ from the CPU lock contract.")
        lock = args.lock.resolve()
        report.update(lock_path=str(lock), lock_sha256=digest(lock),
                      threads={name: os.environ[name] for name in THREAD_NAMES})
        import numpy as np
        import scipy
        import psutil
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            np.show_config()
        report["numpy_blas_configuration"] = output.getvalue()
        report["scipy_version"] = scipy.__version__
        report["available_ram_bytes"] = psutil.virtual_memory().available
        result = capture([sys.executable, "-B", "-m", "pip", "--isolated", "check"], "pip_check", report_dir, timeout=60)
        report["steps"].append(result)
        require(result["returncode"] == 0 and not result["timed_out"], "pip check found inconsistent dependencies.")
        tasks = [
            ("unit_tests", [sys.executable, "-B", str(ROOT / "scripts/check.py"), "--report", str(report_dir / "unit_tests.json")],
             lambda r: check_suite(r, report_dir / "unit_tests.json", args.expected_tests)),
            ("cmt_audit", [sys.executable, "-B", str(ROOT / "scripts/audit_glass004.py"), "--out", str(report_dir / "cmt_audit.json")],
             lambda r: check_cmt(r, report_dir / "cmt_audit.json")),
            ("historical_v2", [sys.executable, "-B", str(ROOT / "scripts/audit_glass007_v2.py"),
                               str(ROOT / "resultados/codex/glass007_v2_run3.json")], check_historical_v2),
            ("bpm_expected_fail", [sys.executable, "-B", str(ROOT / "scripts/run_glass003_v2.py"), "--out", str(report_dir / "bpm_expected_fail.json")],
             lambda r: check_expected_bpm_failure(r, report_dir / "bpm_expected_fail.json")),
        ]
        for label, command, validator in tasks:
            result = capture(command, label, report_dir)
            report["steps"].append(result)
            result["validated"] = validator(result)
        require("torch" not in sys.modules and "cupy" not in sys.modules, "A GPU library was initialized by this verifier.")
        require(digest(lock) == report["lock_sha256"], "The lock changed during verification.")
        report["status"] = "passed"
    except Exception as error:
        report.update(status="failed", error_type=type(error).__name__, error=str(error))
    finally:
        try:
            report["tracked_sha256_after"] = tracked_hashes()
            report["tracked_inputs_unchanged"] = report.get("tracked_sha256_before") == report["tracked_sha256_after"]
            if not report["tracked_inputs_unchanged"]:
                report.update(status="failed", input_integrity_error="Tracked files changed during verification.")
        except Exception as error:
            report.update(status="failed", input_integrity_error=f"{type(error).__name__}: {error}")
    report["elapsed_s"] = time.monotonic() - started
    report["gpu_initialized"] = "torch" in sys.modules or "cupy" in sys.modules
    report["gpu_invariant_verified"] = report["status"] == "passed"
    write_json(report_dir / "verification.json", report)
    print(json.dumps({"status": report["status"], "report": str(report_dir / "verification.json")}))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
