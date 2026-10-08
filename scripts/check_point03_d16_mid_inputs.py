"""Inspect existing mid-mesh inputs, without propagation or adopting a result."""
import json
import numpy as np
import run_point03_d16_mid_time as base


def main():
    groups = [(base.G, 'hashes', ('mass.npz', 'cladding_mass.npz')),
              (base.T, 'artifacts', ('gaussian_q16.npz', 'core_q32.npz', 'intensity_q32.npy')),
              (base.D, 'artifacts', ('damping_q12.npz',)),
              (base.Q, 'artifacts', ('stiffness_duffy16.npz',))]
    for folder, key, names in groups:
        record = base.read(base.ROOT/folder/'report.json')
        for name in names:
            assert base.sha(base.ROOT/folder/name) == record[key][name]
    assert base.sha(base.ROOT/base.Q/'stiffness_duffy16.npz') == base.K_SHA
    M, B, initial, free = base.matrices()
    pin = float(np.vdot(initial, M@initial).real)
    assert abs(pin-1) <= 1e-12 and np.isfinite(initial).all()
    assert M.shape == B.shape == (len(free), len(free)) and len(np.unique(free)) == len(free)
    prior = base.ROOT/'resultados/codex/point03_d16_cloud_recovery_20261008/resultados/codex/cloud_d16_c1_20261008/local_integrity_audit.json'
    report = dict(input_integrity_pass=True, files_checked=7, free_DOF=len(free), initial_physical_power=pin,
                  prerequisite_present=prior.exists(), optical_propagation_executed=False,
                  point03_closed=False, worker_sha256=base.sha(base.ROOT/'scripts/run_point03_d16_mid_time.py'))
    base.write(base.ROOT/'resultados/codex/point03_d16_mid_input_integrity_20261008.json', report)
    print(report)


if __name__ == '__main__':
    main()
