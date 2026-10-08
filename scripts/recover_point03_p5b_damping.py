"""Verify completed coarse damping artifacts after diagnostic shape mismatch."""
import argparse
import json
import math
from datetime import datetime,timezone
from pathlib import Path
import meshio
import numpy as np
from scipy.sparse import load_npz,diags
from skfem import Basis,ElementTriP2
from skfem.io import from_meshio
from check_point03_p4f import jacobian_minima
from point03_fem_detector import shapes
from run_point03_exponential import sha,write


def recover(geometry,out):
    assert not (out/'report.json').exists() and (out/'damping_q8.npz').exists() and (out/'damping_q12.npz').exists()
    prior=json.loads((geometry/'report.json').read_text());assert prior['controls_pass']
    for name,digest in prior['hashes'].items():assert sha(geometry/name)==digest
    raw=meshio.read(geometry/'T96_curved.msh');raw.points*=1e-6
    mesh=from_meshio(raw,force_meshio_type='triangle6',ignore_orientation=True);basis=Basis(mesh,ElementTriP2(),intorder=8)
    A=load_npz(out/'damping_q8.npz');D=load_npz(out/'damping_q12.npz');assert A.shape==D.shape==(basis.N,basis.N)
    ref=shapes(basis.X)[0];lowest=float(np.linalg.eigvalsh((ref*basis.W)@ref.T).min());lower=np.zeros(basis.N)
    np.add.at(lower,basis.element_dofs.ravel(order='F'),np.repeat(jacobian_minima(basis.mapping)*lowest,6));scale=diags(1/np.sqrt(lower));bound=float(np.asarray(abs(scale@(D-A)@scale).sum(axis=1)).max());assert bound<=1e-6
    delta=D-D.T;assert not delta.nnz or max(abs(delta.data))/max(abs(D.data))<=1e-12
    a=51.2;d=12.8;S=4e4;R=64.;exact0=8*S*d*(a/5+d/6)*1e-12;exact2=(16/3)*S*d*(a**3/5+3*a*a*d/6+3*a*d*d/7+d**3/8)*1e-12/R**2
    assert abs(float(D.sum())/exact0-1)<=1e-10
    x,y=basis.doflocs/(64e-6);rng=np.random.default_rng(967);errors=[]
    for _ in range(6):
        c=rng.normal(size=3)+1j*rng.normal(size=3);f=c[0]+c[1]*x+c[2]*y;exact=abs(c[0])**2*exact0+(abs(c[1])**2+abs(c[2])**2)*exact2
        error=abs(float(np.vdot(f,D@f).real)-exact)/exact0;assert error<=1e-10;errors.append(error)
    for _ in range(12):
        f=rng.normal(size=basis.N)+1j*rng.normal(size=basis.N);assert np.vdot(f,D@f).real>=-1e-12*exact0
    report=dict(created_utc=datetime.now(timezone.utc).isoformat(),controls_pass=True,recovered=True,matrices_regenerated=False,reporting_error='Prior optional comparison subtracted different mesh dimensions; scientific checks completed; now independently rechecked.',old_unsplit_difference_bound_m_inverse=None,quadrature_mass_norm_bound_m_inverse=bound,constant_integral=float(D.sum()),constant_exact=exact0,linear_field_errors=errors,no_T96_propagation=True,point03_closed=False,artifacts={p.name:sha(p) for p in out.iterdir() if p.is_file()})
    write(out/'report_recovered.json',report);print(json.dumps({k:report[k] for k in ('controls_pass','quadrature_mass_norm_bound_m_inverse','matrices_regenerated','point03_closed')}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--geometry',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();recover(a.geometry.resolve(),a.out.resolve())
