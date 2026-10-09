"""Headless conforming T96 mesh and weak-operator checks; no propagation."""
import argparse
from datetime import datetime,timezone
import json
import math
import os
from pathlib import Path
import time
import traceback
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import gmsh
import meshio
import numpy as np
import psutil
import scipy
from scipy.sparse import save_npz
import skfem
from skfem import Basis,ElementTriP2
from skfem.io import from_meshio
from skfem.models.poisson import mass,laplace
from run_point03_exponential import ROOT,sha,write
from point03_union_geometry import UnionRegion


def minimum_oriented_jacobian(mapping):
    points=np.array([[0.,1.,0.,.5,0.,.5],[0.,0.,1.,0.,.5,.5]])
    values=mapping.detDF(points)
    sign=np.sign(values[:,0]);assert np.all(sign!=0)
    values=values*sign[:,None]
    f=values[:,0];a=2*(values[:,1]+f-2*values[:,3]);d=values[:,1]-f-a
    c=2*(values[:,2]+f-2*values[:,4]);e=values[:,2]-f-c
    b=4*(values[:,5]-f-.25*a-.25*c-.5*d-.5*e)
    minimum=np.min(values[:,:3],axis=1)
    for aa,dd,ff in ((a,d,f),(c,e,f),(a-b+c,b-2*c+d-e,c+e+f)):
        x=np.divide(-dd,2*aa,out=np.full_like(aa,-1.),where=aa>0)
        candidate=aa*x*x+dd*x+ff
        minimum=np.minimum(minimum,np.where((x>0)&(x<1)&(aa>0),candidate,np.inf))
    determinant=4*a*c-b*b
    x=np.divide(b*e-2*c*d,determinant,out=np.full_like(a,-1.),where=abs(determinant)>0)
    y=np.divide(b*d-2*a*e,determinant,out=np.full_like(a,-1.),where=abs(determinant)>0)
    candidate=a*x*x+b*x*y+c*y*y+d*x+e*y+f
    minimum=np.minimum(minimum,np.where((x>0)&(y>0)&(x+y<1),candidate,np.inf))
    assert np.all(np.isfinite(minimum)) and np.all(minimum>0)
    return float(minimum.min())


def check(out):
    assert not out.exists() and out.is_relative_to(ROOT/'resultados/codex');out.mkdir();start=time.monotonic()
    report=dict(created_utc=datetime.now(timezone.utc).isoformat(),status='failed',no_T96_propagation=True,point03_closed=False)
    try:
        assert psutil.virtual_memory().available>2*1024**3 and psutil.disk_usage(str(out)).free>2*1024**3
        spec=json.loads((ROOT/'resultados/codex/point03_geometry_20261006234649Z/inputs/centres.json').read_text())['spec_um']
        truth=UnionRegion(spec).global_area()['area_um2']
        gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1)
        gmsh.option.setNumber('Mesh.RandomSeed',1);gmsh.model.add('T96_fixed_physical_domain')
        occ=gmsh.model.occ
        disks=[(2,occ.addDisk(x,y,0,r,r)) for x,y,r in spec['disks']]
        union,_=occ.fuse([disks[0]],disks[1:]);assert union and all(dim==2 for dim,tag in union)
        square=(2,occ.addRectangle(-64,-64,0,128,128))
        regions,maps=occ.fragment([square],union);occ.synchronize()
        cladding=sorted({tag for mapping in maps[1:] for dim,tag in mapping if dim==2})
        all_surfaces=sorted({tag for dim,tag in regions if dim==2});background=sorted(set(all_surfaces)-set(cladding))
        assert cladding and background and not set(cladding)&set(background)
        area=sum(occ.getMass(2,tag) for tag in cladding);total=sum(occ.getMass(2,tag) for tag in all_surfaces)
        assert abs(area/truth-1)<=1e-8 and abs(total/128**2-1)<=1e-10
        gmsh.model.addPhysicalGroup(2,cladding,1);gmsh.model.setPhysicalName(2,1,'cladding')
        gmsh.model.addPhysicalGroup(2,background,2);gmsh.model.setPhysicalName(2,2,'background')
        boundary=gmsh.model.getBoundary([(2,tag) for tag in all_surfaces],combined=True,oriented=False)
        outer=[]
        for dim,tag in boundary:
            xmin,ymin,zmin,xmax,ymax,zmax=gmsh.model.getBoundingBox(dim,tag)
            if abs(xmin+64)<1e-5 and abs(xmax+64)<1e-5 or abs(xmin-64)<1e-5 and abs(xmax-64)<1e-5 or abs(ymin+64)<1e-5 and abs(ymax+64)<1e-5 or abs(ymin-64)<1e-5 and abs(ymax-64)<1e-5:outer.append(tag)
        assert len(outer)==4
        gmsh.model.addPhysicalGroup(1,outer,3);gmsh.model.setPhysicalName(1,3,'outer')
        field=gmsh.model.mesh.field.add('MathEval')
        gmsh.model.mesh.field.setString(field,'F','0.35 + 1.05 * Min(1, Max(0, (Sqrt(x*x+y*y)-15)/10))')
        gmsh.model.mesh.field.setAsBackgroundMesh(field)
        for option in ('Mesh.MeshSizeFromPoints','Mesh.MeshSizeFromCurvature','Mesh.MeshSizeExtendFromBoundary'):gmsh.option.setNumber(option,0)
        gmsh.model.mesh.generate(2);gmsh.model.mesh.setOrder(2);gmsh.model.mesh.optimize('HighOrder')
        path=out/'T96_curved.msh';gmsh.write(str(path));gmsh.finalize()
        raw=meshio.read(path);raw.points*=1e-6
        mesh=from_meshio(raw,force_meshio_type='triangle6',ignore_orientation=True)
        assert type(mesh).__name__=='MeshTri2'
        tags=raw.cell_data_dict['gmsh:physical']['triangle6'];clad_cells=np.flatnonzero(tags==1);bg_cells=np.flatnonzero(tags==2)
        assert len(clad_cells)+len(bg_cells)==mesh.nelements and not np.intersect1d(clad_cells,bg_cells).size
        basis=Basis(mesh,ElementTriP2(),intorder=8)
        det=basis.mapping.detDF(basis.X);assert np.all(np.isfinite(det)) and np.all(abs(det)>0)
        # Orientation can be clockwise; each element must retain one sign.
        assert np.all(np.min(det,axis=1)*np.max(det,axis=1)>0)
        min_jacobian=minimum_oriented_jacobian(basis.mapping)
        M=mass.assemble(basis);K=laplace.assemble(basis);C=mass.assemble(basis.with_elements(clad_cells))
        def symmetric_error(matrix):
            delta=matrix-matrix.T
            return float(np.max(abs(delta.data))/max(np.max(abs(matrix.data)),1e-300)) if delta.nnz else 0.
        symmetry={name:symmetric_error(matrix) for name,matrix in (('mass',M),('stiffness',K),('cladding_mass',C))}
        assert max(symmetry.values())<=1e-12 and np.all(M.diagonal()>0)
        constant=float(np.max(abs(K@np.ones(basis.N))))
        assert constant<=1e-10
        area_mass=float(M.sum())*1e12;area_clad=float(C.sum())*1e12
        assert abs(area_mass/128**2-1)<=1e-10 and abs(area_clad/area-1)<=1e-5
        boundary_dofs=basis.get_dofs(lambda x:np.isclose(abs(x[0]),64e-6,rtol=0,atol=1e-12)|np.isclose(abs(x[1]),64e-6,rtol=0,atol=1e-12)).all()
        assert len(boundary_dofs)>0
        np.savez(out/'mesh_arrays.npz',points=mesh.p,triangles=mesh.t,doflocs=basis.doflocs,element_dofs=basis.element_dofs,cladding_cells=clad_cells,boundary_dofs=boundary_dofs)
        for name,matrix in (('mass',M),('stiffness',K),('cladding_mass',C)):save_npz(out/(name+'.npz'),matrix)
        assert time.monotonic()-start<=600
        report.update(status='completed',controls_pass=True,cad_area_um2=area,analytic_area_um2=truth,cad_relative_error=abs(area/truth-1),mass_domain_area_um2=area_mass,mass_cladding_area_um2=area_clad,curved_geometry_relative_error=abs(area_clad/area-1),symmetry=symmetry,constant_stiffness_residual=constant,dofs=basis.N,elements=mesh.nelements,minimum_abs_jacobian=float(abs(det).min()),minimum_oriented_jacobian_all_reference_triangle=min_jacobian,versions=dict(gmsh=gmsh.__version__,skfem=skfem.__version__,meshio=meshio.__version__,numpy=np.__version__,scipy=scipy.__version__),hashes={path.name:sha(path) for path in out.iterdir() if path.is_file()})
    except Exception as error:
        if gmsh.isInitialized():gmsh.finalize()
        report.update(error=str(error),error_type=type(error).__name__,diagnostic=traceback.format_exc())
    report['elapsed_s']=time.monotonic()-start;write(out/'report.json',report)
    print(json.dumps({key:report.get(key) for key in ('status','controls_pass','dofs','elements','cad_relative_error','curved_geometry_relative_error','elapsed_s','error')}))
    return 0 if report.get('controls_pass') else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args();raise SystemExit(check(args.out.resolve()))
