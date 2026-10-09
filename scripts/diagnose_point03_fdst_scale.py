"""Manufactured kinetic-scale diagnostic; no T96 fields, no gate changes."""
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
    start=time.monotonic();n=9;beta=1.444*2*math.pi/1550e-9
    rho=4*math.cos(math.pi/(2*627))**2/(beta*(128e-6/626)**2)
    dx=math.sqrt(4*math.cos(math.pi/(2*(n+1)))**2/(beta*rho));z=.002
    j=np.arange(1,n+1);initial=(np.sin(math.pi*j/(n+1))[:,None]*np.sin(2*math.pi*j/(n+1))[None,:]).astype(np.complex128)
    norm=float(np.vdot(initial,initial).real);sigma=np.zeros((n,n));constant=np.full((n,n),-.003)
    k0=2*math.pi/1550e-9;c=1j/(2*beta*dx*dx)
    eigen=c*(2*math.cos(math.pi/(n+1))+2*math.cos(2*math.pi/(n+1))-4)+1j*k0*(-.003)
    analytic=np.exp(z*eigen)*initial;actual=Solver(constant,sigma,dx,z/3200).advance(initial.copy(),3200)
    constant_error=float(np.linalg.norm(actual-analytic)/np.linalg.norm(analytic));constant_norm_error=abs(float(np.vdot(actual,actual).real/norm)-1)
    board=-.003*((np.indices((n,n)).sum(axis=0)%2).astype(float));matrix,_=operator(board,sigma,dx)
    full=expm(z*matrix.toarray());half=expm(z/2*matrix.toarray());reference=(full@initial.ravel()).reshape((n,n));split_ref=(half@(half@initial.ravel())).reshape((n,n))
    semigroup=float(np.linalg.norm(reference-split_ref)/np.linalg.norm(reference));reference_norm_error=abs(float(np.vdot(reference,reference).real/norm)-1)
    ref_projection=float(abs(np.vdot(initial,reference))**2/norm**2);rows=[]
    for steps in (3200,6400,12800,25600):
        assert time.monotonic()-start<=120
        actual=Solver(board,sigma,dx,z/steps).advance(initial.copy(),steps)
        assert np.all(np.isfinite(actual))
        error=float(np.linalg.norm(actual-reference)/np.linalg.norm(reference));norm_error=abs(float(np.vdot(actual,actual).real/norm)-1)
        projection=float(abs(np.vdot(initial,actual))**2/norm**2)
        rows.append(dict(steps=steps,dz_m=z/steps,dz_rho=z/steps*rho,field_relative_error=error,norm_relative_error=norm_error,projection_power=projection,projection_error=abs(projection-ref_projection)))
    orders=[math.log2(a['field_relative_error']/b['field_relative_error']) for a,b in zip(rows,rows[1:])]
    passed=max(constant_error,constant_norm_error,semigroup,reference_norm_error,max(r['norm_relative_error'] for r in rows))<=1e-9 and time.monotonic()-start<=120
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),manufactured_only=True,no_T96_propagation=True,point03_closed=False,controls_pass=passed,N=n,dx_m=dx,kinetic_spectral_radius_per_m=rho,constant_field_error=constant_error,constant_norm_error=constant_norm_error,dense_semigroup_error=semigroup,dense_norm_error=reference_norm_error,reference_projection=ref_projection,rows=rows,observed_field_orders=orders,order_is_diagnostic_only=True,elapsed_s=time.monotonic()-start,source_sha256={str(p):sha(p) for p in (Path(__file__).resolve(),ROOT/'scripts/point03_fdst.py',ROOT/'scripts/run_point03_exponential.py',ROOT/'Docs/POINT-03-FDST-SCALE-DIAGNOSTIC-CONTRACT.md')})

if __name__=='__main__':
    result=run();write(ROOT/'resultados/codex/point03_fdst_scale_diagnostic_20261007.json',result);print(json.dumps(result));raise SystemExit(0 if result['controls_pass'] else 1)
