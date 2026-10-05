"""Read-only NumPy audit of retained CUDA fields; NOT another wave solver."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
import argparse
import hashlib
import json
from pathlib import Path
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def load_arrays(relative,expected):
    p=(ROOT/relative).resolve()
    if not p.is_relative_to(ROOT/'resultados/codex') or sha(p)!=expected:
        raise ValueError('own retained array hash/path mismatch')
    with np.load(p,allow_pickle=False) as f: return {k:f[k] for k in f.files}


def audit(one,two):
    started=time.monotonic(); checks=[]
    a=json.loads(one.read_text()); b=json.loads(two.read_text())
    for p,d in ((one,a),(two,b)):
        guard=p.with_name(p.stem+'__guard.json'); g=json.loads(guard.read_text())
        checks.append(dict(name=p.stem+'_guard_hash_and_exit',pass_=g['result_sha256']==sha(p)
                           and g['child_finished'] and g['rc'] in (0,2) and g['reason'] is None))
        before=d.get('hashes_before',d.get('source_hashes_before'))
        after=d.get('hashes_after',d.get('source_hashes_after'))
        checks.append(dict(name=p.stem+'_sources',pass_=before==after and
                           all(sha(ROOT/rel)==h for rel,h in before.items())))
    for r in a['records']:
        out=load_arrays(r['output_path'],r['output_sha256'])['output']
        ref=load_arrays(r['fixture_path'],r['fixture_sha256'])
        dx=float(ref['dx_m'])
        err=dict(field_relative=float(np.linalg.norm(out-ref['output'])/np.linalg.norm(ref['output'])),
                 port_absolute=float(np.max(abs(np.sum(ref['basis'].conj()*(out-ref['output']),axis=(1,2))*dx**2))),
                 core_absolute=float(np.max(abs(np.sum(ref['detectors']*(abs(out)**2-abs(ref['output'])**2),axis=(1,2))*dx**2))))
        consistent=max(abs(err[k]-r['errors'][k]) for k in err)<1e-12
        passed=max(err.values())<=r['tolerance'] and r['budget']['balance_relative']<=r['tolerance']
        checks.append(dict(name=r['case'],pass_=consistent and passed==r['pass_'],numeric_pass=passed))
    by={}
    for r in b['rows']:
        v=load_arrays(r['arrays_path'],r['arrays_sha256']); dx=float(v['dx_m'])
        out=v['output']; p=np.sum(v['basis'].conj()*out,axis=(1,2))*dx**2
        cores=np.sum(v['detectors']*abs(out)**2,axis=(1,2))*dx**2/r['budget']['input_power']
        oldp=np.array([complex(*z) for z in r['ports']])
        budget=r['budget']; pin=float(np.sum(abs(v['input'])**2)*dx**2)
        pout=float(np.sum(abs(out)**2)*dx**2)
        valid=max(np.max(abs(p-oldp)),np.max(abs(cores-r['core_powers'])),abs(pin-budget['input_power']),abs(pout-budget['output_power']))<1e-12
        checks.append(dict(name=r['name']+'_arrays_metrics',pass_=bool(valid)))
        by[r['name']]=(p,cores)
    required=all(g['pass_'] for g in b['gates'] if g['required']) and all(r['pass_'] for r in b['rows'])
    old=json.loads((ROOT/'resultados/codex/glass006b_refinement_v2__near_left.json').read_text())
    load_arrays(old['arrays_path'],old['arrays_sha256'])
    by['n320L']=(np.array([complex(*v) for v in old['gaussian_port_amplitudes']]),
                  np.array(old['core_powers_input']))
    pairs={'dx320_384':('n320L','n384L'),'dx384_512':('n384L','n512L'),
           'dx512_640':('n512L','n640L'),'dz512':('n512L','n512Ldz'),
           'dz640':('n640L','n640Ldz'),'coverage512':('n512L','n512Lcoverage32')}
    for gate in b['gates']:
        if gate['name'] in pairs:
            left,right=pairs[gate['name']]
            error=float(max(np.max(abs(by[left][0]-by[right][0])),np.max(abs(by[left][1]-by[right][1]))))
        elif gate['name']=='mirror':
            error=float(np.max(abs(by['n512L'][0]-by['n512R'][0][::-1])))
        else:
            fields=[]
            for name in ('n512L','n512R','n512C'):
                row=next(r for r in b['rows'] if r['name']==name)
                fields.append(load_arrays(row['arrays_path'],row['arrays_sha256'])['output'])
            error=float(np.linalg.norm(fields[2]-(fields[0]+1j*fields[1])/np.sqrt(2))/np.linalg.norm(fields[2]))
        checks.append(dict(name=gate['name']+'_recomputed',pass_=abs(error-gate['error'])<1e-12
                           and (error<gate['threshold'])==gate['pass_']))
    checks.append(dict(name='local_stability_flag_not_global',pass_=required==b['local_stability_pass']
                       and b['global_convergence_certified'] is False and b['independent_ADI_gate'] is False))
    return dict(experiment='GLASS-GPU-readback-audit-v1',gpu_initialized=False,
                independent_wave_solver=False,inputs={str(p.relative_to(ROOT)):sha(p) for p in (one,two)},
                checks=checks,consistent=all(c['pass_'] for c in checks),elapsed_s=time.monotonic()-started,
                precision64_failed_preserved=not all(r['pass_'] for r in a['records'] if r['dtype'].endswith('64')))


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--out',type=Path,required=True); args=p.parse_args()
    target=args.out.resolve()
    if target.exists() or not target.is_relative_to(ROOT/'resultados/codex'): p.error('fresh own output required')
    result=audit(ROOT/'resultados/codex/glass_gpu001_20261005_v1.json',ROOT/'resultados/codex/glass_gpu002_20261005_v1.json')
    with target.open('x',encoding='utf-8',newline='\n') as f: f.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result,indent=2)); raise SystemExit(0 if result['consistent'] else 2)
