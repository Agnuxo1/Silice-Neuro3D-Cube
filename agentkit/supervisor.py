"""Bound an explicitly supplied CPU command and retain its log and exit status."""
from __future__ import annotations

import argparse
import ctypes
from datetime import datetime, timezone
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

from agentkit.evidence import utc_now, write_new_json


def available_ram_gib() -> float:
    """Read available system RAM on the supported Linux and Windows hosts."""
    if sys.platform.startswith("linux"):
        entries = {}
        for line in Path("/proc/meminfo").read_text().splitlines():
            name, value = line.split(":", 1)
            entries[name] = int(value.strip().split()[0]) * 1024
        return entries["MemAvailable"] / 1024**3
    if sys.platform == "win32":
        class MemoryStatus(ctypes.Structure):
            _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong),
                        ("total_phys", ctypes.c_ulonglong), ("available_phys", ctypes.c_ulonglong),
                        ("total_pagefile", ctypes.c_ulonglong), ("available_pagefile", ctypes.c_ulonglong),
                        ("total_virtual", ctypes.c_ulonglong), ("available_virtual", ctypes.c_ulonglong),
                        ("available_extended", ctypes.c_ulonglong)]
        status = MemoryStatus()
        status.length = ctypes.sizeof(status)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            raise OSError("Windows RAM telemetry failed")
        return status.available_phys / 1024**3
    raise RuntimeError("RAM telemetry supports Linux and Windows only")


def stop_tree(process: subprocess.Popen) -> None:
    """Terminate only the child and descendants belonging to this invocation."""
    if sys.platform == "win32":
        if process.poll() is None:
            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                           capture_output=True, timeout=10, check=False)
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
        # Also kill any remaining descendants in this process group.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            return
    except ProcessLookupError:
        return


def supervise(command: list[str], cwd: Path, log_path: Path, report_path: Path,
              seconds: float, ram_floor_gib: float, disk_floor_gib: float,
              absolute_deadline: str | None = None) -> dict:
    """Enforce CPU runtime/free-resource limits without using a shell."""
    if (not command or not all(math.isfinite(v) for v in
            (seconds, ram_floor_gib, disk_floor_gib)) or
            seconds <= 0 or min(ram_floor_gib, disk_floor_gib) < 0):
        raise ValueError("Command and resource limits are invalid")
    deadline = None
    if absolute_deadline:
        stamp = datetime.fromisoformat(absolute_deadline.replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            raise ValueError("Absolute deadline must include its timezone")
        deadline = stamp.timestamp()
        if deadline <= time.time():
            raise ValueError("The authorized execution window has expired")
        seconds = min(seconds, deadline - time.time())
    cwd = cwd.resolve()
    cwd.mkdir(parents=True, exist_ok=True)
    if log_path.exists() or report_path.exists():
        raise FileExistsError("Supervisor output paths must be new")
    gib = 1024**3
    if available_ram_gib() < ram_floor_gib:
        raise RuntimeError("Insufficient free RAM")
    if shutil.disk_usage(cwd).free / gib < disk_floor_gib:
        raise RuntimeError("Insufficient free disk")
    environment = os.environ.copy()
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        environment[key] = "1"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    start = time.monotonic()
    minimum_ram = available_ram_gib()
    minimum_disk = shutil.disk_usage(cwd).free / gib
    reason = "completed"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("xb") as output:
        process = subprocess.Popen(command, cwd=cwd, env=environment,
                                   stdout=output, stderr=subprocess.STDOUT,
                                   shell=False, start_new_session=sys.platform != "win32",
                                   creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP
                                                  if sys.platform == "win32" else 0))
        try:
            while process.poll() is None:
                minimum_ram = min(minimum_ram, available_ram_gib())
                minimum_disk = min(minimum_disk, shutil.disk_usage(cwd).free / gib)
                if time.monotonic() - start >= seconds or (deadline and time.time() >= deadline):
                    reason = "timeout"
                elif minimum_ram < ram_floor_gib:
                    reason = "ram_floor"
                elif minimum_disk < disk_floor_gib:
                    reason = "disk_floor"
                if reason != "completed":
                    stop_tree(process)
                    break
                time.sleep(0.1)
            process.wait(timeout=10)
        finally:
            if process.poll() is None:
                stop_tree(process)
                process.wait(timeout=10)
    report = {"created_utc": utc_now(), "command": command, "cwd": str(cwd),
              "status": reason, "exit_code": process.returncode,
              "elapsed_seconds": time.monotonic() - start,
              "minimum_free_ram_gib": minimum_ram,
              "minimum_free_disk_gib": minimum_disk,
              "scope": "cpu_command_supervision",
              "note": "No GPU reservation, scientific acceptance or permission is granted."}
    write_new_json(report_path, report)
    return report


def main() -> None:
    """Supervise the exact reviewed argument vector supplied after the separator."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--cwd", type=Path, default=Path.cwd())
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--seconds", type=float, default=40)
    parser.add_argument("--ram-floor-gib", type=float, default=4)
    parser.add_argument("--disk-floor-gib", type=float, default=2)
    parser.add_argument("--absolute-deadline")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    report = supervise(command, args.cwd, args.log, args.report, args.seconds,
                       args.ram_floor_gib, args.disk_floor_gib, args.absolute_deadline)
    if report["status"] != "completed" or report["exit_code"] != 0:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
