"""Inspect existing mid-mesh inputs, without propagation or adopting a result."""
import json
import numpy as np
import run_point03_d16_fine_time as base


def main():
    groups = [(base.G, 'artifact_sha256', ('mass.npz', 'cladding_mass.npz')),
              (base.T, 'artifacts', ('gaussian_q16.npz', 'core_q32.npz', 'intensity_q32.npy')),
              (base.D, 'artifacts', ('damping_q12.npz',)),
              (base.Q, 'artifacts', ('stiffness_duffy16.npz',))]
    for folder, key, names in groups:
        record = base.read(base.ROOT/folder/('report_recovered.json' if folder == base.G else 'report.json'))
        for name in names:
            assert base.sha(base.ROOT/folder/name) == record[key][name]
    assert base.sha(base.ROOT/base.Q/'stiffness_duffy16.npz') == base.K_SHA
    M, B, initial, free = base.matrices()
    pin = float(np.vdot(initial, M@initial).real)
    assert abs(pin-1) <= 1e-12 and np.isfinite(initial).all()
    assert M.shape == B.shape == (len(free), len(free)) and len(np.unique(free)) == len(free)
    prior = base.ROOT/'resultados/codex/point03_d16_mid_recovery_20261009/local_integrity_audit.json'
    prerequisite = base.read(prior) if prior.exists() else {}
    prior_pass = bool(prerequisite.get('integrity_pass') and prerequisite.get('temporal_precision_pass'))
    report = dict(input_integrity_pass=True, files_checked=7, free_DOF=len(free), initial_physical_power=pin,
                  prerequisite_present=prior.exists(), prerequisite_pass=prior_pass, optical_propagation_executed=False,
                  point03_closed=False, worker_sha256=base.sha(base.ROOT/'scripts/run_point03_d16_fine_time.py'))
    base.write(base.ROOT/'resultados/codex/point03_d16_fine_input_integrity_20261009.json', report)
    print(report)


if __name__ == '__main__':
    main()
