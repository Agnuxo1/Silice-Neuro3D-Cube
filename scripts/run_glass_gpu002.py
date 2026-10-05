"""Opt-in coherent coupler refinement, bounded GPU128 and exact CPU controls."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
import time
import numpy as np
from run_glass_gpu001 import ROOT,CUTOFF,queue_owned,snapshot,unsafe,sha,write_new
from glass_gpu_guard import guarded
sys.path.insert(0,str(ROOT/'src'))
from silice.gpu_bpm import cuda_propagate
from silice.gpu_refinement import FineGrid,fine_operators
from silice.coupler import geometry,gaussian_ports,project
from silice.bpm import propagate

CASES={'n384L':(384,'L',400,16),'n512L':(512,'L',400,16),
       'n640L':(640,'L',400,16),'n512R':(512,'R',400,16),
       'n512C':(512,'C',400,16),'n512Lcoverage32':(512,'L',400,32),
       'n512Ldz':(512,'L',800,16),'n640Ldz':(640,'L',800,16)}
SOURCES=['src/silice/bpm.py','src/silice/coupler.py','src/silice/coverage.py',
         'src/silice/gpu_bpm.py','src/silice/gpu_refinement.py',
         'scripts/run_glass_gpu001.py','scripts/run_glass_gpu002.py',
         'scripts/glass_gpu_guard.py','Docs/GLASS-GPU-002-CONTRACT.md',
         'resultados/codex/glass006b_refinement_v2__near_left.json',
         'resultados/codex/glass006b_refinement_v2__near_left.npz']


def hashes(): return {p:sha(ROOT/p) for p in SOURCES}


def ports(row): return np.array([complex(*v) for v in row['ports']])


def worker(target):
    if not queue_owned() or time.time()+120>=CUTOFF or unsafe(snapshot(),reserve=1):
        raise RuntimeError('reservation/resource/window gate before CUDA')
    started=time.monotonic(); before=hashes(); deadline=started+110
    import torch
    torch.set_num_threads(1); torch.manual_seed(7)
    if not torch.cuda.is_available(): raise RuntimeError('CUDA required')
    torch.cuda.reset_peak_memory_stats()
    rows=[]; fields={}
    for name,(n,kind,steps,samples) in CASES.items():
        t=time.monotonic(); g=FineGrid(n)
        dn,weights,geo=geometry(g,samples=samples,deadline=deadline)
        q,basis=gaussian_ports(g)
        c=np.array([1,0] if kind=='L' else [0,1],dtype=complex)
        if kind=='C': c=np.array([1,1j])/np.sqrt(2)
        a=np.einsum('a,aij->ij',c,q)
        ops=fine_operators(g,dn,steps)
        prep=time.monotonic()-t
        ga=torch.as_tensor(a,device='cuda',dtype=torch.complex128)
        half,diffr,damp=[torch.as_tensor(v,device='cuda',dtype=torch.complex128 if i<2 else torch.float64)
                         for i,v in enumerate(ops)]
        torch.cuda.synchronize(); t=time.monotonic()
        gb,budget=cuda_propagate(torch,ga,half,diffr,damp,steps=steps,dx_m=g.dx_m,deadline=deadline)
        torch.cuda.synchronize(); gpu_s=time.monotonic()-t
        b=gb.cpu().numpy()
        p=project(b,q,g); cores=(weights*abs(b)**2).sum(axis=(1,2))*g.dx_m**2/budget['input_power']
        parity=None; cpu_s=None
        if name in ('n512L','n640L'):
            t=time.monotonic()
            cb,cbudget=propagate(a,dn,g,length_m=1e-3,steps=steps,deadline=deadline)
            cpu_s=time.monotonic()-t
            parity=float(np.linalg.norm(b-cb)/np.linalg.norm(cb))
            del cb
        path=target.with_name(target.stem+'__'+name+'.npz')
        with path.open('xb') as out:
            np.savez_compressed(out,input=a,output=b,delta_n=dn,detectors=weights,basis=q,
                                dx_m=g.dx_m,width_m=g.width_m,length_m=1e-3)
        valid=bool(budget['balance_relative']<1e-10 and basis['orthogonality_error']<1e-12
                   and max(geo['detector_area_errors'])<1e-10 and geo['fully_core_untouched']
                   and geo['no_double_index'] and (parity is None or parity<1e-10))
        row=dict(name=name,points=n,dx_m=g.dx_m,steps=steps,coverage_samples=samples,
                 ports=[[float(v.real),float(v.imag)] for v in p],core_powers=cores.tolist(),
                 geometry=geo,basis=basis,budget=budget,cpu_field_parity=parity,
                 cpu_propagation_s=cpu_s,geometry_operator_preparation_s=prep,
                 gpu_propagation_budget_s=gpu_s,arrays_path=path.relative_to(ROOT).as_posix(),
                 arrays_sha256=sha(path),pass_=valid)
        rows.append(row)
        if name in ('n512L','n512R','n512C'): fields[name]=b.copy()
        print(json.dumps(dict(case=name,cores=row['core_powers'],parity=parity,pass_=valid)),flush=True)
        del ga,gb,half,diffr,damp
    by={r['name']:r for r in rows}
    old=json.loads((ROOT/'resultados/codex/glass006b_refinement_v2__near_left.json').read_text())
    if sha(ROOT/old['arrays_path'])!=old['arrays_sha256']: raise ValueError('frozen320 fixture drift')
    by['n320L']=dict(ports=old['gaussian_port_amplitudes'],core_powers=old['core_powers_input'])
    gates=[]
    for label,left,right,required in [('dx320_384','n320L','n384L',False),
                                    ('dx384_512','n384L','n512L',False),
                                    ('dx512_640','n512L','n640L',True),
                                    ('dz512','n512L','n512Ldz',True),
                                    ('dz640','n640L','n640Ldz',True),
                                    ('coverage512','n512L','n512Lcoverage32',True)]:
        x,y=by[left],by[right]
        pe=float(np.max(abs(ports(x)-ports(y))))
        ce=float(np.max(abs(np.array(x['core_powers'])-np.array(y['core_powers']))))
        gates.append(dict(name=label,port_error=pe,core_error=ce,error=max(pe,ce),
                          threshold=.005,pass_=max(pe,ce)<.005,required=required,
                          phase_difference_rad=np.angle(ports(y)/ports(x)).tolist()))
    error=float(np.linalg.norm(fields['n512C']-(fields['n512L']+1j*fields['n512R'])/np.sqrt(2))/np.linalg.norm(fields['n512C']))
    gates.append(dict(name='linearity',error=error,threshold=1e-10,pass_=error<1e-10,required=True))
    e=float(np.max(abs(ports(by['n512L'])-ports(by['n512R'])[::-1])))
    gates.append(dict(name='mirror',error=e,threshold=1e-8,pass_=e<1e-8,required=True))
    after=hashes()
    report=dict(experiment='GLASS-GPU-002-v1',status='completed',gpu_used=True,
                backend='scalar_paraxial_CUDA128_NO_RT_NO_physical_device',
                torch_version=torch.__version__,gpu=torch.cuda.get_device_name(),
                time_utc=datetime.now(timezone.utc).isoformat(),elapsed_s=time.monotonic()-started,
                rows=rows,gates=gates,hashes_before=before,hashes_after=after,
                peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated(),
                peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved(),
                local_stability_pass=before==after and all(r['pass_'] for r in rows)
                                     and all(g['pass_'] for g in gates if g['required']),
                global_convergence_certified=False,independent_ADI_gate=False,
                guided_eigenmodes=False,old_failures_preserved=True)
    write_new(target,report)
    return 0 if report['local_stability_pass'] else 2


def main():
    p=argparse.ArgumentParser(); p.add_argument('--worker',action='store_true')
    p.add_argument('--out',type=Path,required=True); args=p.parse_args(); target=args.out.resolve()
    if target.exists() or not target.is_relative_to(ROOT/'resultados/codex'): p.error('fresh own output required')
    return worker(target) if args.worker else guarded(Path(__file__).resolve(),target)


if __name__=='__main__': raise SystemExit(main())
