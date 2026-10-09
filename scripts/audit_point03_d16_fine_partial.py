"""Audit retained F1 fields without claiming a full temporal result."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import numpy as np
from scipy.sparse import load_npz

ROOT = Path(__file__).resolve().parents[1]
STEPS = {'P6_32768': 32768, 'R5_65536': 65536}
K_SHA = 'f251ae68f374cb6ae98288caed1984d528a6147c7b74ada3229e7aa98771074f'
WORKER_SHA = '39b1024a2237edb1938873defd22aaac76e995fdb93adad2e5c7eb3339081456'
DEADLINE = datetime(2026, 10, 9, 13, 45, tzinfo=timezone.utc)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def audit_fields(out, counts, manifest, mass, initial, free):
    """Pure field audit shared with manufactured controls, not a propagator."""
    assert set(counts) == set(STEPS)
    assert all(type(n) is int and 0 <= n <= STEPS[case]//512 for case, n in counts.items())
    assert sum(counts.values()) > 0
    assert not counts['R5_65536'] or counts['P6_32768'] == 64
    pin = float(np.vdot(initial, mass@initial).real)
    assert initial.shape == (len(free),) and abs(pin-1) <= 1e-12
    residual, cases = 0., {}
    for case in STEPS:
        previous, previous_sha, power, retained = None, None, pin, []
        for index in range(1, counts[case]+1):
            path = out/case/f'part{index:03d}.json'
            cp = read(path)
            assert cp['status'] == 'completed' and cp['case'] == case and cp['index'] == index
            assert cp['previous_report_path'] == previous and cp['previous_report_sha256'] == previous_sha
            assert cp['steps_done'] == index*512 and cp['dt_m'] == .002/STEPS[case]
            assert 0 <= cp['elapsed_s'] <= 360
            assert datetime.fromisoformat(cp['started_utc']) > datetime.fromisoformat(manifest['created_utc'])
            assert datetime.fromisoformat(cp['started_utc']) < DEADLINE
            for key in ('resource_start', 'resource_end'):
                assert cp[key]['available_ram_bytes'] > 3*1024**3
                assert cp[key]['free_disk_bytes'] > 2*1024**3
            assert cp['field_path'] == f'{case}/part{index:03d}.npz'
            field_path = out/cp['field_path']
            assert sha(field_path) == cp['field_sha256']
            with np.load(field_path, allow_pickle=False) as data:
                field = data['field'].copy()
            assert field.shape == (len(free),) and field.dtype == np.dtype('complex128')
            assert np.isfinite(field).all()
            actual = float(np.vdot(field, mass@field).real)
            residual = max(residual, abs(actual-cp['physical_power']))
            assert abs(actual-cp['physical_power']) <= 1e-12
            assert abs(power-cp['previous_power']) <= 1e-12 and 0 < actual <= power+1e-9
            previous, previous_sha, power = path.relative_to(out).as_posix(), sha(path), actual
            retained.append(dict(path=previous, sha256=previous_sha,
                                 field_path=cp['field_path'], field_sha256=cp['field_sha256']))
        cases[case] = dict(checkpoints_checked=counts[case],
                           distance_m=counts[case]*512*.002/STEPS[case], checkpoints=retained)
    return dict(partial_integrity_pass=True, checkpoints_checked=sum(counts.values()),
                cases=cases, max_power_residual=residual, full_temporal_assessment=False,
                resource_reservations_audited=False, point03_closed=False)


def audit(out, counts):
    manifest = read(out/'manifest.json')
    assert manifest['numerical_threads'] == 1 and manifest['steps_by_case'] == STEPS
    assert manifest['chunk_steps'] == 512 and manifest['global_budget_s'] == 32000
    assert datetime.fromisoformat(manifest['deadline_utc']) == DEADLINE
    assert manifest['mesh'] == 'fine' and manifest['stiffness_sha256'] == K_SHA
    for name, digest in manifest['source_sha256'].items():
        source = (ROOT/name).resolve()
        assert source.is_relative_to(ROOT.resolve()) and sha(source) == digest
    assert sha(ROOT/'scripts/run_point03_d16_fine_time.py') == WORKER_SHA
    assert sha(ROOT/'resultados/codex/point03_fem_duffy_prototype_20261008/stiffness_duffy16.npz') == K_SHA
    det = ROOT/'resultados/codex/point03_p4f_detector_20261008'
    with np.load(det/'gaussian_q16.npz', allow_pickle=False) as data:
        initial, free = data['field'].copy(), data['free_dofs'].copy()
    assert len(free) == 74049
    mass = load_npz(ROOT/'resultados/codex/point03_p4c_mesh_20261008/mass.npz')[free, :][:, free]
    result = audit_fields(out, counts, manifest, mass, initial[free], free)
    result.update(created_utc=datetime.now(timezone.utc).isoformat(),
                  source_files_checked=len(manifest['source_sha256']),
                  original_manifest_sha256=sha(out/'manifest.json'), auditor_sha256=sha(Path(__file__)),
                  scope='Retained field hashes, dtype, finitude, mass power, chain and worker resources. No final temporal verdict or controller reservation approval.')
    if (out/'execution.json').exists():
        execution = read(out/'execution.json')
        assert execution['manifest_sha256'] == result['original_manifest_sha256']
        assert execution['point03_closed'] is False
        result.update(original_execution_sha256=sha(out/'execution.json'),
                      original_execution_status=execution['status'],
                      original_elapsed_s=execution['elapsed_s'])
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--pade-count', type=int, required=True)
    parser.add_argument('--radau-count', type=int, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.out.resolve(), {'P6_32768': args.pade_count, 'R5_65536': args.radau_count})
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({key:value for key,value in result.items() if key != 'cases'}))
