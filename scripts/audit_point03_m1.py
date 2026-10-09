"""Recompute M1 from raw fields; never invoke its assessor or order solver."""
import argparse
from datetime import datetime,timezone
import json
import math
import os
from pathlib import Path
for variable in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[variable]='1'
import numpy as np
from scipy.optimize import brentq
from point03_linear_detector import Detector
from run_point03_exponential import ROOT,sha,write

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))

def array(path,digest,key='field'):
    assert sha(path)==digest
    with np.load(path,allow_pickle=False) as archive:value=archive[key].copy()
    assert np.all(np.isfinite(value))
    return value

def observed(ns,values):
    a,b=values[0]-values[1],values[1]-values[2]
    if a*b<=0 or min(abs(a),abs(b))<=1e-12:return None
    x=math.log(ns[2]/ns[0]);y=math.log(ns[2]/ns[1]);target=math.log(a/b)
    def residual(p):
        return p*y+math.log(math.expm1(p*(x-y)))-math.log(math.expm1(p*y))-target
    try:return float(brentq(residual,.05,8))
    except ValueError:return None

def audit(folder):
    e=read(folder/'execution.json');a=read(folder/'assessment.json')
    assert e['status']=='completed' and e['sources_unchanged'] and e['elapsed_s']<=18000
    assert not e['point03_closed'] and not a['point03_closed'] and a['closure_requires_independent_audit']
    assert sha(e['assessment_path'])==e['assessment_sha256'] and sha(e['manifest_path'])==e['manifest_sha256']
    m=read(e['manifest_path']);assert m['N']==767 and m['numerical_threads']==1
    for path,digest in m['source_sha256'].items():assert sha(path)==digest
    assert sha(m['prediction_path'])==m['prediction_sha256']
    pred=read(m['prediction_path'])
    for path,digest in pred['source_sha256'].items():assert sha(path)==digest
    assert pred['created_utc']<e['started_utc']<m['created_utc']
    geom=read(folder/'geometry_report.json');assert geom['geometry_pass'] and geom['N']==767 and len(geom['reference_cells'])==48
    assert abs(geom['grid_area']/geom['global_area']-1)<=1e-12
    for cell in geom['reference_cells']:
        assert cell['delta']<=1e-12 and cell['reference']['quality_pass'] and cell['reference']['quality_total']<=1e-13
    initial=array(m['input_path'],m['input_sha256'],'A0');dx=128e-6/767;pin=float(np.vdot(initial,initial).real*dx**2)
    assert initial.shape==(767,767) and initial.dtype==np.dtype('complex128') and abs(pin-1)<=1e-12
    with np.load(m['input_path'],allow_pickle=False) as archive:
        dn=archive['dn'].copy();sigma=archive['sigma'].copy();weights=archive['weights'].copy()
    with np.load(folder/'geometry767.npz',allow_pickle=False) as archive:fraction=archive['fraction'].copy()
    assert np.array_equal(dn,-.003*fraction) and np.all((fraction>=0)&(fraction<=1))
    axis=(np.arange(767)-767//2)*dx
    radius=np.maximum(abs(axis)[:,None],abs(axis)[None,:])/64e-6
    assert np.allclose(sigma,4e4*np.maximum((radius-.8)/.2,0)**4,rtol=1e-13,atol=1e-10)
    assert abs(float(weights.sum()*dx**2)/(math.pi*(6e-6)**2)-1)<=1e-12
    detector=Detector();fields={};measures={};count=0;max_raw_residual=0.
    assert set(e['solutions'])=={'19','31','FDST'} and len(e['children'])==90
    child_index=0
    for label,expected in (('19',19),('31',31),('FDST',40)):
        links=e['solutions'][label]['checkpoints'];assert len(links)==expected
        previous=digest=None;power=pin
        for index,link in enumerate(links,1):
            child=e['children'][child_index];child_index+=1
            assert child['integrator']==label and child['index']==index and child['returncode']==0 and child['elapsed_s']<=370
            assert sha(link['path'])==link['sha256'];cp=read(link['path'])
            assert cp['status']=='completed' and cp['previous_report_path']==previous and cp['previous_report_sha256']==digest
            assert cp['elapsed_s']<=360 and cp['started_utc']>m['created_utc']
            if label=='FDST':
                assert cp['chunk']==index and cp['steps_done']==512*index and cp['steps_total']==20480
                assert cp['dz_m']==.002/20480 and cp['max_negative_amplification']<=1.10 and abs(cp['previous_power']-power)<=1e-12
            else:
                assert cp['N']==767 and cp['segment']==index and cp['segments']==expected and cp['length_m']==.002/expected
            value=array(cp['field_path'],cp['field_sha256']);assert value.shape==(767,767) and value.dtype==np.dtype('complex128')
            actual=float(np.vdot(value,value).real*dx**2);residual=abs(actual-cp['raw_total']);max_raw_residual=max(max_raw_residual,residual)
            assert residual<=1e-12 and 0<actual<=power+1e-9
            for sample in ('resource_start','resource_end'):
                assert cp[sample]['available_ram_bytes']>1.5*1024**3 and cp[sample]['free_disk_bytes']>2*1024**3
            previous,digest,power=link['path'],link['sha256'],actual;count+=1
        fields[label]=value;measures[label]=detector.measure(value,767,pin)
    assert count==90
    h=read(ROOT/'resultados/codex/point03_exponential_20261007_H2/assessment.json')
    assert read(ROOT/'resultados/codex/point03_exponential_20261007_H2/integrity_audit.json')['integrity_pass']
    primary={method:[] for method in ('field','intensity')}
    for n in (320,400,500,640):
        row=next(row for row in h['rows'] if row['N']==n);solution=row['solutions'][str(row['fine_segments'])]
        value=array(solution['field_path'],solution['field_sha256']);measurement=detector.measure(value,n,row['P_in'])
        for method in primary:primary[method].append(measurement[method]['P_core'])
    norms={label:float(np.linalg.norm(value)) for label,value in fields.items()}
    ref_distance=float(np.linalg.norm(fields['19']-fields['31']));time_distance=float(np.linalg.norm(fields['FDST']-fields['31']))
    ref_bound=dx**2*(norms['19']+norms['31'])*ref_distance/pin;time_bound=dx**2*(norms['FDST']+norms['31'])*time_distance/pin
    quad=max(value['change'] for row in measures.values() for value in row.values())
    reconstruct=abs(measures['31']['field']['P_core']-measures['31']['intensity']['P_core'])
    globals_=dict(reference_field=ref_distance/norms['31']<=1e-9,reference_bound=ref_bound<=1e-6,temporal_field=time_distance/norms['31']<=1e-4,temporal_bound=time_bound+ref_bound+quad<=1e-5,quadrature=quad<=1e-10)
    assert globals_==a['global_gates']
    rows={}
    for method,powers in primary.items():
        frozen=pred['prediction'][method];recorded=a['gates'][method]
        assert max(abs(x-y) for x,y in zip(powers,frozen['powers'],strict=True))<=1e-12
        old_orders=[observed([320,400,500],powers[:3]),observed([400,500,640],powers[1:])]
        assert all(p is not None for p in old_orders)
        for x,y in zip(old_orders,frozen['orders'],strict=True):assert abs(x-y)<=1e-8
        forecast=powers[-1]+(powers[-1]-powers[-2])*(1-(640/767)**old_orders[-1])/((640/500)**old_orders[-1]-1)
        assert abs(forecast-frozen['prediction'])<=1e-12
        value=measures['31'][method]['P_core'];new_order=observed([500,640,767],[powers[-2],powers[-1],value])
        disagreement=abs(new_order-old_orders[-1])/max(abs(new_order),abs(old_orders[-1])) if new_order is not None else None
        residual=abs(value-forecast);limit=.1*abs(value-powers[-1])
        reference_error=abs(value-measures['19'][method]['P_core']);temporal_error=abs(value-measures['FDST'][method]['P_core'])
        spatial=1.25*abs(value-powers[-1])/((767/640)**min(new_order,2)-1) if new_order is not None else None
        total=spatial+reference_error+temporal_error+quad+reconstruct if spatial is not None else None
        conditions=dict(holdout=abs(value-powers[-1])>1e-12 and residual<=limit,order=disagreement is not None and disagreement<=.2,reference_power=reference_error<=1e-8,temporal_power=temporal_error<=1e-6,uncertainty=total is not None and total<=1e-3 and total<=.01*abs(value))
        assert conditions==recorded['conditions'] and all(conditions.values())==recorded['pass_']
        for key,expected in dict(actual=value,prediction=forecast,residual=residual,limit=limit,reference_error=reference_error,temporal_error=temporal_error,space_indicator=spatial,total_indicator=total).items():
            assert (expected is None and recorded[key] is None) or (expected is not None and abs(expected-recorded[key])<=1e-12)
        assert (new_order is None and recorded['new_order'] is None) or (new_order is not None and abs(new_order-recorded['new_order'])<=1e-8)
        rows[method]=dict(actual=value,forecast=forecast,residual=residual,limit=limit,new_order=new_order,order_disagreement=disagreement,total_indicator=total,conditions=conditions)
    passed=all(globals_.values()) and all(all(row['conditions'].values()) for row in rows.values())
    assert passed==a['scientific_pass']==e['scientific_pass']
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),integrity_pass=True,acceptance_recomputed=True,scientific_pass=passed,point03_closed=passed,checkpoints_checked=90,primary_fields_remeasured=4,source_files_checked=len(m['source_sha256']),max_raw_power_residual=max_raw_residual,rows=rows,global_gates=globals_,reference_bound=ref_bound,temporal_bound=time_bound,execution_sha256=sha(folder/'execution.json'),assessment_sha256=sha(folder/'assessment.json'),audit_source_sha256=sha(__file__),historical_failures_retained=True,scope='Conditional local scalar core-power convergence under new M1 criteria only; no boundary/phase/Maxwell/fabrication closure.')

if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    result=audit(args.out.resolve());write(args.out/'integrity_audit.json',result);print(json.dumps(result))
