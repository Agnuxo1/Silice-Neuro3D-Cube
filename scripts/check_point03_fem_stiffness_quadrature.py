"""Audit curvature quadrature without replacing any historical matrix."""
import argparse
from datetime import datetime,timezone
import math
import os
from pathlib import Path
import time
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import meshio
import numpy as np
import psutil
from scipy.sparse import diags,load_npz,save_npz
from skfem import Basis,ElementTriP2
from skfem.io import from_meshio
from skfem.models.poisson import laplace
from check_point03_p4f import jacobian_minima
from point03_fem_detector import shapes
from run_point03_exponential import ROOT,sha,write
from audit_point03_p4i import read


def run(label,out):
    assert not out.exists() and out.is_relative_to(ROOT/'resultados/codex')
    # Prevent a second numerical job from competing with the active reference.
    assert (ROOT/'resultados/codex/point03_p4i3_recovery_20261008/execution.json').exists()
    assert psutil.virtual_memory().available>=5*1024**3 and psutil.disk_usage(str(out.parent)).free>2*1024**3
    paths={'prototype':('point03_p4c_mesh_20261008','point03_p4f_detector_20261008'),
           'coarse':('point03_p5a_mesh_coarse_20261008','point03_p5b_detector_coarse_20261008'),
           'mid':('point03_p5a_mesh_mid_20261008','point03_p5b_detector_mid_20261008')}
    geom,det=[ROOT/'resultados/codex'/p for p in paths[label]]
    record=geom/('report_recovered.json' if label=='prototype' else 'report.json')
    prior=read(record);digests=prior['artifact_sha256'] if label=='prototype' else prior['hashes']
    for name,digest in digests.items():assert sha(geom/name)==digest
    out.mkdir();start=time.monotonic()
    raw=meshio.read(geom/'T96_curved.msh');raw.points*=1e-6
    mesh=from_meshio(raw,force_meshio_type='triangle6',ignore_orientation=True)
    with np.load(geom/'mesh_arrays.npz',allow_pickle=False) as data:
        saved_coords=data['doflocs'].copy();saved_elements=data['element_dofs'].copy()
    with np.load(det/'gaussian_q16.npz',allow_pickle=False) as data:free=data['free_dofs'].copy()
    old=load_npz(geom/'stiffness.npz');matrices={};controls={};lower=None
    area=(128e-6)**2
    for q in (8,12,16):
        basis=Basis(mesh,ElementTriP2(),intorder=q)
        assert np.array_equal(basis.doflocs,saved_coords) and np.array_equal(basis.element_dofs,saved_elements)
        K=laplace.assemble(basis);delta=K-K.T
        symmetry=float(np.max(abs(delta.data))/np.max(abs(K.data))) if delta.nnz else 0.
        constant=float(np.max(abs(K@np.ones(basis.N))))
        x,y=basis.doflocs
        ex=float(x@(K@x));ey=float(y@(K@y));cross=float(x@(K@y))
        assert symmetry<=1e-12 and constant<=1e-10
        assert max(abs(ex/area-1),abs(ey/area-1),abs(cross)/area)<=1e-10
        controls[str(q)]=dict(symmetry=symmetry,constant_residual=constant,energy_x_m2=ex,energy_y_m2=ey,
                              exact_linear_energy_m2=area,cross_m2=cross,quadrature_points=len(basis.W))
        save_npz(out/f'stiffness_q{q}.npz',K)
        if q==8:
            reproduction=K-old
            reproduction_error=float(np.max(abs(reproduction.data))/np.max(abs(old.data))) if reproduction.nnz else 0.
            assert reproduction_error<=1e-13
            refshape=shapes(basis.X)[0];refmass=(refshape*basis.W)@refshape.T
            reference_min=float(np.linalg.eigvalsh(refmass).min());assert reference_min>0
            local=jacobian_minima(basis.mapping)*reference_min;lower=np.zeros(basis.N)
            np.add.at(lower,basis.element_dofs.ravel(order='F'),np.repeat(local,6));assert np.all(lower>0)
        matrices[q]=K[free,:][:,free]
        del basis,K
        assert time.monotonic()-start<=900 and psutil.virtual_memory().available>3*1024**3
    scale=diags(1/np.sqrt(lower[free]));C=load_npz(det/'core_q32.npz')[free,:][:,free]
    w=np.load(det/'intensity_q32.npy',allow_pickle=False)[free]
    detector_bounds=dict(field=float(np.asarray(abs(scale@C@scale).sum(axis=1)).max()),intensity=float(np.max(w/lower[free])))
    beta=1.444*2*math.pi/1550e-9;rows={}
    for q in (8,12):
        delta=scale@(matrices[q]-matrices[16])@scale
        generator_bound=float(np.asarray(abs(delta).sum(axis=1)).max())/(2*beta)
        eta=.002*generator_bound
        power_bounds={method:2*value*eta for method,value in detector_bounds.items()}
        rows[f'{q}_vs_16']=dict(generator_mass_norm_bound_m_inverse=generator_bound,field_mass_norm_bound=eta,
                               observable_power_bounds=power_bounds,conservative_consistency_pass=eta<=1e-6 and max(power_bounds.values())<=1e-5)
    sources=[Path(__file__).resolve(),ROOT/'Docs/POINT-03-FEM-STIFFNESS-QUADRATURE-CONTRACT.md',ROOT/'scripts/check_point03_p4f.py',
             ROOT/'scripts/point03_fem_detector.py',record,geom/'T96_curved.msh',geom/'mesh_arrays.npz',geom/'stiffness.npz',
             geom/'mass.npz',det/'core_q32.npz',det/'intensity_q32.npy',det/'gaussian_q16.npz']
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),assembly_controls_pass=True,label=label,controls=controls,
                reproduction_relative_error=reproduction_error,detector_mass_operator_upper_bounds=detector_bounds,pairs=rows,
                source_sha256={str(p):sha(p) for p in sources},artifacts={p.name:sha(p) for p in out.iterdir() if p.is_file()},
                elapsed_s=time.monotonic()-start,point03_closed=False,no_new_propagation=True)
    write(out/'report.json',result);print(dict(label=label,assembly_controls_pass=True,pairs=rows,elapsed_s=result['elapsed_s']))


if __name__=='__main__':
    p=argparse.ArgumentParser(__doc__);p.add_argument('--mesh',choices=('prototype','coarse','mid'),required=True)
    p.add_argument('--out',type=Path,required=True);args=p.parse_args();run(args.mesh,args.out.resolve())
