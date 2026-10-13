"""Small FEMTO-1 intensity model. SI units; numerical evidence only."""
from __future__ import annotations
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def now():
    return datetime.now(timezone.utc).isoformat()

def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')

def save_npz(path, **arrays):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as f:
        np.savez_compressed(f, **arrays)

def save_npy(path, array):
    with Path(path).open('xb') as f:
        np.save(f, array, allow_pickle=False)

def optical_weights(scores):
    scores = np.asarray(scores, dtype=float)
    w = scores - scores.min(axis=0, keepdims=True)
    scale = float(w.sum(axis=0).max())
    if scale <= 0:
        raise ValueError('No class contrast')
    # A single global scale preserves argmax; per-column normalization does not.
    return w / scale, scale

def tree(w):
    w = np.asarray(w, dtype=float)
    if w.shape != (4,16) or np.any(w < 0) or np.any(w.sum(0) > 1+1e-12):
        raise ValueError('Invalid passive weights')
    orders, ratios = [], []
    for col in w.T:
        if np.count_nonzero(col) > 3:
            raise ValueError('Three useful leaves plus discard require a structural zero')
        order = sorted(range(4), key=lambda k: (col[k] == 0, k))[:3]
        a,b,c = col[order]
        d = max(0.,1-float(col.sum()))
        r1 = a+b
        orders.append(order)
        ratios.append([r1,a/(a+b) if a+b else 0.,c/(c+d) if c+d else 0.])
    return np.asarray(orders, dtype=int), np.asarray(ratios)

def from_ratios(orders, r):
    w = np.zeros((4,16))
    for j, (a,b,c) in enumerate(r):
        w[orders[j],j] = [a*b,a*(1-b),(1-a)*c]
    return w

def realization(w, sigma, rng, correlation=.8):
    order,r = tree(w)
    eps = sigma*(math.sqrt(correlation)*rng.standard_normal()
                 + math.sqrt(1-correlation)*rng.standard_normal(r.shape))
    # Gaussian relative perturbation, matching the guide's exploratory model.
    # Clip unphysical negative kappa; report the model as assumed, not measured.
    multiplier = np.maximum(0,1+eps)
    return from_ratios(order,np.sin(multiplier*np.arcsin(np.sqrt(r)))**2)

def fit_readout(power, labels, maxiter=120):
    """Exactly 4 positive gains and 4 offsets; no mixing across detectors."""
    power = np.asarray(power)
    labels = np.asarray(labels, dtype=int)
    scale = max(float(power.std()),1e-8)
    p = power/scale
    def objective(v):
        gains = np.exp(v[:4])
        z = p*gains + v[4:]
        logp = z-logsumexp(z,axis=1,keepdims=True)
        loss = -logp[np.arange(len(labels)),labels].mean() + 1e-5*np.sum(v*v)
        e = np.exp(logp)
        e[np.arange(len(labels)),labels] -= 1
        e /= len(labels)
        grad = np.r_[(e*p).sum(0)*gains,e.sum(0)] + 2e-5*v
        return loss,grad
    result = minimize(objective,np.zeros(8),jac=True,method='L-BFGS-B',
                      bounds=[(-6,8)]*4+[(-100,100)]*4,
                      options={'maxiter':maxiter,'ftol':1e-9})
    return np.exp(result.x[:4])/scale,result.x[4:],bool(result.success)

def accuracy(x, y, w, gain=None, offset=None):
    z = x @ w.T
    if gain is not None:
        z = z*gain+offset
    return float(np.mean(z.argmax(1)==y))

def wilson(k,n):
    z=1.959963984540054
    p=k/n; den=1+z*z/n
    mid=(p+z*z/(2*n))/den
    delta=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [mid-delta,mid+delta]

def metric(pred,y):
    k=int(np.sum(pred==y)); n=len(y)
    return {'accuracy':k/n,'correct':k,'n':n,'wilson95':wilson(k,n)}

def kappa(gap_m):
    table=np.array([[14e-6,471.6394183216887],[16e-6,203.05398235231223],
                    [20e-6,38.51257119356343]])
    if not 14e-6-1e-14 <= gap_m <= 20e-6+1e-14:
        raise ValueError('Provisional step-index model only covers 14–20 um')
    return float(np.exp(np.interp(gap_m,table[:,0],np.log(table[:,1]))))
