"""Prospectively specified read-only detector reconstruction diagnostic F."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import math
import os
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT/'resultados/codex/point03_analytic_20261007T004526617696Z'
LEVELS = ((64,256),(128,512),(256,1024))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def spatial(p):
    d = [b-a for a,b in zip(p,p[1:])]
    valid = all(abs(x)>1e-12 for x in d) and all(x*d[0]>0 for x in d)
    orders = [math.log(abs(d[i]/d[i+1]))/math.log(1.25) for i in (0,1)] if valid else None
    positive = orders is not None and min(orders)>0
    disagreement = abs(orders[1]-orders[0])/max(abs(x) for x in orders) if positive else None
    prediction = p[2]+d[1]**2/d[0] if valid else None
    residual = abs(p[3]-prediction) if prediction is not None else None
    gates = dict(same_nonzero_signed_differences=valid, positive_orders=positive,
                 order_stability=positive and disagreement<=.2,
                 prediction=valid and residual<=.1*abs(d[2]))
    return dict(powers=p,differences=d,orders=orders,order_disagreement=disagreement,
                prediction=prediction,residual=residual,limit=.1*abs(d[2]),gates=gates,
                diagnostic_spatial_pass=all(gates.values()))


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    assert not args.out.exists()
    args.out.mkdir(parents=True)
    start=time.monotonic()
    for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
        os.environ[name]='1'
    import numpy as np
    import psutil
    from scipy.interpolate import RectBivariateSpline
    from numpy.polynomial.legendre import leggauss
    contract = ROOT/'Docs/POINT-03-RECONSTRUCTION-CONTRACT.md'
    report = dict(status='running',created_utc=datetime.now(timezone.utc).isoformat(),
        scope='Postprocessing of known E fields only; does not replace E or close Point 03.',
        contract_sha256=sha(contract),source_sha256=sha(__file__),gpu_used=False,
        levels=LEVELS,controls=[],cases=[],frozen_predictions={})
    inputs={str(contract):sha(contract),str(Path(__file__).resolve()):sha(__file__)}

    def guard():
        assert time.monotonic()-start<115, 'Diagnostic work budget exceeded'
        assert psutil.virtual_memory().available>1.5*1024**3, 'Available RAM too low'
        assert psutil.disk_usage(str(args.out)).free>2*1024**3, 'Available disk too low'

    def load(path, expected):
        guard()
        assert sha(path)==expected, 'Input hash mismatch: '+str(path)
        inputs[str(path)]=expected
        with np.load(path,allow_pickle=False) as z:
            return {k:z[k] for k in z.files}

    polar=[]
    for nr,nt in LEVELS:
        t,w=leggauss(nr)
        radius=6e-6*np.sqrt((t+1)/2)
        theta=2*np.pi*np.arange(nt)/nt
        xx=radius[:,None]*np.cos(theta)[None,:]
        yy=radius[:,None]*np.sin(theta)[None,:]
        polar.append((xx,yy,w/2))

    def measure(field,n):
        guard()
        axis=(np.arange(n)-n//2)*(128e-6/n)
        assert np.all(np.isfinite(field)) and field.shape==(n,n)
        splines={'field':(RectBivariateSpline(axis,axis,field.real,kx=3,ky=3,s=0),
                          RectBivariateSpline(axis,axis,field.imag,kx=3,ky=3,s=0)),
                 'intensity':(RectBivariateSpline(axis,axis,np.abs(field)**2,kx=3,ky=3,s=0),)}
        result={}
        for method, spl in splines.items():
            values=[]
            minimum=math.inf
            for xx,yy,w in polar:
                guard()
                assert xx.min()>axis[0] and xx.max()<axis[-1] and yy.min()>axis[0] and yy.max()<axis[-1]
                a=spl[0].ev(yy.ravel(),xx.ravel()).reshape(xx.shape)
                intensity=(a*a+spl[1].ev(yy.ravel(),xx.ravel()).reshape(xx.shape)**2) if method=='field' else a
                assert np.all(np.isfinite(intensity))
                minimum=min(minimum,float(intensity.min()))
                values.append(float(np.pi*(6e-6)**2*np.sum(w*intensity.mean(axis=1))))
            result[method]=dict(powers=values,quadrature_change=abs(values[-1]-values[-2]),
                                minimum_intensity=minimum,
                                positivity_pass=minimum>=-1e-12*float((np.abs(field)**2).max()))
        return result

    try:
        original=json.loads((STUDY/'assessment.json').read_text())
        inputs[str(STUDY/'assessment.json')]=sha(STUDY/'assessment.json')
        assert original['integrity_pass'] and original['scientific_pass'] is False
        for n in (256,320,400,500):
            axis=(np.arange(n)-n//2)*(128e-6/n)
            xx,yy=np.meshgrid(axis,axis)
            beam=(math.sqrt(2/(math.pi*(6e-6)**2))*np.exp(-(xx*xx+yy*yy)/(6e-6)**2)).astype(np.complex128)
            controls=measure(beam,n)
            for item in controls.values():
                item['analytic_error']=abs(item['powers'][-1]-(1-math.exp(-2)))
                item['pass']=item['positivity_pass'] and item['quadrature_change']<=1e-10 and item['analytic_error']<=(1e-6 if n==500 else 1e-5)
            report['controls'].append(dict(N=n,methods=controls))
        # The new postprocessed prediction is saved before computing N500.
        primary={'field':[],'intensity':[]}
        for index,expected in enumerate(original['independent_measurements']):
            n=expected['N']
            if index==3:
                record={}
                for method,p in primary.items():
                    d0,d1=p[1]-p[0],p[2]-p[1]
                    record[method]=dict(powers=p.copy(),prediction=p[2]+d1*d1/d0,
                                        order=math.log(abs(d0/d1))/math.log(1.25))
                report['frozen_predictions']=record
                (args.out/'prediction.json').write_text(json.dumps(dict(created_utc=datetime.now(timezone.utc).isoformat(),
                    record=record,scope='New reconstruction holdout; optical trajectories already known.'),indent=2)+'\n')
            data=load(expected['input_npz_path'],expected['input_npz_sha256'])
            field=load(expected['final_npz_path'],expected['final_npz_sha256'])['field']
            dx=128e-6/n
            p_in=float(np.sum(np.abs(data['A0'])**2)*dx**2)
            raw=float(np.sum(np.abs(field)**2*data['weights'])*dx**2/p_in)
            assert abs(raw-expected['P_core'])<=1e-12
            methods=measure(field,n)
            for method,item in methods.items():
                item['P_core']=item['powers'][-1]/p_in
                item['quadrature_pass']=item['quadrature_change']/p_in<=1e-8
                if index<4:
                    primary[method].append(item['P_core'])
            report['cases'].append(dict(case_id=expected['case_id'],N=n,dz_um=expected['dz_m']*1e6,
                                        P_in=p_in,E_piecewise_constant=raw,methods=methods))
        report['spatial']={m:spatial(p) for m,p in primary.items()}
        report['longitudinal']={}
        for method in primary:
            values={c['case_id']:c['methods'][method]['P_core'] for c in report['cases']}
            controls={}
            for n in (400,500):
                a=values[f'n{n}_geom_z125']-values[f'n{n}_geom_z0625']
                b=values[f'n{n}_geom_z0625']-values[f'n{n}_geom_z03125']
                q=math.log(abs(a/b))/math.log(2) if abs(a)>1e-12 and abs(b)>1e-12 and a*b>0 else None
                controls[str(n)]=dict(a=a,b=b,q=q,original_band_pass=q is not None and 1.8<=q<=2.2)
            report['longitudinal'][method]=controls
        gap=abs(primary['field'][-1]-primary['intensity'][-1])
        report['finest_method_difference']=gap
        report['finest_method_agreement_pass']=gap<=1e-7
        report['control_pass']=all(m['pass'] for c in report['controls'] for m in c['methods'].values())
        report['quadrature_pass']=all(m['quadrature_pass'] and m['positivity_pass'] for c in report['cases'] for m in c['methods'].values())
        report['inputs_unchanged']=all(sha(p)==d for p,d in inputs.items())
        report['status']='completed'
    except Exception as err:
        report.update(status='failed',error_type=type(err).__name__,error=str(err),diagnostic=traceback.format_exc())
    report['input_sha256']=inputs
    report['elapsed_s']=time.monotonic()-start
    report['point03_closed']=False
    (args.out/'diagnostic.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:report.get(k) for k in ['status','control_pass','quadrature_pass','finest_method_difference','elapsed_s','error']}))
    return 0 if report['status']=='completed' else 1


if __name__=='__main__':
    raise SystemExit(main())
