"""Independent hat-basis matrix assembly and norm bound; manufactured fields only."""
from datetime import datetime,timezone
import json
from pathlib import Path
import time
from run_point03_exponential import ROOT,sha,write
import numpy as np
from scipy.sparse import coo_matrix
from point03_linear_detector import Detector

def run():
    start=time.monotonic();detector=Detector();rng=np.random.default_rng(917);report=dict(created_utc=datetime.now(timezone.utc).isoformat(),manufactured_only=True,no_T96_fields_read=True,pass_=False,matrices=[],pairs=[])
    basis=np.array([[1,-1,-1,1],[0,1,0,-1],[0,0,1,-1],[0,0,0,1]],dtype=float);powers=[(0,0),(1,0),(0,1),(1,1)]
    for n in (400,626):
        g=detector.geometry(n);dx=128e-6/n;area=dx*dx;radius=g['radius_m'];operators={}
        for level in (16,32):
            row=[];col=[];val=[];intensity=np.zeros(n*n);min_local=0.;min_entry=0.
            for (iy,ix),m in zip(g['indices'],g['moments'+str(level)],strict=True):
                q=np.array([[m[p+r,s+t] for r,t in powers] for p,s in powers]);mass=radius*radius*(basis@q@basis.T)
                weights=radius*radius*(basis@np.array([m[p,s] for p,s in powers]));indices=np.array([iy*n+ix,iy*n+ix+1,(iy+1)*n+ix,(iy+1)*n+ix+1])
                min_local=min(min_local,float(np.linalg.eigvalsh(mass).min()/area));min_entry=min(min_entry,float(mass.min()/area),float(weights.min()/area))
                assert min_local>=-1e-12 and min_entry>=-1e-12
                row.extend(np.repeat(indices,4));col.extend(np.tile(indices,4));val.extend(mass.ravel());intensity[indices]+=weights
            matrix=coo_matrix((val,(row,col)),shape=(n*n,n*n)).tocsr();rows=np.asarray(matrix.sum(axis=1)).ravel()
            row_ratio=float(np.max(np.abs(matrix).sum(axis=1))/area);density_ratio=float(intensity.max()/area);identity=float(np.abs(rows-intensity).max()/area)
            area_error=abs(float(rows.sum())/(np.pi*radius*radius)-1)
            assert row_ratio<=1+1e-12 and density_ratio<=1+1e-12 and identity<=1e-12 and area_error<=1e-12
            report['matrices'].append(dict(N=n,quadrature=level,active_cells=len(g['indices']),min_local_eigenvalue_relative_cell_area=min_local,min_entry_relative_cell_area=min_entry,row_bound_relative_cell_area=row_ratio,intensity_bound_relative_cell_area=density_ratio,hat_partition_identity_error=identity,area_relative_error=area_error))
            operators[level]=(matrix,intensity)
        for pair in range(4):
            a=(rng.normal(size=(n,n))+1j*rng.normal(size=(n,n))).astype(np.complex128);a/=float(np.linalg.norm(a))*dx
            b=a+.01*(rng.normal(size=(n,n))+1j*rng.normal(size=(n,n)))/(n*dx)
            ma=detector.measure(a,n);mb=detector.measure(b,n);bound=area*(float(np.linalg.norm(a))+float(np.linalg.norm(b)))*float(np.linalg.norm(a-b))
            worst=0.;ratio=0.
            for k,level in enumerate((16,32)):
                matrix,weights=operators[level];values={}
                for name,field in (('a',a),('b',b)):
                    v=field.ravel();values[name]=dict(field=float(np.vdot(v,matrix@v).real),intensity=float(np.dot(weights,np.abs(v)**2)))
                    actual=ma if name=='a' else mb
                    for method in ('field','intensity'):worst=max(worst,abs(values[name][method]-actual[method]['levels'][k]))
                for method in ('field','intensity'):
                    difference=abs(values['a'][method]-values['b'][method]);assert difference<=bound*(1+1e-12)+1e-12;ratio=max(ratio,difference/bound)
            assert worst<=1e-12
            report['pairs'].append(dict(N=n,pair=pair,max_energy_recomputation_error=worst,maximum_difference_to_bound_ratio=ratio,bound=bound))
    elapsed=time.monotonic()-start;assert elapsed<=120
    report.update(pass_=True,elapsed_s=elapsed,source_sha256={str(p):sha(p) for p in (Path(__file__).resolve(),ROOT/'scripts/point03_linear_detector.py',ROOT/'Docs/POINT-03-DETECTOR-BOUND-CONTRACT.md')});return report

if __name__=='__main__':
    try:r=run()
    except Exception as err:
        import traceback
        r=dict(pass_=False,manufactured_only=True,no_T96_fields_read=True,error_type=type(err).__name__,error=str(err),diagnostic=traceback.format_exc())
    write(ROOT/'resultados/codex/point03_detector_bound_20261007.json',r);print(json.dumps(r));raise SystemExit(0 if r['pass_'] else 1)
