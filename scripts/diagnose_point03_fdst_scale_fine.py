"""Finer manufactured diagnostic; retains all previous optical and toy outcomes."""
from datetime import datetime,timezone
import json
import math
from pathlib import Path
import time
from run_point03_exponential import ROOT,operator,sha,write
import numpy as np
from scipy.linalg import expm
from point03_fdst import Solver

def run():
    start=time.monotonic();priorpath=ROOT/'resultados/codex/point03_fdst_scale_diagnostic_20261007.json';prior=json.loads(priorpath.read_text(encoding='utf-8'))
    assert prior['controls_pass'] and prior['manufactured_only'] and prior['no_T96_propagation']
    for path,digest in prior['source_sha256'].items():assert sha(path)==digest
    n=9;beta=1.444*2*math.pi/1550e-9;rho=4*math.cos(math.pi/(2*627))**2/(beta*(128e-6/626)**2)
    dx=math.sqrt(4*math.cos(math.pi/(2*(n+1)))**2/(beta*rho));assert dx==prior['dx_m'];z=.002
    j=np.arange(1,n+1);initial=(np.sin(math.pi*j/(n+1))[:,None]*np.sin(2*math.pi*j/(n+1))[None,:]).astype(np.complex128)
    norm=float(np.vdot(initial,initial).real);sigma=np.zeros((n,n));board=-.003*((np.indices((n,n)).sum(axis=0)%2).astype(float));matrix,_=operator(board,sigma,dx)
    full=expm(z*matrix.toarray());half=expm(z/2*matrix.toarray());reference=(full@initial.ravel()).reshape((n,n));split_ref=(half@(half@initial.ravel())).reshape((n,n))
    semigroup=float(np.linalg.norm(reference-split_ref)/np.linalg.norm(reference));refnorm=abs(float(np.vdot(reference,reference).real/norm)-1)
    rows=[]
    for steps in (51200,102400,204800):
        assert time.monotonic()-start<=120
        actual=Solver(board,sigma,dx,z/steps).advance(initial.copy(),steps)
        assert np.all(np.isfinite(actual))
        rows.append(dict(steps=steps,dz_m=z/steps,dz_rho=z/steps*rho,field_relative_error=float(np.linalg.norm(actual-reference)/np.linalg.norm(reference)),norm_relative_error=abs(float(np.vdot(actual,actual).real/norm)-1)))
    orders=[math.log2(a['field_relative_error']/b['field_relative_error']) for a,b in zip(rows,rows[1:])]
    gates=dict(norm=max([refnorm,semigroup]+[r['norm_relative_error'] for r in rows])<=1e-9,fine_accuracy=rows[-1]['field_relative_error']<=1e-6,order=all(3.8<=p<=4.2 for p in orders),budget=time.monotonic()-start<=120)
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),manufactured_only=True,no_T96_propagation=True,point03_closed=False,extension_pass=all(gates.values()),gates=gates,rows=rows,observed_orders=orders,dense_semigroup_error=semigroup,dense_norm_error=refnorm,prior_path=str(priorpath),prior_sha256=sha(priorpath),elapsed_s=time.monotonic()-start,source_sha256={str(p):sha(p) for p in (Path(__file__).resolve(),ROOT/'scripts/point03_fdst.py',ROOT/'scripts/run_point03_exponential.py',ROOT/'Docs/POINT-03-FDST-SCALE-FINE-CONTRACT.md')})

if __name__=='__main__':
    result=run();write(ROOT/'resultados/codex/point03_fdst_scale_fine_20261007.json',result);print(json.dumps(result));raise SystemExit(0 if result['extension_pass'] else 1)
