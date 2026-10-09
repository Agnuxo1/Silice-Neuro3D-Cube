"""Pinned own-child Blender watchdog, with FIFO ownership and fixed deadlines."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import threading
import psutil

ROOT=Path(__file__).resolve().parents[1]
BLENDER=Path(r'D:/TOOLS/Blender/blender-4.5.14-windows-x64/blender.exe')
HOLDER=Path(r'D:/PROJECTS/.cognition/gpu_queue/holder.json')
DEADLINE=datetime(2026,10,9,13,45,tzinfo=timezone.utc)


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sample():
    s={'available_ram_gib':psutil.virtual_memory().available/2**30}
    r=subprocess.run(['nvidia-smi','--query-gpu=memory.used,temperature.gpu,utilization.gpu',
                      '--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=5)
    if r.returncode: raise RuntimeError('nvidia metadata query failed')
    rows=r.stdout.strip().splitlines()
    if len(rows)!=1: raise RuntimeError('unregistered GPU count')
    used,temp,util=[float(x.strip()) for x in rows[0].split(',')]
    s.update(vram_used_gib=used/1024,temperature_c=temp,utilization_percent=util)
    return s


def allowed(s, preflight=False):
    return (s['available_ram_gib'] >= (8 if preflight else 6)
            and s['vram_used_gib'] <= 4 and s['temperature_c'] <= 80)


def verify_profile(profile_path, commit=None):
    profile_path.resolve().relative_to(ROOT/'resultados/codex')
    p=json.loads(profile_path.read_text(encoding='utf-8'))
    expected={'Docs/POINT-03-RENDER-GPU-CONTRACT.md',
              'Docs/POINT-03-RENDER-BUFFER-CALIBRATION-CONTRACT.md',
              'scripts/point03_render_buffer_reference.py',
              'scripts/check_point03_render_buffer.py',
              'scripts/run_point03_render_buffer_blender.py',
              'scripts/guard_point03_render_buffer.py',
              'scripts/audit_point03_render_buffer.py'}
    if set(p['sources_sha256']) != expected: raise RuntimeError('source set mismatch')
    if sha(Path(sys.executable)) != p['guard_python_sha256']: raise RuntimeError('direct Python executable changed')
    if psutil.__version__ != p['guard_psutil_version']: raise RuntimeError('psutil runtime changed')
    if sha(BLENDER) != p['blender_sha256']: raise RuntimeError('Blender executable changed')
    for name,digest in p['sources_sha256'].items():
        if sha(ROOT/name) != digest: raise RuntimeError('frozen source changed')
        if commit:
            r=subprocess.run(['git','-c','safe.directory='+str(ROOT), 'show',commit+':'+name],
                             cwd=ROOT,capture_output=True,timeout=10)
            if r.returncode or hashlib.sha256(r.stdout).hexdigest()!=digest:
                raise RuntimeError('published Git source mismatch')
    return p


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--profile',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--published-commit')
    ap.add_argument('--preflight-only',action='store_true');args=ap.parse_args()
    out=args.out.resolve();out.relative_to(ROOT/'resultados/codex')
    out.mkdir(exist_ok=False)
    report={'status':'blocked_before_launch','samples':[],'new_gpu_execution':False,
            'new_t96_field':False,'point03_closed':False,'child_pid':None,'child_finished':True}
    started=time.monotonic(); proc=None; rc=2; hard_cut=None; cut_event=threading.Event()
    try:
        p=verify_profile(args.profile,args.published_commit)
        report['profile_sha256']=sha(args.profile);report['sources_sha256']=p['sources_sha256']
        report['profile_relative']=args.profile.resolve().relative_to(ROOT).as_posix()
        report['published_commit']=args.published_commit;report['blender_sha256']=p['blender_sha256']
        s=sample();report['samples'].append(s)
        report['resource_preflight_pass']=allowed(s,preflight=True)
        if args.preflight_only:
            report['status']='preflight_ready' if report['resource_preflight_pass'] else 'resource_block_retained'
            rc=0 if report['resource_preflight_pass'] else 2
        else:
            if not args.published_commit: raise RuntimeError('publication pin required before GPU')
            if not allowed(s,preflight=True): raise RuntimeError('RAM/VRAM/temperature preflight')
            if datetime.now(timezone.utc).timestamp()+130 >= DEADLINE.timestamp():
                raise RuntimeError('insufficient time before absolute deadline')
            h=json.loads(HOLDER.read_text(encoding='utf-8'))
            if (os.environ.get('GPUQ_HOLDER')!='1' or h.get('child_pid')!=os.getpid()
                or h.get('pid')!=os.getppid()
                or abs(h['child_ctime']-psutil.Process().create_time())>=2):
                raise RuntimeError('own live FIFO reservation required')
            # The GUI context needed by the graphics API stays hidden; no user scene is opened.
            si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
            with (out/'blender_stdout.txt').open('xb') as so, (out/'blender_stderr.txt').open('xb') as se:
                launch=time.monotonic()
                proc=subprocess.Popen([str(BLENDER),'--factory-startup','--threads','1','--python',
                    str(ROOT/'scripts/run_point03_render_buffer_blender.py'),'--','--out',str(out),
                    '--profile',str(args.profile.resolve())],cwd=ROOT,stdout=so,stderr=se,
                    startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
                def stop_owned_child():
                    if proc.poll() is None:
                        cut_event.set()
                        try:proc.kill()
                        except ProcessLookupError:pass
                # Independent of a slow metadata query or graphics-driver call.
                hard_cut=threading.Timer(115,stop_owned_child);hard_cut.daemon=True;hard_cut.start()
                report.update(child_pid=proc.pid,child_finished=False,new_gpu_execution=True)
                while proc.poll() is None:
                    s=sample()
                    try:s['owned_rss_gib']=psutil.Process(proc.pid).memory_info().rss/2**30
                    except psutil.NoSuchProcess:
                        if proc.poll() is not None:break
                        raise
                    report['samples'].append(s)
                    if (not allowed(s) or s['owned_rss_gib']>1.5 or time.monotonic()-launch>=120
                        or datetime.now(timezone.utc)>=DEADLINE):
                        raise RuntimeError('own-child watchdog resource/time limit')
                    time.sleep(.5)
                report['elapsed_child_with_startup_s']=time.monotonic()-launch
            if cut_event.is_set():raise RuntimeError('independent own-child hard cutoff')
            rc=proc.returncode
            result=json.loads((out/'render_result.json').read_text(encoding='utf-8'))
            report['status']='completed' if rc==0 and result['status']=='completed' else 'failure_retained'
    except Exception as error:
        report['error_type']=type(error).__name__;report['reason']=str(error)[:250]
        if proc is not None and proc.poll() is None:
            proc.kill();proc.wait(timeout=5)
        rc=2
        if proc is not None:report['status']='failure_retained'
    finally:
        if hard_cut is not None:hard_cut.cancel()
        report['child_finished']=proc is None or proc.poll() is not None
        report['elapsed_guard_s']=time.monotonic()-started
        report['finished_utc']=datetime.now(timezone.utc).isoformat()
        with (out/'guard.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
    print(json.dumps({k:report[k] for k in ['status','new_gpu_execution','child_finished']}))
    return rc


if __name__=='__main__':raise SystemExit(main())
