"""Read-only recovery audit of the completed Stage E, without wave solvers."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import math
import os
import subprocess
import time
import traceback


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--study', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    assert not args.out.exists()
    args.out.mkdir(parents=True)
    start = time.monotonic()
    for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
        os.environ[name] = '1'
    import numpy as np
    study = args.study.resolve()
    root = Path(__file__).resolve().parents[1]
    execution = json.loads((study/'execution.json').read_text())
    original = json.loads((study/'assessment.json').read_text())
    report = {'created_utc': datetime.now(timezone.utc).isoformat(), 'status':'running',
              'study':str(study), 'execution_sha256':digest(study/'execution.json'),
              'assessment_sha256':digest(study/'assessment.json'),
              'scope':'Saved bytes and array arithmetic; no new propagation or independent physical validation.',
              'jev':{'provenance':'local','remote_advice':False,
                     'reason':'Inherited security block retained; local v2-doctor ready is not a remote recommendation.'}}
    checked = {}
    try:
        assert execution['status'] == 'completed' and execution['operational_pass']
        assert execution['completed_chunk_count'] == 144
        inventories = [original['files_verified'], execution['frozen_input_sha256_before'],
                       execution['produced_sha256']]
        inventories.append({str(root/k):v for k,v in execution['tracked_sha256_before'].items()})
        for inventory in inventories:
            for filename, expected in inventory.items():
                if filename not in checked:
                    checked[filename] = digest(filename)
                assert checked[filename] == expected, 'Changed file: '+filename
        report['verified_files'] = len(checked)
        report['input_and_historical_hashes_unchanged'] = True
        report['tracked_files_verified'] = len(execution['tracked_sha256_before'])
        fields_checked, rows = 0, []
        manifest = json.loads((study/'manifest.json').read_text())
        assert {c['case_id'] for c in manifest['case_plan']} == {c['case_id'] for c in original['independent_measurements']}
        for expected in original['independent_measurements']:
            case = json.loads(Path(expected['case_path']).read_text())
            n, dx = expected['N'], 128e-6/expected['N']
            with np.load(expected['input_npz_path'], allow_pickle=False) as z:
                a0, weights = z['A0'], z['weights']
                p_in = float(np.sum(np.abs(a0)**2)*dx**2)
            previous, completed = None, 0
            for link in case['checkpoint_reports']:
                cp = json.loads(Path(link['path']).read_text())
                assert digest(link['path']) == link['sha256']
                assert cp['steps_start'] == completed and cp['steps_done'] == completed+200
                assert cp['previous_checkpoint_path'] == previous
                if previous is not None:
                    assert digest(previous) == cp['previous_checkpoint_sha256']
                else:
                    assert cp['previous_checkpoint_sha256'] is None
                    assert cp['input_npz_path'] == expected['input_npz_path']
                    assert digest(cp['input_npz_path']) == cp['input_npz_sha256']
                with np.load(cp['npz_path'], allow_pickle=False) as z:
                    field = z['field']
                assert field.shape == (n,n) and field.dtype == np.dtype('complex128')
                assert np.all(np.isfinite(field))
                total = float(np.sum(np.abs(field)**2)*dx**2/p_in)
                core = float(np.sum(np.abs(field)**2*weights)*dx**2/p_in)
                assert abs(core-cp['P_core']) <= 1e-12 and abs(total-cp['P_total']) <= 1e-12
                assert 0 <= core <= total+1e-12 and total*p_in <= 1.001
                completed += 200
                previous = link['path']
                fields_checked += 1
            assert completed == expected['steps_completed'] and cp['npz_path'] == expected['final_npz_path']
            assert abs(core-expected['P_core']) <= 1e-12
            rows.append(dict(case_id=expected['case_id'], N=n, dz_um=expected['dz_m']*1e6,
                             steps=completed, P_in=p_in, P_core=core, P_total=total))
        report['checkpoint_arrays_decompressed_and_remeasured'] = fields_checked
        assert fields_checked == 144
        report['cases'] = rows
        p = [c['P_core'] for c in rows[:4]]
        d = [b-a for a,b in zip(p,p[1:])]
        orders = [math.log(d[i]/d[i+1])/math.log(1.25) for i in (0,1)]
        pred = p[2]+d[1]**2/d[0]
        assert abs(pred-original['holdout']['predicted_core_power']) <= 1e-14
        report['spatial'] = dict(powers=p, differences=d, orders=orders,
            order_disagreement=abs(orders[1]-orders[0])/max(orders),
            prediction=pred, residual=abs(p[3]-pred), limit=.1*abs(d[2]),
            residual_to_limit=abs(p[3]-pred)/(.1*abs(d[2])),
            accepted_uncertainty=None, scientific_pass=False)
        report['original_scientific_pass'] = original['scientific_pass']
        assert original['scientific_pass'] is False and original['accepted_gci'] is None
        report['status'] = 'completed'
        report['integrity_pass'] = True
    except Exception as err:
        report.update(status='failed',integrity_pass=False,error_type=type(err).__name__,error=str(err),
                      diagnostic=traceback.format_exc())
    report['elapsed_s'] = time.monotonic()-start
    report['verified_sha256'] = checked
    (args.out/'audit.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:report.get(k) for k in ['status','integrity_pass','verified_files',
        'checkpoint_arrays_decompressed_and_remeasured','elapsed_s','error']}))
    return 0 if report.get('integrity_pass') else 1


if __name__ == '__main__':
    raise SystemExit(main())
