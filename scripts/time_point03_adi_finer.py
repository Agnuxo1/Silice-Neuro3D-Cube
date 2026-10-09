"""Manufactured ADI cost; analytical discrete Cayley reference."""
from datetime import datetime,timezone
import json
import math
import os
from pathlib import Path
import time
for variable in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[variable]='1'
from run_point03_exponential import ROOT,sha,write,guard,load
import numpy as np
assert json.loads((ROOT/'resultados/codex/point03_fdst_accuracy_20261007_L2/execution.json').read_text(encoding='utf-8'))['status']=='completed'
n=767;dx=128e-6/n;dz=.002/32000;steps=100;j=np.arange(1,n+1)
field=(np.sin(math.pi*j/(n+1))[:,None]*np.sin(2*math.pi*j/(n+1))[None,:]).astype(np.complex128)
source=ROOT/'experimentos/glass009_claude/adi2d.py';backend=ROOT/'scripts/point03_sparse_adi.py'
adi=load('finer_cost_adi',source);sparse=load('finer_cost_sparse',backend)
cls=sparse.make_sparse_stepper(adi.Stepper)
assert cls.step is adi.Stepper.step and cls._lap is adi.Stepper._lap and cls.__init__ is adi.Stepper.__init__
resources=[guard(ROOT/'resultados/codex')];start=time.monotonic()
stepper=cls(np.zeros((n,n)),np.zeros((n,n)),dx,dz);setup=time.monotonic()-start
actual=field.copy();advance_start=time.monotonic()
for _ in range(steps):actual=stepper.step(actual)
elapsed=time.monotonic()-advance_start;total=time.monotonic()-start
beta=1.444*2*math.pi/1550e-9
factor=1.
for mode in (1,2):
    eigen=1j/(2*beta*dx*dx)*(-4*math.sin(mode*math.pi/(2*(n+1)))**2)
    factor*=((1+dz/2*eigen)/(1-dz/2*eigen))**steps
error=float(np.linalg.norm(actual-factor*field)/np.linalg.norm(field));resources.append(guard(ROOT/'resultados/codex'))
passed=bool(error<=1e-10 and total<=180 and np.all(np.isfinite(actual)))
paths=[Path(__file__).resolve(),source,backend,ROOT/'Docs/POINT-03-ADI-FINER-COST-CONTRACT.md']
result=dict(created_utc=datetime.now(timezone.utc).isoformat(),manufactured_only=True,no_T96_propagation=True,N=n,dz_m=dz,steps=steps,setup_s=setup,advance_s=elapsed,total_s=total,seconds_per_step=elapsed/steps,field_relative_error=error,pass_=passed,forecasts_s={str(count):setup+elapsed/steps*count for count in (32000,64000)},resources=resources,factor_metadata=stepper.sparse_metadata(),source_sha256={str(path):sha(path) for path in paths})
write(ROOT/'resultados/codex/point03_adi_finer_cost_20261007.json',result)
print(json.dumps({key:result[key] for key in ('N','pass_','total_s','seconds_per_step','field_relative_error','forecasts_s')}),flush=True)
raise SystemExit(0 if passed else 1)
