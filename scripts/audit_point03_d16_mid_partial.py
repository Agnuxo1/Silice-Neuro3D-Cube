"""Audit immutable completed M2 fields; never infer a final temporal verdict."""
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


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def audit(out, counts):
    manifest = read(out/'manifest.json')
    assert manifest['numerical_threads'] == 1
    assert manifest['steps_by_case'] == STEPS and manifest['chunk_steps'] == 1024
    for name, digest in manifest['source_sha256'].items():
        assert sha(ROOT/name) == digest
    detector = ROOT/'resultados/codex/point03_p5b_detector_mid_20261008'
    with np.load(detector/'gaussian_q16.npz', allow_pickle=False) as data:
        initial, free = data['field'].copy(), data['free_dofs'].copy()
    mass = load_npz(ROOT/'resultados/codex/point03_p5a_mesh_mid_20261008/mass.npz')[free, :][:, free]
    pin = float(np.vdot(initial[free], mass@initial[free]).real)
    assert abs(pin-1) <= 1e-12
    residual = 0.
    cases = {}
    for case, count in counts.items():
        assert 0 <= count <= STEPS[case]//1024
        previous, previous_sha, power = None, None, pin
        retained = []
        for index in range(1, count+1):
            path = out/case/f'part{index:03d}.json'
            cp = read(path)
            assert cp['status'] == 'completed' and cp['case'] == case and cp['index'] == index
            assert cp['previous_report_path'] == previous and cp['previous_report_sha256'] == previous_sha
            assert cp['steps_done'] == index*1024 and cp['dt_m'] == .002/STEPS[case]
            assert cp['elapsed_s'] <= 360 and cp['started_utc'] > manifest['created_utc']
            for key in ('resource_start', 'resource_end'):
                assert cp[key]['available_ram_bytes'] > 3*1024**3
                assert cp[key]['free_disk_bytes'] > 2*1024**3
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
        cases[case] = dict(checkpoints_checked=count, distance_m=count*1024*.002/STEPS[case],
                           checkpoints=retained)
    return dict(created_utc=datetime.now(timezone.utc).isoformat(), partial_integrity_pass=True,
                checkpoints_checked=sum(counts.values()), cases=cases, max_power_residual=residual,
                source_files_checked=len(manifest['source_sha256']),
                original_manifest_sha256=sha(out/'manifest.json'),
                auditor_sha256=sha(Path(__file__)), full_temporal_assessment=False,
                resource_reservations_audited=False, point03_closed=False,
                scope='Field hashes, dtype, finitude, power, chain, worker resources and frozen sources. Controller reservations require its final execution record.')


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
    print(json.dumps({key: value for key, value in result.items() if key != 'cases'}))
