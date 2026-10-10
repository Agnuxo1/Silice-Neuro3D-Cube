"""V8 independiente: n_eff del caso i (camisa continua) en caja L, h=0.25, s_sub=8. Codigo propio (no importa solver2d ni run_tracks).
Uso: python -B v8_f31.py L [k]
"""
import sys, json, time, math
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla
LAM = 1.55; K0 = 2*np.pi/LAM
A, T = 6.0, 6.0
N1 = 1.444; N2 = 1.439
SIG = 1.44219587036024
def cell_n2(x, h, s):
    N = x.size
    offs = (np.arange(s)+0.5)/s*h - 0.5*h
    xf = (x[:, None]+offs[None, :]).ravel()
    out = np.empty((N, N))
    for j0 in range(0, N, 64):
        j1 = min(N, j0+64)
        yf = (x[j0:j1, None]+offs[None, :]).ravel()
        X, Y = np.meshgrid(xf, yf)
        r = np.hypot(X, Y)
        n = np.where(r <= A, N1, np.where(r <= A+T, N2, N1))
        out[j0:j1, :] = (n**2).reshape(j1-j0, s, N, s).mean(axis=(1, 3))
    return out
def run(L, h=0.25, k=10, s=8):
    t0 = time.time()
    nh = int(round(L/h)); N = 2*nh+1
    x = (np.arange(N)-(N-1)/2)*h
    c = cell_n2(x, h, s)
    M = N-2
    Tm = sp.diags([np.ones(M-1), -2*np.ones(M), np.ones(M-1)], [-1, 0, 1], format="csr")/h**2
    I = sp.identity(M, format="csr")
    P = (sp.kron(I, Tm)+sp.kron(Tm, I)+sp.diags(K0**2*c[1:-1, 1:-1].ravel())).tocsc()
    vals, vecs = sla.eigsh(P, k=k, sigma=(K0*SIG)**2, which="LM")
    o = np.argsort(vals)[::-1]; vals = vals[o]; vecs = vecs[:, o]
    neff = np.sqrt(vals)/K0
    X, Y = np.meshgrid(x[1:-1], x[1:-1])
    R = np.hypot(X, Y).ravel()
    res = []
    for m in range(k):
        p2 = vecs[:, m]**2
        res.append(dict(neff=float(neff[m]), P12=float(p2[R <= 12].sum()/p2.sum())))
    sel = [m for m in range(k) if res[m]["P12"] >= 0.5 and abs(res[m]["neff"]-SIG) <= 0.002]
    out = dict(L=L, h=h, s_sub=s, unknowns=M*M, modes=res, sel=(sel[0] if sel else None),
               n_core=(res[sel[0]]["neff"] if sel else None), t=time.time()-t0)
    return out
if __name__ == "__main__":
    L = float(sys.argv[1]); k = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    o = run(L, k=k)
    json.dump(o, open(f"v8_f31_L{L:g}.json", "w"), indent=1)
    print(L, o["unknowns"], o["n_core"], o["sel"], [round(m["P12"], 3) for m in o["modes"][:4]], round(o["t"], 1), flush=True)
