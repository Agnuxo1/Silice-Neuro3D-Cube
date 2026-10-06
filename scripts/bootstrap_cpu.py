"""Build the pinned Windows CPU environment without modifying global Python."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import struct
import subprocess
import sys
import tempfile
import time
import uuid
import venv

ROOT = Path(__file__).resolve().parents[1]
MARKER = ".silice-cpu-environment.json"
THREAD_NAMES = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write("\n")


def require_platform() -> None:
    if (sys.platform != "win32" or platform.python_implementation() != "CPython"
            or sys.version_info[:3] != (3, 13, 7) or struct.calcsize("P") != 8
            or platform.machine().lower() not in ("amd64", "x86_64")):
        raise RuntimeError("This lock requires Windows x64 and CPython 3.13.7.")


def cpu_environment() -> dict[str, str]:
    result = os.environ.copy()
    result.update({name: "1" for name in THREAD_NAMES})
    result.update(PYTHONDONTWRITEBYTECODE="1", PIP_DISABLE_PIP_VERSION_CHECK="1",
                  PIP_REQUIRE_VIRTUALENV="1")
    result.pop("PYTHONPATH", None)
    result.pop("PYTHONHOME", None)
    return result


def capture(command: list[str], directory: Path, label: str, report_dir: Path,
            environment: dict[str, str], timeout: int | None = 40) -> dict:
    started = time.monotonic()
    result = {"command": command, "cwd": str(directory), "timeout_s": timeout}
    try:
        run = subprocess.run(command, cwd=directory, env=environment, shell=False,
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


def tracked_hashes() -> dict[str, str]:
    run = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"], shell=False,
                         capture_output=True, timeout=40)
    if run.returncode:
        raise RuntimeError("Git source inventory failed: " + run.stderr.decode("utf-8", "replace"))
    result = {}
    for relative in run.stdout.decode("utf-8", "surrogateescape").split("\0"):
        if relative:
            path = ROOT / relative
            if not path.is_file():
                raise FileNotFoundError("Tracked input is missing: " + relative)
            result[relative] = digest(path)
    return result


def checked(result: dict, label: str) -> None:
    if result.get("returncode") != 0 or result.get("timed_out"):
        raise RuntimeError(f"{label} failed; see its captured output.")


def isolated_install_probe(python: Path, report_dir: Path, environment: dict) -> dict:
    # -I ignores PYTHONPATH and user site; the temporary cwd is outside the repo.
    code = """import json, pathlib, sys
import silice
from silice import bpm, coverage, tracks
prefix = pathlib.Path(sys.prefix).resolve()
modules = {m.__name__: str(pathlib.Path(m.__file__).resolve()) for m in (silice, bpm, coverage, tracks)}
if not all(pathlib.Path(p).is_relative_to(prefix) for p in modules.values()):
    raise RuntimeError('Package imported from outside this virtual environment')
print(json.dumps({'prefix': str(prefix), 'modules': modules, 'sys_path': sys.path}))
"""
    with tempfile.TemporaryDirectory(prefix="silice_installed_probe_") as temporary:
        if Path(temporary).resolve().is_relative_to(ROOT.resolve()):
            raise RuntimeError("The installed-package probe needs a temporary cwd outside the repository.")
        result = capture([str(python), "-I", "-B", "-c", code], Path(temporary),
                         "installed_package", report_dir, environment)
    checked(result, "Installed-package isolation probe")
    result["data"] = json.loads(result["stdout"])
    if Path(result["data"]["prefix"]).resolve() != python.parent.parent.resolve():
        raise RuntimeError("The installed-package probe used an unexpected virtual environment.")
    root = ROOT.resolve()
    for entry in result["data"]["sys_path"]:
        if entry and Path(entry).resolve().is_relative_to(root) and not Path(entry).resolve().is_relative_to(python.parent.parent):
            raise RuntimeError("Repository source directory leaked into isolated sys.path.")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheelhouse", type=Path,
                        help="Optional directory of hashed wheels; when provided, installation is offline.")
    parser.add_argument("--lock", type=Path, default=ROOT / "requirements/cpu-win-py313.lock")
    parser.add_argument("--venv", type=Path, default=ROOT / ".venv")
    parser.add_argument("--expected-tests", type=int, default=51)
    args = parser.parse_args()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    report_dir = ROOT / "resultados/codex" / f"env_{stamp}_{uuid.uuid4().hex[:8]}"
    report_dir.mkdir(parents=True, exist_ok=False)
    report = {"schema": "silice.cpu-bootstrap.v1", "status": "running",
              "started_utc": datetime.now(timezone.utc).isoformat(),
              "source_root": str(ROOT.resolve()), "report_directory": str(report_dir),
              "bootstrap_python": sys.executable, "steps": [], "gpu_initialized": False}
    started = time.monotonic()
    try:
        report["tracked_sha256_before"] = tracked_hashes()
        require_platform()
        lock, target = args.lock.resolve(), args.venv.resolve()
        wheelhouse = args.wheelhouse.resolve() if args.wheelhouse else None
        if not lock.is_file() or (wheelhouse is not None and not wheelhouse.is_dir()):
            raise FileNotFoundError("The lock and any supplied wheelhouse must already exist.")
        if target != ROOT.resolve() / ".venv":
            raise ValueError("The owned environment must be the repository's .venv directory.")
        report.update(lock_path=str(lock), lock_sha256=digest(lock),
                      wheelhouse=str(wheelhouse) if wheelhouse else None,
                      dependency_index=None if wheelhouse else "https://pypi.org/simple",
                      environment_path=str(target))
        identity = {"schema": "silice.cpu-venv.v1", "source_root": str(ROOT.resolve()),
                    "python_minor": "3.13", "platform": "win_amd64"}
        if target.exists():
            marker = target / MARKER
            if not target.is_dir() or not marker.is_file():
                raise RuntimeError("Refusing to reuse or delete an unowned existing environment.")
            if json.loads(marker.read_text(encoding="utf-8")) != identity:
                raise RuntimeError("Existing environment ownership does not match this repository.")
            report["environment_reused"] = True
        else:
            # A failed creation remains for inspection; it is never silently deleted.
            venv.EnvBuilder(with_pip=False, system_site_packages=False, clear=False,
                            symlinks=False).create(target)
            write_json(target / MARKER, identity)
            report["environment_reused"] = False
        python = target / "Scripts/python.exe"
        if not python.is_file():
            raise FileNotFoundError("The owned environment has no Python executable.")
        configuration = (target / "pyvenv.cfg").read_text(encoding="utf-8").lower()
        if "include-system-site-packages = false" not in configuration:
            raise RuntimeError("The environment exposes global site packages.")
        environment = cpu_environment()
        ensure_pip = capture([str(python), "-B", "-m", "ensurepip", "--upgrade"],
                             ROOT, "ensurepip", report_dir, environment)
        report["steps"].append(ensure_pip)
        checked(ensure_pip, "Virtual-environment pip bootstrap")
        source_arguments = (["--no-index", "--find-links", str(wheelhouse)] if wheelhouse
                            else ["--index-url", "https://pypi.org/simple"])
        install = capture([str(python), "-B", "-m", "pip", "--isolated", "install",
                           *source_arguments, "--require-hashes",
                           "--only-binary=:all:", "--no-deps", "-r", str(lock)],
                          ROOT, "locked_dependencies", report_dir, environment)
        report["steps"].append(install)
        checked(install, "Locked dependency installation")
        if digest(lock) != report["lock_sha256"]:
            raise RuntimeError("The dependency lock changed during installation.")
        package = capture([str(python), "-B", "-m", "pip", "--isolated", "install", "--no-index",
                           "--no-build-isolation", "--no-deps", "--force-reinstall", str(ROOT)],
                          ROOT, "local_package", report_dir, environment)
        report["steps"].append(package)
        checked(package, "Noneditable local package installation")
        report["steps"].append(isolated_install_probe(python, report_dir, environment))
        verify = capture([str(python), "-B", str(ROOT / "scripts/verify_environment.py"),
                          "--report-dir", str(report_dir), "--lock", str(lock),
                          "--expected-tests", str(args.expected_tests)], ROOT,
                         "verification", report_dir, environment, timeout=None)
        # Only the supervisor has no outer timeout: the verifier bounds every
        # child to 40 seconds (60 for pip metadata). Killing this supervisor
        # prematurely could orphan its active child, so wait for its report.
        report["steps"].append(verify)
        checked(verify, "CPU environment verification")
        verification = json.loads((report_dir / "verification.json").read_text(encoding="utf-8"))
        if verification.get("status") != "passed":
            raise RuntimeError("Verifier did not report a completed passing environment gate.")
        report.update(status="passed", verifier_report=str(report_dir / "verification.json"),
                      verifier_sha256=digest(report_dir / "verification.json"))
    except Exception as error:
        report.update(status="failed", error_type=type(error).__name__, error=str(error))
    finally:
        try:
            report["tracked_sha256_after"] = tracked_hashes()
            report["tracked_inputs_unchanged"] = report.get("tracked_sha256_before") == report["tracked_sha256_after"]
            if not report["tracked_inputs_unchanged"]:
                report.update(status="failed", input_integrity_error="Tracked files changed during bootstrap.")
        except Exception as error:
            report.update(status="failed", input_integrity_error=f"{type(error).__name__}: {error}")
    report["elapsed_s"] = time.monotonic() - started
    report["gpu_invariant_verified"] = report["status"] == "passed"
    write_json(report_dir / "bootstrap.json", report)
    print(json.dumps({"status": report["status"], "report": str(report_dir / "bootstrap.json")}))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
