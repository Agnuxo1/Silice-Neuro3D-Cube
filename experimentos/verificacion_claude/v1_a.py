"""V1-A: solver FD 2D propio (independiente de solver2d.py) y observable de potencia. Ver CONTRATO-V1.md."""
import os
os.environ["OMP_NUM_THREADS"] = "1"
import json, sys, time, datetime
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla
from scipy.special import j0, j1, k0 as bk0, k1 as bk1
from scipy.optimize import brentq
from scipy.integrate import quad

LAM, A, N1, N2 = 1.55, 6.0, 1.444, 1.439
K = 2*np.pi/LAM
V = K*A*np.sqrt(N1**2-N2**2)

def analytic():
    f = lambda u: u*j1(u)/j0(u) - np.sqrt(V*V-u*u)*bk1(np.sqrt(V*V-u*u))/bk0(np.sqrt(V*V-u*u))
    u = brentq(f, 1e-3, 2.4048, xtol=1e-15, rtol=1e-15)
    w = np.sqrt(V*V-u*u)
    neff = np.sqrt(N1**2-(u/(K*A))**2)
    gam = (j0(u)**2+j1(u)**2)/(j1(u)**2+j0(u)**2*(bk1(w)/bk0(w))**2)
    pc = quad(lambda r: j0(u*r/A)**2*r, 0, A, epsabs=0, epsrel=1e-13)[0]
    po = quad(lambda r: (j0(u)/bk0(w)*bk0(w*r/A))**2*r, A, np.inf, epsabs=0, epsrel=1e-13)[0]
    return dict(u=u, w=w, neff=neff, gam_closed=gam, gam_quad=pc/(pc+po))

def grid(L, h):
    nh = int(round(L/h)); N = 2*nh+1
    x = (np.arange(N)-nh)*h
    return N, x

def cell_mean(fun, x, h, s):
    # media sobre la celda h x h centrada en cada nodo, s x s subpuntos (punto medio)
    off = ((np.arange(s)+0.5)/s-0.5)*h
    xs = (x[:, None]+off[None, :]).ravel()
    N = len(x)
    out = np.empty((N, N))
    B = 32
    for j0_ in range(0, N, B):
        j1_ = min(N, j0_+B)
        ys = (x[j0_:j1_, None]+off[None, :]).ravel()
        X, Y = np.meshgrid(xs, ys)
        out[j0_:j1_] = fun(X, Y).reshape(j1_-j0_, s, N, s).mean(axis=(1, 3))
    return out

def solve(L, h, s, nm=1):
    N, x = grid(L, h)
    n2 = cell_mean(lambda X, Y: np.where(np.hypot(X, Y) <= A, N1**2, N2**2), x, h, s)
    M = N-2
    t = sp.diags([np.ones(M-1), -2*np.ones(M), np.ones(M-1)], [-1, 0, 1])/h**2
    I = sp.identity(M)
    Pm = (sp.kron(I, t)+sp.kron(t, I)+sp.diags((K**2*n2[1:-1, 1:-1]).ravel())).tocsc()
    sigma = K**2*n2.max()
    w, v = sla.eigsh(Pm, k=nm, sigma=sigma, which="LM")
    k = np.argmax(w)
    psi = np.zeros((N, N)); psi[1:-1, 1:-1] = v[:, k].reshape(M, M)
    psi /= np.sqrt((psi**2).sum())*h
    if psi.flat[np.argmax(np.abs(psi))] < 0: psi = -psi
    return np.sqrt(w[k])/K, x, psi

def gamma_fd(x, psi, h, s):
    cov = cell_mean(lambda X, Y: (np.hypot(X, Y) < A).astype(float), x, h, s)
    return float((cov*psi**2).sum()/(psi**2).sum())

def gamma_on_analytic(x, h, s, u, w):
    X, Y = np.meshgrid(x, x)
    r = np.hypot(X, Y)
    pa = np.where(r <= A, j0(u*np.minimum(r, A)/A), j0(u)/bk0(w)*bk0(w*np.maximum(r, A)/A))
    cov = cell_mean(lambda XX, YY: (np.hypot(XX, YY) < A).astype(float), x, h, s)
    return float((cov*pa**2).sum()/(pa**2).sum())

if __name__ == "__main__":
    out = {"inicio_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    an = analytic(); out["analitico"] = an
    print("analitico", an, flush=True)
    runs = {}
    def R(L, h, s):
        t0 = time.time()
        ne, x, psi = solve(L, h, s)
        runs[f"L{L:g}_h{h:g}_s{s}"] = ne
        print(f"L={L} h={h} s={s} neff={ne:.13f} t={time.time()-t0:.1f}s", flush=True)
        return ne, x, psi
    keep = {}
    for h in (0.5, 0.25, 0.125):
        keep[h] = R(40, h, 8)
        R(40, h, 1)
    R(60, 0.25, 8)
    for h in (0.25, 0.125, 0.0625):
        R(24, h, 8)
    # observable
    obs = {}
    for h in (0.25, 0.125):
        ne, x, psi = keep[h]
        d = {}
        for s in (1, 8, 32):
            g = gamma_fd(x, psi, h, s)
            d[f"s{s}"] = dict(gamma=g, err_rel=abs(g-an["gam_closed"])/an["gam_closed"])
        ga = gamma_on_analytic(x, h, 32, an["u"], an["w"])
        d["psi_analitica_s32"] = dict(gamma=ga, err_rel=abs(ga-an["gam_closed"])/an["gam_closed"])
        obs[f"h{h:g}"] = d
        print("obs", h, d, flush=True)
    out["runs_neff"] = runs; out["observable"] = obs
    out["fin_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    json.dump(out, open("v1_a_resultados.json", "w"), indent=1)
