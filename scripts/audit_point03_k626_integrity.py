"""Post-run verification of a completed K626 probe, without propagation."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
from run_point03_exponential import sha,write
import numpy as np

def audit(out):
    execution=json.loads((out/'execution.json').read_text(encoding='utf-8'));assert execution['status']=='completed' and execution['sources_unchanged']
    manifest=json.loads(Path(execution['manifest_path']).read_text(encoding='utf-8'));assert sha(execution['manifest_path'])==execution['manifest_sha256']
    for p,d in manifest['source_sha256'].items():assert sha(p)==d
    case=manifest['plan'][0];assert case['N']==626 and sha(case['input_path'])==case['input_sha256']
    dx=128e-6/626
    with np.load(case['input_path'],allow_pickle=False) as inp:
        for k in ('A0','dn','sigma','weights'):assert inp[k].shape==(626,626) and np.all(np.isfinite(inp[k]))
        assert inp['A0'].dtype==np.dtype('complex128') and np.min(inp['sigma'])>=0
        assert np.min(inp['dn'])>=-.003-1e-14 and np.max(inp['dn'])<=1e-14
        assert np.min(inp['weights'])>=0 and np.max(inp['weights'])<=1
        pin=float(np.sum(np.abs(inp['A0'])**2)*dx*dx);assert abs(pin-1)<=1e-12
    assert sha(execution['assessment_path'])==execution['assessment_sha256']
    assessment=json.loads(Path(execution['assessment_path']).read_text(encoding='utf-8'));assert assessment['integrity_pass'] and assessment['checkpoints_checked']==28
    geometry=json.loads((out/'geometry_report.json').read_text(encoding='utf-8'));assert geometry['geometry_pass'] and len(geometry['reference_cells'])==48
    count=0;chains=[]
    for part,sol in execution['solutions'].items():
        previous=None;previous_sha=None;power=pin;max_growth=0
        assert len(sol['checkpoints'])==int(part)
        for i,link in enumerate(sol['checkpoints'],1):
            assert sha(link['path'])==link['sha256'];cp=json.loads(Path(link['path']).read_text(encoding='utf-8'))
            assert cp['status']=='completed' and cp['N']==626 and cp['segments']==int(part) and cp['segment']==i
            assert cp['previous_report_path']==previous and cp['previous_report_sha256']==previous_sha and cp['elapsed_s']<=360
            assert sha(cp['field_path'])==cp['field_sha256']
            with np.load(cp['field_path'],allow_pickle=False) as inp:field=inp['field']
            assert field.shape==(626,626) and field.dtype==np.dtype('complex128') and np.all(np.isfinite(field))
            actual=float(np.sum(np.abs(field)**2)*dx*dx);assert abs(actual-cp['raw_total'])<=1e-12 and 0<actual<=power+1e-10
            max_growth=max(max_growth,actual-power);power=actual;previous=link['path'];previous_sha=link['sha256'];count+=1
        assert sol['field_path']==cp['field_path'] and sol['field_sha256']==cp['field_sha256']
        chains.append(dict(segments=int(part),final_raw_power=power,max_positive_power_increment=max_growth))
    assert count==28 and len(execution['children'])==28
    assert all(c['returncode']==0 and c['elapsed_s']<=370 for c in execution['children'])
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),integrity_pass=True,N=626,checkpoints_checked=count,geometry_reference_cells=48,input_power=pin,chains=chains,scientific_pass=assessment['scientific_pass'],point03_closed=assessment['point03_closed'],scope='Evidence integrity recheck, not an additional optical solver.')

def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--probe',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=audit(a.probe);write(a.output,r);print(json.dumps(r));return 0
if __name__=='__main__':raise SystemExit(main())
