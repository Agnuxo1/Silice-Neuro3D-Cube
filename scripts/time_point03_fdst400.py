"""Manufactured N400 timing before a separate direct-accuracy contrast."""
from datetime import datetime,timezone
import json
import math
from pathlib import Path
import time
from run_point03_exponential import ROOT,sha,write
import numpy as np
from point03_fdst import Solver
n=400;dx=128e-6/n;dz=.002/6400;steps=100;j=np.arange(1,n+1)
field=(np.sin(384*math.pi*j/(n+1))[:,None]*np.sin(382*math.pi*j/(n+1))[None,:]).astype(np.complex128)
beta=1.444*2*math.pi/1550e-9;c=1j/(2*beta*dx*dx)
eigen=c*(2*math.cos(384*math.pi/(n+1))+2*math.cos(382*math.pi/(n+1))-4)
solver=Solver(np.zeros((n,n)),np.zeros((n,n)),dx,dz);start=time.monotonic();actual=solver.advance(field.copy(),steps);elapsed=time.monotonic()-start
exact=np.exp(dz*steps*eigen)*field;error=float(np.linalg.norm(actual-exact)/np.linalg.norm(exact));passed=error<=1e-10 and elapsed<=120 and np.all(np.isfinite(actual))
r=dict(created_utc=datetime.now(timezone.utc).isoformat(),manufactured_only=True,no_T96_propagation=True,pass_=bool(passed),N=n,steps=steps,dz_m=dz,elapsed_s=elapsed,seconds_per_step=elapsed/steps,field_relative_error=error,source_sha256={str(p):sha(p) for p in (Path(__file__).resolve(),ROOT/'scripts/point03_fdst.py',ROOT/'scripts/run_point03_exponential.py',ROOT/'Docs/POINT-03-FDST-400-TIMING-CONTRACT.md')})
write(ROOT/'resultados/codex/point03_fdst400_timing_20261007.json',r);print(json.dumps(r));raise SystemExit(0 if passed else 1)
