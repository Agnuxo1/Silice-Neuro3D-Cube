"""Verify prepared immutable input hashes and mass norm; never propagate."""
from pathlib import Path
import json
import numpy as np
from run_point03_d16_time import ROOT, G, T, D, Q, K_SHA, read, sha, matrices


def main():
    package = ROOT/'resultados/codex/point03_d16_cloud_package_retry_20261008'
    manifest = read(package/'transfer_manifest.json')
    for row in manifest['files']:
        assert (ROOT/row['path']).stat().st_size == row['bytes'] and sha(ROOT/row['path']) == row['sha256']
    for name in ('mass.npz', 'cladding_mass.npz'):
        assert sha(ROOT/G/name) == read(ROOT/G/'report.json')['hashes'][name]
    for name in ('gaussian_q16.npz', 'core_q32.npz', 'intensity_q32.npy'):
        assert sha(ROOT/T/name) == read(ROOT/T/'report.json')['artifacts'][name]
    assert sha(ROOT/D/'damping_q12.npz') == read(ROOT/D/'report_recovered.json')['artifacts']['damping_q12.npz']
    assert sha(ROOT/Q/'stiffness_duffy16.npz') == K_SHA
    M, B, initial, free = matrices()
    pin = float(np.vdot(initial, M@initial).real)
    assert abs(pin-1) <= 1e-12 and np.isfinite(initial).all()
    assert M.shape == B.shape == (len(free), len(free))
    assert len(np.unique(free)) == len(free)
    report = dict(input_integrity_pass=True, package_source_files_checked=len(manifest['files']),
                  free_DOF=len(free), initial_physical_power=pin,
                  stiffness_sha256=K_SHA, optical_propagation_executed=False, point03_closed=False)
    target = ROOT/'resultados/codex/point03_d16_input_integrity_20261008.json'
    with target.open('x', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(report)


if __name__ == '__main__':
    main()
