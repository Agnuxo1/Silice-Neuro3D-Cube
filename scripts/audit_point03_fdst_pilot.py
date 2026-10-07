"""Independent read-only integrity and acceptance recomputation for FDST pilot."""
import argparse
from datetime import datetime,timezone
import json
import math
from pathlib import Path
from run_point03_exponential import ROOT,sha,write
import numpy as np
from point03_linear_detector import Detector

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))

def audit(out):
    e=read(out/'execution.json');a=read(out/'assessment.json')
    assert e['status']=='completed' and e['sources_unchanged'] and e['elapsed_s']<=7200
    assert sha(e['assessment_path'])==e['assessment_sha256'] and sha(e['manifest_path'])==e['manifest_sha256']
    m=read(e['manifest_path']);assert m['created_utc']<e['finished_utc'] and m['steps']==[3200,6400,12800] and m['numerical_threads']==1
    for path,digest in m['source_sha256'].items():assert sha(path)==digest
    assert sha(m['input_path'])==m['input_sha256']
    with np.load(m['input_path'],allow_pickle=False) as data:initial=data['A0']
    dx=128e-6/626;pin=float(np.vdot(initial,initial).real*dx*dx)
    reference=read(m['reference_execution_path']);sol=reference['solutions']['17'];assert sha(sol['field_path'])==sol['field_sha256']
    with np.load(sol['field_path'],allow_pickle=False) as data:ref=data['field'].copy()
    detector=Detector();ref_measures=detector.measure(ref,626,pin);rows=[];count=0;max_power_residual=0.
    for s,row in zip(e['solutions'],a['rows'],strict=True):
        assert s['steps_total']==row['steps'];previous=None;digest=None;power=pin
        assert len(s['checkpoints'])==s['steps_total']//400
        for i,link in enumerate(s['checkpoints'],1):
            assert sha(link['path'])==link['sha256'];cp=read(link['path'])
            assert cp['status']=='completed' and cp['steps_total']==s['steps_total'] and cp['steps_done']==400*i and cp['chunk']==i
            assert cp['previous_report_path']==previous and cp['previous_report_sha256']==digest and cp['started_utc']>m['created_utc']
            assert cp['dz_m']==.002/s['steps_total'] and cp['elapsed_s']<=360 and cp['max_negative_amplification']<=1.10
            assert sha(cp['field_path'])==cp['field_sha256']
            with np.load(cp['field_path'],allow_pickle=False) as data:field=data['field'].copy()
            assert field.shape==(626,626) and field.dtype==np.dtype('complex128') and np.all(np.isfinite(field))
            actual=float(np.vdot(field,field).real*dx*dx);residual=abs(actual-cp['raw_total']);max_power_residual=max(max_power_residual,residual)
            assert residual<=1e-12 and 0<actual<=power+1e-9 and abs(power-cp['previous_power'])<=1e-12
            for key in ('resource_start','resource_end'):assert cp[key]['available_ram_bytes']>1.5*1024**3 and cp[key]['free_disk_bytes']>2*1024**3
            previous=link['path'];digest=link['sha256'];power=actual;count+=1
        measures=detector.measure(field,626,pin);errors=dict(field=float(np.linalg.norm(field-ref)/np.linalg.norm(ref)))
        for method in ('field','intensity'):errors['power_'+method]=abs(measures[method]['P_core']-ref_measures[method]['P_core'])
        for key,value in errors.items():assert abs(value-row['errors'][key])<=1e-12
        for method in ('field','intensity'):
            assert abs(measures[method]['P_core']-row['methods'][method]['P_core'])<=1e-12 and measures[method]['change']<=1e-10
        rows.append(errors)
    assert count==56 and len(e['solutions'])==3 and not a['point03_closed'] and not e['point03_closed']
    orders={key:[math.log2(x[key]/y[key]) if x[key]>0 and y[key]>0 else None for x,y in zip(rows,rows[1:])] for key in rows[0]}
    passed=all(p is not None and 3.5<=p<=4.5 for ps in orders.values() for p in ps) and rows[-1]['field']<=1e-4 and all(rows[-1][key]<=1e-6 for key in ('power_field','power_intensity'))
    assert passed==a['pilot_pass']==e['pilot_pass'] and orders==a['observed_orders']
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),integrity_pass=True,acceptance_recomputed=True,pilot_pass=passed,point03_closed=False,checkpoints_checked=count,source_files_checked=len(m['source_sha256']),max_raw_power_residual=max_power_residual,observed_orders=orders,assessment_sha256=sha(out/'assessment.json'),execution_sha256=sha(out/'execution.json'),manifest_sha256=sha(out/'manifest.json'),audit_source_sha256=sha(__file__))

def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--out',type=Path,required=True);args=p.parse_args();folder=args.out.resolve()
    r=audit(folder);write(folder/'integrity_audit.json',r);print(json.dumps(r));return 0
if __name__=='__main__':raise SystemExit(main())
