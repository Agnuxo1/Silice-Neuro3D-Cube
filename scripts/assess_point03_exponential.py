"""H evaluator: hashes, reconstruction, direct temporal error and spatial gates."""
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m

def spatial(powers):
    diffs=[b-a for a,b in zip(powers,powers[1:])]
    base=all(abs(d)>1e-12 for d in diffs) and all(d*diffs[0]>0 for d in diffs)
    if not base:return dict(pass_=False,differences=diffs,reason='unresolved or oscillatory')
    orders=[math.log(abs(a/b))/math.log(1.25) for a,b in zip(diffs,diffs[1:])]
    if min(orders)<=0:return dict(pass_=False,differences=diffs,orders=orders,reason='nonpositive order')
    disagreement=abs(orders[1]-orders[0])/max(orders)
    pred=powers[2]+diffs[1]/(1.25**orders[0]);res=abs(powers[3]-pred);limit=.1*abs(diffs[2])
    indicator=1.25*abs(diffs[-1])/(1.25**min(orders[-1],2.)-1)
    return dict(pass_=disagreement<=.2 and res<=limit,differences=diffs,orders=orders,order_disagreement=disagreement,predicted_500=pred,residual_500=res,limit_500=limit,u_space=indicator,p_indicator=min(orders[-1],2.))

def assess(path,prediction):
    import numpy as np
    from importlib.metadata import version
    import platform
    assert platform.python_version()=='3.13.7'
    assert version('numpy')=='2.2.6' and version('scipy')=='1.15.1'
    execution=json.loads(Path(path).read_text());manifest=json.loads(Path(execution['manifest_path']).read_text())
    assert sha(execution['manifest_path'])==execution['manifest_sha256']
    for p,d in manifest['source_sha256'].items():assert sha(p)==d
    assert manifest['selfcheck']['pass_']
    detector_module=load('h_detector',ROOT/'scripts/assess_point03_reconstructed.py');detector=detector_module.Detector()
    g=json.loads((Path(manifest['g_path'])/'assessment.json').read_text())
    report=dict(created_utc=datetime.now(timezone.utc).isoformat(),integrity_pass=True,scientific_pass=False,point03_closed=False,rows=[],prediction_only=prediction,scope='Local scalar core-power convergence; no field/phase/boundary/Maxwell/fabrication validation.')
    assert [r['N'] for r in execution['results']]==([256,320,400,500] if prediction else [256,320,400,500,640])
    for result,case in zip(execution['results'],manifest['plan']):
        n=result['N'];assert n==case['N'] and sha(case['input_path'])==case['input_sha256']
        with np.load(case['input_path'],allow_pickle=False) as inp:a0=inp['A0']
        dx=128e-6/n;pin=float(np.sum(np.abs(a0)**2)*dx*dx);assert abs(pin-1)<=1e-12
        fields={};methods={}
        for segments in (4,8):
            sol=result['solutions'][str(segments)];previous=None;previous_sha=None
            assert len(sol['checkpoints'])==segments
            for i,link in enumerate(sol['checkpoints'],1):
                assert sha(link['path'])==link['sha256'];cp=json.loads(Path(link['path']).read_text())
                assert cp['status']=='completed' and cp['N']==n and cp['segments']==segments and cp['segment']==i and cp['length_m']==.002/segments
                assert cp['elapsed_s']<=360 and cp['previous_report_path']==previous and cp['previous_report_sha256']==previous_sha
                assert sha(cp['field_path'])==cp['field_sha256']
                with np.load(cp['field_path'],allow_pickle=False) as inp:field=inp['field']
                assert field.shape==(n,n) and field.dtype==np.dtype('complex128') and np.all(np.isfinite(field))
                raw=float(np.sum(np.abs(field)**2)*dx*dx);assert 0<raw<=1.001 and abs(raw-cp['raw_total'])<=1e-12
                assert all(cp[k]['available_ram_bytes']>1.5*1024**3 and cp[k]['free_disk_bytes']>2*1024**3 for k in ('resource_start','resource_end'))
                previous=link['path'];previous_sha=link['sha256']
            assert cp['field_path']==sol['field_path'] and sha(sol['field_path'])==sol['field_sha256']
            fields[segments]=field.copy();methods[str(segments)]=detector.measure(field,n,pin)
        consistency=float(np.linalg.norm(fields[4]-fields[8])/np.linalg.norm(fields[8]))
        row=dict(N=n,solutions=result['solutions'],P_in=pin,P_total=float(np.sum(np.abs(fields[8])**2)*dx*dx/pin),methods=methods,reference_field_difference=consistency,reference_power_difference={m:abs(methods['4'][m]['P_core']-methods['8'][m]['P_core']) for m in ('field','intensity')},adi_comparisons=[])
        assert all(0<=v['P_core']<=row['P_total']+1e-8 for vals in methods.values() for v in vals.values())
        comparisons=[c for c in g['rows'] if c['N']==n and c['dz_m'] in (.3125e-6,.15625e-6)]
        assert len(comparisons)==(2 if n in (400,500) else 1)
        for c in comparisons:
            assert sha(c['field_path'])==c['field_sha256']
            with np.load(c['field_path'],allow_pickle=False) as inp:adi=inp['field']
            limits=1e-6 if c['dz_m']==.3125e-6 else 2.5e-7
            errors={m:abs(c['methods'][m]['P_core']-methods['8'][m]['P_core']) for m in ('field','intensity')}
            row['adi_comparisons'].append(dict(id=c['id'],dz_m=c['dz_m'],errors=errors,limit=limits,pass_=max(errors.values())<=limits,raw_field_relative_error=float(np.linalg.norm(adi-fields[8])/np.linalg.norm(fields[8]))))
        report['rows'].append(row)
    powers={m:[r['methods']['8'][m]['P_core'] for r in report['rows']] for m in ('field','intensity')}
    report['predictions']={m:detector_module.predict640(ps[:4]) for m,ps in powers.items()}
    report['spatial']={m:spatial(ps[:4]) for m,ps in powers.items()}
    if prediction:
        report['new_reference_holdout_not_propagated']=True
        report['G640_already_available']=True
        return report
    frozen=json.loads(Path(execution['prediction_path']).read_text())
    assert sha(execution['prediction_path'])==execution['prediction_sha256'] and frozen['new_reference_holdout_not_propagated']
    assert execution['holdout_started_utc']>frozen['created_utc']
    first=json.loads(Path(report['rows'][-1]['solutions']['4']['checkpoints'][0]['path']).read_text())
    assert first['started_utc']>execution['holdout_started_utc']
    assert report['predictions']==frozen['predictions']
    report['holdout']={}
    for m,ps in powers.items():
        pred=report['predictions'][m]['prediction'];res=abs(ps[-1]-pred) if pred is not None else None;limit=.1*abs(ps[-1]-ps[-2])
        report['holdout'][m]=dict(prediction=pred,actual=ps[-1],residual=res,limit=limit,pass_=res is not None and abs(ps[-1]-ps[-2])>1e-12 and res<=limit)
    report['gaussian_controls']=[]
    for n in (256,320,400,500,640):
        ax=(np.arange(n)-n//2)*128e-6/n;xx,yy=np.meshgrid(ax,ax)
        field=(math.sqrt(2/(math.pi*(6e-6)**2))*np.exp(-(xx*xx+yy*yy)/(6e-6)**2)).astype(np.complex128)
        vals=detector.measure(field,n)
        for v in vals.values():v.update(error=abs(v['P_core']-(1-math.exp(-2))),pass_=abs(v['P_core']-(1-math.exp(-2)))<=(1e-6 if n>=500 else 1e-5) and v['change']<=1e-10)
        report['gaussian_controls'].append(dict(N=n,methods=vals))
    rows=report['rows'];report['reference_consistency_pass']=all(r['reference_field_difference']<=1e-9 and max(r['reference_power_difference'].values())<=1e-10 for r in rows)
    report['temporal_direct_pass']=all(c['pass_'] for r in rows for c in r['adi_comparisons'])
    report['quadrature_pass']=all(v['change']<=1e-8 for r in rows for vals in r['methods'].values() for v in vals.values())
    report['gaussian_pass']=all(v['pass_'] for r in report['gaussian_controls'] for v in r['methods'].values())
    report['method_agreement']={str(r['N']):abs(r['methods']['8']['field']['P_core']-r['methods']['8']['intensity']['P_core']) for r in rows if r['N']>=500}
    report['uncertainty_indicators']={}
    r=rows[3];mid=next(c for c in r['adi_comparisons'] if c['dz_m']==.3125e-6)
    for m in ('field','intensity'):
        terms=dict(space=report['spatial'][m].get('u_space'),temporal=mid['errors'][m],detector=report['method_agreement']['500'],quadrature=r['methods']['8'][m]['change'],reference=r['reference_power_difference'][m])
        combined=sum(terms.values()) if terms['space'] is not None else None
        report['uncertainty_indicators'][m]=dict(terms=terms,combined=combined,pass_=combined is not None and combined<=1e-3 and combined<=.01*powers[m][3],rigorous_bound=False)
    report['scientific_pass']=all([report['reference_consistency_pass'],report['temporal_direct_pass'],report['quadrature_pass'],report['gaussian_pass'],max(report['method_agreement'].values())<=1e-7,all(s['pass_'] for s in report['spatial'].values()),all(s['pass_'] for s in report['holdout'].values()),all(s['pass_'] for s in report['uncertainty_indicators'].values())])
    report['point03_closed']=report['scientific_pass']
    report['original_G_scientific_pass']=g['scientific_pass']
    report['holdout_chronology_pass']=True
    return report
