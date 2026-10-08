"""Analytical square moments and conservative normalized damping comparison."""
import argparse
from datetime import datetime,timezone
import math
import os
import json
from pathlib import Path
import time
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import meshio
import numpy as np
from scipy.sparse import load_npz,save_npz,diags
from skfem import Basis,ElementTriP2
from skfem.io import from_meshio
from point03_fem_detector import shapes
from check_point03_p4f import jacobian_minima
from point03_fem_damping import assemble
from run_point03_exponential import ROOT,sha,write


def run(out):
    assert not out.exists();out.mkdir();start=time.monotonic();base=ROOT/'resultados/codex/point03_p4c_mesh_20261008'
    prior=json.loads((base/'report_recovered.json').read_text());assert prior['integrity_pass']
    for name,digest in prior['artifact_sha256'].items():assert sha(base/name)==digest
    raw=meshio.read(base/'T96_curved.msh');raw.points*=1e-6
    mesh=from_meshio(raw,force_meshio_type='triangle6',ignore_orientation=True);basis=Basis(mesh,ElementTriP2(),intorder=8)
    matrices=[];counts=[]
    for q in (8,12):
        D,count=assemble(basis,q);save_npz(out/f'damping_q{q}.npz',D);matrices.append(D);counts.append(count)
        assert time.monotonic()-start<=600
    ref=shapes(basis.X)[0];lowest=float(np.linalg.eigvalsh((ref*basis.W)@ref.T).min())
    lower=np.zeros(basis.N);np.add.at(lower,basis.element_dofs.ravel(order='F'),np.repeat(jacobian_minima(basis.mapping)*lowest,6));scale=diags(1/np.sqrt(lower))
    def bound(delta):return float(np.asarray(abs(scale@delta@scale).sum(axis=1)).max())
    comparison=bound(matrices[1]-matrices[0]);assert comparison<=1e-6
    D=matrices[1];delta=D-D.T;assert not delta.nnz or max(abs(delta.data))/max(abs(D.data))<=1e-12
    a=51.2;d=12.8;S=4e4;R=64.
    exact0=8*S*d*(a/5+d/6)*1e-12
    exact2=(16/3)*S*d*(a**3/5+3*a*a*d/6+3*a*d*d/7+d**3/8)*1e-12/R**2
    assert abs(float(D.sum())/exact0-1)<=1e-10
    x,y=basis.doflocs/(64e-6);rng=np.random.default_rng(967);errors=[]
    for _ in range(6):
        c=rng.normal(size=3)+1j*rng.normal(size=3);field=c[0]+c[1]*x+c[2]*y
        exact=abs(c[0])**2*exact0+(abs(c[1])**2+abs(c[2])**2)*exact2
        error=abs(float(np.vdot(field,D@field).real)-exact)/exact0;assert error<=1e-10;errors.append(error)
    for _ in range(12):
        field=rng.normal(size=basis.N)+1j*rng.normal(size=basis.N);assert np.vdot(field,D@field).real>=-1e-12*exact0
    old=load_npz(ROOT/'resultados/codex/point03_p4e_cost_20261008/damping.npz')
    report=dict(created_utc=datetime.now(timezone.utc).isoformat(),controls_pass=True,active_elements=counts,quadrature_mass_norm_bound_m_inverse=comparison,old_unsplit_difference_bound_m_inverse=bound(D-old),constant_integral=float(D.sum()),constant_exact=exact0,linear_field_errors=errors,elapsed_s=time.monotonic()-start,no_T96_propagation=True,point03_closed=False,source_sha256={str(path):sha(path) for path in (Path(__file__),ROOT/'scripts/point03_fem_damping.py',ROOT/'Docs/POINT-03-P4G-CONTRACT.md')},artifacts={p.name:sha(p) for p in out.iterdir() if p.is_file()})
    write(out/'report.json',report);print(json.dumps({k:report[k] for k in ('controls_pass','active_elements','quadrature_mass_norm_bound_m_inverse','old_unsplit_difference_bound_m_inverse','elapsed_s','point03_closed')}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args();run(args.out.resolve())
