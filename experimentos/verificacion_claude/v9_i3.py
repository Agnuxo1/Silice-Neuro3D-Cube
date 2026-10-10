"""V9 verificacion independiente de I3 (curvas r3). Implementacion propia (no importa curvas_r3 ni solver2d).
Uso: OMP_NUM_THREADS=1 python -B v9_i3.py L_um [h_um]
Modelo: lam=1.55, a=6, n1=1.444, n2=1.439, n_eq = n_xy (1+X/R), Dirichlet, 5 puntos, promedio subpixel s=8.
Hace: recto; cadena 50,30,20,15,10 por solape (S potencia); ruta directa recto->R=10 con sigma en n_recto;
      lista de los 12 modos en R=10 con su solape con el recto; P_out.
"""
import os, sys, json, math, time
os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla
import scipy.special as sps
from scipy.optimize import brentq

L = float(sys.argv[1]); h = float(sys.argv[2]) if len(sys.argv) > 2 else 0.25
LAM, A, N1, N2, SS = 1.55, 6.0, 1.444, 1.439, 8
K0 = 2 * math.pi / LAM
HERE = os.path.dirname(os.path.abspath(__file__))
T0 = time.time()
def log(*a):
    print(*a, flush=True)

# analitica LP01 (step-index, escalar): U J1(U) K0(W) = W K1(W) J0(U)
V = K0 * A * math.sqrt(N1**2 - N2**2)
f = lambda U: U * sps.j1(U) * sps.k0(math.sqrt(V**2 - U**2)) - math.sqrt(V**2 - U**2) * sps.k1(math.sqrt(V**2 - U**2)) * sps.j0(U)
Us = np.linspace(1e-6, V - 1e-6, 4000); fv = np.array([f(u) for u in Us])
i = int(np.where(np.sign(fv[:-1]) != np.sign(fv[1:]))[0][0])
U = brentq(f, Us[i], Us[i + 1], xtol=1e-15, rtol=1e-15)
N_AN = math.sqrt(N1**2 - (U / (K0 * A))**2)

nh = int(round(L / h)); N = 2 * nh + 1
x = (np.arange(N) - (N - 1) / 2) * h
offs = ((np.arange(SS) + 0.5) / SS - 0.5) * h
xf = (x[:, None] + offs[None, :]).ravel()

def cell_n2(R_mm):
    out = np.empty((N, N))
    for j0 in range(0, N, 32):
        j1 = min(N, j0 + 32)
        yf = (x[j0:j1, None] + offs[None, :]).ravel()
        X, Y = np.meshgrid(xf, yf)
        n = np.where(np.hypot(X, Y) < A, N1, N2)
        if R_mm is not None:
            n = n * (1 + X / (1000.0 * R_mm))
        out[j0:j1] = (n**2).reshape(j1 - j0, SS, N, SS).mean(axis=(1, 3))
    return out

M = N - 2
T = sp.diags([np.ones(M - 1), -2 * np.ones(M), np.ones(M - 1)], [-1, 0, 1], format="csr") / h**2
Id = sp.identity(M, format="csr")
LAP = (sp.kron(Id, T) + sp.kron(T, Id)).tocsr()
XX = np.tile(x[None, :], (N, 1)); YY = np.tile(x[:, None], (1, N)); RR = np.hypot(XX, YY)

def modes(cn2, sigma, k=12):
    P = (LAP + sp.diags(K0**2 * cn2[1:-1, 1:-1].ravel())).tocsc()
    vals, vecs = sla.eigsh(P, k=k, sigma=sigma, which="LM")
    out = []
    for m in range(k):
        v = np.real(vecs[:, m]); b2 = float(np.real(vals[m]))
        res = float(np.linalg.norm(P @ v - b2 * v) / (abs(b2) * np.linalg.norm(v)))
        full = np.zeros((N, N)); full[1:-1, 1:-1] = v.reshape(M, M)
        full /= math.sqrt(float((full**2).sum()) * h * h)
        out.append(dict(neff=math.sqrt(b2) / K0, psi=full, res=res))
    return out

S = lambda a, b: float((a * b).sum() * h * h) ** 2

res = dict(L=L, h=h, N=N, n_an=N_AN)
c0 = cell_n2(None)
m0 = modes(c0, (K0 * N_AN)**2, 6)
b0 = min(m0, key=lambda m: abs(m["neff"] - N_AN))
psi_rec = b0["psi"]; res["recto_neff"] = b0["neff"]; res["recto_err_an"] = b0["neff"] - N_AN
log(f"L={L} N={N} recto neff={b0['neff']:.12f} err_an={b0['neff']-N_AN:+.3e} t={time.time()-T0:.0f}s")

prev_neff, prev_psi = b0["neff"], psi_rec
chain = {}
for R in (() if (len(sys.argv) > 3 and sys.argv[3] == "direct") else (50.0, 30.0, 20.0, 15.0, 10.0)):
    c = cell_n2(R); ms = modes(c, (K0 * prev_neff)**2)
    Sp = [S(m["psi"], prev_psi) for m in ms]; k = int(np.argmax(Sp)); m = ms[k]
    Pw = m["psi"]**2 * h * h; xt = 1000 * R * (m["neff"] / N2 - 1)
    srt = sorted(Sp, reverse=True)
    chain[str(R)] = dict(neff=m["neff"], S_prev=Sp[k], S_prev_2nd=srt[1], S_rec=S(m["psi"], psi_rec), res=m["res"],
                         P_out=float(Pw[XX > xt].sum()), x_t=xt, centroid=float((XX * Pw).sum()),
                         neff12=[mm["neff"] for mm in ms])
    prev_neff, prev_psi = m["neff"], m["psi"]
    log(f"  R={R:g} neff={m['neff']:.12f} S_prev={Sp[k]:.5f} S_rec={chain[str(R)]['S_rec']:.5f} 2nd={srt[1]:.4f} "
        f"P_out={chain[str(R)]['P_out']:.3e} t={time.time()-T0:.0f}s")
res["chain"] = chain

# ruta directa recto -> R=10 (sin cadena), sigma en el n_eff del recto; lista completa de 12 modos con solape con el recto
c = cell_n2(10.0)
SIG = float(sys.argv[4]) if len(sys.argv) > 4 else b0["neff"]
ms = modes(c, (K0 * SIG)**2)
lst = sorted([dict(neff=m["neff"], S_rec=S(m["psi"], psi_rec), res=m["res"]) for m in ms], key=lambda d: -d["S_rec"])
res["directo_R10"] = lst
log("  directo R=10 (sigma=n_recto): top por S_rec:", [(round(d["neff"], 9), round(d["S_rec"], 4)) for d in lst[:4]])
res["sum_S_rec_12"] = sum(d["S_rec"] for d in lst)
res["runtime_s"] = time.time() - T0
json.dump(res, open(os.path.join(HERE, f"v9_i3_L{int(L)}_h{h}" + ("_direct" if (len(sys.argv) > 3 and sys.argv[3] == "direct") else "") + ("_sig" + sys.argv[4] if len(sys.argv) > 4 else "") + ".json"), "w"), indent=1)
log("done", res["runtime_s"])
