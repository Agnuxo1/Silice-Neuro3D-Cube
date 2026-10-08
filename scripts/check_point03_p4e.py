"""Viability of generalized weak T96 propagation; no Gaussian/core measurement."""
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
from scipy.sparse import load_npz,save_npz
from skfem import Basis,ElementTriP2,BilinearForm
from skfem.io import from_meshio
from point03_fem_time import Pade6
from run_point03_exponential import ROOT,sha,write


def run(out):
    assert not out.exists();out.mkdir();start=time.monotonic()
    assert psutil.virtual_memory().available>3*1024**3 and psutil.disk_usage(str(out)).free>2*1024**3
    source=ROOT/'resultados/codex/point03_p4c_mesh_20261008';prior=json.loads((source/'report_recovered.json').read_text())
    assert prior['integrity_pass'] and prior['geometry_and_assembly_controls_pass']
    for name,digest in prior['artifact_sha256'].items():assert sha(source/name)==digest
    raw=meshio.read(source/'T96_curved.msh');raw.points*=1e-6
    mesh=from_meshio(raw,force_meshio_type='triangle6',ignore_orientation=True);basis=Basis(mesh,ElementTriP2(),intorder=8)
    @BilinearForm
    def damping(u,v,w):
        r=np.maximum(abs(w.x[0]),abs(w.x[1]))/64e-6
        sigma=4e4*np.maximum((r-.8)/.2,0)**4
        return sigma*u*v
    D=damping.assemble(basis)
    M=load_npz(source/'mass.npz');K=load_npz(source/'stiffness.npz');C=load_npz(source/'cladding_mass.npz')
    assert all((matrix-matrix.T).nnz==0 for matrix in (M,K,C,D))
    with np.load(source/'mesh_arrays.npz',allow_pickle=False) as data:boundary=data['boundary_dofs'].copy()
    free=np.setdiff1d(np.arange(basis.N),boundary)
    mass=M[free,:][:,free].tocsc();k0=2*math.pi/1550e-9;beta=1.444*k0
    generator=(-1j*K/(2*beta)-1j*k0*.003*C-D)[free,:][:,free].tocsc()
    x,y=basis.doflocs[:,free];initial=(np.sin(math.pi*(x+64e-6)/128e-6)*np.sin(math.pi*(y+64e-6)/128e-6)).astype(complex)
    initial/=math.sqrt(float(np.vdot(initial,mass@initial).real))
    timings=[];fields=[]
    for steps,dt in ((100,.002/8192),(200,.002/16384)):
        before=time.monotonic();solver=Pade6(mass,generator,dt);factor_time=time.monotonic()-before
        memory=sum(factor.L.data.nbytes+factor.L.indices.nbytes+factor.L.indptr.nbytes+factor.U.data.nbytes+factor.U.indices.nbytes+factor.U.indptr.nbytes for factor,right in solver.factors)
        before=time.monotonic();field=solver.advance(initial,steps);advance=time.monotonic()-before
        power=float(np.vdot(field,mass@field).real);assert np.all(np.isfinite(field)) and 0<power<=1+1e-9
        fields.append(field);timings.append(dict(steps=steps,dt_m=dt,factor_elapsed_s=factor_time,advance_elapsed_s=advance,seconds_per_step=advance/steps,physical_power=power,factor_memory_bytes=memory))
        np.savez(out/f'field_steps{steps}.npz',field=field,initial=initial,free_dofs=free)
        assert time.monotonic()-start<=600
    difference=fields[0]-fields[1]
    relative=math.sqrt(float(np.vdot(difference,mass@difference).real)/float(np.vdot(fields[1],mass@fields[1]).real))
    forecast=timings[0]['seconds_per_step']*8192
    save_npz(out/'damping.npz',D)
    report=dict(created_utc=datetime.now(timezone.utc).isoformat(),controls_pass=relative<=1e-5 and forecast<=7200,field_relative_difference=relative,forecast8192_s=forecast,timings=timings,elapsed_s=time.monotonic()-start,Gaussian_T96_propagated=False,core_power_measured=False,point03_closed=False,source_sha256={str(path):sha(path) for path in (Path(__file__),ROOT/'scripts/point03_fem_time.py',ROOT/'Docs/POINT-03-P4E-CONTRACT.md')},artifacts={path.name:sha(path) for path in out.iterdir() if path.is_file()})
    write(out/'report.json',report);print(json.dumps({key:report[key] for key in ('controls_pass','field_relative_difference','forecast8192_s','timings','elapsed_s','point03_closed')}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args();run(args.out.resolve())
