"""Known high sine eigenmode and cost before preparing the blind fixed-domain input."""
from datetime import datetime,timezone
import hashlib
import json
import math
import os
from pathlib import Path
import time
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import numpy as np
from point03_fdst import Solver
from run_point03_exponential import ROOT,write

n=799;dx=128e-6/800;dz=.002/25600;j=np.arange(1,n+1)
start=time.monotonic()
field=(np.sin(783*math.pi*j/(n+1))[:,None]*np.sin(781*math.pi*j/(n+1))[None,:]).astype(np.complex128)
zero=np.zeros((n,n));solver=Solver(zero,zero,dx,dz)
before=time.monotonic();actual=solver.advance(field.copy(),100);elapsed=time.monotonic()-before
k0=2*math.pi/1550e-9
eigenvalue=(-4*math.sin(783*math.pi/(2*(n+1)))**2-4*math.sin(781*math.pi/(2*(n+1)))**2)/(2*1.444*k0*dx**2)
exact=field*np.exp(1j*eigenvalue*dz*100)
error=float(np.linalg.norm(actual-exact)/np.linalg.norm(exact))
passed=error<=1e-10 and time.monotonic()-start<=200 and elapsed/100*25600<=12000
report=dict(created_utc=datetime.now(timezone.utc).isoformat(),pass_=passed,N=n,dx_m=dx,dz_m=dz,steps=100,field_error=error,advance_elapsed_s=elapsed,forecast_full_FDST_s=elapsed/100*25600,no_T96_geometry_or_propagation=True,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
write(ROOT/'resultados/codex/point03_p2_cost_20261007.json',report)
print(json.dumps(report));raise SystemExit(0 if passed else 1)
