"""Manufactured cost only: no T96 input or geometry preparation."""
import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
for variable in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[variable]='1'
from run_point03_exponential import ROOT,sha,write,guard

def worker(n,output):
    import numpy as np
    from point03_fdst import Solver
    assert n in (767,959,1199)
    dx=128e-6/n;dz=.002/32768;steps=100;indices=np.arange(1,n+1)
    first,second=n-16,n-18
    field=(np.sin(first*math.pi*indices/(n+1))[:,None]*np.sin(second*math.pi*indices/(n+1))[None,:]).astype(np.complex128)
    beta=1.444*2*math.pi/1550e-9
    eigen=1j/(2*beta*dx*dx)*(2*math.cos(first*math.pi/(n+1))+2*math.cos(second*math.pi/(n+1))-4)
    solver=Solver(np.zeros((n,n)),np.zeros((n,n)),dx,dz)
    started=time.monotonic();actual=solver.advance(field.copy(),steps);elapsed=time.monotonic()-started
    exact=np.exp(dz*steps*eigen)*field
    error=float(np.linalg.norm(actual-exact)/np.linalg.norm(exact))
    passed=bool(error<=1e-10 and elapsed<=180 and np.all(np.isfinite(actual)))
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),manufactured_only=True,no_T96_propagation=True,N=n,steps=steps,dz_m=dz,elapsed_s=elapsed,seconds_per_step=elapsed/steps,field_relative_error=error,pass_=passed,forecasts_s={str(count):elapsed/steps*count for count in (32768,65536,131072)},source_sha256={str(p):sha(p) for p in (Path(__file__).resolve(),ROOT/'scripts/point03_fdst.py',ROOT/'Docs/POINT-03-FDST-FINER-COST-CONTRACT.md')})
    write(output,result);print(json.dumps(result),flush=True)
    return 0 if passed else 1

def run(out):
    prior=json.loads((ROOT/'resultados/codex/point03_fdst_accuracy_20261007_L2/execution.json').read_text(encoding='utf-8'))
    assert prior['status']=='completed'
    assert not out.exists();out.mkdir(parents=True)
    started=time.monotonic();records=[]
    for n in (767,959,1199):
        assert time.monotonic()-started<=600
        guard(out);output=out/f'n{n}.json'
        with (out/f'n{n}.log').open('xb') as log:
            try:
                child=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--worker','--n',str(n),'--out',str(output)],stdout=log,stderr=subprocess.STDOUT,timeout=190,check=False)
                record=dict(N=n,returncode=child.returncode,result_path=str(output),result_sha256=sha(output) if output.exists() else None)
            except subprocess.TimeoutExpired:
                record=dict(N=n,returncode=None,operational_timeout=True)
        records.append(record);print(json.dumps(record),flush=True)
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),manufactured_only=True,no_T96_propagation=True,elapsed_s=time.monotonic()-started,children=records)
    write(out/'execution.json',result)
    return 0 if all(row['returncode']==0 for row in records) else 1

if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--out',type=Path,required=True);parser.add_argument('--worker',action='store_true');parser.add_argument('--n',type=int)
    args=parser.parse_args()
    raise SystemExit(worker(args.n,args.out.resolve()) if args.worker else run(args.out.resolve()))
