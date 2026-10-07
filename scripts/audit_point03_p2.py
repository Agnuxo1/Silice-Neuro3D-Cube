"""Recompute fixed-domain P2 eligibility from raw fields without its assessor."""
import argparse
from datetime import datetime,timezone
import json
import math
import os
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import numpy as np
from run_point03_exponential import ROOT,sha,write
from point03_linear_detector import Detector
from run_point03_m1 import order


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def independent_order(ms,powers):
    try:return order(ms,powers)
    except (AssertionError,ValueError):return None


def raw(path,digest,key='field'):
    assert sha(path)==digest
    with np.load(path,allow_pickle=False) as data:return data[key].copy()


def audit(out):
    e=read(out/'execution.json');m=read(out/'coarse_manifest.json');coarse=read(out/'coarse_assessment.json');pred=read(out/'prediction.json')
    assert e['status']=='completed' and e['sources_unchanged'] and e['elapsed_s']<=36000 and not e['point03_closed']
    manifests=[m]
    if e['stage']=='holdout_complete':manifests.append(read(out/'fine_manifest.json'))
    for manifest in manifests:
        assert manifest['numerical_threads']==1 and manifest['ghost_bounds_m']==[-64e-6,64e-6]
        for path,digest in manifest['source_sha256'].items():assert sha(path)==digest
    p1=ROOT/'resultados/codex/point03_fixed_domain_20261007_P1'
    p1a=read(p1/'integrity_audit.json');p1m=read(p1/'manifest.json')
    assert p1a['integrity_pass'] and p1a['controls_eligible']
    plans={case['M']:case for manifest in manifests for case in manifest['plan']}
    plans[400]=dict(M=400,N=399,input_path=p1m['input_path'],input_sha256=p1m['input_sha256'],P_in=p1m['P_in'],original_input_path=p1m['original_input_path'],original_input_sha256=p1m['original_input_sha256'])
    inputs={};areas=[]
    for M,case in plans.items():
        assert case['N']==M-1 and sha(case['input_path'])==case['input_sha256'] and sha(case['original_input_path'])==case['original_input_sha256']
        with np.load(case['input_path'],allow_pickle=False) as data:arrays={key:data[key].copy() for key in ('A0','dn','sigma','weights')}
        with np.load(case['original_input_path'],allow_pickle=False) as data:original={key:data[key].copy() for key in arrays}
        assert all(np.array_equal(value,original[key][1:,1:]) and value.shape==(M-1,M-1) for key,value in arrays.items())
        dx=128e-6/M;pin=float(np.sum(abs(arrays['A0'])**2)*dx**2)
        assert abs(pin-case['P_in'])<=1e-12 and abs(pin-float(np.sum(abs(original['A0'])**2)*dx**2))<=1e-12
        assert np.all(original['dn'][0,:]==0) and np.all(original['dn'][:,0]==0)
        areas.append(float(-arrays['dn'].sum()*dx**2/.003));inputs[M]=pin
    assert max(areas)/min(areas)-1<=1e-12
    detector=Detector();fields={};measure={};count=new_count=0;residual=0.
    for M in sorted(plans):
        fields[M]={};measure[M]={};pin=inputs[M];dx=128e-6/M
        for label,solution in e['solutions'][str(M)].items():
            previous=digest=None;power=pin;links=solution['checkpoints'];expected=int(label[1:])
            assert len(links)==expected
            for index,link in enumerate(links,1):
                cp=read(link['path']);assert sha(link['path'])==link['sha256'] and cp['status']=='completed'
                if M==400:
                    assert cp['segment']==index and cp['segments']==expected and cp['N']==399
                else:
                    new_count+=1
                    assert cp['M']==M and cp['N']==M-1 and cp['index']==index and cp['total']==expected
                    event=next(item for item in e['children'] if item['M']==M and item['label']==label and item['index']==index)
                    assert event['returncode']==0 and event['elapsed_s']<=370
                assert cp['previous_report_path']==previous and cp['previous_report_sha256']==digest and cp['dx_m']==dx and cp['elapsed_s']<=360
                for sample in ('resource_start','resource_end'):
                    assert cp[sample]['available_ram_bytes']>1.5*1024**3 and cp[sample]['free_disk_bytes']>2*1024**3
                if label.startswith('E'):assert cp['length_m']==.002/expected
                else:assert cp['steps_total']==25600 and cp['steps_done']==400*index and cp['dz_m']==.002/25600 and cp['max_negative_amplification']<=1.10
                field=raw(cp['field_path'],cp['field_sha256']);assert field.shape==(M-1,M-1) and field.dtype==np.dtype('complex128') and np.all(np.isfinite(field))
                total=float(np.sum(abs(field)**2)*dx**2);residual=max(residual,abs(total-cp['raw_total']))
                assert abs(total-cp['raw_total'])<=1e-12 and 0<total<=power+1e-9 and abs(cp['previous_power']-power)<=1e-12
                previous,digest,power=link['path'],link['sha256'],total;count+=1
            fields[M][label]=np.pad(field,((1,0),(1,0)));measure[M][label]=detector.measure(fields[M][label],M,pin)
    assert new_count==len(e['children'])
    references={};coarse_ok=True
    for M in sorted(plans):
        labels=sorted((label for label in fields[M] if label.startswith('E')),key=lambda label:int(label[1:]));assert len(labels)==2
        a,b=(fields[M][label] for label in labels);na=float(np.linalg.norm(a));nb=float(np.linalg.norm(b));distance=float(np.linalg.norm(a-b))
        bound=(128e-6/M)**2*(na+nb)*distance/inputs[M]
        quad=max(value['change'] for row in measure[M].values() for value in row.values())
        powers={method:abs(measure[M][labels[0]][method]['P_core']-measure[M][labels[1]][method]['P_core']) for method in ('field','intensity')}
        eligible=distance/nb<=1e-9 and bound<=1e-6 and quad<=1e-10 and max(powers.values())<=1e-8
        references[M]=dict(fine=labels[1],eligible=eligible,bound=bound,quad=quad,power_errors=powers)
        if M!=800:
            assert eligible==coarse[str(M)]['eligible'];coarse_ok=coarse_ok and eligible
            for label in labels:
                for method in ('field','intensity'):assert abs(measure[M][label][method]['P_core']-coarse[str(M)]['measured'][label][method]['P_core'])<=1e-12
    predicted={}
    for method in ('field','intensity'):
        powers=[measure[M][references[M]['fine']][method]['P_core'] for M in (320,400,500,640)]
        orders=[independent_order((320,400,500),powers[:3]),independent_order((400,500,640),powers[1:])]
        stable=all(p is not None for p in orders) and abs(orders[0]-orders[1])/max(abs(orders[0]),abs(orders[1]))<=.2
        forecast=powers[-1]+(powers[-1]-powers[-2])*(1-(640/800)**orders[-1])/((640/500)**orders[-1]-1) if stable else None
        assert stable==pred['methods'][method]['eligible']
        if stable:assert abs(forecast-pred['methods'][method]['prediction'])<=1e-12
        predicted[method]=dict(powers=powers,orders=orders,forecast=forecast)
        coarse_ok=coarse_ok and stable
    assert coarse_ok==pred['eligible']
    rows={};passed=False;global_ok=False
    if e['stage']=='holdout_complete':
        assert coarse_ok and e['prediction_git_commit']
        import subprocess
        blob=subprocess.check_output(['git','-c',f'safe.directory={ROOT.as_posix()}','show',e['prediction_git_commit']+':'+(out/'prediction.json').relative_to(ROOT).as_posix()],cwd=ROOT)
        import hashlib
        assert hashlib.sha256(blob).hexdigest()==sha(out/'prediction.json')
        assert pred['created_utc']<read(out/'geometry_report.json').get('created_utc',manifests[-1]['created_utc'])
        geometry=read(out/'geometry_report.json');assert geometry['geometry_pass'] and geometry['N']==800 and len(geometry['reference_cells'])==48 and abs(geometry['grid_area']/geometry['global_area']-1)<=1e-12
        for cell in geometry['reference_cells']:assert cell['delta']<=1e-12 and cell['reference']['quality_pass'] and cell['reference']['quality_total']<=1e-13
        assert read(out/'gaussian_control.json')['pass_']
        a,b=fields[800]['F64'],fields[800]['E41'];norm_a=float(np.linalg.norm(a));norm_b=float(np.linalg.norm(b));distance=float(np.linalg.norm(a-b));ref=references[800]
        time_bound=(128e-6/800)**2*(norm_a+norm_b)*distance/inputs[800];global_ok=ref['eligible'] and distance/norm_b<=1e-4 and ref['quad']<=1e-10 and time_bound+ref['bound']+ref['quad']<=1e-5
        reconstruction=abs(measure[800]['E41']['field']['P_core']-measure[800]['E41']['intensity']['P_core'])
        recorded=read(out/'assessment.json');assert global_ok==recorded['global_eligible']
        for method in ('field','intensity'):
            old=predicted[method];value=measure[800]['E41'][method]['P_core'];last=old['powers'][-1]
            p=independent_order((500,640,800),(old['powers'][-2],last,value));disagreement=abs(p-old['orders'][-1])/max(abs(p),abs(old['orders'][-1])) if p is not None else None
            error=abs(value-old['forecast']);limit=.1*abs(value-last);temporal=abs(value-measure[800]['F64'][method]['P_core'])
            space=1.25*abs(value-last)/(1.25**min(p,2)-1) if p is not None else None
            indicator=space+temporal+ref['power_errors'][method]+ref['quad']+reconstruction if space is not None else None
            conditions=dict(holdout=abs(value-last)>1e-12 and error<=limit,order=disagreement is not None and disagreement<=.2,temporal=temporal<=1e-6,indicator=indicator is not None and indicator<=1e-3 and indicator<=.01*abs(value))
            assert conditions==recorded['rows'][method]['conditions']
            for key,expected in dict(actual=value,residual=error,limit=limit,temporal_error=temporal,total_indicator=indicator).items():
                assert (expected is None and recorded['rows'][method][key] is None) or abs(expected-recorded['rows'][method][key])<=1e-12
            rows[method]=dict(actual=value,prediction=old['forecast'],residual=error,limit=limit,order=p,order_disagreement=disagreement,total_indicator=indicator,conditions=conditions)
        passed=global_ok and all(all(row['conditions'].values()) for row in rows.values())
    else:assert e['stage']=='prerequisites_failed' and not coarse_ok
    assert passed==e['scientific_pass']
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),integrity_pass=True,scientific_pass=passed,point03_closed=passed,coarse_eligible=coarse_ok,global_eligible=global_ok,stage=e['stage'],checkpoints_checked=count,new_checkpoints_checked=new_count,max_raw_power_residual=residual,rows=rows,predictions_recomputed=predicted,historical_failures_retained=True,scope='Conditional local scalar core-power convergence for fixed physical domain only; no general boundary/phase/Maxwell/fabrication closure.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    result=audit(args.out.resolve());write(args.out/'integrity_audit.json',result);print(json.dumps(result))
