"""Additional post-run verification of G's declared integrity requirements."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import traceback

for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[k]='1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('--study',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    import numpy as np
    report=dict(created_utc=datetime.now(timezone.utc).isoformat(),integrity_pass=False,
                scope='Identity, byte and array audit; no propagation or second physical solver.',verified_chunks=0,cases=[])
    try:
        p=args.study.resolve();e=json.loads((p/'execution.json').read_text())
        assert e['status']=='completed' and e['sources_unchanged'] and e['inputs_unchanged']
        assert sha(e['assessment_path'])==e['assessment_sha256']
        a=json.loads(Path(e['assessment_path']).read_text())
        assert sha(e['manifest_path'])==e['manifest_sha256']
        m=json.loads(Path(e['manifest_path']).read_text())
        for path,d in m['source_sha256'].items():assert sha(path)==d
        for path,d in m['input_sha256'].items():assert sha(path)==d
        assert len(e['results'])==len(a['rows'])==9 and len(e['children'])==224
        expected=[('g_n256_mid',256,.3125e-6,6400,False),('g_n320_mid',320,.3125e-6,6400,False),
                  ('n400_geom_z03125',400,.3125e-6,6400,True),('n500_geom_z03125',500,.3125e-6,6400,True),
                  ('n400_geom_z0625',400,.625e-6,3200,True),('n500_geom_z0625',500,.625e-6,3200,True),
                  ('g_n400_fine',400,.15625e-6,12800,False),('g_n500_fine',500,.15625e-6,12800,False),
                  ('g_n640_holdout',640,.3125e-6,6400,False)]
        for case,row,identity in zip(e['results'],a['rows'],expected):
            assert tuple(case[k] for k in ('id','N','dz_m','steps','reused'))==identity
            assert tuple(row[k] for k in ('id','N','dz_m','steps','reused'))==identity
            assert abs(case['dz_m']*case['steps']-.002)<=1e-15
            assert sha(case['input_path'])==case['input_sha256']
            with np.load(case['input_path'],allow_pickle=False) as z:
                arrays={k:z[k] for k in z.files}
            n=case['N'];dx=128e-6/n
            assert set(arrays)=={'A0','dn','sigma','weights'}
            assert all(v.shape==(n,n) and np.all(np.isfinite(v)) for v in arrays.values())
            assert arrays['A0'].dtype==np.dtype('complex128')
            assert all(arrays[k].dtype==np.dtype('float64') for k in ('dn','sigma','weights'))
            assert np.all((arrays['dn']>=-.003)&(arrays['dn']<=0))
            assert np.all(arrays['sigma']>=0) and np.all((arrays['weights']>=0)&(arrays['weights']<=1))
            pin=float(np.sum(np.abs(arrays['A0'])**2)*dx*dx)
            assert abs(pin-1)<=1e-12
            assert abs(float(arrays['weights'].sum()*dx*dx)/(math.pi*(6e-6)**2)-1)<=1e-12
            if case['reused']:
                assert sha(case['E_case_path'])==case['E_case_sha256']
                original=json.loads(Path(case['E_case_path']).read_text())
                assert (original['N'],original['dz_m'],original['steps_completed'])==(n,case['dz_m'],case['steps'])
                assert original['final_npz_sha256']==case['field_sha256'] and original['final_npz_path']==case['field_path']
            else:
                previous=None;done=0
                for link in case['checkpoints']:
                    assert sha(link['path'])==link['sha256']
                    cp=json.loads(Path(link['path']).read_text())
                    assert cp['case_id']==case['id'] and cp['N']==n
                    assert cp['start_step']==done and cp['steps_done']==200 and cp['completed_step']==done+200
                    assert cp['previous_report_path']==previous
                    assert cp['previous_report_sha256']==(sha(previous) if previous else None)
                    assert cp['status']=='completed' and cp['elapsed_s']<35
                    assert sha(cp['field_path'])==cp['field_sha256']
                    with np.load(cp['field_path'],allow_pickle=False) as z:field=z['field']
                    assert field.shape==(n,n) and field.dtype==np.dtype('complex128') and np.all(np.isfinite(field))
                    raw=float(np.sum(np.abs(field)**2)*dx*dx)
                    assert abs(raw-cp['raw_total'])<=1e-12 and 0<raw<=1.001
                    assert all(s['available_ram_bytes']>1.5*1024**3 and s['free_disk_bytes']>2*1024**3 for s in cp['resource_samples'])
                    for factor in cp['factor_metadata']['factors']:
                        assert factor['perm_r']['identity'] and factor['perm_c']['identity']
                    previous=link['path'];done+=200;report['verified_chunks']+=1
                assert done==case['steps'] and cp['field_path']==case['field_path']
            assert sha(case['field_path'])==case['field_sha256']
            report['cases'].append(dict(id=case['id'],N=n,steps=case['steps'],reused=case['reused']))
        prediction=json.loads(Path(e['prediction_path']).read_text())
        assert sha(e['prediction_path'])==e['prediction_sha256']
        assert e['holdout_started_utc']>prediction['created_utc']
        first=json.loads(Path(e['results'][-1]['checkpoints'][0]['path']).read_text())
        assert first['started_utc']>e['holdout_started_utc']
        original_e=json.loads((p.parent/'point03_analytic_20261007T004526617696Z/execution.json').read_text())
        assert all(sha(path)==d for path,d in original_e['produced_sha256'].items())
        report.update(integrity_pass=True,E_outputs_unchanged=True,scientific_pass=a['scientific_pass'],
                      new_steps=sum(c['steps'] for c in e['results'] if not c['reused']),
                      new_holdout_chronology_pass=True,assessment_sha256=sha(e['assessment_path']))
    except Exception as err:
        report.update(error_type=type(err).__name__,error=str(err),diagnostic=traceback.format_exc())
    with args.out.open('x',encoding='utf-8') as f:
        json.dump(report,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({k:report.get(k) for k in ['integrity_pass','verified_chunks','E_outputs_unchanged','scientific_pass','error']}))
    return 0 if report['integrity_pass'] else 1


if __name__=='__main__':raise SystemExit(main())
