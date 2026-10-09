"""Reuse frozen pilot computation with explicit opt-in fine-grid inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

import run_glass006b_pilot as pilot
import numpy as np

ROOT = pilot.ROOT
PARENT = 'resultados/codex/glass006b_pilot_v1.json'
NAMES = ('near_left','near_right','near_coherent')
pilot.INPUTS += ['scripts/run_glass006b_refinement.py','Docs/GLASS-006B-REFINEMENT-CONTRACT.md',PARENT]
for name in NAMES:
    values = list(pilot.CASES[name])
    values[0] = 320
    pilot.CASES[name] = tuple(values)


def run_all(target):
    start = time.monotonic()
    sources = pilot.hashes()
    parent = json.loads((ROOT/PARENT).read_text())
    if parent['status'] != 'completed' or parent['hashes_before'] != parent['hashes_after']:
        raise ValueError('valid frozen parent required')
    for path, sha in parent['hashes_before'].items():
        if sources[path] != sha:
            raise ValueError('original computation source changed')
    paths = {n:target.with_name(target.stem+'__'+n+'.json') for n in NAMES}
    if target.exists() or any(p.exists() or p.with_suffix('.npz').exists() for p in paths.values()):
        raise FileExistsError('fresh own prefix required')
    rows=[]
    children=[]
    for name,path in paths.items():
        t = time.monotonic()
        try:
            child = subprocess.run([sys.executable,'-B',str(Path(__file__).resolve()),'--case',name,'--out',str(path)],
                                   cwd=ROOT,timeout=30,capture_output=True,text=True)
            info=dict(name=name,rc=child.returncode,elapsed_s=time.monotonic()-t,stderr=child.stderr[-1000:])
        except subprocess.TimeoutExpired:
            info=dict(name=name,rc='timeout',elapsed_s=time.monotonic()-t)
        children.append(info)
        print(json.dumps(info),flush=True)
        if path.exists():
            row=json.loads(path.read_text())
            row.update(report_path=path.relative_to(ROOT).as_posix(),report_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
            rows.append(row)
        if info['rc']!=0 or pilot.hashes()!=sources:
            break
    gates=[]
    if len(rows)==3 and all(r['status']=='completed' for r in rows):
        for row in rows:
            old=next(c for c in parent['cases'] if c['name']==row['name'])
            error=float(max(np.max(np.abs(pilot.unpacked(row['gaussian_port_amplitudes'])-pilot.unpacked(old['gaussian_port_amplitudes']))),
                            np.max(np.abs(np.array(row['core_powers_input'])-np.array(old['core_powers_input'])))))
            gates.append(dict(name='dx05_to04_'+row['name'],error=error,threshold=.005,pass_=error<.005))
        data={r['name']:r for r in rows}
        l,r=[pilot.unpacked(data[n]['gaussian_port_amplitudes']) for n in NAMES[:2]]
        e=float(max(abs(l[0]-r[1]),abs(l[1]-r[0])))
        gates.append(dict(name='mirror_symmetry_and_reciprocity',error=e,threshold=1e-8,pass_=e<1e-8))
        fields=[]
        for n in NAMES:
            path=ROOT/data[n]['arrays_path']
            if hashlib.sha256(path.read_bytes()).hexdigest()!=data[n]['arrays_sha256']:
                raise ValueError('array hash changed')
            with np.load(path,allow_pickle=False) as arrays:
                fields.append(arrays['output'])
        e=float(np.linalg.norm(fields[2]-(fields[0]+1j*fields[1])/np.sqrt(2))/np.linalg.norm(fields[2]))
        gates.append(dict(name='full_field_linearity',error=e,threshold=1e-10,pass_=e<1e-10))
    completed=len(gates)==5
    report=dict(experiment='GLASS-006b-refinement-v2',status='completed' if completed else 'incomplete_retained',
                cases=rows,children=children,gates=gates,elapsed_s=time.monotonic()-start,gpu_used=False,
                hashes_before=sources,hashes_after=pilot.hashes(),
                parent_sha256=sources[PARENT],historical_v1_numeric_pass=False,
                fine_pair_stability_pass=bool(completed and pilot.hashes()==sources and all(r['numeric_pass'] for r in rows)
                                             and all(g['pass_'] for g in gates)),
                reduction_pass=bool(completed and all(r['reduction_pass'] for r in rows)),
                global_convergence_certified=False,independent_peer_gate=False)
    pilot.write_new(target,report)
    return 0 if report['fine_pair_stability_pass'] and report['reduction_pass'] else 2


def main():
    parser=argparse.ArgumentParser()
    choice=parser.add_mutually_exclusive_group(required=True)
    choice.add_argument('--case',choices=NAMES)
    choice.add_argument('--all',action='store_true')
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    path=args.out.resolve()
    if not path.is_relative_to(ROOT/'resultados/codex') or path.exists() or path.with_suffix('.npz').exists():
        parser.error('new own output required')
    if args.all:
        return run_all(path)
    try:
        result=pilot.run_case(args.case,path)
    except Exception as error:
        result=dict(name=args.case,status='failure_retained',error_type=type(error).__name__,error=str(error),gpu_used=False)
    pilot.write_new(path,result)
    return 0 if result['status']=='completed' else 2


if __name__=='__main__':
    raise SystemExit(main())
