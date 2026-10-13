"""F1R2: second registered replacement of the lost F1 run, with a resource-retry rule.

F1R (2026-10-13) failed operationally at chunk 22/192: the unchanged worker's
own resource guard (available RAM > 3 GiB at chunk end) tripped during a RAM
spike from other processes on the shared machine. F1R2 is F1R plus one rule:
a chunk whose child failed **inside the worker's resource guard** is
recomputed after RAM recovers, up to MAX_ATTEMPTS times; the failed attempt's
files are kept as part###.attemptK.{json,log,npz} and listed in
execution.json["retries"]. Any other failure (numerical, power check,
timeout, budget) still stops the run. Chunks are deterministic, so a retry
recomputes exactly the same field from the same inputs.

The numerical worker is Codex's original scripts/run_point03_d16_fine_time.py,
unchanged and SHA-checked. run() and audit() are derived from the originals
by exact text substitutions, each asserted to occur exactly once.

Usage:
  python -B run_f1r2.py run   --root <extracted F1 package root> --out <root>/resultados/agent/f1r2_20261013
  python -B run_f1r2.py audit --root <root> --out <same folder>
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_f1r as base  # noqa: E402  (same folder; F1R substitutions and loader)

MAX_ATTEMPTS = 5
RETRY_BLOCK_OLD = """                before = time.monotonic()
                with Path(str(prefix)+'.log').open('xb') as log:
                    child = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=min(370., 32000-(time.monotonic()-start), deadline_remaining()))
                cp = Path(str(prefix)+'.json')
"""
RETRY_BLOCK_NEW = """                child, cp, before, reservation = _f1r2_run_chunk(command, prefix, reservation, start, e, case, index)
"""
HELPER = '''
def _f1r2_run_chunk(command, prefix, reservation, start, e, case, index):
    """Run one chunk; retry only failures raised inside the worker's resource guard."""
    for attempt in range(1, _F1R2_MAX_ATTEMPTS + 1):
        before = time.monotonic()
        with Path(str(prefix)+'.log').open('xb') as log:
            child = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=min(370., 32000-(time.monotonic()-start), deadline_remaining()))
        cp = Path(str(prefix)+'.json')
        record = read(cp) if cp.exists() else {}
        if child.returncode == 0 and record.get('status') == 'completed':
            return child, cp, before, reservation
        in_guard = 'in guard' in record.get('diagnostic', '')
        if not in_guard or attempt == _F1R2_MAX_ATTEMPTS:
            return child, cp, before, reservation
        moved = {}
        for suffix in ('.json', '.log', '.npz'):
            source = Path(str(prefix)+suffix)
            if source.exists():
                target = Path(str(prefix)+'.attempt'+str(attempt)+suffix)
                source.rename(target)
                moved[suffix] = target.name
        retry = dict(case=case, index=index, attempt=attempt, error_type=record.get('error_type'),
                     moved=moved, failed_utc=datetime.now(timezone.utc).isoformat())
        wait_start = time.monotonic()
        while psutil.virtual_memory().available <= 3*1024**3:
            assert time.monotonic()-wait_start <= 1800 and time.monotonic()-start <= 32000 and deadline_remaining() > 0
            time.sleep(5)
        time.sleep(30)
        reservation = dict(available_ram_bytes=psutil.virtual_memory().available,
                           free_disk_bytes=psutil.disk_usage(str(prefix.parent)).free)
        retry.update(wait_s=time.monotonic()-wait_start, retry_reservation=reservation)
        e.setdefault('retries', []).append(retry)
    return child, cp, before, reservation
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("run", "audit"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    scripts = root / "scripts"
    sys.path.insert(0, str(scripts))
    worker_path = scripts / "run_point03_d16_fine_time.py"
    controls = json.loads((root / "resultados/codex/point03_d16_fine_worker_controls_20261009/report.json").read_text(encoding="utf-8"))
    import hashlib
    assert hashlib.sha256(worker_path.read_bytes()).hexdigest() == controls["tested_worker_sha256"], "worker changed"
    if args.mode == "run":
        f1 = base.load(worker_path, "run_point03_d16_fine_time")
        f1.DEADLINE = base.NEW_DEADLINE
        f1.__dict__["_F1R2_MAX_ATTEMPTS"] = MAX_ATTEMPTS
        exec(compile(HELPER, "f1r2_helper", "exec"), f1.__dict__)
        run, _ = base.derive(f1, "run", base.RUN_SUBSTITUTIONS + [(RETRY_BLOCK_OLD, RETRY_BLOCK_NEW)])
        return run(args.out.resolve())
    auditor = base.load(scripts / "audit_point03_d16_fine_time.py", "audit_point03_d16_fine_time")
    audit, _ = base.derive(auditor, "audit", base.AUDIT_SUBSTITUTIONS)
    out = args.out.resolve()
    result = audit(out)
    execution = json.loads((out / "execution.json").read_text(encoding="utf-8"))
    result["f1r2_retries"] = execution.get("retries", [])
    result["f1r_substitutions"] = {"run": base.RUN_SUBSTITUTIONS + [(RETRY_BLOCK_OLD, RETRY_BLOCK_NEW)],
                                   "audit": base.AUDIT_SUBSTITUTIONS}
    with (out / "integrity_audit.json").open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, default=str)
    print(json.dumps({k: result[k] for k in ("integrity_pass", "temporal_precision_pass",
                                             "relative_field_difference", "power_differences",
                                             "PSD_observable_bounds")}, default=str))
    print("retries:", len(result["f1r2_retries"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
