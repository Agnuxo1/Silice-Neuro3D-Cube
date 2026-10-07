"""Independent symmetric diagonalization check, manufactured zero absorption only."""
from datetime import datetime,timezone
import json
import math
from pathlib import Path
from run_point03_exponential import ROOT,operator,sha,write
import numpy as np
from scipy.linalg import eigh,expm

p=ROOT/'resultados/codex/point03_fdst_scale_diagnostic_20261007.json';prior=json.loads(p.read_text(encoding='utf-8'))
for path,digest in prior['source_sha256'].items():assert sha(path)==digest
n=9;dx=prior['dx_m'];z=.002;j=np.arange(1,n+1)
initial=(np.sin(math.pi*j/(n+1))[:,None]*np.sin(2*math.pi*j/(n+1))[None,:]).astype(np.complex128)
norm=float(np.vdot(initial,initial).real);board=-.003*((np.indices((n,n)).sum(axis=0)%2).astype(float))
matrix,_=operator(board,np.zeros((n,n)),dx);dense=matrix.toarray();assert np.max(np.abs(dense.real))==0
h=dense.imag;assert np.array_equal(h,h.T)
values,vectors=eigh(h,driver='evd');spectral=vectors@(np.exp(1j*z*values)*(vectors.T@initial.ravel()));pade=expm(z*dense)@initial.ravel()
residual=float(np.linalg.norm(h@vectors-vectors*values)/np.linalg.norm(h));orthogonality=float(np.linalg.norm(vectors.T@vectors-np.eye(n*n)))
field_error=float(np.linalg.norm(spectral-pade)/np.linalg.norm(pade));projection=float(abs(np.vdot(initial.ravel(),spectral))**2/norm**2)
projection_error=abs(projection-prior['reference_projection']);norm_error=abs(float(np.vdot(spectral,spectral).real/norm)-1)
gates=dict(eigen_residual=residual<=1e-13,orthogonality=orthogonality<=1e-13,field=field_error<=1e-9,projection=projection_error<=1e-9,norm=norm_error<=1e-9)
r=dict(created_utc=datetime.now(timezone.utc).isoformat(),manufactured_only=True,no_T96_propagation=True,point03_closed=False,oracle_audit_pass=all(gates.values()),gates=gates,eigen_residual=residual,orthogonality=orthogonality,field_difference=field_error,projection_difference=projection_error,norm_error=norm_error,prior_path=str(p),prior_sha256=sha(p),source_sha256={str(q):sha(q) for q in (Path(__file__).resolve(),ROOT/'scripts/run_point03_exponential.py',ROOT/'Docs/POINT-03-FDST-DENSE-ORACLE-CONTRACT.md')})
write(ROOT/'resultados/codex/point03_fdst_dense_oracle_audit_20261007.json',r);print(json.dumps(r));raise SystemExit(0 if r['oracle_audit_pass'] else 1)
