"""Guarded CUDA parity pilot from retained CPU arrays; fresh outputs only."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
import psutil

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from silice.gpu_bpm import operators, validate_field, cuda_propagate
from silice.bpm import propagate
from silice.coverage import CellGrid

CUTOFF = datetime(2026,10,5,13,13,6,tzinfo=timezone.utc).timestamp()
SOURCES = ['src/silice/gpu_bpm.py','src/silice/bpm.py',
           'scripts/run_glass_gpu001.py','Docs/GLASS-GPU-001-CONTRACT.md']
FIXTURES = [('pilot_v1','near_left'),('pilot_v1','near_right'),
            ('pilot_v1','near_coherent'),('refinement_v2','near_left')]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes():
    return {p:sha(ROOT/p) for p in SOURCES}


def write_new(path,data):
    with path.open('x',encoding='utf-8',newline='\n') as f:
        f.write(json.dumps(data,indent=2,allow_nan=False)+'\n')


def snapshot():
    q = subprocess.run(['nvidia-smi','--query-gpu=memory.used,temperature.gpu,utilization.gpu',
                        '--format=csv,noheader,nounits'],capture_output=True,text=True,
                       timeout=3,check=True)
    values = [float(x.strip()) for x in q.stdout.strip().splitlines()[0].split(',')]
    return dict(ram_gib=psutil.virtual_memory().available/2**30,
                vram_gib=values[0]/1024,temperature_c=values[1],utilization_pct=values[2])


def unsafe(s,reserve=0):
    return s['ram_gib']-reserve < 4 or s['vram_gib'] > 18 or s['temperature_c'] > 80


def queue_owned():
    p = Path('D:/PROJECTS/.cognition/gpu_queue/holder.json')
    h = json.loads(p.read_text(encoding='utf-8'))
    # gpuq owns supervisor; supervisor owns direct worker (never an arbitrary PID).
    return (os.environ.get('GPUQ_HOLDER') == '1' and
            h.get('name') == os.environ.get('GPUQ_NAME') and
            h.get('child_pid') in (os.getpid(),os.getppid()))


def metrics(a,ref,arrays,dx):
    delta = a-ref
    ports = np.sum(arrays['basis'].conj()*a,axis=(1,2))*dx**2
    ref_ports = np.sum(arrays['basis'].conj()*ref,axis=(1,2))*dx**2
    cores = np.sum(arrays['detectors']*abs(a)**2,axis=(1,2))*dx**2
    ref_cores = np.sum(arrays['detectors']*abs(ref)**2,axis=(1,2))*dx**2
    return dict(field_relative=float(np.linalg.norm(delta)/np.linalg.norm(ref)),
                port_absolute=float(np.max(abs(ports-ref_ports))),
                core_absolute=float(np.max(abs(cores-ref_cores))))


def worker(target):
    if not queue_owned():
        raise RuntimeError('live own gpuq holder required before CUDA')
    if time.time()+120 >= CUTOFF or unsafe(snapshot(),reserve=1):
        raise RuntimeError('deadline/resources not safe for pilot')
    started = time.monotonic()
    before = hashes()
    # Optional dependency is already installed; no automatic installation.
    import torch
    torch.set_num_threads(1)
    torch.manual_seed(7)
    if not torch.cuda.is_available():
        raise RuntimeError('CUDA not available; no CPU fallback')
    deadline = min(started+110,time.monotonic()+CUTOFF-time.time())
    records,outputs = [],{}
    torch.cuda.reset_peak_memory_stats()
    for dtype in (torch.complex128,torch.complex64):
        tolerance = 1e-10 if dtype == torch.complex128 else 1e-4
        for family,name in FIXTURES:
            report_path = ROOT/f'resultados/codex/glass006b_{family}__{name}.json'
            report = json.loads(report_path.read_text(encoding='utf-8'))
            npz = ROOT/report['arrays_path']
            if sha(npz) != report['arrays_sha256']:
                raise ValueError('frozen fixture hash mismatch')
            t = time.monotonic()
            with np.load(npz,allow_pickle=False) as archive:
                arrays = {k:archive[k] for k in archive.files}
            n = report['points']; dx = float(arrays['dx_m'])
            a = validate_field(arrays['input'],n)
            ops = operators(n,report['width_m'],report['length_m'],report['steps'],arrays['delta_n'])
            prep = time.monotonic()-t
            t = time.monotonic()
            ga = torch.as_tensor(a,device='cuda',dtype=dtype)
            half,diffr,damp = [torch.as_tensor(v,device='cuda',dtype=dtype if i<2 else
                                (torch.float64 if dtype==torch.complex128 else torch.float32))
                               for i,v in enumerate(ops)]
            torch.cuda.synchronize(); h2d = time.monotonic()-t
            t = time.monotonic()
            gb,budget = cuda_propagate(torch,ga,half,diffr,damp,steps=report['steps'],dx_m=dx,deadline=deadline)
            torch.cuda.synchronize(); cold = time.monotonic()-t
            t = time.monotonic(); b = gb.cpu().numpy(); d2h = time.monotonic()-t
            errors = metrics(b,arrays['output'],arrays,dx)
            key = f'{family}__{name}__{str(dtype).split(".")[-1]}'
            output = target.with_name(target.stem+'__'+key+'.npz')
            t = time.monotonic()
            with output.open('xb') as f:
                np.savez_compressed(f,output=b)
            disk = time.monotonic()-t
            record = dict(case=key,fixture_path=npz.relative_to(ROOT).as_posix(),fixture_sha256=sha(npz),
                          reference_json_sha256=sha(report_path),dtype=str(dtype),
                          errors=errors,budget=budget,tolerance=tolerance,
                          pass_=bool(max(errors.values())<=tolerance and budget['balance_relative']<=tolerance),
                          preparation_s=prep,h2d_s=h2d,cold_propagation_budget_s=cold,
                          d2h_s=d2h,disk_s=disk,output_path=output.relative_to(ROOT).as_posix(),
                          output_sha256=sha(output),hot_gpu_s=[],hot_cpu_s=[])
            if family=='pilot_v1':
                outputs[(name,str(dtype))] = b.copy()
            if family=='pilot_v1' and name=='near_left':
                # Cold propagation above is the CUDA warmup; CPU gets one warmup.
                for _ in range(3):
                    t = time.monotonic()
                    hot,hot_budget = cuda_propagate(torch,ga,half,diffr,damp,steps=report['steps'],dx_m=dx,deadline=deadline)
                    torch.cuda.synchronize(); record['hot_gpu_s'].append(time.monotonic()-t)
                    hot_errors = metrics(hot.cpu().numpy(),arrays['output'],arrays,dx)
                    if max(hot_errors.values())>tolerance or hot_budget['balance_relative']>tolerance:
                        record['pass_'] = False
                if dtype==torch.complex128:
                    g = CellGrid(n,report['width_m'])
                    for rep in range(4):
                        t = time.monotonic()
                        cb,cbudget = propagate(a,arrays['delta_n'],g,length_m=report['length_m'],
                                               steps=report['steps'],deadline=deadline)
                        elapsed = time.monotonic()-t
                        if rep:
                            record['hot_cpu_s'].append(elapsed)
                        if np.linalg.norm(cb-arrays['output'])/np.linalg.norm(cb)>1e-10:
                            raise ValueError('matched CPU reference drift')
            records.append(record)
            print(json.dumps(dict(case=key,errors=errors,pass_=record['pass_'])),flush=True)
            del gb,ga,half,diffr,damp
    linearity = []
    for dtype in ('torch.complex128','torch.complex64'):
        l,r,c = [outputs[(name,dtype)] for name in ('near_left','near_right','near_coherent')]
        error = float(np.linalg.norm(c-(l+1j*r)/np.sqrt(2))/np.linalg.norm(c))
        limit = 1e-10 if dtype.endswith('128') else 1e-4
        linearity.append(dict(dtype=dtype,error=error,threshold=limit,pass_=error<=limit))
    after = hashes()
    result = dict(experiment='GLASS-GPU-001-v1',status='completed',gpu_used=True,
                  backend='scalar_paraxial_cuda_ssfm_NOT_RT_NOT_physical_optics',
                  torch_version=torch.__version__,cuda_version=torch.version.cuda,
                  gpu=torch.cuda.get_device_name(),python=sys.version,
                  time_utc=datetime.now(timezone.utc).isoformat(),deadline_utc='2026-10-05T13:13:06Z',
                  records=records,linearity=linearity,source_hashes_before=before,source_hashes_after=after,
                  peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated(),
                  peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved(),elapsed_s=time.monotonic()-started,
                  pass_=before==after and all(r['pass_'] for r in records) and all(r['pass_'] for r in linearity),
                  old_dx_and_gaussian_reduction_failures_unchanged=True,independent_peer_gate=False)
    write_new(target,result)
    return 0 if result['pass_'] else 2


def supervisor(target):
    telemetry = target.with_name(target.stem+'__guard.json')
    if telemetry.exists() or target.exists():
        raise FileExistsError('new target and guard required')
    if not queue_owned():
        raise RuntimeError('own gpuq reservation required')
    started=time.monotonic(); samples=[]; reason=None; proc=None
    try:
        s=snapshot(); samples.append(s)
        if unsafe(s,reserve=1) or time.time()+120>=CUTOFF:
            raise RuntimeError('unsafe preflight resources or absolute cutoff')
        proc=subprocess.Popen([sys.executable,'-B',str(Path(__file__).resolve()),'--worker','--out',str(target)],cwd=ROOT)
        while proc.poll() is None:
            s=snapshot(); samples.append(s)
            if unsafe(s) or time.monotonic()-started>=120 or time.time()>=CUTOFF:
                raise RuntimeError('watchdog resource/time/cutoff gate')
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


def main():
    p=argparse.ArgumentParser(); p.add_argument('--worker',action='store_true')
    p.add_argument('--out',type=Path,required=True); args=p.parse_args()
    target=args.out.resolve()
    if not target.is_relative_to(ROOT/'resultados/codex') or target.exists():
        p.error('fresh own result path required')
    return worker(target) if args.worker else supervisor(target)


if __name__=='__main__':
    raise SystemExit(main())
