"""V7: solver FD propio (independiente de solver2d.py), Dirichlet en [-L,L]^2, 5 puntos, n^2 promediado por celda (s x s).
Uso: python -B v7_fd.py f2 <L> <h> <K>              caso i de F2 (anillo 6<r<12 n=1.439; resto 1.444), shift en n_eff=1.44219587
     python -B v7_fd.py i2 <R_mm|inf> <L> <h> <K>   guia curvada I2 (nucleo r<6 n1=1.444 sobre fondo 1.439; n_eq=n(1+X/R)), shift = max n2
Salida: JSON a stdout (una linea) y a v7_<...>.json"""
import sys, json, time, math
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla
LAM = 1.55; K0 = 2 * math.pi / LAM
def cellavg(f, x, h, s):
    N = len(x); offs = (np.arange(s) + .5) / s * h - .5 * h
    out = np.empty((N, N))
    xs = (x[:, None] + offs[None, :]).ravel()
    for j0 in range(0, N, 32):
        j1 = min(N, j0 + 32)
        ys = (x[j0:j1, None] + offs[None, :]).ravel()
        X, Y = np.meshgrid(xs, ys)
        out[j0:j1] = f(X, Y).reshape(j1 - j0, s, N, s).mean(axis=(1, 3))
    return out
def solve(nfun, L, h, K, sigma2, s=8):
    nh = int(round(L / h)); N = 2 * nh + 1
    x = (np.arange(N) - (N - 1) / 2) * h
    n2 = cellavg(lambda X, Y: nfun(X, Y) ** 2, x, h, s)
    M = N - 2
    T = sp.diags([np.ones(M - 1), -2 * np.ones(M), np.ones(M - 1)], [-1, 0, 1], format="csr") / h ** 2
    I = sp.identity(M, format="csr")
    P = (sp.kron(I, T) + sp.kron(T, I) + sp.diags(K0 ** 2 * n2[1:-1, 1:-1].ravel())).tocsc()
    sig = sigma2(n2)
    w, v = sla.eigsh(P, k=K, sigma=sig, which="LM")
    o = np.argsort(w)[::-1]; w = w[o]; v = v[:, o]
    neff = np.sqrt(w) / K0
    psi = []
    for m in range(K):
        f = np.zeros((N, N)); f[1:-1, 1:-1] = v[:, m].reshape(M, M)
        f /= math.sqrt((f * f).sum() * h * h); psi.append(f)
    return neff, psi, x, N, M * M
mode = sys.argv[1]; t0 = time.time()
if mode in ("f2", "f2t", "f2e"):
    L, h, K = float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4])
    NT = int(sys.argv[5]) if mode != "f2" else None
    def nf(X, Y):
        n = np.full(X.shape, 1.444)
        if mode == "f2":
            r = np.hypot(X, Y); n[(r >= 6) & (r <= 12)] = 1.439
        elif mode == "f2t":
            for k in range(NT):
                th = 2 * math.pi * k / NT
                n[np.hypot(X - 9 * math.cos(th), Y - 9 * math.sin(th)) <= 1.5] = 1.439
        else:
            f = NT * 1.5 ** 2 / (2 * 9 * 6); ne = math.sqrt(f * 1.439 ** 2 + (1 - f) * 1.444 ** 2)
            r = np.hypot(X, Y); n[(r >= 6) & (r <= 12)] = ne
        return n
    import os; SIG = float(os.environ.get("SIG", "1.44219587036024"))
    neff, psi, x, N, unk = solve(nf, L, h, K, lambda n2: (K0 * SIG) ** 2)
    X, Y = np.meshgrid(x, x); r = np.hypot(X, Y)
    P12 = [float((p * p)[r <= 12].sum() * h * h) for p in psi]
    cands = [m for m in range(K) if P12[m] >= .5 and abs(neff[m] - SIG) <= .002]
    imax = int(np.argmax(P12))
    sel = max(cands, key=lambda m: neff[m]) if cands else None
    out = dict(mode=mode, NT=NT, L=L, h=h, K=K, unknowns=unk, bound=sel is not None,
               n_core=float(neff[sel]) if sel is not None else None, P12=P12[sel] if sel is not None else None,
               n_maxP=float(neff[imax]), P_maxP=P12[imax], t=time.time() - t0)
    fn = f"v7_{mode}{NT if NT else ''}_L{L:g}_h{h:g}" + (f"_sig{SIG:.5f}" if 'SIG' in os.environ else '') + ".json"
else:
    Rm, L, h, K = sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5])
    Ru = None if Rm == "inf" else 1000 * float(Rm)
    def nf(X, Y):
        r = np.hypot(X, Y); n = np.where(r <= 6, 1.444, 1.439)
        return n if Ru is None else n * (1 + X / Ru)
    def nf0(X, Y):
        r = np.hypot(X, Y); return np.where(r <= 6, 1.444, 1.439)
    near = len(sys.argv) > 6
    NEAR = float(sys.argv[6]) if near else None
    s2 = (lambda n2: (K0 * NEAR) ** 2) if near else (lambda n2: K0 ** 2 * n2.max())
    # recto de la misma caja (para solape S y D = n_curvo - n_recto)
    neff0, psi0, x, N, unk = solve(nf0, L, h, 1, s2)
    out = dict(mode="i2", R_mm=Rm, L=L, h=h, K=K, unknowns=unk, n_recto=float(neff0[0]))
    if Ru is not None:
        neff, psi, x, N, unk = solve(nf, L, h, K, s2)
        S = [float((((p * psi0[0]).sum() * h * h)) ** 2) for p in psi]
        m = int(np.argmax(S)); X, Y = np.meshgrid(x, x)
        out.update(n_core=float(neff[m]), S=S[m], idx=m, D=float(neff[m] - neff0[0]),
                   x_mean=float(((psi[m] ** 2) * X).sum() * h * h))
    out["t"] = time.time() - t0
    fn = f"v7_i2{'n' if near else ''}_R{Rm}_L{L:g}_h{h:g}.json"
json.dump(out, open(fn, "w"), indent=1); print(json.dumps(out), flush=True)
