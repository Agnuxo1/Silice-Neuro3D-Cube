"""BPM propio (split-step Strang, Fourier) para el acoplador de dos nucleos. No importa bpm.py ni solver2d.
Modos de un nucleo: FD propio con la misma malla (h=0.2, N=405). Compara kappa ajustado con kappa_FD de G1."""
import json, sys, time, numpy as np
import scipy.fft as sf, scipy.sparse as sp, scipy.sparse.linalg as sla
from scipy.optimize import least_squares
sys.dont_write_bytecode = True
LAM, A, N1, N2 = 1.55, 6.0, 1.444, 1.439
k0 = 2*np.pi/LAM
H = 0.2; NH = 202; N = 2*NH+1; X = (np.arange(N)-NH)*H    # semilado 40.4
KFD = {14.0: 0.0004716394183216887, 16.0: 0.00020305398235231223, 20.0: 3.851257119356343e-05}   # kappa_FD de G1 (h=0.125)

def n2_of(centers, s=8):
    sub = (np.arange(s)+0.5)/s*H - 0.5*H
    acc = np.zeros((N, N)); X0, Y0 = np.meshgrid(X, X, indexing="ij")
    for a in range(s):
        for b in range(s):
            xx = X0+sub[a]; yy = Y0+sub[b]
            ins = np.zeros((N, N), bool)
            for c in centers: ins |= np.hypot(xx-c, yy) <= A
            acc += np.where(ins, N1**2, N2**2)
    return acc/(s*s)

def mode(n2):
    M = N-2; ni = n2[1:-1, 1:-1]
    T = sp.diags([np.ones(M-1), -2*np.ones(M), np.ones(M-1)], [-1, 0, 1], format="csr")/H**2
    I = sp.identity(M, format="csr")
    P = (sp.kron(I, T)+sp.kron(T, I)+sp.diags(k0**2*ni.ravel())).tocsc()
    vals, vecs = sla.eigsh(P, k=1, sigma=k0**2*N1**2*1.0005, which="LM")
    f = np.zeros((N, N)); f[1:-1, 1:-1] = vecs[:, 0].reshape(M, M)
    f /= np.sqrt(np.sum(f*f)*H*H)
    if f.flat[np.argmax(np.abs(f))] < 0: f = -f
    return f, np.sqrt(vals[0])/k0

def cap():
    Xg, Yg = np.meshgrid(X, X, indexing="ij")
    s = np.maximum(abs(Xg), abs(Yg)); t = np.clip((s-28.0)/(X.max()-28.0), 0, 1)
    return 2*k0*N1*0.5*t*t

def propagate(n2, E0, psiR, dz, z_end, use_cap=True):
    nref = N1
    V = k0**2*(n2-nref**2) - (1j*cap() if use_cap else 0)
    kx = 2*np.pi*np.fft.fftfreq(N, d=H); K2 = kx[:, None]**2+kx[None, :]**2
    D = np.exp(1j*dz*K2/(2*k0*nref)); Ph = np.exp(-1j*dz*V/(4*k0*nref))
    nsteps = int(round(z_end/dz)); A_ = E0.astype(complex)
    n0 = np.sum(E0*E0)*H*H; nR = np.sum(psiR*psiR)*H*H
    z = np.zeros(nsteps+1); p2 = np.zeros(nsteps+1); pt = np.zeros(nsteps+1)
    p2[0] = abs(np.sum(psiR*A_)*H*H)**2/(nR*n0); pt[0] = 1.0
    for k in range(1, nsteps+1):
        A_ = Ph*A_
        A_ = sf.ifft2(D*sf.fft2(A_, workers=1), workers=1)
        A_ = Ph*A_
        z[k] = k*dz
        p2[k] = abs(np.sum(psiR*A_)*H*H)**2/(nR*n0)
        pt[k] = np.sum(abs(A_)**2)*H*H/n0
    return z, p2, pt

def analyze(z, p2, pt, kfd):
    lc = np.pi/(2*kfd)
    # primer maximo local con P2>0.05, refinado por parabola
    kmax = None
    for k in range(1, len(p2)-1):
        if p2[k] > 0.05 and p2[k] >= p2[k-1] and p2[k] > p2[k+1]: kmax = k; break
    res = {"Lc_FD_um": lc}
    if kmax is not None:
        y0, y1, y2 = p2[kmax-1], p2[kmax], p2[kmax+1]
        den = y0-2*y1+y2; off = 0.5*(y0-y2)/den if den != 0 else 0.0
        zm = z[kmax]+off*(z[1]-z[0])
        res.update({"z_max_um": float(zm), "P2_max": float(y1), "loss_at_zmax": float(1-pt[kmax]), "rel_dev_Lc": float(abs(zm-lc)/lc)})
    # ajuste P2 = a sin^2(kappa z + 0) hasta 1.15 Lc
    m = z <= 1.15*lc
    r = least_squares(lambda q: q[0]*np.sin(q[1]*z[m])**2 - p2[m], [1.0, kfd], x_scale=[1, kfd])
    res.update({"fit_amp": float(r.x[0]), "fit_kappa_per_um": float(r.x[1]), "fit_rel_vs_kFD": float(r.x[1]/kfd-1), "fit_rms": float(np.sqrt(np.mean(r.fun**2)))})
    return res

if __name__ == "__main__":
    plan = [(14.0, 5.0), (14.0, 2.0), (14.0, 0.5), (14.0, 10.0), (16.0, 5.0), (20.0, 5.0), (20.0, 10.0), (14.0, 1.0), (16.0, 1.0), (20.0, 1.0)]
    only = sys.argv[1:] 
    out = {}
    modes = {}
    for d, dz in plan:
        if only and f"{d}_{dz}" not in only: continue
        t0 = time.time()
        if d not in modes:
            n2 = n2_of([-d/2, d/2]); fl, nl = mode(n2_of([-d/2])); fr, nr = mode(n2_of([d/2])); modes[d] = (n2, fl, fr)
        n2, fl, fr = modes[d]
        lc = np.pi/(2*KFD[d]); z_end = 10000.0 if d == 20.0 else 1.25*lc
        z_end = np.ceil(z_end/dz)*dz
        z, p2, pt = propagate(n2, fl, fr, dz, z_end)
        res = analyze(z, p2, pt, KFD[d])
        i10 = int(np.argmin(abs(z-10000.0))) if z[-1] >= 10000-dz else None
        if i10 is not None: res["P2_at_10mm"] = float(p2[i10]); res["z_at_10mm"] = float(z[i10]); res["P_total_10mm"] = float(pt[i10])
        res.update({"d": d, "dz": dz, "time_s": round(time.time()-t0, 1), "steps": len(z)-1})
        out[f"{d}_{dz}"] = res; print(res, flush=True)
        np.savez(f"v_curva_d{d}_dz{dz}.npz", z=z[::max(1, int(round(1.0/dz)))], p2=p2[::max(1, int(round(1.0/dz)))], pt=pt[::max(1, int(round(1.0/dz)))])
        json.dump(out, open(f"v_bpm_propio_{'_'.join(only) if only else 'all'}.json", "w"), indent=1)
