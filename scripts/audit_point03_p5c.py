"""Replay generalized-mass coarse FEM records without the run evaluator."""
import argparse
from datetime import datetime, timezone
import math
import os
from pathlib import Path
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import numpy as np
from scipy.sparse import load_npz
from run_point03_exponential import sha, write
from audit_point03_p4i import read


def audit(folder):
    m = read(folder / 'manifest.json')
    e = read(folder / 'execution.json')
    a = read(folder / 'assessment.json')
    assert e['status'] == 'completed' and e['sources_unchanged'] and e['elapsed_s'] <= 36000
    assert sha(folder / 'manifest.json') == e['manifest_sha256']
    assert sha(folder / 'assessment.json') == e['assessment_sha256']
    assert m['numerical_threads'] == 1 and len(e['children']) == 256
    assert m['plan'] == [dict(id='P6_32768', method='P6', steps=32768), dict(id='R5_32768', method='R5', steps=32768)]
    for path, digest in m['source_sha256'].items():
        assert sha(path) == digest
    det = Path(m['detector_folder'])
    with np.load(det / 'gaussian_q16.npz', allow_pickle=False) as data:
        free = data['free_dofs'].copy()
        initial = data['field'][free].copy()
    M = load_npz(Path(m['geometry_folder']) / 'mass.npz')[free, :][:, free]
    C = load_npz(det / 'core_q32.npz')[free, :][:, free]
    w = np.load(det / 'intensity_q32.npy', allow_pickle=False)[free]
    pin = float(np.vdot(initial, M @ initial).real)
    assert abs(pin - 1) <= 1e-12 and abs(pin - m['P_in']) <= 1e-12
    fields = {}
    residual = 0.
    count = event_index = 0
    for case in m['plan']:
        links = e['solutions'][case['id']]['checkpoints']
        assert len(links) == 128
        previous = digest = None
        power = pin
        for index, link in enumerate(links, 1):
            cp = read(link['path'])
            event = e['children'][event_index]
            event_index += 1
            assert event['case'] == case['id'] and event['index'] == index and event['returncode'] == 0 and event['elapsed_s'] <= 370
            assert sha(link['path']) == link['sha256'] and cp['status'] == 'completed'
            assert cp['case'] == case['id'] and cp['index'] == index and cp['steps_done'] == 256 * index
            assert cp['steps_total'] == 32768 and cp['dt_m'] == .002 / 32768 and cp['elapsed_s'] <= 360
            assert cp['started_utc'] > m['created_utc']
            assert cp['previous_report_path'] == previous and cp['previous_report_sha256'] == digest
            assert sha(cp['field_path']) == cp['field_sha256']
            for sample in ('resource_start', 'resource_end'):
                assert cp[sample]['available_ram_bytes'] > 3 * 1024**3 and cp[sample]['free_disk_bytes'] > 2 * 1024**3
            with np.load(cp['field_path'], allow_pickle=False) as data:
                field = data['field'].copy()
            assert field.dtype == np.dtype('complex128') and field.shape == (len(free),) and np.all(np.isfinite(field))
            physical = float(np.vdot(field, M @ field).real)
            residual = max(residual, abs(physical - cp['physical_power']))
            assert abs(physical - cp['physical_power']) <= 1e-12 and abs(power - cp['previous_power']) <= 1e-12
            assert 0 < physical <= power + 1e-9
            previous, digest, power = link['path'], link['sha256'], physical
            count += 1
        fields[case['id']] = field
    powers = {label: dict(field=float(np.vdot(f, C @ f).real), intensity=float(w @ abs(f)**2)) for label, f in fields.items()}
    d = fields['P6_32768'] - fields['R5_32768']
    relative = math.sqrt(float(np.vdot(d, M @ d).real) / float(np.vdot(fields['R5_32768'], M @ fields['R5_32768']).real))
    bounds = {}
    changes = {}
    for method in ('field', 'intensity'):
        squared = float(np.vdot(d, C @ d).real) if method == 'field' else float(w @ abs(d)**2)
        assert squared >= -1e-20
        bounds[method] = (math.sqrt(powers['P6_32768'][method]) + math.sqrt(powers['R5_32768'][method])) * math.sqrt(max(0., squared))
        changes[method] = abs(powers['P6_32768'][method] - powers['R5_32768'][method])
        assert abs(bounds[method] - a['PSD_observable_bounds'][method]) <= 1e-12
        assert abs(changes[method] - a['power_differences'][method]) <= 1e-12
        for label in powers:
            assert abs(powers[label][method] - a['powers'][label][method]) <= 1e-12
    assert abs(relative - a['relative_field_difference']) <= 1e-12
    passed = relative <= 1e-4 and max(bounds.values()) <= 1e-5 and max(changes.values()) <= 1e-6
    assert passed == a['temporal_precision_pass'] == e['temporal_precision_pass']
    return dict(created_utc=datetime.now(timezone.utc).isoformat(), integrity_pass=True, temporal_precision_pass=passed,
                point03_closed=False, checkpoints_checked=count, max_power_residual=residual, powers=powers,
                relative_field_difference=relative, PSD_observable_bounds=bounds, power_differences=changes)


if __name__ == '__main__':
    p = argparse.ArgumentParser(__doc__)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    result = audit(args.out.resolve())
    write(args.out / 'integrity_audit.json', result)
    print(result)
