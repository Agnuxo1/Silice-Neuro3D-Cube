"""Independent fine-window P3 remeasurement; re-audit all retained P2 fields."""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import numpy as np
from audit_point03_p2 import audit as audit_old,independent_order
from point03_linear_detector import Detector
from run_point03_exponential import ROOT,sha,write


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def audit(out):
    old=audit_old(ROOT/'resultados/codex/point03_fixed_domain_20261007_P2')
    assert old['integrity_pass'] and not old['scientific_pass'] and old['checkpoints_checked']==87
    e=read(out/'execution.json');a=read(out/'assessment.json');m=read(out/'manifest.json')
    assert e['status']=='completed' and e['sources_unchanged'] and e['elapsed_s']<=36000 and not e['point03_closed']
    assert sha(out/'manifest.json')==e['manifest_sha256'] and sha(out/'assessment.json')==e['assessment_sha256']
    for path,digest in m['source_sha256'].items():assert sha(path)==digest
    assert m['ghost_bounds_m']==[-64e-6,64e-6] and m['numerical_threads']==1
    predpath=ROOT/'resultados/codex/point03_p3_prediction_20261008.json';pred=read(predpath)
    assert sha(predpath)==e['prediction_sha256'] and pred['created_utc']<e['started_utc']<m['created_utc']
    for path,digest in pred['source_sha256'].items():assert sha(path)==digest
    case=m['plan'][0];assert case['M']==800 and case['N']==799 and case['dx_m']==128e-6/800
    assert sha(case['input_path'])==case['input_sha256'] and sha(case['original_input_path'])==case['original_input_sha256']
    with np.load(case['input_path'],allow_pickle=False) as data:arrays={key:data[key].copy() for key in ('A0','dn','sigma','weights')}
    with np.load(case['original_input_path'],allow_pickle=False) as data:original={key:data[key].copy() for key in arrays}
    assert all(np.array_equal(arrays[key],value[1:,1:]) for key,value in original.items())
    dx=128e-6/800;pin=float(np.sum(abs(arrays['A0'])**2)*dx**2)
    assert abs(pin-case['P_in'])<=1e-12 and abs(pin-float(np.sum(abs(original['A0'])**2)*dx**2))<=1e-12
    geometry=read(out/'geometry_report.json');assert geometry['N']==800 and geometry['geometry_pass'] and len(geometry['reference_cells'])==48 and abs(geometry['grid_area']/geometry['global_area']-1)<=1e-12
    for cell in geometry['reference_cells']:assert cell['delta']<=1e-12 and cell['reference']['quality_pass'] and cell['reference']['quality_total']<=1e-13
    assert read(out/'gaussian_control.json')['pass_']
    detector=Detector();fields={};measure={};count=event_index=0;max_residual=0.
    assert len(e['children'])==134 and set(e['solutions'])=={'E29','E41','F64'}
    for label,expected in (('E29',29),('E41',41),('F64',64)):
        links=e['solutions'][label]['checkpoints'];assert len(links)==expected
        previous=digest=None;power=pin
        for index,link in enumerate(links,1):
            cp=read(link['path']);assert sha(link['path'])==link['sha256']
            event=e['children'][event_index];event_index+=1
            assert event['M']==800 and event['label']==label and event['index']==index and event['returncode']==0 and event['elapsed_s']<=370
            assert cp['status']=='completed' and cp['M']==800 and cp['N']==799 and cp['index']==index and cp['total']==expected and cp['elapsed_s']<=360
            assert cp['previous_report_path']==previous and cp['previous_report_sha256']==digest and cp['dx_m']==dx and cp['started_utc']>m['created_utc']
            for sample in ('resource_start','resource_end'):assert cp[sample]['available_ram_bytes']>1.5*1024**3 and cp[sample]['free_disk_bytes']>2*1024**3
            if label.startswith('E'):assert cp['length_m']==.002/expected
            else:assert cp['steps_done']==index*400 and cp['steps_total']==25600 and cp['dz_m']==.002/25600 and cp['max_negative_amplification']<=1.10
            assert sha(cp['field_path'])==cp['field_sha256']
            with np.load(cp['field_path'],allow_pickle=False) as data:field=data['field'].copy()
            assert field.shape==(799,799) and field.dtype==np.dtype('complex128') and np.all(np.isfinite(field))
            total=float(np.sum(abs(field)**2)*dx**2);max_residual=max(max_residual,abs(total-cp['raw_total']))
            assert abs(total-cp['raw_total'])<=1e-12 and 0<total<=power+1e-9 and abs(cp['previous_power']-power)<=1e-12
            previous,digest,power=link['path'],link['sha256'],total;count+=1
        fields[label]=np.pad(field,((1,0),(1,0)));measure[label]=detector.measure(fields[label],800,pin)
    norms={label:float(np.linalg.norm(value)) for label,value in fields.items()}
    ref_distance=float(np.linalg.norm(fields['E29']-fields['E41']));time_distance=float(np.linalg.norm(fields['F64']-fields['E41']))
    ref_bound=dx**2*(norms['E29']+norms['E41'])*ref_distance/pin
    time_bound=dx**2*(norms['F64']+norms['E41'])*time_distance/pin
    quad=max(row['change'] for measurements in measure.values() for row in measurements.values())
    reconstruction=abs(measure['E41']['field']['P_core']-measure['E41']['intensity']['P_core'])
    global_ok=ref_distance/norms['E41']<=1e-9 and ref_bound<=1e-6 and time_distance/norms['E41']<=1e-4 and time_bound+ref_bound+quad<=1e-5 and quad<=1e-10
    rows={}
    for method in ('field','intensity'):
        powers=old['predictions_recomputed'][method]['powers'][1:]
        p0=independent_order((400,500,640),powers);assert p0 is not None and 1.8<=p0<=2.2
        forecast=powers[-1]+(powers[-1]-powers[-2])*(1-(640/800)**p0)/((640/500)**p0-1)
        assert abs(forecast-pred['methods'][method]['prediction'])<=1e-12
        value=measure['E41'][method]['P_core'];p=independent_order((500,640,800),(powers[-2],powers[-1],value))
        disagreement=abs(p-p0)/max(abs(p),abs(p0)) if p is not None else None
        residual=abs(value-forecast);limit=.1*abs(value-powers[-1])
        reference=abs(value-measure['E29'][method]['P_core']);temporal=abs(value-measure['F64'][method]['P_core'])
        space=1.25*abs(value-powers[-1])/(1.25**min(p,2)-1) if p is not None else None
        indicator=space+reference+temporal+quad+reconstruction if space is not None else None
        conditions=dict(holdout=abs(value-powers[-1])>1e-12 and residual<=limit,order=disagreement is not None and disagreement<=.2,temporal=temporal<=1e-6,indicator=indicator is not None and indicator<=1e-3 and indicator<=.01*abs(value))
        recorded=a['rows'][method];assert conditions==recorded['conditions']
        for key,expected_value in dict(actual=value,residual=residual,limit=limit,temporal_error=temporal,total_indicator=indicator).items():
            assert (expected_value is None and recorded[key] is None) or abs(expected_value-recorded[key])<=1e-12
        global_ok=global_ok and reference<=1e-8
        rows[method]=dict(actual=value,prediction=forecast,residual=residual,limit=limit,new_order=p,order_disagreement=disagreement,reference_error=reference,temporal_error=temporal,total_indicator=indicator,conditions=conditions)
    passed=global_ok and all(all(row['conditions'].values()) for row in rows.values())
    assert global_ok==a['global_eligible'] and passed==a['scientific_pass']==e['scientific_pass']
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),integrity_pass=True,scientific_pass=passed,point03_closed=passed,checkpoints_checked=count+87,new_checkpoints_checked=count,primary_window_M=[400,500,640,800],M320_diagnostic_retained=True,P2_pass=False,global_eligible=global_ok,reference_bound=ref_bound,temporal_bound=time_bound,max_raw_power_residual=max_residual,rows=rows,scope='New prospectively tested fine window; conditional local scalar core power only; all older failures retained.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    result=audit(args.out.resolve());write(args.out/'integrity_audit.json',result);print(json.dumps(result))
