"""Positive high quadrature, streamed over immutable curved FEM meshes."""
import argparse
from datetime import datetime,timezone
import gc
import math
import os
from pathlib import Path
import time
import traceback
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import meshio
import numpy as np
import psutil
from scipy.sparse import csr_matrix,diags,load_npz,save_npz
from scipy.special import roots_legendre
from skfem import Basis,ElementTriP2
from skfem.io import from_meshio
from skfem.models.poisson import laplace
from check_point03_p4f import jacobian_minima
from point03_fem_detector import shapes
from run_point03_exponential import ROOT,sha,write
from audit_point03_p4i import read


def rule(n):
    nodes,weights=roots_legendre(n);s=(nodes+1)/2;w=weights/2
    X,Y=np.meshgrid(s,s,indexing='ij');W1,W2=np.meshgrid(w,w,indexing='ij')
    points=np.array([X.ravel(),((1-X)*Y).ravel()]);weight=((1-X)*W1*W2).ravel()
    assert weight.min()>0 and abs(weight.sum()-.5)<=1e-13
    maximum=0.
    for i in range(11):
        for j in range(11-i):
            truth=math.factorial(i)*math.factorial(j)/math.factorial(i+j+2)
            maximum=max(maximum,abs(float(weight@(points[0]**i*points[1]**j))-truth))
    assert maximum<=1e-13
    return (points,weight),dict(points_per_axis=n,total_points=len(weight),maximum_moment_absolute_error=maximum)


def run(label,out):
    assert not out.exists() and out.is_relative_to(ROOT/'resultados/codex')
    assert (ROOT/'resultados/codex/point03_p4i3_recovery2_20261008/execution.json').exists()
    out.mkdir();start=time.monotonic();report=dict(status='failed',created_utc=datetime.now(timezone.utc).isoformat(),label=label,
                                                 point03_closed=False,no_new_propagation=True)
    try:
        report['resource_start']=dict(available_ram_bytes=psutil.virtual_memory().available,free_disk_bytes=psutil.disk_usage(str(out)).free)
        assert report['resource_start']['available_ram_bytes']>=3.5*1024**3 and report['resource_start']['free_disk_bytes']>2*1024**3
        paths={'prototype':('point03_p4c_mesh_20261008','point03_p4f_detector_20261008'),
               'coarse':('point03_p5a_mesh_coarse_20261008','point03_p5b_detector_coarse_20261008'),
               'mid':('point03_p5a_mesh_mid_20261008','point03_p5b_detector_mid_20261008')}
        geom,det=[ROOT/'resultados/codex'/p for p in paths[label]]
        record=geom/('report_recovered.json' if label=='prototype' else 'report.json');prior=read(record)
        for name,digest in (prior['artifact_sha256'] if label=='prototype' else prior['hashes']).items():assert sha(geom/name)==digest
        raw=meshio.read(geom/'T96_curved.msh');raw.points*=1e-6
        mesh=from_meshio(raw,force_meshio_type='triangle6',ignore_orientation=True)
        with np.load(geom/'mesh_arrays.npz',allow_pickle=False) as data:
            coords=data['doflocs'].copy();ed=data['element_dofs'].copy()
        with np.load(det/'gaussian_q16.npz',allow_pickle=False) as data:free=data['free_dofs'].copy()
        old=load_npz(geom/'stiffness.npz');N=old.shape[0];area=(128e-6)**2;matrices={};controls={};quadrature_controls={}
        probe=Basis(mesh,ElementTriP2(),intorder=8,elements=np.array([0],dtype=np.int32))
        assert np.array_equal(probe.doflocs,coords)
        refshape=shapes(probe.X)[0];refmass=(refshape*probe.W)@refshape.T;reference_min=float(np.linalg.eigvalsh(refmass).min())
        assert reference_min>0;local=jacobian_minima(probe.mapping)*reference_min;lower=np.zeros(N)
        np.add.at(lower,ed.ravel(order='F'),np.repeat(local,6));assert np.all(lower>0)
        del probe;gc.collect()
        for labelq in ('tri8','duffy12','duffy16','duffy24'):
            quadrature=None
            if labelq!='tri8':quadrature,quadrature_controls[labelq]=rule(int(labelq[5:]))
            K=csr_matrix((N,N),dtype=np.float64)
            for first in range(0,mesh.nelements,256):
                indices=np.arange(first,min(first+256,mesh.nelements),dtype=np.int32)
                basis=Basis(mesh,ElementTriP2(),elements=indices,**({'intorder':8} if quadrature is None else {'quadrature':quadrature}))
                assert np.array_equal(basis.element_dofs,ed[:,indices])
                K=K+laplace.assemble(basis)
                del basis
                assert time.monotonic()-start<=1800 and psutil.virtual_memory().available>3*1024**3
            delta=K-K.T;symmetry=float(np.max(abs(delta.data))/np.max(abs(K.data))) if delta.nnz else 0.
            constant=float(np.max(abs(K@np.ones(N))));x,y=coords
            ex=float(x@(K@x));ey=float(y@(K@y));cross=float(x@(K@y))
            assert symmetry<=1e-12 and constant<=1e-10 and max(abs(ex/area-1),abs(ey/area-1),abs(cross)/area)<=1e-10
            controls[labelq]=dict(symmetry=symmetry,constant_residual=constant,energy_x_m2=ex,energy_y_m2=ey,cross_m2=cross)
            save_npz(out/f'stiffness_{labelq}.npz',K)
            if labelq=='tri8':
                difference=K-old;reproduction=float(np.max(abs(difference.data))/np.max(abs(old.data))) if difference.nnz else 0.
                assert reproduction<=1e-13
            matrices[labelq]=K[free,:][:,free]
            del K;gc.collect();print(f'Duffy {label} {labelq} assembled',flush=True)
        scale=diags(1/np.sqrt(lower[free]));C=load_npz(det/'core_q32.npz')[free,:][:,free]
        w=np.load(det/'intensity_q32.npy',allow_pickle=False)[free]
        L=dict(field=float(np.asarray(abs(scale@C@scale).sum(axis=1)).max()),intensity=float(np.max(w/lower[free])))
        pairs={};beta=1.444*2*math.pi/1550e-9
        for key in ('duffy12','duffy16'):
            delta=scale@(matrices[key]-matrices['duffy24'])@scale
            bound=float(np.asarray(abs(delta).sum(axis=1)).max())/(2*beta);eta=.002*bound;power={k:2*v*eta for k,v in L.items()}
            pairs[key+'_vs_duffy24']=dict(generator_mass_norm_bound_m_inverse=bound,field_mass_norm_bound=eta,
                                          observable_power_bounds=power,conservative_consistency_pass=eta<=1e-6 and max(power.values())<=1e-5)
        files=[Path(__file__).resolve(),ROOT/'Docs/POINT-03-FEM-DUFFY-CONTRACT.md',ROOT/'scripts/check_point03_p4f.py',
               ROOT/'scripts/point03_fem_detector.py',record,geom/'T96_curved.msh',geom/'mesh_arrays.npz',geom/'stiffness.npz',
               geom/'mass.npz',det/'core_q32.npz',det/'intensity_q32.npy',det/'gaussian_q16.npz']
        report.update(status='completed',assembly_controls_pass=True,controls=controls,quadrature_controls=quadrature_controls,
                      reproduction_relative_error=reproduction,detector_mass_operator_upper_bounds=L,pairs=pairs,
                      source_sha256={str(p):sha(p) for p in files},artifacts={p.name:sha(p) for p in out.iterdir() if p.is_file()})
    except Exception as error:report.update(error=str(error),error_type=type(error).__name__,diagnostic=traceback.format_exc())
    report.update(elapsed_s=time.monotonic()-start,resource_end=dict(available_ram_bytes=psutil.virtual_memory().available,free_disk_bytes=psutil.disk_usage(str(out)).free))
    write(out/'report.json',report);print({k:report.get(k) for k in ('status','label','assembly_controls_pass','pairs','elapsed_s','error')},flush=True)
    return 0 if report['status']=='completed' else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(__doc__);p.add_argument('--mesh',choices=('prototype','coarse','mid'),required=True)
    p.add_argument('--out',type=Path,required=True);args=p.parse_args();raise SystemExit(run(args.mesh,args.out.resolve()))
