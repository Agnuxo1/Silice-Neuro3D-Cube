"""Independent full checkpoint and observable audit, without importing evaluator."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import numpy as np
from scipy.sparse import load_npz

ROOT = Path(__file__).resolve().parents[1]

STEPS = {'P6_32768': 32768, 'R5_65536': 65536}

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit(out):
    m, e, a = (read(out/name) for name in ('manifest.json', 'execution.json', 'assessment.json'))
    assert e['status'] == 'completed' and e['elapsed_s'] <= 32000 and e.get('wait_s', 0.) <= 900
    assert datetime.fromisoformat(e['finished_utc']) <= datetime(2026, 10, 9, 13, 45, tzinfo=timezone.utc)
    assert not e['point03_closed'] and m['numerical_threads'] == 1 and m['steps_by_case'] == STEPS and m['chunk_steps'] == 512 and m['global_budget_s'] == 32000
    assert sha(out/'manifest.json') == e['manifest_sha256'] and sha(out/'assessment.json') == e['assessment_sha256']
    for name, digest in m['source_sha256'].items():
        assert sha(ROOT/name) == digest
    assert m['stiffness_sha256'] == 'f251ae68f374cb6ae98288caed1984d528a6147c7b74ada3229e7aa98771074f'
    det = ROOT/'resultados/codex/point03_p4f_detector_20261008'
    with np.load(det/'gaussian_q16.npz', allow_pickle=False) as data:
        initial, free = data['field'].copy(), data['free_dofs'].copy()
    M = load_npz(ROOT/'resultados/codex/point03_p4c_mesh_20261008/mass.npz')[free, :][:, free]
    C = load_npz(det/'core_q32.npz')[free, :][:, free]
    w = np.load(det/'intensity_q32.npy', allow_pickle=False)[free]
    pin = float(np.vdot(initial[free], M@initial[free]).real)
    assert abs(pin-1) <= 1e-12 and len(e['children']) == 192
    fields, powers, residual = {}, {}, 0.
    checked = 0
    for case in ('P6_32768', 'R5_65536'):
        links = e['solutions'][case]['checkpoints']
        assert len(links) == STEPS[case]//512
        previous, previous_sha, power = None, None, pin
        for index, link in enumerate(links, 1):
            event = e['children'][checked]
            cp = read(out/link['path'])
            assert event['case'] == case and event['index'] == index and event['returncode'] == 0 and event['elapsed_s'] <= 370
            assert event['reservation']['available_ram_bytes'] > 6*1024**3 and event['reservation']['free_disk_bytes'] > 2*1024**3
            assert sha(out/link['path']) == link['sha256'] and cp['status'] == 'completed' and cp['case'] == case and cp['index'] == index
            assert cp['previous_report_path'] == previous and cp['previous_report_sha256'] == previous_sha
            assert cp['steps_done'] == index*512 and cp['dt_m'] == .002/STEPS[case] and cp['elapsed_s'] <= 360
            assert cp['started_utc'] > m['created_utc']
            for resource in ('resource_start', 'resource_end'):
                assert cp[resource]['available_ram_bytes'] > 3*1024**3 and cp[resource]['free_disk_bytes'] > 2*1024**3
            assert sha(out/cp['field_path']) == cp['field_sha256']
            with np.load(out/cp['field_path'], allow_pickle=False) as data:
                field = data['field'].copy()
            assert field.shape == (len(free),) and field.dtype == np.dtype('complex128') and np.isfinite(field).all()
            actual = float(np.vdot(field, M@field).real)
            residual = max(residual, abs(actual-cp['physical_power']))
            assert abs(actual-cp['physical_power']) <= 1e-12 and abs(power-cp['previous_power']) <= 1e-12
            assert 0 < actual <= power+1e-9
            previous, previous_sha, power = link['path'], link['sha256'], actual
            checked += 1
        fields[case] = field
        powers[case] = {'field': float(np.vdot(field, C@field).real), 'intensity': float(w@abs(field)**2)}
        for label in ('field', 'intensity'):
            assert abs(powers[case][label]-a['powers'][case][label]) <= 1e-12
    difference = fields['P6_32768']-fields['R5_65536']
    relative = math.sqrt(float(np.vdot(difference, M@difference).real)/float(np.vdot(fields['R5_65536'], M@fields['R5_65536']).real))
    errors, bounds = {}, {}
    for label in ('field', 'intensity'):
        square = float(np.vdot(difference, C@difference).real) if label == 'field' else float(w@abs(difference)**2)
        assert square >= -1e-20
        bounds[label] = (math.sqrt(powers['P6_32768'][label])+math.sqrt(powers['R5_65536'][label]))*math.sqrt(max(0., square))
        errors[label] = abs(powers['P6_32768'][label]-powers['R5_65536'][label])
        assert abs(bounds[label]-a['PSD_observable_bounds'][label]) <= 1e-12 and abs(errors[label]-a['power_differences'][label]) <= 1e-12
    assert abs(relative-a['relative_field_difference']) <= 1e-12
    passed = relative <= 1e-4 and max(errors.values()) <= 1e-6 and max(bounds.values()) <= 1e-5
    assert passed == a['temporal_precision_pass'] == e['temporal_precision_pass']
    return dict(created_utc=datetime.now(timezone.utc).isoformat(), integrity_pass=True,
                temporal_precision_pass=passed, point03_closed=False, checkpoints_checked=checked,
                max_power_residual=residual, powers=powers, relative_field_difference=relative,
                power_differences=errors, PSD_observable_bounds=bounds)


if __name__ == '__main__':
    p = argparse.ArgumentParser(__doc__)
    p.add_argument('--out', type=Path, required=True)
    out = p.parse_args().out.resolve()
    result = audit(out)
    with (out/'integrity_audit.json').open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result))
