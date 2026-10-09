"""Manufactured 3-DOF worker/portable-chain controls; no T96 propagation."""
import argparse
from pathlib import Path
from unittest.mock import patch
import numpy as np
from scipy.linalg import expm
from scipy.sparse import csc_matrix
import run_point03_d16_mid_refined_time as target


def main():
    out = target.ROOT/'resultados/codex/point03_d16_mid_refined_worker_controls_20261008'
    assert not out.exists()
    out.mkdir()
    M = csc_matrix([[2., .1, 0], [.1, 1.5, .05], [0, .05, 1.]])
    B = csc_matrix(-1j*np.array([[3., .4, .1], [.4, 2., -.2], [.1, -.2, 1.]])-np.diag([.1, .03, .05]))
    initial = np.array([1., .2j, -.1], complex)
    initial /= np.sqrt(np.vdot(initial, M@initial).real)
    target.write(out/'manifest.json', {'purpose': 'Synthetic 3-DOF software control only; not T96',
                                      'source_sha256': {'scripts/run_point03_d16_mid_refined_time.py': target.sha(Path(target.__file__))}})
    manifest_sha = target.sha(out/'manifest.json')
    resource = {'available_ram_bytes': 10*1024**3, 'free_disk_bytes': 10*1024**3,
                'synthetic_resource_sample': True}
    errors = {}
    for case in ('P6_32768', 'R5_65536'):
        folder = out/case
        folder.mkdir()
        previous = None
        for index in (1, 2):
            args = argparse.Namespace(case=case, index=index, prefix=folder/f'part{index:03d}',
                                      manifest=out/'manifest.json', manifest_sha=manifest_sha, previous=previous)
            with patch.object(target, 'matrices', return_value=(M, B, initial.copy(), np.arange(3))), \
                 patch.object(target, 'guard', return_value=resource):
                assert target.worker(args) == 0
            cp = target.read(Path(str(args.prefix)+'.json'))
            with np.load(out/cp['field_path'], allow_pickle=False) as data:
                actual = data['field'].copy()
            truth = expm(np.linalg.solve(M.toarray(), B.toarray())*(index*1024*.002/target.STEPS[case]))@initial
            error = float(np.linalg.norm(actual-truth))
            assert error <= 1e-10
            errors[f'{case}_{index}'] = error
            previous = Path(str(args.prefix)+'.json')
        bad = dict(cp)
        bad['field_sha256'] = '0'*64
        target.write(folder/'bad_previous.json', bad)
        args.index, args.prefix, args.previous = 3, folder/'rejected003', folder/'bad_previous.json'
        with patch.object(target, 'matrices', return_value=(M, B, initial.copy(), np.arange(3))), \
             patch.object(target, 'guard', return_value=resource):
            assert target.worker(args) == 1
        rejected = target.read(Path(str(args.prefix)+'.json'))
        assert rejected['status'] == 'failed' and 'field_path' not in rejected
    report = dict(controls_pass=True, manufactured_DOF=3, dense_errors=errors,
                  bad_previous_hash_rejected_in_both_families=True,
                  resources_mocked_for_software_test=True, t96_propagated=False,
                  point03_closed=False, tested_worker_sha256=target.sha(Path(target.__file__)))
    target.write(out/'report.json', report)
    print(report)


if __name__ == '__main__':
    main()
