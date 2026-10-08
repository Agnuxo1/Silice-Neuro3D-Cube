"""Manufactured software controls for the new R5_65536 worker only."""
import argparse
import os
from pathlib import Path
from unittest.mock import patch
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import numpy as np
from scipy.linalg import expm
from scipy.sparse import csc_matrix
import run_point03_d16_refine as target


def main():
    out = target.ROOT/'resultados/codex/point03_d16_refine_worker_controls_20261008'
    assert not out.exists()
    out.mkdir()
    M = csc_matrix([[2., .1, 0], [.1, 1.5, .05], [0, .05, 1.]])
    B = csc_matrix(-1j*np.array([[3., .4, .1], [.4, 2., -.2], [.1, -.2, 1.]])-np.diag([.1, .03, .05]))
    initial = np.array([1., .2j, -.1], complex)
    initial /= np.sqrt(np.vdot(initial, M@initial).real)
    target.write(out/'manifest.json', {'purpose': 'Manufactured3DOF only',
                 'source_sha256': {'scripts/run_point03_d16_refine.py': target.sha(Path(target.__file__))}})
    resource = {'available_ram_bytes': 10*1024**3, 'free_disk_bytes': 10*1024**3, 'synthetic_resource_sample': True}
    folder = out/'R5_65536'
    folder.mkdir()
    previous, errors = None, []
    for index in (1, 2):
        args = argparse.Namespace(case='R5_65536', index=index, prefix=folder/f'part{index:03d}',
                                  manifest=out/'manifest.json', manifest_sha=target.sha(out/'manifest.json'), previous=previous)
        with patch.object(target, 'matrices', return_value=(M, B, initial.copy(), np.arange(3))), \
             patch.object(target, 'guard', return_value=resource):
            assert target.worker(args) == 0
        cp = target.read(Path(str(args.prefix)+'.json'))
        assert cp['dt_m'] == .002/65536 and cp['steps_done'] == index*1024
        with np.load(out/cp['field_path'], allow_pickle=False) as data:
            value = data['field'].copy()
        truth = expm(np.linalg.solve(M.toarray(), B.toarray())*(index*1024*.002/65536))@initial
        error = float(np.linalg.norm(value-truth))
        assert error <= 1e-10
        errors.append(error)
        previous = Path(str(args.prefix)+'.json')
    bad = dict(cp)
    bad['field_sha256'] = '0'*64
    target.write(folder/'bad_previous.json', bad)
    args.index, args.prefix, args.previous = 3, folder/'rejected003', folder/'bad_previous.json'
    with patch.object(target, 'matrices', return_value=(M, B, initial.copy(), np.arange(3))), \
         patch.object(target, 'guard', return_value=resource):
        assert target.worker(args) == 1
    report = dict(controls_pass=True, dense_errors=errors, bad_previous_hash_rejected=True,
                  resources_mocked_for_software_test=True, t96_propagated=False, point03_closed=False,
                  tested_worker_sha256=target.sha(Path(target.__file__)))
    target.write(out/'report.json', report)
    print(report)


if __name__ == '__main__':
    main()
