"""Solver FD 2D escalar INDEPENDIENTE (no importa solver2d ni src/silice).
(d2/dx2+d2/dy2+k0^2 n^2) psi = beta^2 psi, Dirichlet en [-L,L]^2, nodos x_i=(i-(N-1)/2)h, N=2*round(L/h)+1.
n^2 por celda = media de ss x ss submuestras de la funcion n2(X,Y). Shift-invert eigsh.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import math, numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla
LAM = 1.55
K0 = 2 * math.pi / LAM

def make_grid(L, h):
    nh = int(round(L / h)); N = 2 * nh + 1
    x = (np.arange(N) - (N - 1) / 2.0) * h
    return N, x

def cell_avg(n2fun, x, h, ss):
    off = (np.arange(ss) + 0.5) / ss - 0.5
    acc = np.zeros((x.size, x.size))
    for oy in off:
        Y = (x[:, None] + oy * h) * np.ones((1, x.size))
        for ox in off:
            X = (x[None, :] + ox * h) * np.ones((x.size, 1))
            acc += n2fun(X, Y)
    return acc / (ss * ss)

def solve(n2fun, L, h, sigma_neff, k, ss=4):
    N, x = make_grid(L, h)
    n2 = cell_avg(n2fun, x, h, ss)
    M = N - 2
    T = sp.diags([np.ones(M - 1), -2 * np.ones(M), np.ones(M - 1)], [-1, 0, 1], format="csr") / h**2
    I = sp.identity(M, format="csr")
    A = (sp.kron(I, T) + sp.kron(T, I) + sp.diags(K0**2 * n2[1:-1, 1:-1].ravel())).tocsc()
    vals, vecs = sla.eigsh(A, k=k, sigma=(K0 * sigma_neff) ** 2, which="LM")
    o = np.argsort(vals)[::-1]
    vals = vals[o]; vecs = vecs[:, o]
    neff = np.sqrt(vals) / K0
    psis = []
    for m in range(k):
        f = np.zeros((N, N)); f[1:-1, 1:-1] = vecs[:, m].reshape(M, M)
        f /= math.sqrt((f**2).sum() * h * h)
        psis.append(f)
    return neff, psis, x
