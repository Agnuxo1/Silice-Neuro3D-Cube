"""G2 recovery evidence assessment and reconstructed detector; imports no wave solver."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path,data):
    with Path(path).open('x',encoding='utf-8') as f:
        json.dump(data,f,indent=2,allow_nan=False)
        f.write('\n')


def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


class Detector:
    def __init__(self):
        import numpy as np
        from scipy.special import roots_legendre
        self.np=np
        self.polar=[]
        for nr,nt in ((64,256),(128,512),(256,1024)):
            t,w=roots_legendre(nr)
            radius=6e-6*np.sqrt((t+1)/2)
            theta=2*np.pi*np.arange(nt)/nt
            self.polar.append((radius[:,None]*np.cos(theta),radius[:,None]*np.sin(theta),w/2))

    def measure(self,field,n,pin=1.):
        from scipy.interpolate import RectBivariateSpline
        np=self.np
        axis=(np.arange(n)-n//2)*(128e-6/n)
        assert field.shape==(n,n) and np.all(np.isfinite(field))
        splines={'field':(RectBivariateSpline(axis,axis,field.real,kx=3,ky=3,s=0),
                          RectBivariateSpline(axis,axis,field.imag,kx=3,ky=3,s=0)),
                 'intensity':(RectBivariateSpline(axis,axis,np.abs(field)**2,kx=3,ky=3,s=0),)}
        result={}
        for method,spl in splines.items():
            values=[]
            minimum=math.inf
            for xx,yy,w in self.polar:
                assert min(xx.min(),yy.min())>axis[0] and max(xx.max(),yy.max())<axis[-1]
                a=spl[0].ev(yy.ravel(),xx.ravel()).reshape(xx.shape)
                intensity=a*a+spl[1].ev(yy.ravel(),xx.ravel()).reshape(xx.shape)**2 if method=='field' else a
                assert np.all(np.isfinite(intensity))
                minimum=min(minimum,float(intensity.min()))
                values.append(float(np.pi*(6e-6)**2*np.sum(w*intensity.mean(axis=1))/pin))
            assert minimum>=-1e-12*float((np.abs(field)**2).max()),'Negative reconstructed intensity'
            result[method]={'P_core':values[-1],'levels':values,'change':abs(values[-1]-values[-2])}
        return result


def predict640(powers):
    p1,p2,p3=powers[-3:]
    d0,d1=p2-p1,p3-p2
    if abs(d0)<=1e-12 or abs(d1)<=1e-12 or d0*d1<=0:
        return {'prediction':None,'p':None,'reason':'Unresolvable/oscillatory differences'}
    p=math.log(abs(d0/d1))/math.log(1.25)
    if p<=0 or not math.isfinite(p):
        return {'prediction':None,'p':p,'reason':'Nonpositive/nonfinite observed order'}
    pinf=p3+d1/(1.25**p-1)
    return dict(prediction=pinf+(p3-pinf)*(500/640)**p,p=p,conditional_pinf=pinf)


def read_rows(manifest,results,detector):
    import numpy as np
    rows=[]
    for case in results:
        ip=Path(case['input_path']); fp=Path(case['field_path'])
        assert sha(ip)==case['input_sha256'] and sha(fp)==case['field_sha256']
        with np.load(ip,allow_pickle=False) as z:
            a0,weights=z['A0'],z['weights']
        with np.load(fp,allow_pickle=False) as z:
            field=z['field']
        n=case['N']; dx=128e-6/n
        assert a0.dtype==np.dtype('complex128') and field.dtype==np.dtype('complex128')
        assert field.shape==(n,n) and np.all(np.isfinite(field))
        pin=float(np.sum(np.abs(a0)**2)*dx*dx)
        total=float(np.sum(np.abs(field)**2)*dx*dx)
        assert abs(pin-1)<=1e-12 and 0<total<=1.001
        methods=detector.measure(field,n,pin)
        for item in methods.values():
            assert 0<=item['P_core']<=total/pin+1e-8
        rows.append(dict(case,methods=methods,P_in=pin,P_total=total/pin,
                         P_core_cell=float(np.sum(np.abs(field)**2*weights)*dx*dx/pin)))
    return rows


def evaluate(path,mode,out):
    started=time.monotonic()
    execution=json.loads(Path(path).read_text())
    import platform
    from importlib.metadata import version
    assert platform.python_version()=='3.13.7'
    assert all(version(k)==v for k,v in {'numpy':'2.2.6','scipy':'1.15.1','psutil':'6.1.1'}.items())
    manifest=json.loads(Path(execution['manifest_path']).read_text())
    assert sha(execution['manifest_path'])==execution['manifest_sha256']
    for filename,digest in manifest['source_sha256'].items():
        assert sha(filename)==digest,'Scientific source changed'
    assert sha(manifest['geometry_report_path'])==manifest['geometry_report_sha256']
    geometry=json.loads(Path(manifest['geometry_report_path']).read_text())
    assert geometry['geometry_pass'] and len(geometry['reference_cells'])==48
    assert abs(geometry['grid_area']/geometry['global_area']-1)<=1e-12
    assert all(c['reference']['quality_pass'] and c['reference']['quality_total']<=1e-13 and c['delta']<=1e-12 for c in geometry['reference_cells'])
    for case in execution['results']:
        if case.get('reused'):
            assert sha(case['E_case_path'])==case['E_case_sha256']
        else:
            previous=None; previous_sha=None; done=0
            for checkpoint in case['checkpoints']:
                assert sha(checkpoint['path'])==checkpoint['sha256']
                cp=json.loads(Path(checkpoint['path']).read_text())
                assert cp['previous_report_path']==previous and cp['start_step']==done
                assert cp['previous_report_sha256']==previous_sha
                assert cp['steps_done'] in (100,200) and sha(cp['field_path'])==cp['field_sha256']
                done+=cp['steps_done']; previous=checkpoint['path'];previous_sha=checkpoint['sha256']
            assert done==case['steps'] and cp['field_path']==case['field_path']
    detector=Detector()
    rows=read_rows(manifest,execution['results'],detector)
    eass=load_module('g_scalar_assessor',ROOT/'scripts/assess_point03_analytic.py')
    assert eass.self_check()['self_check_pass']
    report=dict(created_utc=datetime.now(timezone.utc).isoformat(),mode=mode,rows=rows,
                manifest_sha256=sha(execution['manifest_path']),execution_sha256=sha(path),
                source_sha256=sha(__file__),scientific_pass=False,point03_closed=False,
                integrity_pass=True,geometry_pass=True,
                scope='Conditional scalar-functional convergence only; no field/phase/boundary or physical validation.')
    if mode=='prediction':
        assert len(rows)==8 and all(r['N']!=640 for r in rows)
        report['predictions']={m:predict640([r['methods'][m]['P_core'] for r in rows[:4]]) for m in ('field','intensity')}
        report['new_holdout_not_propagated']=True
    else:
        assert len(rows)==9
        report['gaussian_controls']=[]
        for n in (256,320,400,500,640):
            np=detector.np
            axis=(np.arange(n)-n//2)*(128e-6/n)
            xx,yy=np.meshgrid(axis,axis)
            a=(math.sqrt(2/(math.pi*(6e-6)**2))*np.exp(-(xx*xx+yy*yy)/(6e-6)**2)).astype(np.complex128)
            vals=detector.measure(a,n)
            for v in vals.values():
                v['error']=abs(v['P_core']-(1-math.exp(-2)))
                v['pass']=v['error']<=(1e-6 if n>=500 else 1e-5) and v['change']<=1e-10
            report['gaussian_controls'].append(dict(N=n,methods=vals))
        frozen=json.loads(Path(execution['prediction_path']).read_text())
        assert sha(execution['prediction_path'])==execution['prediction_sha256']
        assert frozen['new_holdout_not_propagated']
        assert execution['holdout_started_utc']>frozen['created_utc']
        mapped=[f'n{n}_geom_z0625' for n in (256,320,400,500)]
        mapped += ['n400_geom_z125','n500_geom_z125','n400_geom_z03125','n500_geom_z03125']
        report['mapped_dz_um']={'coarse':.625,'mid':.3125,'fine':.15625}
        report['scalar_assessments']={}
        report['holdout']={}
        for method in ('field','intensity'):
            values=[dict(case_id=id_,P_core=row['methods'][method]['P_core']) for id_,row in zip(mapped,rows[:8])]
            report['scalar_assessments'][method]=eass.assess_values(values)
            predicted=predict640([r['methods'][method]['P_core'] for r in rows[:4]])
            assert predicted==frozen['predictions'][method]
            p=rows[-1]['methods'][method]['P_core']; p500=rows[3]['methods'][method]['P_core']
            residual=abs(p-predicted['prediction']) if predicted['prediction'] is not None else None
            limit=.1*abs(p-p500)
            report['holdout'][method]=dict(predicted,actual=p,residual=residual,limit=limit,
                pass_=residual is not None and abs(p-p500)>1e-12 and residual<=limit)
        report['quadrature_pass']=all(v['change']<=1e-8 for row in rows for v in row['methods'].values())
        report['gaussian_pass']=all(v['pass'] for c in report['gaussian_controls'] for v in c['methods'].values())
        report['method_agreement']={str(n):abs(rows[i]['methods']['field']['P_core']-rows[i]['methods']['intensity']['P_core']) for n,i in ((500,3),(640,8))}
        report['scientific_pass']=all(a['scientific_pass'] for a in report['scalar_assessments'].values()) and all(h['pass_'] for h in report['holdout'].values()) and report['quadrature_pass'] and report['gaussian_pass'] and max(report['method_agreement'].values())<=1e-7 and manifest['geometry_pass']
        report['point03_closed']=report['scientific_pass']
    report['elapsed_s']=time.monotonic()-started
    assert report['elapsed_s']<120
    write(out,report)
    print(json.dumps({'mode':mode,'scientific_pass':report['scientific_pass'],'out':str(out)}),flush=True)
    return 0 if mode=='prediction' or report['scientific_pass'] else 2


def main():
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('--execution',type=Path,required=True)
    parser.add_argument('--mode',choices=['prediction','final'],required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    try:
        return evaluate(args.execution,args.mode,args.out)
    except Exception as err:
        import traceback
        write(args.out,dict(status='failed',scientific_pass=None,point03_closed=False,
                            error_type=type(err).__name__,error=str(err),diagnostic=traceback.format_exc()))
        print(json.dumps({'status':'failed','error_type':type(err).__name__}),flush=True)
        return 1


if __name__=='__main__':
    raise SystemExit(main())
