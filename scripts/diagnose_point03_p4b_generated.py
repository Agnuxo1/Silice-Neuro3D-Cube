"""Analytical well: exact weak potential coupling versus nodal averaging."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import time
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import numpy as np
from scipy.integrate import quad
from scipy.linalg import eigh, eigh_tridiagonal
from scipy.optimize import brentq
from audit_point03_m1 import observed
from diagnose_point03_n1 import integrals
from run_point03_exponential import ROOT, write
HALF = 6e-06
L = 6.4e-05
BETA = 1.444 * 2 * math.pi / 1.55e-06
V = 0.003 * 2 * math.pi / 1.55e-06
Z = 0.002

def local_core(x, h):
    lo, hi = (max(x, -HALF), min(x + h, HALF))
    if hi <= lo:
        return np.zeros((2, 2))
    a, b = ((lo - x) / h, (hi - x) / h)
    m0 = h * (b - a)
    m1 = h * (b * b - a * a) / 2
    m2 = h * (b ** 3 - a ** 3) / 3
    return np.array([[m0 - 2 * m1 + m2, m1 - m2], [m1 - m2, m2]])

def run(out):
    start = time.monotonic()
    upper = min(math.pi / (2 * HALF), math.sqrt(2 * BETA * V))

    def eq(k):
        q = math.sqrt(2 * BETA * V - k * k)
        return k * math.tan(k * HALF) - q / math.tanh(q * (L - HALF))
    k = brentq(eq, 1.0, upper * (1 - 1e-12), xtol=1e-09)
    q = math.sqrt(2 * BETA * V - k * k)
    energy = k * k / (2 * BETA)
    inside = HALF + math.sin(2 * k * HALF) / (2 * k)
    outside = math.cos(k * HALF) ** 2 * (math.sinh(2 * q * (L - HALF)) / (2 * q) - (L - HALF)) / math.sinh(q * (L - HALF)) ** 2
    scale = 1 / math.sqrt(inside + outside)
    truth = inside / (inside + outside)

    def phi(x):
        x = np.abs(x)
        return scale * np.where(x <= HALF, np.cos(k * x), math.cos(k * HALF) * np.sinh(q * (L - x)) / math.sinh(q * (L - HALF)))
    norm = 2 * (quad(lambda x: float(phi(x)) ** 2, 0, HALF, epsabs=1e-13, epsrel=1e-13)[0] + quad(lambda x: float(phi(x)) ** 2, HALF, L, epsabs=1e-13, epsrel=1e-13)[0])
    assert abs(norm - 1) <= 1e-12 and abs(eq(k)) / max(k, q) <= 1e-12
    moment_errors = []
    for offset in (0.1, 0.3, 0.7):
        h = 0.000128 / 128
        for edge in (-HALF, HALF):
            x = edge - offset * h
            mass = h * np.array([[1 / 3, 1 / 6], [1 / 6, 1 / 3]])
            local = V * (mass - local_core(x, h))
            exact = np.zeros((2, 2))
            points = [x, *[b for b in (-HALF, HALF) if x < b < x + h], x + h]
            for i in (0, 1):
                for j in (0, 1):

                    def f(t):
                        u = (t - x) / h
                        shapes = (1 - u, u)
                        return (V if abs(t) > HALF else 0) * shapes[i] * shapes[j]
                    exact[i, j] = sum((quad(f, a, b, epsabs=1e-18, epsrel=1e-12)[0] for a, b in zip(points, points[1:])))
            error = float(np.max(abs(local - exact)) / (V * h))
            assert error <= 1e-12
            moment_errors.append(error)
    rows = []
    for n in (127, 255, 511, 1023):
        h = 2 * L / (n + 1)
        x = -L + np.arange(1, n + 1) * h
        md = np.full(n, 2 * h / 3)
        mo = np.full(n - 1, h / 6)
        kd = np.full(n, 1 / (BETA * h))
        ko = np.full(n - 1, -1 / (2 * BETA * h))
        vd = np.zeros(n)
        vo = np.zeros(n - 1)
        for cell in range(n + 1):
            value = V * (h * np.array([[1 / 3, 1 / 6], [1 / 6, 1 / 3]]) - local_core(-L + cell * h, h))
            for local, global_node in ((0, cell - 1), (1, cell)):
                if 0 <= global_node < n:
                    vd[global_node] += value[local, local]
            if 1 <= cell < n:
                vo[cell - 1] += value[0, 1]
        mass = np.diag(md) + np.diag(mo, 1) + np.diag(mo, -1)
        assert np.all(md > 2 * abs(np.r_[mo, 0])) and np.array_equal(mass, mass.T)
        initial = phi(x).astype(complex)
        input_mass = float(np.vdot(initial, mass @ initial).real)
        initial /= math.sqrt(input_mass)
        fraction = np.maximum(0, np.minimum(x + h / 2, HALF) - np.maximum(x - h / 2, -HALF)) / h
        variants = (('nodal', kd / h + V * (abs(x) >= HALF), ko / h, False), ('cell_average', kd / h + V * (1 - fraction), ko / h, False), ('FEM_lumped', (kd + vd) / h, (ko + vo) / h, False), ('FEM_consistent', kd + vd, ko + vo, True))
        for name, diagonal, off, generalized in variants:
            if generalized:
                H = np.diag(diagonal) + np.diag(off, 1) + np.diag(off, -1)
                values, vectors = eigh(H, mass, driver='gvd')
                coefficients = vectors.T @ (mass @ initial)
                scheme_input = float(np.vdot(initial, mass @ initial).real)
            else:
                values, vectors = eigh_tridiagonal(diagonal, off, lapack_driver='stev')
                coefficients = vectors.T @ initial
                scheme_input = float(np.vdot(initial, initial).real * h)
            residuals = []
            for index in (0, n // 2, n - 1):
                v = vectors[:, index]
                action = diagonal * v
                action[:-1] += off * v[1:]
                action[1:] += off * v[:-1]
                target = mass @ v if generalized else v
                denominator = (max(abs(diagonal)) + 2 * max(abs(off)) + abs(values[index]) * (h if generalized else 1)) * float(np.linalg.norm(v))
                residuals.append(float(np.linalg.norm(action - values[index] * target) / denominator))
            assert max(residuals) <= 1e-11
            final = vectors @ (np.exp(-1j * values * Z) * coefficients)
            physical_norm = float(np.vdot(final, mass @ final).real)
            scheme_final = physical_norm if generalized else float(np.vdot(final, final).real * h)
            assert abs(scheme_final - scheme_input) <= 1e-10
            measurement = integrals(np.r_[-L, x, L], np.r_[0, final, 0])
            rows.append(dict(N=n, h_m=h, variant=name, P_core=measurement, error={method: value - truth for method, value in measurement.items()}, physical_output_norm=physical_norm, scheme_norm_change=abs(scheme_final - scheme_input), input_reconstruction_norm_before_scaling=input_mass, eigenpair_residual=max(residuals), raw_field_error=float(np.linalg.norm(final - initial * np.exp(-1j * energy * Z)) / np.linalg.norm(initial))))
            rawfolder = out.parent / (out.stem + '_raw')
            rawfolder.mkdir(exist_ok=True)
            rawpath = rawfolder / f'n{n}_{name}.npz'
            assert not rawpath.exists()
            np.savez(rawpath, axis=x, initial=initial, field=final, diagonal=diagonal, off=off, eigenvalues=values[[0, n // 2, n - 1]], eigenvectors=vectors[:, [0, n // 2, n - 1]], mass_diagonal=md, mass_off=mo, generalized=generalized)
            rows[-1]['raw_path'] = str(rawpath)
            rows[-1]['raw_sha256'] = hashlib.sha256(rawpath.read_bytes()).hexdigest()
            assert time.monotonic() - start <= 180
    diagnostics = {}
    for variant in ('nodal', 'cell_average', 'FEM_lumped', 'FEM_consistent'):
        selected = {row['N']: row for row in rows if row['variant'] == variant}
        diagnostics[variant] = {}
        for method in ('field', 'intensity'):
            p0 = observed((128, 256, 512), [selected[n]['P_core'][method] for n in (127, 255, 511)])
            p = observed((256, 512, 1024), [selected[n]['P_core'][method] for n in (255, 511, 1023)])
            stable = p0 is not None and p is not None and (abs(p - p0) / max(abs(p), abs(p0)) <= 0.2)
            indicator = 1.25 * abs(selected[1023]['P_core'][method] - selected[511]['P_core'][method]) / ((1024 / 512) ** min(p, 2) - 1) if p is not None else None
            error = abs(selected[1023]['error'][method])
            covered = indicator is not None and error <= indicator
            diagnostics[variant][method] = dict(orders=[p0, p], stable=stable, known_error=error, indicator=indicator, covered=covered)
    supported = all((row['stable'] and row['covered'] for row in diagnostics['FEM_consistent'].values()))
    result = dict(created_utc=datetime.now(timezone.utc).isoformat(), controls_pass=True, hypothesis_supported=supported, point03_closed=False, truth_core_power=truth, moment_errors=moment_errors, rows=rows, diagnostics=diagnostics, elapsed_s=time.monotonic() - start, source_sha256={str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in (Path(__file__), ROOT / 'Docs/POINT-03-P4B-CONTRACT.md')}, scope='Known 1D diagnostic only; all input conventions declared; no T96 propagation or causal closure.')
    write(out, result)
    print(json.dumps({key: result[key] for key in ('controls_pass', 'hypothesis_supported', 'truth_core_power', 'diagnostics', 'elapsed_s', 'point03_closed')}))
if __name__ == '__main__':
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.output)
