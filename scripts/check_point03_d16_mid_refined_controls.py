"""Dense manufactured temporal check and positive/negative observable controls."""
from pathlib import Path
import json
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import numpy as np
from scipy.linalg import expm
from scipy.sparse import csc_matrix
from point03_fem_time import Pade6
from point03_fem_radau import Radau5
from run_point03_d16_mid_refined_time import evaluate


def main():
    M = csc_matrix([[2., .1, 0], [.1, 1.5, .05], [0, .05, 1.]])
    B = csc_matrix(-1j*np.array([[3., .4, .1], [.4, 2., -.2], [.1, -.2, 1.]])-np.diag([.1, .03, .05]))
    initial = np.array([1., .2j, -.1], complex)
    initial /= np.sqrt(np.vdot(initial, M@initial).real)
    truth = expm(np.linalg.solve(M.toarray(), B.toarray())*.2)@initial
    errors = {}
    for cls in (Pade6, Radau5):
        actual = cls(M, B, .2/32).advance(initial, 32)
        errors[cls.__name__] = float(np.linalg.norm(actual-truth))
        assert errors[cls.__name__] <= 1e-10
        assert 0 < np.vdot(actual, M@actual).real <= 1+1e-12
    C = csc_matrix(np.diag([.5, .4, .3]))
    w = np.array([.5, .4, .3])
    positive = evaluate(M, C, w, truth, truth)
    assert positive['temporal_precision_pass']
    phase = evaluate(M, C, w, truth, truth*np.exp(.02j))
    assert not phase['temporal_precision_pass']
    assert max(phase['power_differences'].values()) <= 1e-12
    amplitude = evaluate(M, C, w, truth, truth*.99)
    assert not amplitude['temporal_precision_pass']
    report = dict(controls_pass=True, dense_errors=errors, phase_only_error_rejected=True,
                  amplitude_error_rejected=True, point03_closed=False)
    out = Path(__file__).resolve().parents[1]/'resultados/codex/point03_d16_mid_refined_evaluator_controls_20261008.json'
    with out.open('x', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(report)


if __name__ == '__main__':
    main()
