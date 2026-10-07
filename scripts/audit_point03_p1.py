"""Independently remeasure P1 cropped input, chains, references and hypothesis."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path

for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import numpy as np
from point03_linear_detector import Detector
from run_point03_exponential import sha, write


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def audit(folder):
    e=read(folder/'execution.json');a=read(folder/'assessment.json');m=read(folder/'manifest.json')
    assert e['status']=='completed' and e['sources_unchanged'] and e['elapsed_s']<=2400
    assert sha(folder/'manifest.json')==e['manifest_sha256'] and sha(folder/'assessment.json')==e['assessment_sha256']
    for path,digest in m['source_sha256'].items():assert sha(path)==digest
    for path,digest in ((m['input_path'],m['input_sha256']),(m['original_input_path'],m['original_input_sha256']),(m['baseline_path'],m['baseline_sha256'])):assert sha(path)==digest
    assert m['N']==399 and m['dx_m']==128e-6/400 and m['numerical_threads']==1
    assert m['preflight']['pass_'] and m['preflight']['principal_submatrix_exact']
    assert m['preflight']['sine_field_error']<=1e-9 and m['preflight']['sine_power_error']<=1e-10
    with np.load(m['original_input_path'],allow_pickle=False) as data:original={key:data[key].copy() for key in ('A0','dn','sigma','weights')}
    with np.load(m['input_path'],allow_pickle=False) as data:cropped={key:data[key].copy() for key in original}
    assert all(np.array_equal(cropped[key],original[key][1:,1:]) for key in original)
    dx=m['dx_m'];pin=float(np.sum(abs(cropped['A0'])**2)*dx**2);original_pin=float(np.sum(abs(original['A0'])**2)*dx**2)
    assert abs(pin-m['P_in'])<=1e-12 and abs(original_pin-m['baseline_P_in'])<=1e-12 and abs(pin-original_pin)<=1e-12
    assert len(e['children'])==12 and set(e['solutions'])=={'5','7'}
    detector=Detector();fields={};measure={};child=0;raw_residual=0.
    for label in ('5','7'):
        links=e['solutions'][label]['checkpoints'];assert len(links)==int(label)
        previous=digest=None;power=pin
        for index,link in enumerate(links,1):
            cp=read(link['path']);assert sha(link['path'])==link['sha256']
            event=e['children'][child];child+=1
            assert event['segments']==int(label) and event['index']==index and event['returncode']==0 and event['elapsed_s']<=370
            assert cp['status']=='completed' and cp['segment']==index and cp['segments']==int(label) and cp['N']==399
            assert cp['previous_report_path']==previous and cp['previous_report_sha256']==digest and cp['dx_m']==dx and cp['length_m']==.002/int(label)
            assert cp['elapsed_s']<=360 and cp['started_utc']>m['created_utc']
            for sample in ('resource_start','resource_end'):
                assert cp[sample]['available_ram_bytes']>1.5*1024**3 and cp[sample]['free_disk_bytes']>2*1024**3
            assert sha(cp['field_path'])==cp['field_sha256']
            with np.load(cp['field_path'],allow_pickle=False) as data:field=data['field'].copy()
            assert field.shape==(399,399) and field.dtype==np.dtype('complex128') and np.all(np.isfinite(field))
            actual=float(np.sum(abs(field)**2)*dx**2)
            raw_residual=max(raw_residual,abs(actual-cp['raw_total']))
            assert abs(actual-cp['raw_total'])<=1e-12 and 0<actual<=power+1e-9 and abs(cp['previous_power']-power)<=1e-12
            previous,digest,power=link['path'],link['sha256'],actual
        fields[label]=np.pad(field,((1,0),(1,0)))
        measure[label]=detector.measure(fields[label],400,pin)
    with np.load(m['baseline_path'],allow_pickle=False) as data:base=data['field'].copy()
    baseline=detector.measure(base,400,original_pin)
    norms={label:float(np.linalg.norm(value)) for label,value in fields.items()}
    distance=float(np.linalg.norm(fields['5']-fields['7']))
    bound=dx**2*(norms['5']+norms['7'])*distance/pin
    quad=max(value['change'] for row in (*measure.values(),baseline) for value in row.values())
    rows={}
    for method in ('field','intensity'):
        actual=measure['7'][method]['P_core'];old=baseline[method]['P_core']
        change=abs(actual-old);reference=abs(actual-measure['5'][method]['P_core'])
        row=dict(actual=actual,baseline=old,change=change,reference_change=reference,hypothesis_pass=change<=1e-6,reference_pass=reference<=1e-8)
        recorded=a['rows'][method]
        for key in ('actual','baseline','change','reference_change'):assert abs(row[key]-recorded[key])<=1e-12
        for key in ('hypothesis_pass','reference_pass'):assert row[key]==recorded[key]
        rows[method]=row
    eligible=distance/norms['7']<=1e-9 and bound<=1e-6 and quad<=1e-10 and all(row['reference_pass'] for row in rows.values())
    passed=eligible and all(row['hypothesis_pass'] for row in rows.values())
    assert eligible==a['controls_eligible'] and passed==a['hypothesis_pass']==e['hypothesis_pass']
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),integrity_pass=True,controls_eligible=eligible,hypothesis_pass=passed,point03_closed=False,checkpoints_checked=12,source_files_checked=len(m['source_sha256']),rows=rows,max_raw_power_residual=raw_residual,reference_bound=bound,reference_field_difference=distance/norms['7'],quadrature_change=quad,auditor_source_sha256=sha(__file__),scope='N400 boundary-placement diagnosis only; neither general boundary validation nor T96 convergence.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    result=audit(args.out.resolve());write(args.out/'integrity_audit.json',result);print(json.dumps(result))
