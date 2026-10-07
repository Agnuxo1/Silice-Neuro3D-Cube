"""Read-only L2 audit; recomputes gates without the controller assessor."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
for variable in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[variable]='1'
import numpy as np
from point03_linear_detector import Detector
from run_point03_exponential import sha, write

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def load(path, digest, key='field'):
    assert sha(path) == digest
    with np.load(path, allow_pickle=False) as data:
        value = data[key].copy()
    assert np.all(np.isfinite(value))
    return value

def verify_manifest(path, digest):
    assert sha(path) == digest
    manifest = read(path)
    for source, expected in manifest['source_sha256'].items():
        assert sha(source) == expected
    initial = load(manifest['input_path'], manifest['input_sha256'], 'A0')
    return manifest, initial

def compare(field, references, n, pin, recorded):
    dx = 128e-6/n
    primary, other = references[-1], references[0]
    assert field.shape == primary.shape == other.shape == (n, n)
    detector = Detector()
    measures = [detector.measure(value, n, pin) for value in [field, other, primary]]
    norm = [float(np.linalg.norm(value)) for value in [field, other, primary]]
    distance = float(np.linalg.norm(field-primary))
    consistency = float(np.linalg.norm(other-primary))
    errors = {method: abs(measures[0][method]['P_core']-measures[2][method]['P_core']) for method in ('field', 'intensity')}
    quadrature = max(result['change'] for row in measures for result in row.values())
    bound = dx**2*(norm[0]+norm[2])*distance/pin
    reference_bound = dx**2*(norm[1]+norm[2])*consistency/pin
    values = dict(field_relative_error=distance/norm[2], reference_field_difference=consistency/norm[2], bound_vs_computed_reference=bound, reference_consistency_bound=reference_bound, quadrature_change=quadrature, combined_reference_relative_indicator=bound+reference_bound+quadrature)
    for key, value in values.items():
        assert abs(value-recorded[key]) <= 1e-12
    for method, value in errors.items():
        assert abs(value-recorded['power_errors'][method]) <= 1e-12
        assert abs(measures[0][method]['P_core']-recorded['methods'][method]['P_core']) <= 1e-12
    gates = dict(field=values['field_relative_error'] <= 1e-4, power=all(value <= 1e-6 for value in errors.values()), reference_field=values['reference_field_difference'] <= 1e-9, quadrature=quadrature <= 1e-10, observable_bound=values['combined_reference_relative_indicator'] <= 1e-5)
    assert gates == recorded['gates'] and all(gates.values()) == recorded['pass_']
    return dict(N=n, **values, power_errors=errors, gates=gates, pass_=all(gates.values()))

def audit(folder):
    execution = read(folder/'execution.json')
    assert execution['status'] == 'completed' and execution['sources_unchanged']
    assert execution['elapsed_s'] <= 7200 and not execution['point03_closed']
    assert sha(execution['assessment_path']) == execution['assessment_sha256']
    assessment = read(execution['assessment_path'])
    manifest, initial = verify_manifest(execution['manifest_path'], execution['manifest_sha256'])
    assert manifest['N'] == 400 and manifest['steps_total'] == 12800
    assert manifest['worker_numeric_changes'] == 3 and manifest['numerical_threads'] == 1
    assert len(execution['checkpoints']) == len(execution['children']) == 32
    dx = 128e-6/400
    pin = float(np.vdot(initial, initial).real*dx**2)
    previous = digest = None
    power = pin
    max_residual = 0.
    for index, (link, child) in enumerate(zip(execution['checkpoints'], execution['children'], strict=True), 1):
        assert child['chunk'] == index and child['returncode'] == 0 and child['elapsed_s'] <= 370
        assert sha(link['path']) == link['sha256']
        checkpoint = read(link['path'])
        assert checkpoint['status'] == 'completed' and checkpoint['chunk'] == index
        assert checkpoint['steps_done'] == index*400 and checkpoint['steps_total'] == 12800
        assert checkpoint['previous_report_path'] == previous and checkpoint['previous_report_sha256'] == digest
        assert checkpoint['started_utc'] > manifest['created_utc'] and checkpoint['elapsed_s'] <= 360
        assert checkpoint['dz_m'] == .002/12800 and checkpoint['max_negative_amplification'] <= 1.10
        field = load(checkpoint['field_path'], checkpoint['field_sha256'])
        assert field.shape == (400, 400) and field.dtype == np.dtype('complex128')
        actual = float(np.vdot(field, field).real*dx**2)
        residual = abs(actual-checkpoint['raw_total'])
        max_residual = max(max_residual, residual)
        assert residual <= 1e-12 and abs(power-checkpoint['previous_power']) <= 1e-12
        assert 0 < actual <= power+1e-9
        for key in ('resource_start', 'resource_end'):
            assert checkpoint[key]['available_ram_bytes'] > 1.5*1024**3
            assert checkpoint[key]['free_disk_bytes'] > 2*1024**3
        previous, digest, power = link['path'], link['sha256'], actual
    references = [load(reference['path'], reference['sha256']) for reference in manifest['reference_fields']]
    rows = [compare(field, references, 400, pin, assessment['rows'][0])]
    old_execution = read(manifest['L1_execution_path'])
    old_manifest, old_initial = verify_manifest(old_execution['manifest_path'], old_execution['manifest_sha256'])
    old_checkpoint_link = old_execution['solutions'][-1]['checkpoints'][-1]
    assert sha(old_checkpoint_link['path']) == old_checkpoint_link['sha256']
    old_checkpoint = read(old_checkpoint_link['path'])
    old_field = load(old_checkpoint['field_path'], old_checkpoint['field_sha256'])
    old_pin = float(np.vdot(old_initial, old_initial).real*(128e-6/626)**2)
    reference_execution = read(manifest['K626_execution_path'])
    references = [load(reference_execution['solutions'][part]['field_path'], reference_execution['solutions'][part]['field_sha256']) for part in ('11', '17')]
    rows.append(compare(old_field, references, 626, old_pin, assessment['rows'][1]))
    assert not read(manifest['L1_assessment_path'])['pilot_pass']
    passed = all(row['pass_'] for row in rows)
    assert passed == assessment['L2_accuracy_pass'] == execution['L2_accuracy_pass']
    assert assessment['L1_still_negative'] and not assessment['point03_closed']
    assert abs(assessment['P_in']-pin) <= 1e-12 and abs(assessment['P_total']-power/pin) <= 1e-12
    return dict(created_utc=datetime.now(timezone.utc).isoformat(), integrity_pass=True, acceptance_recomputed=True, L2_accuracy_pass=passed, point03_closed=False, L1_still_negative=True, checkpoints_checked=32, source_files_checked=len(manifest['source_sha256']), max_raw_power_residual=max_residual, rows=rows, execution_sha256=sha(folder/'execution.json'), assessment_sha256=sha(folder/'assessment.json'), audit_source_sha256=sha(__file__), scope='Practical accuracy versus computed FD references only; no spatial or observed-order acceptance.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.out.resolve())
    write(args.out/'integrity_audit.json', result)
    print(json.dumps(result))
