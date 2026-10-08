"""Independent bounded audit of completed, immutable C2 checkpoints only."""
import argparse
import math
from pathlib import Path
import numpy as np
from scipy.sparse import load_npz
from run_point03_d16_time import ROOT, G, T, read, sha, write


def main(count, name):
    out = ROOT/'resultados/codex/point03_d16_refine_20261008'
    m = read(out/'manifest.json')
    for path, digest in m['source_sha256'].items():
        assert sha(ROOT/path) == digest
    with np.load(ROOT/T/'gaussian_q16.npz', allow_pickle=False) as data:
        free, initial = data['free_dofs'].copy(), data['field'].copy()
    M = load_npz(ROOT/G/'mass.npz')[free, :][:, free]
    power = float(np.vdot(initial[free], M@initial[free]).real)
    previous, previous_sha, maximum = None, None, 0.
    for index in range(1, count+1):
        path = out/'R5_65536'/f'part{index:03d}.json'
        cp = read(path)
        assert cp['status'] == 'completed' and cp['case'] == 'R5_65536' and cp['index'] == index
        assert cp['previous_report_path'] == previous and cp['previous_report_sha256'] == previous_sha
        assert cp['steps_done'] == index*1024 and cp['dt_m'] == .002/65536 and cp['elapsed_s'] <= 360
        for resource in ('resource_start', 'resource_end'):
            assert cp[resource]['available_ram_bytes'] > 3*1024**3 and cp[resource]['free_disk_bytes'] > 2*1024**3
        assert sha(out/cp['field_path']) == cp['field_sha256']
        with np.load(out/cp['field_path'], allow_pickle=False) as data:
            field = data['field'].copy()
        assert field.shape == (len(free),) and field.dtype == np.dtype('complex128') and np.isfinite(field).all()
        actual = float(np.vdot(field, M@field).real)
        maximum = max(maximum, abs(actual-cp['physical_power']))
        assert abs(actual-cp['physical_power']) <= 1e-12 and abs(power-cp['previous_power']) <= 1e-12 and 0 < actual <= power+1e-9
        previous, previous_sha, power = path.relative_to(out).as_posix(), sha(path), actual
    report = dict(partial_integrity_pass=True, checkpoints_checked=count, max_power_residual=maximum,
                  distance_m=count*1024*.002/65536, full_temporal_assessment=False, point03_closed=False,
                  final_checked_report=previous, final_checked_report_sha256=previous_sha)
    write(out/name, report)
    print(report)


if __name__ == '__main__':
    p = argparse.ArgumentParser(__doc__)
    p.add_argument('--count', type=int, required=True)
    p.add_argument('--name', required=True)
    args = p.parse_args()
    main(args.count, args.name)
