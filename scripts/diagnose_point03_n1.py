"""Manufactured finite-well eigenstate: spatial diagnostic, not T96 closure."""
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
from scipy.linalg import eigh_tridiagonal
from scipy.optimize import brentq
from audit_point03_m1 import observed

ROOT = Path(__file__).resolve().parents[1]
A = 6e-6
L = 64e-6
BETA = 1.444 * 2 * math.pi / 1550e-9
V = .003 * 2 * math.pi / 1550e-9
Z = .002


def integrals(axis, values):
    field = intensity = 0.
    for x0, x1, f0, f1 in zip(axis[:-1], axis[1:], values[:-1], values[1:]):
        lo, hi = max(x0, -A), min(x1, A)
        if hi <= lo:
            continue
        h = x1 - x0
        u, v = (lo - x0) / h, (hi - x0) / h
        m0, m1, m2 = h * (v-u), h * (v*v-u*u)/2, h * (v**3-u**3)/3
        delta = f1 - f0
        field += abs(f0)**2*m0 + 2*float((f0.conjugate()*delta).real)*m1 + abs(delta)**2*m2
        intensity += abs(f0)**2*m0 + (abs(f1)**2-abs(f0)**2)*m1
    return {'field': float(field), 'intensity': float(intensity)}


def run(destination):
    start = time.monotonic()
    upper = min(math.pi/(2*A), math.sqrt(2*BETA*V))
    def equation(k):
        q = math.sqrt(2*BETA*V-k*k)
        return k*math.tan(k*A)-q/math.tanh(q*(L-A))
    k = brentq(equation, 1., upper*(1-1e-12), xtol=1e-9)
    q = math.sqrt(2*BETA*V-k*k)
    energy = k*k/(2*BETA)
    core_norm = A + math.sin(2*k*A)/(2*k)
    outer_norm = math.cos(k*A)**2*(math.sinh(2*q*(L-A))/(2*q)-(L-A))/math.sinh(q*(L-A))**2
    scale = 1/math.sqrt(core_norm+outer_norm)
    truth = core_norm/(core_norm+outer_norm)
    def phi(x):
        x = np.abs(x)
        return scale*np.where(x<=A, np.cos(k*x), math.cos(k*A)*np.sinh(q*(L-x))/math.sinh(q*(L-A)))
    modal_residual = abs(equation(k))/max(k, q)
    continuous_norm = 2*(quad(lambda x: float(phi(x))**2, 0, A, epsabs=1e-13)[0]+quad(lambda x: float(phi(x))**2, A, L, epsabs=1e-13)[0])
    core_quad = 2*quad(lambda x: float(phi(x))**2, 0, A, epsabs=1e-13)[0]
    assert modal_residual<=1e-12 and abs(continuous_norm-1)<=1e-12 and abs(core_quad-truth)<=1e-12
    rng = np.random.default_rng(941)
    poly_residuals = []
    axis = np.linspace(-L, L, 22)
    for _ in range(6):
        c0, c1 = rng.normal(size=2)+1j*rng.normal(size=2)
        values = c0+c1*axis/L
        result = integrals(axis, values)
        expected = 2*A*abs(c0)**2+2*A**3/(3*L**2)*abs(c1)**2
        residual = abs(result['field']-expected)
        poly_residuals.append(residual)
        assert residual<=1e-12 and result['intensity']>=result['field']-1e-12
    rows = []
    for n in (256,320,400,500,626,640,767,959,1199):
        h = 2*L/(n+1)
        x = -L+np.arange(1,n+1)*h
        initial = phi(x)
        input_norm = float(np.vdot(initial,initial).real*h)
        initial = initial/math.sqrt(input_norm)
        fraction = np.maximum(0,np.minimum(x+h/2,A)-np.maximum(x-h/2,-A))/h
        for name, potential in (('nodal',V*(np.abs(x)>=A)),('cell_average',V*(1-fraction))):
            off = np.full(n-1,-1/(2*BETA*h*h))
            diagonal = np.full(n,1/(BETA*h*h))+potential
            eigenvalues, eigenvectors = eigh_tridiagonal(diagonal,off,lapack_driver='stev')
            residuals = []
            for index in (0,n//2,n-1):
                vector = eigenvectors[:,index]
                action = diagonal*vector
                action[:-1] += off*vector[1:]
                action[1:] += off*vector[:-1]
                residuals.append(float(np.linalg.norm(action-eigenvalues[index]*vector)/(np.max(abs(diagonal))+2*np.max(abs(off)))))
            assert max(residuals)<=1e-12
            final = eigenvectors @ (np.exp(-1j*eigenvalues*Z)*(eigenvectors.T@initial))
            total = float(np.vdot(final,final).real*h)
            assert abs(total-1)<=1e-10
            measurement = integrals(np.r_[-L,x,L],np.r_[0,final,0])
            rows.append(dict(N=n,h_m=h,variant=name,interface_fraction=(A+L)/h%1,input_norm=input_norm,raw_total=total,eigenpair_residual=max(residuals),P_core=measurement,error={method:measurement[method]-truth for method in measurement},raw_field_error=float(np.linalg.norm(final-initial*np.exp(-1j*energy*Z))/np.linalg.norm(initial))))
            assert time.monotonic()-start<=120
    diagnostics = {}
    for variant in ('nodal','cell_average'):
        diagnostics[variant] = {}
        selected = {row['N']:row for row in rows if row['variant']==variant}
        for method in ('field','intensity'):
            triples = ((320,400,500),(400,500,640),(500,640,767))
            orders = [observed([n+1 for n in triple],[selected[n]['P_core'][method] for n in triple]) for triple in triples]
            unstable = any(value is None for value in orders) or any(abs(left-right)/max(abs(left),abs(right))>.2 for left,right in zip(orders,orders[1:]) if left is not None and right is not None)
            errors = [selected[n]['error'][method] for n in sorted(selected)]
            sign_change = any(left*right<0 for left,right in zip(errors,errors[1:]))
            diagnostics[variant][method] = dict(orders=orders,unstable=unstable,error_sign_change=sign_change)
    supported = any(row['unstable'] or row['error_sign_change'] for row in diagnostics['nodal'].values())
    report = dict(created_utc=datetime.now(timezone.utc).isoformat(),controls_pass=True,hypothesis_supported=supported,point03_closed=False,truth_core_power=truth,k_m_inverse=k,q_m_inverse=q,energy_m_inverse=energy,continuous_norm=continuous_norm,modal_residual=modal_residual,polynomial_residuals=poly_residuals,rows=rows,diagnostics=diagnostics,elapsed_s=time.monotonic()-start,source_sha256={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in (Path(__file__),ROOT/'Docs/POINT-03-N1-CONTRACT.md',ROOT/'scripts/audit_point03_m1.py')},scope='Analytical 1D contrast only; not causal attribution or T96 convergence. No T96 propagation performed.')
    assert not destination.exists() and destination.resolve().is_relative_to(ROOT/'resultados/codex')
    destination.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:report[key] for key in ('controls_pass','hypothesis_supported','truth_core_power','diagnostics','elapsed_s','point03_closed')}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args().output)
