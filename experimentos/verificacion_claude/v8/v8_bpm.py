"""V8 independiente: BPM escalar paraxial (Strang) con CAP, codigo propio. Solo CPU, 1 hilo.
Uso: python -B v8_bpm.py  -> v8_bpm.json
"""
import json, time, sys
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla
import scipy.fft as sf
from scipy import special as sps
from scipy.optimize import brentq
LAM = 1.55; K0 = 2*np.pi/LAM; A = 6.0; N1 = 1.444; N2 = 1.439; NREF = N1
def cell_n2(x, h, s=16):
    N = x.size
    offs = (np.arange(s)+0.5)/s*h - 0.5*h
    xf = (x[:, None]+offs[None, :]).ravel()
    out = np.empty((N, N))
    for j0 in range(0, N, 50):
        j1 = min(N, j0+50)
        yf = (x[j0:j1, None]+offs[None, :]).ravel()
        X, Y = np.meshgrid(xf, yf)            # [iy, ix]
        n = np.where(np.hypot(X, Y) <= A, N1, N2)
        out[j0:j1, :] = (n**2).reshape(j1-j0, s, N, s).mean(axis=(1, 3))
    return out                                  # simetrico en x<->y (disco centrado), asi que no importa la orientacion
def lp01(x):
    V = K0*A*np.sqrt(N1**2-N2**2)
    f = lambda u: u*sps.j1(u)/sps.j0(u) - np.sqrt(V**2-u**2)*sps.k1(np.sqrt(V**2-u**2))/sps.k0(np.sqrt(V**2-u**2))
    u = brentq(f, 1e-6, 2.404825); w = np.sqrt(V**2-u**2)
    neff = np.sqrt(N1**2-(u/(K0*A))**2)
    X, Y = np.meshgrid(x, x, indexing="ij"); r = np.hypot(X, Y)
    psi = np.where(r <= A, sps.j0(u*np.minimum(r, A)/A)/sps.j0(u), sps.k0(w*np.maximum(r, A)/A)/sps.k0(w))
    return psi, neff, u, w, V
def fd_mode(n2, h):
    N = n2.shape[0]; M = N-2
    Tm = sp.diags([np.ones(M-1), -2*np.ones(M), np.ones(M-1)], [-1, 0, 1], format="csr")/h**2
    I = sp.identity(M, format="csr")
    P = (sp.kron(I, Tm)+sp.kron(Tm, I)+sp.diags(K0**2*n2[1:-1, 1:-1].ravel())).tocsc()
    vals, vecs = sla.eigsh(P, k=1, sigma=K0**2*n2.max(), which="LM")
    psi = np.zeros((N, N)); psi[1:-1, 1:-1] = vecs[:, 0].reshape(M, M)
    psi /= np.sqrt((psi**2).sum()*h*h)
    if psi.flat[np.argmax(np.abs(psi))] < 0: psi = -psi
    return psi, float(np.sqrt(vals[0])/K0)
def cap(x, s0, w, R0):
    X, Y = np.meshgrid(x, x, indexing="ij"); s = np.maximum(abs(X), abs(Y))
    t = np.clip((s-s0)/w, 0, 1); return 2*K0*NREF*R0*t*t
def prop(n2, E0, h, dz, zend, G, curve_every=50.0):
    N = E0.shape[0]
    V = K0**2*(n2-NREF**2) - 1j*G
    k = 2*np.pi*np.fft.fftfreq(N, d=h); K2 = k[:, None]**2+k[None, :]**2
    D = np.exp(1j*dz*K2/(2*K0*NREF)); Pp = np.exp(-1j*dz*V/(4*K0*NREF))
    Ak = E0.astype(complex).copy(); P0 = (abs(Ak)**2).sum()*h*h
    ns = int(round(zend/dz)); every = int(round(curve_every/dz)); curve = {}; umax = 0.0
    for i in range(1, ns+1):
        Ak = Pp*Ak; Ak = sf.ifft2(D*sf.fft2(Ak, workers=1), workers=1); Ak = Pp*Ak
        if i % every == 0:
            curve[int(round(i*dz))] = 1 - (abs(Ak)**2).sum()*h*h/P0
    X, Y = np.meshgrid((np.arange(N)-(N-1)//2)*h, (np.arange(N)-(N-1)//2)*h, indexing="ij")
    s = np.maximum(abs(X), abs(Y))
    Pend = (abs(Ak)**2).sum()*h*h
    return dict(loss=1-Pend/P0, curve=curve, tail28=float((abs(Ak)**2*(s > 28)).sum()*h*h/P0))
def run(W, h, s0, wcap, R0, tag, out):
    t0 = time.time()
    M = int(round(W/h)); x = (np.arange(2*M+1)-M)*h
    n2 = cell_n2(x, h)
    psi_a, neff_a, u, w, V = lp01(x)
    psi_f, neff_f = fd_mode(n2, h)
    G = cap(x, s0, wcap, R0)
    # perturbativo de primer orden: Gamma_modo = int 2R0 t^2 |psi|^2 / int |psi|^2  (tasa de potencia por um) = int G/(k0 nref) |psi|^2/int|psi|^2
    pert = {}
    for nm, ps in (("an", psi_a), ("fd", psi_f)):
        g = float((G*ps**2).sum()/(ps**2).sum()/(K0*NREF))
        pert[nm] = dict(rate_per_um=g, loss_1mm=1-np.exp(-g*1000.0))
    ov = float((psi_a*psi_f).sum()**2/((psi_a**2).sum()*(psi_f**2).sum()))
    r = dict(tag=tag, W=W, h=h, s0=s0, wcap=wcap, R0=R0, neff_an=neff_a, neff_fd=neff_f, dneff=neff_f-neff_a,
             overlap2_fd_an=ov, pert=pert, runs={})
    for nm, ps in (("an", psi_a), ("fd", psi_f)):
        for dz in DZS:
            q = prop(n2, ps, h, dz, 1000.0, G)
            r["runs"][f"{nm}_dz{dz:g}"] = q
            print(tag, nm, dz, "loss1mm=%.4e" % q["loss"], "tail28=%.3e" % q["tail28"], round(time.time()-t0, 1), flush=True)
    out[tag] = r
if __name__ == "__main__":
    mode = sys.argv[1]
    out = {}
    if mode == "base":
        DZS = [1.0, 0.5, 0.25]
        run(40.0, 0.2, 28.0, 12.0, 0.5, "base_W40", out)
        run(40.0, 0.2, 28.0, 12.0, 0.0, "nocap_W40", out)
    elif mode == "wide":
        DZS = [1.0]
        run(60.0, 0.2, 48.0, 12.0, 0.5, "wide_W60_s048", out)
    json.dump(out, open(f"v8_bpm_{mode}.json", "w"), indent=1)
