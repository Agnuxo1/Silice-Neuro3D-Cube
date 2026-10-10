"""V1-B: BPM propio (split-step Strang, numpy.fft), independiente de bpm.py. Ver CONTRATO-V1.md.
Uso: python -B v1_b.py h dz [zmax]"""
import os
os.environ["OMP_NUM_THREADS"] = "1"
import json, sys, time
import numpy as np
from scipy.special import j0, j1, k0 as bk0, k1 as bk1
from scipy.optimize import brentq

LAM, A, N1, N2 = 1.55, 6.0, 1.444, 1.439
K = 2*np.pi/LAM
NREF = N1
V = K*A*np.sqrt(N1**2-N2**2)
f = lambda u: u*j1(u)/j0(u) - np.sqrt(V*V-u*u)*bk1(np.sqrt(V*V-u*u))/bk0(np.sqrt(V*V-u*u))
U = brentq(f, 1e-3, 2.4048, xtol=1e-15, rtol=1e-15)
W = np.sqrt(V*V-U*U)
NEFF = np.sqrt(N1**2-(U/(K*A))**2)
NPAR = NREF+(NEFF**2-NREF**2)/(2*NREF)

def run(h, dz, zmax=1000.0, rec_every=1):
    M = int(round(40.0/h)); N = 2*M+1
    x = (np.arange(N)-M)*h
    X, Y = np.meshgrid(x, x, indexing="ij")
    # n^2 promediado por celda 16x16
    s = 16
    off = ((np.arange(s)+0.5)/s-0.5)*h
    acc = np.zeros((N, N))
    for ox in off:
        for oy in off:
            acc += np.where(np.hypot(X+ox, Y+oy) <= A, N1**2, N2**2)
    n2 = acc/(s*s)
    r = np.hypot(X, Y)
    E0 = np.where(r <= A, j0(U*np.minimum(r, A)/A)/j0(U), bk0(W*np.maximum(r, A)/A)/bk0(W)).astype(complex)
    S = np.maximum(np.abs(X), np.abs(Y))
    t = np.clip((S-28.0)/12.0, 0, 1)
    G = 2*K*NREF*0.5*t*t
    kk = 2*np.pi*np.fft.fftfreq(N, d=h)
    K2 = kk[:, None]**2+kk[None, :]**2
    D = np.exp(1j*dz*K2/(2*K*NREF))
    Pm = np.exp(-1j*dz*(K**2*(n2-NREF**2)-1j*G)/(4*K*NREF))
    nst = int(round(zmax/dz))
    Aa = E0.copy()
    h2 = h*h
    n0 = (np.abs(E0)**2).sum()*h2
    zs = [0.0]; ip = [(np.conj(E0)*Aa).sum()*h2]; pw = [n0]
    for k in range(1, nst+1):
        Aa = Pm*Aa
        Aa = np.fft.ifft2(D*np.fft.fft2(Aa))
        Aa = Pm*Aa
        if k % rec_every == 0:
            zs.append(k*dz); ip.append((np.conj(E0)*Aa).sum()*h2); pw.append((np.abs(Aa)**2).sum()*h2)
    zs = np.array(zs); ip = np.array(ip); pw = np.array(pw)
    ph = np.unwrap(np.angle(ip))
    ne = NREF-ph/(K*np.maximum(zs, 1e-30)); ne[0] = np.nan
    ov2 = np.abs(ip)**2/(n0*pw)
    # pendiente entre 500 y 1000
    i5 = np.argmin(abs(zs-500)); i1 = np.argmin(abs(zs-zmax))
    slope = NREF-(ph[i1]-ph[i5])/(K*(zs[i1]-zs[i5]))
    return dict(h=h, dz=dz, zmax=zmax, N=N, neff_impl=float(ne[i1]), overlap2=float(ov2[i1]),
                loss=float(1-pw[i1]/pw[0]), neff_slope_500_end=float(slope),
                neff_ref=float(NEFF), neff_par=float(NPAR)), zs, ne, ov2, pw

if __name__ == "__main__":
    h = float(sys.argv[1]); dz = float(sys.argv[2]); zmax = float(sys.argv[3]) if len(sys.argv) > 3 else 1000.0
    t0 = time.time()
    res, zs, ne, ov2, pw = run(h, dz, zmax, rec_every=max(1, int(round(5.0/dz))))
    res["tiempo_s"] = time.time()-t0
    print(json.dumps(res), flush=True)
    json.dump(res, open(f"v1_b_h{h:g}_dz{dz:g}.json", "w"), indent=1)
