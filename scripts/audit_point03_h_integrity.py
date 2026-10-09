"""Independent post-run audit of H2's retained and new checkpoint chains."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import numpy as np

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def audit(out):
    execution=json.loads((out/'execution.json').read_text(encoding='utf-8'))
    assert execution['status']=='completed' and execution['sources_unchanged']
    manifest=json.loads(Path(execution['manifest_path']).read_text(encoding='utf-8'))
    assert sha(execution['manifest_path'])==execution['manifest_sha256']
    for p,d in manifest['source_sha256'].items():assert sha(p)==d
    assert sha(execution['assessment_path'])==execution['assessment_sha256']
    assert sha(execution['prediction_path'])==execution['prediction_sha256']
    assessment=json.loads(Path(execution['assessment_path']).read_text(encoding='utf-8'))
    assert assessment['integrity_pass']
    assert len(execution['children'])==28 and all(c['returncode']==0 and c['elapsed_s']<=370 for c in execution['children'])
    rows=[];count=0
    for case,result in zip(manifest['plan'],execution['results']):
        n=case['N'];dx=128e-6/n;assert result['N']==n and sha(case['input_path'])==case['input_sha256']
        with np.load(case['input_path'],allow_pickle=False) as data:
            assert set(data.files)>={'A0','dn','sigma'}
            for key in ('A0','dn','sigma'):assert data[key].shape==(n,n) and np.all(np.isfinite(data[key]))
            assert data['A0'].dtype==np.dtype('complex128') and np.min(data['sigma'])>=0
            initial=float(np.sum(np.abs(data['A0'])**2)*dx*dx)
        assert abs(initial-1)<=1e-12
        expected=(11,17) if n==640 else (4,8)
        assert sorted(map(int,result['solutions']))==list(expected)
        for segments in expected:
            sol=result['solutions'][str(segments)];previous=None;previous_sha=None;power=initial;worst_growth=0
            assert len(sol['checkpoints'])==segments
            for i,link in enumerate(sol['checkpoints'],1):
                assert sha(link['path'])==link['sha256'];cp=json.loads(Path(link['path']).read_text(encoding='utf-8'))
                assert cp['N']==n and cp['segments']==segments and cp['segment']==i and cp['status']=='completed'
                assert cp['previous_report_path']==previous and cp['previous_report_sha256']==previous_sha
                assert cp['length_m']==.002/segments and cp['elapsed_s']<=360
                assert sha(cp['field_path'])==cp['field_sha256']
                with np.load(cp['field_path'],allow_pickle=False) as data:field=data['field']
                assert field.shape==(n,n) and field.dtype==np.dtype('complex128') and np.all(np.isfinite(field))
                actual=float(np.sum(np.abs(field)**2)*dx*dx)
                assert abs(actual-cp['raw_total'])<=1e-12 and actual>0
                growth=actual-power;worst_growth=max(worst_growth,growth)
                assert growth<=1e-10,'Dissipative semidiscrete operator must not increase norm'
                previous=link['path'];previous_sha=link['sha256'];power=actual;count+=1
            assert sol['field_path']==cp['field_path'] and sol['field_sha256']==cp['field_sha256']
            rows.append(dict(N=n,segments=segments,initial_power=initial,final_power=power,max_positive_power_increment=worst_growth))
    assert count==76
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),integrity_pass=True,checkpoints_checked=count,new_checkpoints=28,retained_checkpoints=48,source_files_checked=len(manifest['source_sha256']),rows=rows,scientific_pass=assessment['scientific_pass'],point03_closed=assessment['point03_closed'],scope='Hashes, chains, shapes, raw powers, dissipativity and operational limits; no added scientific acceptance criterion.')

def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--h',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args();report=audit(args.h)
    with args.output.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(report));return 0
if __name__=='__main__':raise SystemExit(main())
