"""Known dense reference for generalized rational propagation with weak potential."""
import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import time
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import numpy as np
from scipy.linalg import expm
from scipy.sparse import csc_matrix, diags
from scipy.special import roots_legendre
from diagnose_point03_p4a import local_core, BETA, V, L, Z
from point03_fem_radau import Radau5 as Pade6
from run_point03_exponential import ROOT, sha, write

def run(folder):
    assert not folder.exists()
    folder.mkdir()
    start = time.monotonic()
    n = 127
    h = 2 * L / (n + 1)
    md = np.full(n, 2 * h / 3)
    mo = np.full(n - 1, h / 6)
    mass = diags((mo, md, mo), (-1, 0, 1), format='csc')
    kd = np.full(n, 1 / (BETA * h))
    ko = np.full(n - 1, -1 / (2 * BETA * h))
    vd = np.zeros(n)
    vo = np.zeros(n - 1)
    damping = np.zeros((n, n))
    nodes, weights = roots_legendre(3)
    for cell in range(n + 1):
        x = -L + cell * h
        value = V * (h * np.array([[1 / 3, 1 / 6], [1 / 6, 1 / 3]]) - local_core(x, h))
        points = x + (nodes + 1) * h / 2
        t = (nodes + 1) / 2
        shape = np.array([1 - t, t])
        sig = 2000 * (points + L) / (2 * L)
        local = shape * (weights * sig * h / 2) @ shape.T
        for i, global_i in ((0, cell - 1), (1, cell)):
            if not 0 <= global_i < n:
                continue
            vd[global_i] += value[i, i]
            for j, global_j in ((0, cell - 1), (1, cell)):
                if 0 <= global_j < n:
                    damping[global_i, global_j] += local[i, j]
        if 1 <= cell < n:
            vo[cell - 1] += value[0, 1]
    H = diags((ko + vo, kd + vd, ko + vo), (-1, 0, 1), format='csc')
    rng = np.random.default_rng(953)
    initial = rng.normal(size=n) + 1j * rng.normal(size=n)
    initial /= math.sqrt(float(np.vdot(initial, mass @ initial).real))

    def norm(a):
        return math.sqrt(float(np.vdot(a, mass @ a).real))
    results = []
    for label, D in (('zero', np.zeros_like(damping)), ('varying', damping)):
        assert np.allclose(D, D.T, atol=1e-14) and np.linalg.eigvalsh(D).min() >= -1e-14
        generator = -1j * H - csc_matrix(D)
        dense = np.linalg.solve(mass.toarray(), generator.toarray())
        reference = expm(Z * dense) @ initial
        assert norm(reference) <= 1 + 1e-09
        errors = []
        rows = []
        for steps in (8192, 16384, 32768):
            solver = Pade6(mass, generator, Z / steps)
            actual = solver.advance(initial, steps)
            error = norm(actual - reference) / norm(reference)
            errors.append(error)
            filename = folder / f'{label}_{steps}.npz'
            np.savez(filename, field=actual, reference=reference, initial=initial)
            physical = norm(actual) ** 2
            assert np.all(np.isfinite(actual)) and physical <= 1 + 1e-09
            if label == 'zero':
                pass
            rows.append(dict(steps=steps, error=error, physical_power=physical, reference_power=norm(reference) ** 2, field_path=str(filename), field_sha256=sha(filename)))
            assert time.monotonic() - start <= 180
        orders = [math.log2(a / b) for a, b in zip(errors, errors[1:])]
        passed = errors[-1] <= 1e-07 and all((4.5 <= p <= 5.5 for p in orders)) and (abs(rows[-1]['physical_power'] - rows[-1]['reference_power']) <= 1e-07)
        results.append(dict(damping=label, rows=rows, orders=orders, pass_=passed))
    report = dict(created_utc=datetime.now(timezone.utc).isoformat(), controls_pass=all((row['pass_'] for row in results)), results=results, elapsed_s=time.monotonic() - start, no_T96_propagation=True, roots=dict(poles=[dict(real=float(v.real),imag=float(v.imag)) for v in solver.poles],zeros=[dict(real=float(v.real),imag=float(v.imag)) for v in solver.zeros]), point03_closed=False, source_sha256={str(path): sha(path) for path in (Path(__file__), ROOT / 'scripts/point03_fem_radau.py', ROOT / 'Docs/POINT-03-P4H-CONTRACT.md')})
    write(folder / 'report.json', report)
    print(json.dumps({key: report[key] for key in ('controls_pass', 'elapsed_s', 'results', 'point03_closed')}))
if __name__ == '__main__':
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    run(args.out.resolve())
