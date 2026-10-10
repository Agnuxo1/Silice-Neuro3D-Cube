"""V6: FD escalar PROPIO (cuadrante con simetria par-par, Neumann en los ejes) + analitica LP01 propia.
No importa nada de solver2d_claude. Solo numpy/scipy. OMP_NUM_THREADS=1.
Uso: python -B v6_fd_propio.py <L> <h> <s> [full]
  full: dominio completo [-L,L]^2 sin simetria (comprobacion cruzada del cuadrante)
Salida: una linea JSON.
"""
import os, sys, json, time
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla
from scipy.special import jv, kv
from scipy.optimize import brentq

LAM, A, N1, N2 = 1.55, 6.0, 1.444, 1.439
K0 = 2 * np.pi / LAM
_tr = getattr(np, "trapezoid", None) or np.trapz


def analitica():
    """neff y Gamma LP01 con formulacion propia: continuidad de la log-derivada, brentq sobre neff."""
    def g(neff):
        U = A * K0 * np.sqrt(N1**2 - neff**2)
        W = A * K0 * np.sqrt(neff**2 - N2**2)
        # -U J1/J0 = -W K1/K0  ->  U J1 K0 - W K1 J0 = 0  (escrito con jv/kv de orden entero)
        return U * jv(1, U) * kv(0, W) - W * kv(1, W) * jv(0, U)
    xs = np.linspace(N2 + 1e-9, N1 - 1e-9, 20001)
    v = g(xs)
    i = np.where(np.sign(v[:-1]) != np.sign(v[1:]))[0]
    roots = [brentq(g, xs[k], xs[k + 1], xtol=1e-16, rtol=1e-15) for k in i]
    neff = max(roots)
    U = A * K0 * np.sqrt(N1**2 - neff**2)
    W = A * K0 * np.sqrt(neff**2 - N2**2)
    # Gamma por integracion directa con trapecio fino (no la forma cerrada)
    r_in = np.linspace(0, A, 400001)
    r_out = np.linspace(A, 400.0, 4000001)
    f_in = jv(0, U * r_in / A)
    C = jv(0, U) / kv(0, W)
    f_out = C * kv(0, W * r_out / A)
    Pin = _tr(f_in**2 * r_in, r_in)
    Pout = _tr(f_out**2 * r_out, r_out)
    return dict(neff=neff, U=U, W=W, n_roots=len(roots), Gamma=Pin / (Pin + Pout), C=C)


def cell_n2(L, h, s, half):
    nh = int(round(L / h))
    if half:
        x = np.arange(0, nh + 1) * h          # cuadrante: nodos 0..nh
    else:
        x = (np.arange(2 * nh + 1) - nh) * h
    offs = (np.arange(s) + 0.5) / s * h - 0.5 * h
    xf = (x[:, None] + offs[None, :]).ravel()
    n2 = np.full((x.size, x.size), N2**2)
    out = np.empty((x.size, x.size))
    for j0 in range(0, x.size, 32):
        j1 = min(x.size, j0 + 32)
        yf = (x[j0:j1, None] + offs[None, :]).ravel()
        X, Y = np.meshgrid(xf, yf)
        inside = ((X * X + Y * Y) <= A * A) if os.environ.get("V6_LE") else ((X * X + Y * Y) < A * A)
        val = np.where(inside, N1**2, N2**2).astype(float)
        out[j0:j1, :] = val.reshape(j1 - j0, s, x.size, s).mean(axis=(1, 3))
    return x, out, nh


def solve_quadrant(L, h, s):
    x, c, nh = cell_n2(L, h, s, True)
    M = nh  # incognitas por eje: i = 0..nh-1 (nodo nh es Dirichlet)
    main = -2.0 * np.ones(M)
    up = np.ones(M - 1)
    lo = np.ones(M - 1)
    up[0] = 2.0  # fantasma Neumann: psi_{-1} = psi_1
    T = sp.diags([lo, main, up], [-1, 0, 1], format="csr")
    w = np.ones(M); w[0] = 0.5          # peso del nodo en el eje
    D = sp.diags(np.sqrt(w)); Di = sp.diags(1 / np.sqrt(w))
    S = (D @ T @ Di).tocsr() / h**2     # simetrica
    assert abs(S - S.T).max() < 1e-9 * abs(S).max()
    I = sp.identity(M, format="csr")
    n2 = c[:M, :M]
    P = (sp.kron(I, S) + sp.kron(S, I) + sp.diags(K0**2 * n2.ravel())).tocsc()
    sigma = K0**2 * N1**2 * 1.0000001
    vals, vecs = sla.eigsh(P, k=2, sigma=sigma, which="LM")
    o = np.argsort(vals)[::-1]
    vals, vecs = vals[o], vecs[:, o]
    beta2 = vals[0]
    neff = np.sqrt(beta2) / K0
    # psi en nodos (deshacer simetrizacion), indices [iy, ix]
    phi = vecs[:, 0].reshape(M, M)
    psi = phi / np.sqrt(w)[:, None] / np.sqrt(w)[None, :]
    # pesos de suma sobre el plano completo: x4 y nodo de eje con 1/2
    W2 = 4.0 * np.outer(w, w)
    norm = np.sum(W2 * psi**2) * h * h
    psi = psi / np.sqrt(norm)
    X, Y = np.meshgrid(x[:M], x[:M])
    # cobertura del nucleo por celda (mismo s) para Gamma
    return neff, psi, W2, x[:M], n2


def gamma_obs(psi, W2, x, h, s):
    offs = (np.arange(s) + 0.5) / s * h - 0.5 * h
    M = x.size
    xf = (x[:, None] + offs[None, :]).ravel()
    cov = np.empty((M, M))
    for j0 in range(0, M, 32):
        j1 = min(M, j0 + 32)
        yf = (x[j0:j1, None] + offs[None, :]).ravel()
        X, Y = np.meshgrid(xf, yf)
        ins = ((X * X + Y * Y) < A * A).astype(float)
        cov[j0:j1, :] = ins.reshape(j1 - j0, s, M, s).mean(axis=(1, 3))
    num = np.sum(W2 * cov * psi**2)
    den = np.sum(W2 * psi**2)
    return num / den


def solve_full(L, h, s):
    x, c, nh = cell_n2(L, h, s, False)
    N = x.size
    M = N - 2
    T = sp.diags([np.ones(M - 1), -2 * np.ones(M), np.ones(M - 1)], [-1, 0, 1], format="csr") / h**2
    I = sp.identity(M, format="csr")
    n2 = c[1:-1, 1:-1]
    P = (sp.kron(I, T) + sp.kron(T, I) + sp.diags(K0**2 * n2.ravel())).tocsc()
    vals = sla.eigsh(P, k=1, sigma=K0**2 * N1**2 * 1.0000001, which="LM", return_eigenvectors=False)
    return np.sqrt(vals[0]) / K0


if __name__ == "__main__":
    L = float(sys.argv[1]); h = float(sys.argv[2]); s = int(sys.argv[3])
    mode = sys.argv[4] if len(sys.argv) > 4 else "quad"
    t0 = time.time()
    an = analitica()
    if mode == "full":
        ne = solve_full(L, h, s)
        print(json.dumps(dict(modo="full", L=L, h=h, s=s, neff=ne, err=ne - an["neff"], neff_ana=an["neff"], t=time.time() - t0)))
    else:
        ne, psi, W2, x, n2 = solve_quadrant(L, h, s)
        G = gamma_obs(psi, W2, x, h, s)
        print(json.dumps(dict(modo="quad", L=L, h=h, s=s, neff=ne, err=ne - an["neff"], neff_ana=an["neff"],
                              Gamma_FD=G, Gamma_ana=an["Gamma"], errG_rel=(G - an["Gamma"]) / an["Gamma"],
                              U=an["U"], W=an["W"], n_roots=an["n_roots"], t=time.time() - t0)))
