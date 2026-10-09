"""Independent C2 audit: retained P6 plus every new R5_65536 checkpoint."""
import argparse
from datetime import datetime, timezone
import math
import os
from pathlib import Path
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import numpy as np
from scipy.sparse import load_npz
from run_point03_d16_time import ROOT, read, sha, write, G, T


def audit(out):
    m, e, a = (read(out/name) for name in ('manifest.json', 'execution.json', 'assessment.json'))
    assert e['status'] == 'completed' and e['elapsed_s'] <= 22000 and e.get('wait_s', 0.) <= 900
    assert not e['point03_closed'] and m['steps'] == 65536 and m['chunk_steps'] == 1024 and m['numerical_threads'] == 1
    assert sha(out/'manifest.json') == e['manifest_sha256'] and sha(out/'assessment.json') == e['assessment_sha256']
    for name, digest in m['source_sha256'].items():
        assert sha(ROOT/name) == digest
    det = ROOT/T
    with np.load(det/'gaussian_q16.npz', allow_pickle=False) as data:
        initial, free = data['field'].copy(), data['free_dofs'].copy()
    M = load_npz(ROOT/G/'mass.npz')[free, :][:, free]
    C = load_npz(det/'core_q32.npz')[free, :][:, free]
    w = np.load(det/'intensity_q32.npy', allow_pickle=False)[free]
    pin = float(np.vdot(initial[free], M@initial[free]).real)
    assert abs(pin-1) <= 1e-12
    ref = read(ROOT/m['retained_P6_report'])
    assert sha(ROOT/m['retained_P6_report']) == m['retained_P6_report_sha256'] == 'a6b060faaff0d02ea6ee6cb2b7b0331d3962d5815bd97548af95e6d4830877a3'
    assert ref['case'] == 'P6_32768' and ref['index'] == 32 and ref['status'] == 'completed'
    assert sha(ROOT/m['retained_P6_field']) == m['retained_P6_field_sha256'] == ref['field_sha256']
    with np.load(ROOT/m['retained_P6_field'], allow_pickle=False) as data:
        p6 = data['field'].copy()
    assert p6.shape == (len(free),) and p6.dtype == np.dtype('complex128') and np.isfinite(p6).all()
    assert abs(float(np.vdot(p6, M@p6).real)-ref['physical_power']) <= 1e-12
    assert len(e['children']) == len(e['checkpoints']) == 64
    previous, previous_sha, power, residual = None, None, pin, 0.
    for index, (event, link) in enumerate(zip(e['children'], e['checkpoints']), 1):
        cp = read(out/link['path'])
        assert event['case'] == cp['case'] == 'R5_65536' and event['index'] == cp['index'] == index
        assert event['returncode'] == 0 and event['elapsed_s'] <= 370 and cp['elapsed_s'] <= 360
        assert event['reservation']['available_ram_bytes'] > 6*1024**3 and event['reservation']['free_disk_bytes'] > 2*1024**3
        assert cp['status'] == 'completed' and sha(out/link['path']) == link['sha256']
        assert cp['previous_report_path'] == previous and cp['previous_report_sha256'] == previous_sha
        assert cp['steps_done'] == index*1024 and cp['dt_m'] == .002/65536 and cp['started_utc'] > m['created_utc']
        for item in ('resource_start', 'resource_end'):
            assert cp[item]['available_ram_bytes'] > 3*1024**3 and cp[item]['free_disk_bytes'] > 2*1024**3
        assert sha(out/cp['field_path']) == cp['field_sha256']
        with np.load(out/cp['field_path'], allow_pickle=False) as data:
            r5 = data['field'].copy()
        assert r5.shape == (len(free),) and r5.dtype == np.dtype('complex128') and np.isfinite(r5).all()
        actual = float(np.vdot(r5, M@r5).real)
        residual = max(residual, abs(actual-cp['physical_power']))
        assert abs(actual-cp['physical_power']) <= 1e-12 and abs(power-cp['previous_power']) <= 1e-12 and 0 < actual <= power+1e-9
        previous, previous_sha, power = link['path'], link['sha256'], actual
    powers = {name: dict(field=float(np.vdot(f, C@f).real), intensity=float(w@abs(f)**2))
              for name, f in (('P6_32768', p6), ('R5_65536', r5))}
    difference = p6-r5
    relative = math.sqrt(float(np.vdot(difference, M@difference).real)/float(np.vdot(r5, M@r5).real))
    errors, bounds = {}, {}
    for item in ('field', 'intensity'):
        squared = float(np.vdot(difference, C@difference).real) if item == 'field' else float(w@abs(difference)**2)
        assert squared >= -1e-20
        bounds[item] = sum(math.sqrt(p[item]) for p in powers.values())*math.sqrt(max(0., squared))
        errors[item] = abs(powers['P6_32768'][item]-powers['R5_65536'][item])
        assert abs(bounds[item]-a['PSD_observable_bounds'][item]) <= 1e-12 and abs(errors[item]-a['power_differences'][item]) <= 1e-12
        for name in powers:
            assert abs(powers[name][item]-a['powers'][name][item]) <= 1e-12
    assert abs(relative-a['relative_field_difference']) <= 1e-12
    passed = relative <= 1e-4 and max(errors.values()) <= 1e-6 and max(bounds.values()) <= 1e-5
    assert passed == a['temporal_precision_pass'] == e['temporal_precision_pass']
    return dict(created_utc=datetime.now(timezone.utc).isoformat(), integrity_pass=True, temporal_precision_pass=passed,
                point03_closed=False, new_checkpoints_checked=64, retained_P6_report_sha256=m['retained_P6_report_sha256'],
                max_power_residual=residual, powers=powers, relative_field_difference=relative,
                power_differences=errors, PSD_observable_bounds=bounds)


if __name__ == '__main__':
    p = argparse.ArgumentParser(__doc__)
    p.add_argument('--out', type=Path, required=True)
    out = p.parse_args().out.resolve()
    report = audit(out)
    write(out/'integrity_audit.json', report)
    print(report)
