#!/usr/bin/env python3
"""External fresh-attempt launcher for frozen Point 03 geometry driver D.

Standard library only. Install/run outside tracked files after source freeze.
The launcher creates ONLY a sibling *_launch evidence directory; the driver
creates its own fresh output. No module from the scientific study is imported.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

DRIVER_SHA = "1e937e953d7980d572c5ff9ef1406980047a25baddf2d43793ee92d71c0cf3d3"
OUTER_TIMEOUT_S = 640
THREADS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path, data):
    text = json.dumps(data, indent=2, allow_nan=False) + "\n"
    with Path(path).open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def read_json(path):
    def reject(value):
        raise ValueError("Nonfinite JSON value: " + value)
    return json.loads(Path(path).read_text(encoding="utf-8"), parse_constant=reject)


def stop_launched_tree(process, launch):
    """Stop only this launched process group/tree; retain termination evidence."""
    result = {"pid": process.pid, "already_exited": process.poll() is not None}
    if result["already_exited"]:
        return result
    if os.name == "nt":
        command = ["taskkill", "/PID", str(process.pid), "/T", "/F"]
        result["command"] = command
        try:
            killed = subprocess.run(command, shell=False, capture_output=True, timeout=10)
            result["tree_termination_returncode"] = killed.returncode
            for name, data in (("stdout", killed.stdout), ("stderr", killed.stderr)):
                path = launch / f"termination.{name}.log"
                with path.open("xb", buffering=0) as handle:
                    handle.write(data)
                result[name + "_path"] = str(path)
        except Exception as error:
            result["tree_termination_error"] = f"{type(error).__name__}: {error}"
        if process.poll() is None:
            process.kill()
            result["parent_kill_fallback"] = True
    else:
        os.killpg(process.pid, signal.SIGKILL)
        result["process_group_sigkill"] = True
    try:
        result["returncode_after_cleanup"] = process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        result["cleanup_wait_timed_out"] = True
    result["scope"] = "Tree/group belonging to the launcher-created driver PID; no other process selection. Cleanup time is reported outside the 640 s driver wait."
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path,
                        help="Existing source checkout containing the committed D scripts and Point 01 .venv")
    parser.add_argument("--out-dir", type=Path,
                        help="Fresh direct child resultados/codex/point03_geometry_*; default uses current UTC")
    args = parser.parse_args()
    root = args.root.resolve()
    results = root / "resultados/codex"
    default_name = "point03_geometry_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out = args.out_dir.resolve() if args.out_dir is not None else results / default_name
    launch = Path(str(out) + "_launch")
    driver = root / "scripts/audit_point03_geometry.py"
    python = root / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    study = root / "resultados/codex/point03_refinement_20261006T220909702270Z/manifest.json"
    sources = (driver, root / "scripts/point03_union_geometry.py",
               root / "scripts/point03_geometry_reference.py", root / "Docs/POINT-03-GEOMETRY-CONTRACT.md",
               root / "src/silice/tracks.py", study, python)
    if not root.is_dir() or not results.is_dir() or any(not path.is_file() for path in sources):
        parser.error("Expected existing checkout, committed D sources, original B manifest and Point 01 .venv")
    if out.parent != results.resolve() or not out.name.startswith("point03_geometry_") or out.name.endswith("_launch"):
        parser.error("--out-dir must be a fresh direct resultados/codex/point03_geometry_* directory")
    if out.exists() or launch.exists():
        parser.error("Both driver output and sibling _launch must be fresh; no overwrite or resume")
    before = {str(path): sha(path) for path in sources}
    if before[str(driver)] != DRIVER_SHA:
        parser.error("Driver differs from the reviewed 1e937e95... version; do not launch unreviewed code")
    env = dict(os.environ)
    env.update({name: "1" for name in THREADS})
    env.update(PYTHONUNBUFFERED="1", PYTHONDONTWRITEBYTECODE="1")
    command = [str(python), "-B", "-u", str(driver), "--study", str(study), "--out-dir", str(out)]
    launch.mkdir(exist_ok=False)
    started = time.monotonic()
    report = {"schema": "silice.point03-geometry.launch.v1", "status": "failed",
              "created_utc": datetime.now(timezone.utc).isoformat(), "root": str(root),
              "out_dir": str(out), "launch_dir": str(launch), "command": command,
              "outer_driver_wait_timeout_s": OUTER_TIMEOUT_S,
              "threads": {name: env[name] for name in THREADS},
              "pythonunbuffered": env["PYTHONUNBUFFERED"], "driver_sha256": DRIVER_SHA,
              "launcher_path": str(Path(__file__).resolve()), "launcher_sha256": sha(Path(__file__).resolve()),
              "sources_sha256_before": before,
              "scope": "External launch/cost evidence only; the unchanged driver owns 14 sequential children with 35/40/600 s limits and scientific acceptance. No scientific module is imported here."}
    write_json(launch / "attempt.json", dict(report, status="launch_started",
                                           interruption_scope="A missing launch_result.json means final cost/status is unknown; no implicit resume or recovery."))
    stdout_path, stderr_path = launch / "driver.stdout.log", launch / "driver.stderr.log"
    process, driver_started = None, None
    try:
        # Binary unbuffered handles preserve the exact child stream. Python -u
        # and PYTHONUNBUFFERED=1 make driver progress visible immediately.
        with stdout_path.open("xb", buffering=0) as stdout, stderr_path.open("xb", buffering=0) as stderr:
            options = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
            driver_started = time.monotonic()
            process = subprocess.Popen(command, cwd=root, env=env, shell=False,
                                       stdout=stdout, stderr=stderr, **options)
            report["pid"] = process.pid
            write_json(launch / "process_started.json", {"pid": process.pid, "command": command,
                                                       "started_utc": datetime.now(timezone.utc).isoformat()})
            print(json.dumps({"progress": "driver_started", "pid": process.pid,
                              "out_dir": str(out), "stdout": str(stdout_path), "stderr": str(stderr_path)}), flush=True)
            try:
                report["returncode"] = process.wait(timeout=OUTER_TIMEOUT_S)
            except subprocess.TimeoutExpired:
                report["timed_out"] = True
                report["error"] = "Exterior 640 s driver wait expired"
                report["termination"] = stop_launched_tree(process, launch)
            except KeyboardInterrupt:
                report["interrupted"] = True
                report["termination"] = stop_launched_tree(process, launch)
                report["error"] = "Launcher interrupted; no automatic recovery"
    except (Exception, KeyboardInterrupt) as error:
        report.update(error_type=type(error).__name__, error=str(error))
        if isinstance(error, KeyboardInterrupt):
            report["interrupted"] = True
        if process is not None and process.poll() is None:
            report["termination"] = stop_launched_tree(process, launch)
    if driver_started is not None:
        report["driver_process_elapsed_s_including_cleanup"] = time.monotonic() - driver_started
    report.update(stdout_path=str(stdout_path), stderr_path=str(stderr_path))
    execution = out / "execution.json"
    if execution.is_file():
        try:
            result = read_json(execution)
            report["execution"] = {"path": str(execution), "sha256": sha(execution),
                                   "status": result.get("status"), "operational_pass": result.get("operational_pass"),
                                   "geometry_pass": result.get("geometry_pass"), "elapsed_s": result.get("elapsed_s"),
                                   "children": len(result.get("children", []))}
            if (report.get("returncode") == 0 and not report.get("timed_out") and not report.get("interrupted")
                    and not report.get("error")
                    and result.get("status") == "completed" and result.get("operational_pass") is True
                    and result.get("geometry_pass") is True):
                report["status"] = "completed"
        except Exception as error:
            report["execution_read_error"] = f"{type(error).__name__}: {error}"
    else:
        report["execution_missing"] = True
    try:
        after = {str(path): sha(path) for path in sources}
        report.update(sources_sha256_after=after, sources_unchanged=after == before)
        if after != before:
            report.update(status="failed", integrity_error="Launch sources or executable changed")
    except Exception as error:
        report.update(status="failed", integrity_error=f"{type(error).__name__}: {error}")
    report["elapsed_s"] = time.monotonic() - started
    report["launch_artifact_sha256"] = {str(path): sha(path) for path in launch.iterdir() if path.is_file()}
    write_json(launch / "launch_result.json", report)
    print(json.dumps({"status": report["status"], "launch_result": str(launch / "launch_result.json")}), flush=True)
    if report.get("timed_out"):
        return 124
    if report.get("interrupted"):
        return 130
    return 0 if report["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
