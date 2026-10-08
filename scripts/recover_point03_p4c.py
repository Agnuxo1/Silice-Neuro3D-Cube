"""Recover the reporting-only failure by verifying saved mesh and matrices."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import meshio
import numpy as np
from scipy.sparse import load_npz
from skfem import Basis,ElementTriP2
from skfem.io import from_meshio
from check_point03_p4c import minimum_oriented_jacobian
from point03_union_geometry import UnionRegion
from run_point03_exponential import ROOT,sha,write


def recover(folder):
    partial=folder/'report.json';text=partial.read_text(encoding='utf-8')
    try:json.loads(text);raise AssertionError('Expected retained truncated report')
    except json.JSONDecodeError:pass
    prefix=json.loads(text.split('"dofs":',1)[0]+'"reporting_error": "numpy int32 not JSON serializable"}')
    assert prefix['status']=='completed' and prefix['controls_pass']
    raw=meshio.read(folder/'T96_curved.msh');raw.points*=1e-6
    mesh=from_meshio(raw,force_meshio_type='triangle6',ignore_orientation=True);basis=Basis(mesh,ElementTriP2(),intorder=8)
    M=load_npz(folder/'mass.npz');K=load_npz(folder/'stiffness.npz');C=load_npz(folder/'cladding_mass.npz')
    assert M.shape==K.shape==C.shape==(basis.N,basis.N) and np.all(M.diagonal()>0)
    for matrix in (M,K,C):assert (matrix-matrix.T).nnz==0 and np.all(np.isfinite(matrix.data))
    minimum=minimum_oriented_jacobian(basis.mapping)
    spec=json.loads((ROOT/'resultados/codex/point03_geometry_20261006234649Z/inputs/centres.json').read_text())['spec_um']
    truth=UnionRegion(spec).global_area()['area_um2']
    assert abs(prefix['cad_area_um2']/truth-1)<=1e-8
    domain=float(M.sum())*1e12;clad=float(C.sum())*1e12
    assert abs(domain/128**2-1)<=1e-10 and abs(clad/prefix['cad_area_um2']-1)<=1e-5
    assert abs(domain-prefix['mass_domain_area_um2'])<=1e-8 and abs(clad-prefix['mass_cladding_area_um2'])<=1e-8
    constant=float(np.max(abs(K@np.ones(basis.N))));assert constant<=1e-10
    tags=raw.cell_data_dict['gmsh:physical']['triangle6'];assert np.all(np.isin(tags,[1,2]))
    with np.load(folder/'mesh_arrays.npz',allow_pickle=False) as data:
        assert np.array_equal(data['doflocs'],basis.doflocs) and np.array_equal(data['element_dofs'],basis.element_dofs)
        assert np.array_equal(data['cladding_cells'],np.flatnonzero(tags==1))
        assert len(data['boundary_dofs'])>0
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),integrity_pass=True,geometry_and_assembly_controls_pass=True,reporting_failure_retained=True,geometry_regenerated=False,T96_propagation_performed=False,point03_closed=False,dofs=int(basis.N),elements=int(mesh.nelements),minimum_oriented_jacobian=minimum,cad_relative_error=abs(prefix['cad_area_um2']/truth-1),curved_geometry_relative_error=abs(clad/prefix['cad_area_um2']-1),constant_stiffness_residual=constant,original_partial_report_sha256=sha(partial),artifact_sha256={path.name:sha(path) for path in folder.iterdir() if path.is_file()},scope='Saved conforming mesh/operator controls only; original NumPy serialization failure preserved.')
    write(folder/'report_recovered.json',result);print(json.dumps({key:result[key] for key in ('integrity_pass','geometry_and_assembly_controls_pass','dofs','elements','cad_relative_error','curved_geometry_relative_error','point03_closed')}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args();recover(args.out.resolve())
