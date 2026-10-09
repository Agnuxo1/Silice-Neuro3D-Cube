"""Frozen nine-case CPU pilot. Retain fields and failures; no peer execution."""
import os
for variable in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[variable] = '1'
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
import numpy as np
import psutil
from silice.bpm import power, propagate
from silice.coverage import CellGrid, weighted_core_power
from silice.coupler import geometry, gaussian_ports, project, galerkin_generator, reduced_prediction

# points,width,length,steps,separation,input_kind,vacuum
CASES = {
    'near_left': (256,128e-6,1e-3,400,14e-6,'left',False),
    'near_right': (256,128e-6,1e-3,400,14e-6,'right',False),
    'near_coherent': (256,128e-6,1e-3,400,14e-6,'coherent',False),
    'far_left': (256,128e-6,1e-3,400,32e-6,'left',False),
    'vacuum_left': (256,128e-6,1e-3,400,14e-6,'left',True),
    'near_half': (256,128e-6,.5e-3,200,14e-6,'left',False),
    'near_dz': (256,128e-6,1e-3,500,14e-6,'left',False),
    'near_coarse': (192,128e-6,1e-3,400,14e-6,'left',False),
    'near_wide': (256,128e-6*256/192,1e-3,400,14e-6,'left',False),
}
INPUTS = ['src/silice/bpm.py','src/silice/coverage.py','src/silice/tracks.py',
          'src/silice/coupler.py','scripts/run_glass006b_pilot.py',
          'Docs/GLASS-006B-PILOT-CONTRACT.md']


def hashes():
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in INPUTS}


def write_new(path, data):
    encoded = json.dumps(data, indent=2, allow_nan=False)+'\n'
    with path.open('x', encoding='utf-8', newline='\n') as out:
        out.write(encoded)


def packed(values):
    return [[float(v.real),float(v.imag)] for v in values]


def unpacked(values):
    return np.array([complex(*v) for v in values])


def run_case(name, target):
    started = time.monotonic()
    deadline = started+28
    before = hashes()
    free = psutil.virtual_memory().available
    if free-256*1024**2 < 1024**3:
        raise RuntimeError('need1GiB free AFTER256MiB CPU reserve')
    n,width,length,steps,separation,kind,vacuum = CASES[name]
    g = CellGrid(n,width)
    dn,weights,meta = geometry(g,separation_m=separation,deadline=deadline)
    fine,_,_ = geometry(g,separation_m=separation,samples=32,deadline=deadline)
    area_error = float(abs(abs(dn).sum()/abs(fine).sum()-1))
    del fine
    q,basis_meta = gaussian_ports(g,separation)
    if vacuum:
        dn.fill(0)
    h,reduction_meta = galerkin_generator(q,dn,g)
    c = np.array([1,0] if kind == 'left' else [0,1],dtype=complex)
    if kind == 'coherent':
        c = np.array([1,1j])/math.sqrt(2)
    a = np.einsum('a,aij->ij',c,q)
    prediction = reduced_prediction(h,length,c)
    preparation_s = time.monotonic()-started
    prop_started = time.monotonic()
    b,budget = propagate(a,dn,g,length_m=length,steps=steps,deadline=deadline)
    propagation_s = time.monotonic()-prop_started
    ports = project(b,q,g)
    reconstruction = np.einsum('a,aij->ij',ports,q)
    unprojected = power(b-reconstruction,g)/budget['input_power']
    cores = [weighted_core_power(b,w,g,budget['input_power']) for w in weights]
    field_path = target.with_suffix('.npz')
    with field_path.open('xb') as out:
        np.savez_compressed(out,input=a,output=b,delta_n=dn,detectors=weights,basis=q,
                            generator=h,dx_m=g.dx_m,width_m=width,length_m=length)
    after = hashes()
    numeric = bool(budget['balance_relative']<1e-10 and basis_meta['orthogonality_error']<1e-12
                   and max(meta['detector_area_errors'])<1e-10 and area_error<1e-3
                   and meta['fully_core_untouched'] and meta['no_double_index'])
    return dict(name=name,status='completed',time_utc=datetime.now(timezone.utc).isoformat(),
                gpu_used=False,points=n,width_m=width,length_m=length,
                **budget,geometry=meta,basis=basis_meta,reduction=reduction_meta,
                coverage16_vs32_relative=area_error,input_amplitudes=packed(c),
                gaussian_port_amplitudes=packed(ports),reduced_prediction=packed(prediction),
                reduction_max_complex_error=float(np.max(np.abs(ports-prediction))),
                reduction_pass=bool(np.max(np.abs(ports-prediction))<.05),
                core_powers_input=cores,projected_power_input=float(np.vdot(ports,ports).real),
                unprojected_power_input=unprojected,
                projection_budget_error=float(abs(np.vdot(ports,ports).real+unprojected-budget['output_power'])),
                preparation_s=preparation_s,propagation_s=propagation_s,
                elapsed_s=time.monotonic()-started,ram_free_before_gib=free/1024**3,
                rss_after_mib=psutil.Process().memory_info().rss/1024**2,
                arrays_path=field_path.relative_to(ROOT).as_posix(),
                arrays_sha256=hashlib.sha256(field_path.read_bytes()).hexdigest(),
                hashes_before=before,hashes_after=after,sources_unchanged=before==after,
                numeric_pass=numeric)


def comparisons(cases):
    by = {c['name']:c for c in cases if c['status']=='completed'}
    if len(by)!=len(CASES):
        return []
    gates = []
    left,right = [unpacked(by[n]['gaussian_port_amplitudes']) for n in ('near_left','near_right')]
    symmetry = float(max(abs(left[0]-right[1]),abs(left[1]-right[0])))
    gates.append(dict(name='mirror_symmetry_and_reciprocity',error=symmetry,threshold=1e-8,pass_=symmetry<1e-8))
    outputs = []
    for name in ('near_left','near_right','near_coherent'):
        c = by[name]
        path = ROOT/c['arrays_path']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=c['arrays_sha256']:
            raise ValueError('retained array hash changed')
        with np.load(path,allow_pickle=False) as arrays:
            outputs.append(arrays['output'])
    delta = outputs[2]-(outputs[0]+1j*outputs[1])/math.sqrt(2)
    error = float(np.linalg.norm(delta)/np.linalg.norm(outputs[2]))
    gates.append(dict(name='full_field_linearity',error=error,threshold=1e-10,pass_=error<1e-10))
    for label,ref,candidate in [('dx','near_left','near_coarse'),('dz','near_left','near_dz'),
                               ('domain_equal_dx','near_coarse','near_wide')]:
        a,b = by[ref],by[candidate]
        e = float(max(np.max(np.abs(unpacked(a['gaussian_port_amplitudes'])-unpacked(b['gaussian_port_amplitudes']))),
                      np.max(np.abs(np.array(a['core_powers_input'])-np.array(b['core_powers_input'])))))
        gates.append(dict(name=label,error=e,threshold=.005,pass_=e<.005))
    return gates


def run_all(target):
    started = time.monotonic()
    sources = hashes()
    children=[]
    cases=[]
    for name in CASES:
        output=target.with_name(target.stem+'__'+name+'.json')
        if output.exists() or output.with_suffix('.npz').exists():
            raise FileExistsError('fresh case prefix required; completed cases must not be repeated')
    for name in CASES:
        output=target.with_name(target.stem+'__'+name+'.json')
        start=time.monotonic()
        try:
            run=subprocess.run([sys.executable,'-B',str(Path(__file__).resolve()),'--case',name,'--out',str(output)],
                               cwd=ROOT,capture_output=True,text=True,timeout=30)
            child=dict(name=name,rc=run.returncode,elapsed_s=time.monotonic()-start,
                       stderr=run.stderr[-1200:])
        except subprocess.TimeoutExpired:
            child=dict(name=name,rc='timeout',elapsed_s=time.monotonic()-start)
        children.append(child)
        print(json.dumps(child),flush=True)
        if output.exists():
            case=json.loads(output.read_text(encoding='utf-8'))
            case['report_path']=output.relative_to(ROOT).as_posix()
            case['report_sha256']=hashlib.sha256(output.read_bytes()).hexdigest()
            cases.append(case)
        if child['rc']!=0 or hashes()!=sources:
            break
    gates=comparisons(cases)
    completed=len(cases)==len(CASES) and all(c['status']=='completed' for c in cases)
    summary=dict(experiment='GLASS-006b-pilot-v1',status='completed' if completed else 'incomplete_retained',
                 cases=cases,children=children,gates=gates,gpu_used=False,
                 hashes_before=sources,hashes_after=hashes(),elapsed_s=time.monotonic()-started,
                 numeric_pass=bool(completed and hashes()==sources and all(c['numeric_pass'] for c in cases)
                                   and all(g['pass_'] for g in gates)),
                 reduction_pass=bool(completed and all(next(c for c in cases if c['name']==n)['reduction_pass']
                                     for n in ('near_left','near_right','near_half'))),
                 scope='ideal_scalar_BPM_with_Gaussian_ports; NOT_validated_modal_CMT_or_fabrication',
                 independent_peer_gate=False,boundary_certified=False)
    write_new(target,summary)
    return 0 if summary['numeric_pass'] and summary['reduction_pass'] else 2


def main():
    parser=argparse.ArgumentParser()
    choice=parser.add_mutually_exclusive_group(required=True)
    choice.add_argument('--case',choices=CASES)
    choice.add_argument('--all',action='store_true')
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    target=args.out.resolve()
    if not target.is_relative_to(ROOT/'resultados/codex') or target.exists() or target.with_suffix('.npz').exists():
        parser.error('new own output path required')
    if args.all:
        return run_all(target)
    try:
        result=run_case(args.case,target)
    except Exception as error:
        result=dict(name=args.case,status='failure_retained',error_type=type(error).__name__,error=str(error),gpu_used=False)
    write_new(target,result)
    # Numerical/reduction FAILs remain data, not operational crashes.
    return 0 if result['status']=='completed' else 2


if __name__=='__main__':
    raise SystemExit(main())
