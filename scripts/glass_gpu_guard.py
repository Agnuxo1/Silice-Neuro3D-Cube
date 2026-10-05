"""Reusable own-child watchdog; leaves other processes/reservations untouched."""
import json
from pathlib import Path
import subprocess
import sys
import time
from run_glass_gpu001 import queue_owned,snapshot,unsafe,CUTOFF,ROOT,write_new,sha


def guarded(script,target):
    telemetry=target.with_name(target.stem+'__guard.json')
    if target.exists() or telemetry.exists():
        raise FileExistsError('fresh result/guard required')
    if not queue_owned():
        raise RuntimeError('live own gpuq reservation required')
    started=time.monotonic(); samples=[]; proc=None; reason=None
    try:
        s=snapshot(); samples.append(s)
        if unsafe(s,reserve=1) or time.time()+120>=CUTOFF:
            raise RuntimeError('preflight resources/cutoff')
        proc=subprocess.Popen([sys.executable,'-B',str(script),'--worker','--out',str(target)],cwd=ROOT)
        while proc.poll() is None:
            s=snapshot(); samples.append(s)
            if unsafe(s) or time.monotonic()-started>=120 or time.time()>=CUTOFF:
                raise RuntimeError('watchdog resources/time/cutoff')
            time.sleep(.5)
        rc=proc.returncode
    except Exception as error:
        reason=f'{type(error).__name__}: {error}'
        if proc is not None and proc.poll() is None:
            proc.kill(); proc.wait(timeout=5)
        rc=15
    write_new(telemetry,dict(status='completed' if rc==0 else 'failure_retained',rc=rc,
                           reason=reason,samples=samples,elapsed_s=time.monotonic()-started,
                           child_pid=proc.pid if proc else None,child_finished=proc is None or proc.poll() is not None,
                           result_sha256=sha(target) if target.exists() else None))
    print(json.dumps(dict(guard_rc=rc,reason=reason,samples=len(samples))),flush=True)
    return rc
