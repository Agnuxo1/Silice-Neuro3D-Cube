"""Bounded scalar preflight for the frozen Stage E assessor; no optics."""
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(r"D:\PROJECTS\Silice-Neuro3D-Cube-work-20261006")
ASSESSOR_SHA = "18f99c958e8766e57322ec637942c004a11aa7a4e2ae688b4f1a005f7964590a"
FREEZE = "f0d10e1ddef0ab79f571e574eb06cd86e9deffff"
THREADS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")

def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8*1024**2), b""):
            digest.update(block)
    return digest.hexdigest()

def snapshot():
    raw = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"], check=True,
                         capture_output=True, timeout=15).stdout
    return {name:sha(ROOT/name) for name in raw.decode("utf-8").split("\0") if name}

def write(path, data):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(data, indent=2, allow_nan=False)+"\n")

def main():
    started = time.monotonic()
    out = ROOT/"resultados/codex"/("point03_analytic_preflight_"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
    out.mkdir(exist_ok=False)
    report = {"schema":"silice.point03-analytic.preflight.v1", "status":"FAIL", "out_dir":str(out),
              "created_utc":datetime.now(timezone.utc).isoformat(), "physical_propagations":0,
              "scope":"Frozen-assessor scalar/parser self-checks only; no propagation or geometry module import."}
    write(out/"attempt.json", report)
    code = 1
    try:
        assessor = ROOT/"scripts/assess_point03_analytic.py"
        assert sha(assessor) == ASSESSOR_SHA
        head = subprocess.run(["git","-C",str(ROOT),"rev-parse","HEAD"],check=True,capture_output=True,timeout=15).stdout.decode().strip()
        assert head == FREEZE, "Unexpected preflight source freeze"
        report.update(source_freeze_commit=head, assessor_sha256=ASSESSOR_SHA, python=platform.python_version(),
                      executable=sys.executable, prefix=sys.prefix, tracked_sha256_before=snapshot())
        for source, name in ((assessor,"assessor_source.py"),
                             (ROOT/".audit_tmp/assess_point03_analytic_review1.py","assessor_review1.py"),
                             (Path(__file__),"preflight_wrapper.py")):
            with (out/name).open("xb") as stream:
                stream.write(source.read_bytes())
        env = dict(os.environ)
        env.update({key:"1" for key in THREADS})
        env.update(PYTHONUNBUFFERED="1", PYTHONDONTWRITEBYTECODE="1")
        command = [sys.executable,"-B","-u",str(assessor),"--self-check","--out",str(out/"self_checks.json")]
        report.update(command=command, threads={key:env[key] for key in THREADS}, hard_child_timeout_s=40)
        child_start = time.monotonic()
        with (out/"self_checks.stdout.log").open("xb",buffering=0) as stdout, (out/"self_checks.stderr.log").open("xb",buffering=0) as stderr:
            child = subprocess.run(command,cwd=ROOT,env=env,stdout=stdout,stderr=stderr,shell=False,timeout=40)
        report.update(child_elapsed_s=time.monotonic()-child_start, returncode=child.returncode)
        result = json.loads((out/"self_checks.json").read_text(encoding="utf-8"))
        report.update(self_check_pass=result.get("self_check_pass"), checks=result.get("checks"), checks_count=result.get("checks_count"))
        assert child.returncode == 0 and result.get("status") == "completed" and result.get("operational_pass") is True
        assert result.get("self_check_pass") is True and result.get("checks_count") == 18
        assert result.get("physical_propagations") == 0 and all(row.get("pass") is True for row in result["checks"])
        assert result.get("assessor_sha256") == ASSESSOR_SHA
        report["status"], code = "PASS", 0
    except (Exception, KeyboardInterrupt) as error:
        report.update(error_type=type(error).__name__, error=str(error))
        code = 1
    try:
        after = snapshot()
        unchanged = after == report.get("tracked_sha256_before")
        report.update(tracked_sha256_after=after, tracked_unchanged=unchanged)
        if not unchanged:
            report["status"], code = "FAIL", 1
    except Exception as error:
        report.update(status="FAIL", integrity_error=type(error).__name__+": "+str(error))
        code = 1
    report["elapsed_s"] = time.monotonic()-started
    report["produced_sha256"] = {str(path):sha(path) for path in out.iterdir() if path.is_file()}
    write(out/"execution.json",report)
    print(json.dumps({key:report.get(key) for key in ("status","out_dir","checks_count","self_check_pass","child_elapsed_s","elapsed_s","error_type","error","tracked_unchanged")}),flush=True)
    return code

if __name__ == "__main__":
    raise SystemExit(main())
