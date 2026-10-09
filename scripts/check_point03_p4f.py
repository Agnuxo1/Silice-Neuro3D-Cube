"""Circular weak detector and physical Gaussian projection controls."""
import argparse
from datetime import datetime,timezone
import json
import math
import os
from pathlib import Path
import time
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import meshio
import numpy as np
import psutil
from scipy.sparse import load_npz,save_npz,diags
from scipy.sparse.linalg import splu
from skfem import Basis,ElementTriP2,LinearForm
from skfem.io import from_meshio
from point03_fem_detector import R,assemble,curved_outside,shapes
from run_point03_exponential import ROOT,sha,write


def jacobian_minima(mapping):
    pts=np.array([[0.,1.,0.,.5,0.,.5],[0.,0.,1.,0.,.5,.5]])
    values=mapping.detDF(pts);sign=np.sign(values[:,0]);values*=sign[:,None]
    f=values[:,0];a=2*(values[:,1]+f-2*values[:,3]);d=values[:,1]-f-a
    c=2*(values[:,2]+f-2*values[:,4]);e=values[:,2]-f-c;b=4*(values[:,5]-f-.25*a-.25*c-.5*d-.5*e)
    result=np.min(values[:,:3],axis=1)
    for aa,dd,ff in ((a,d,f),(c,e,f),(a-b+c,b-2*c+d-e,c+e+f)):
        x=np.divide(-dd,2*aa,out=np.full_like(aa,-1.),where=aa>0)
        result=np.minimum(result,np.where((aa>0)&(x>0)&(x<1),aa*x*x+dd*x+ff,np.inf))
    det=4*a*c-b*b
    x=np.divide(b*e-2*c*d,det,out=np.full_like(a,-1.),where=abs(det)>0)
    y=np.divide(b*d-2*a*e,det,out=np.full_like(a,-1.),where=abs(det)>0)
    result=np.minimum(result,np.where((x>0)&(y>0)&(x+y<1),a*x*x+b*x*y+c*y*y+d*x+e*y+f,np.inf))
    assert np.all(result>0);return result


def run(out):
    assert not out.exists();out.mkdir();start=time.monotonic()
    assert psutil.virtual_memory().available>2*1024**3 and psutil.disk_usage(str(out)).free>2*1024**3
    source=ROOT/'resultados/codex/point03_p4c_mesh_20261008';prior=json.loads((source/'report_recovered.json').read_text());assert prior['integrity_pass']
    for name,digest in prior['artifact_sha256'].items():assert sha(source/name)==digest
    raw=meshio.read(source/'T96_curved.msh');raw.points*=1e-6
    mesh=from_meshio(raw,force_meshio_type='triangle6',ignore_orientation=True);basis=Basis(mesh,ElementTriP2(),intorder=8)
    geometry=curved_outside(basis);M=load_npz(source/'mass.npz');Cs=[];weights=[];statistics=[]
    for q in (16,32):
        C,w,stats=assemble(basis,q);Cs.append(C);weights.append(w);statistics.append(stats)
        save_npz(out/f'core_q{q}.npz',C);np.save(out/f'intensity_q{q}.npy',w)
        assert time.monotonic()-start<=1800
    refshape=shapes(basis.X)[0];refmass=(refshape*basis.W)@refshape.T;reference_min=float(np.linalg.eigvalsh(refmass).min());assert reference_min>0
    local_min=jacobian_minima(basis.mapping)*reference_min;lower=np.zeros(basis.N)
    np.add.at(lower,basis.element_dofs.ravel(order='F'),np.repeat(local_min,6));assert np.all(lower>0)
    scale=diags(1/np.sqrt(lower));delta=scale@(Cs[1]-Cs[0])@scale
    qbound=float(np.asarray(abs(delta).sum(axis=1)).max());assert qbound<=1e-10
    area=math.pi*R**2;C=Cs[1];w=weights[1];assert w.min()>=-1e-20
    assert abs(float(w.sum())/area-1)<=1e-10
    x,y=basis.doflocs/R;assert abs(float(w@x)/area)<=1e-10 and abs(float(w@y)/area)<=1e-10
    rng=np.random.default_rng(957);controls=[]
    for _ in range(6):
        coefficients=rng.normal(size=3)+1j*rng.normal(size=3);field=coefficients[0]+coefficients[1]*x+coefficients[2]*y
        exact=area*(abs(coefficients[0])**2+(abs(coefficients[1])**2+abs(coefficients[2])**2)/4)
        value=float(np.vdot(field,C@field).real);error=abs(value-exact)/area
        assert error<=1e-10
        controls.append(dict(error_scaled_by_area=error,field_integral=value,exact=exact,intensity_integral=float(w@abs(field)**2)))
    for _ in range(12):
        field=rng.normal(size=basis.N)+1j*rng.normal(size=basis.N)
        power=float(np.vdot(field,C@field).real);total=float(np.vdot(field,M@field).real)
        assert power>=-1e-10*total and power<=total*(1+1e-10)
    with np.load(source/'mesh_arrays.npz',allow_pickle=False) as data:boundary=data['boundary_dofs'].copy()
    free=np.setdiff1d(np.arange(basis.N),boundary);mf=M[free,:][:,free].tocsc();factor=splu(mf)
    initials=[];norms=[]
    @LinearForm
    def gaussian(v,ww):return math.sqrt(2/math.pi)/6e-6*np.exp(-(ww.x[0]**2+ww.x[1]**2)/(6e-6)**2)*v
    for q in (12,16):
        b=Basis(mesh,ElementTriP2(),intorder=q);rhs=gaussian.assemble(b)
        field=np.zeros(basis.N,dtype=np.complex128);field[free]=factor.solve(rhs[free]);norm=float(np.vdot(field,M@field).real);norms.append(norm);field/=math.sqrt(norm);initials.append(field)
        np.savez(out/f'gaussian_q{q}.npz',field=field,free_dofs=free)
    change=initials[0]-initials[1];input_error=math.sqrt(float(np.vdot(change,M@change).real));assert input_error<=1e-9
    f=initials[1];power=float(np.vdot(f,C@f).real);intensity=float(w@abs(f)**2)
    report=dict(created_utc=datetime.now(timezone.utc).isoformat(),controls_pass=True,geometry=geometry,quadrature_mass_norm_bound=qbound,statistics=statistics,polynomial_controls=controls,input_quadrature_field_difference=input_error,input_projection_norm_before_scaling=norms,initial_core_field=power,initial_core_intensity=intensity,Gaussian_continuum_core=1-math.exp(-2),initial_projection_core_error=abs(power-(1-math.exp(-2))),no_T96_propagation=True,point03_closed=False,elapsed_s=time.monotonic()-start,source_sha256={str(path):sha(path) for path in (Path(__file__),ROOT/'scripts/point03_fem_detector.py',ROOT/'Docs/POINT-03-P4F-CONTRACT.md')},artifacts={path.name:sha(path) for path in out.iterdir() if path.is_file()})
    write(out/'report.json',report);print(json.dumps({key:report[key] for key in ('controls_pass','quadrature_mass_norm_bound','statistics','input_quadrature_field_difference','initial_projection_core_error','elapsed_s','point03_closed')}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args();run(args.out.resolve())
