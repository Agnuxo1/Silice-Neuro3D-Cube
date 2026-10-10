"""V8 independiente: G3 (acoplador de dos nucleos, d) con BPM propio y comparacion con supermodos FD. Uso: python -B v8_g3.py d dz [zend_mm]"""
import sys, json, time
import numpy as np
import scipy.sparse as sp, scipy.sparse.linalg as sla, scipy.fft as sf
LAM = 1.55; K0 = 2*np.pi/LAM; A = 6.0; N1 = 1.444; N2 = 1.439; NREF = N1
W = 40.0; H = 0.2
def n2map(x, h, centers, s=16):
    N = x.size; offs = (np.arange(s)+0.5)/s*h-0.5*h
    xf = (x[:, None]+offs[None, :]).ravel(); out = np.empty((N, N))
    for j0 in range(0, N, 50):
        j1 = min(N, j0+50); yf = (x[j0:j1, None]+offs[None, :]).ravel()
        X, Y = np.meshgrid(xf, yf); ins = np.zeros(X.shape, bool)
        for xc in centers: ins |= np.hypot(X-xc, Y) <= A
        out[j0:j1, :] = (np.where(ins, N1, N2)**2).reshape(j1-j0, s, N, s).mean(axis=(1, 3))
    return out   # [iy, ix]
def fd_modes(n2, h, k, nsig):
    N = n2.shape[0]; M = N-2
    Tm = sp.diags([np.ones(M-1), -2*np.ones(M), np.ones(M-1)], [-1, 0, 1], format="csr")/h**2
    I = sp.identity(M, format="csr")
    P = (sp.kron(I, Tm)+sp.kron(Tm, I)+sp.diags(K0**2*n2[1:-1, 1:-1].ravel())).tocsc()
    vals, vecs = sla.eigsh(P, k=k, sigma=(K0*nsig)**2, which="LM")
    o = np.argsort(vals)[::-1]; vals = vals[o]; vecs = vecs[:, o]
    ps = []
    for m in range(k):
        f = np.zeros((N, N)); f[1:-1, 1:-1] = vecs[:, m].reshape(M, M); f /= np.sqrt((f**2).sum()*h*h); ps.append(f)
    return np.sqrt(vals)/K0, ps
def main(d, dz, zend_mm=None):
    t0 = time.time(); M = int(round(W/H)); x = (np.arange(2*M+1)-M)*H
    # supermodos (dos nucleos)
    n2c = n2map(x, H, [-d/2, d/2])
    nv, pv = fd_modes(n2c, H, 4, 1.44219)
    beta = K0*nv
    # los dos modos guiados mas altos con simetria par/impar: tomar los dos de mayor n_eff
    dbeta = beta[0]-beta[1]
    Lc_super = np.pi/dbeta
    # modo de un nucleo en -d/2
    n2L = n2map(x, H, [-d/2]); n2R = n2map(x, H, [d/2])
    nL, pL = fd_modes(n2L, H, 1, 1.44219); nR, pR = fd_modes(n2R, H, 1, 1.44219)
    psiL = pL[0].T.copy(); psiR = pR[0].T.copy()    # [ix,iy]
    n2b = n2c.T.copy()
    X, Y = np.meshgrid(x, x, indexing="ij"); s = np.maximum(abs(X), abs(Y))
    t = np.clip((s-28.0)/12.0, 0, 1); G = 2*K0*NREF*0.5*t*t
    V = K0**2*(n2b-NREF**2)-1j*G
    k = 2*np.pi*np.fft.fftfreq(2*M+1, d=H); K2 = k[:, None]**2+k[None, :]**2
    D = np.exp(1j*dz*K2/(2*K0*NREF)); Pp = np.exp(-1j*dz*V/(4*K0*NREF))
    zend = (zend_mm*1000 if zend_mm else 1.1*Lc_super)
    ns = int(round(zend/dz)); Ak = psiL.astype(complex); P0 = (abs(Ak)**2).sum()*H*H
    nR2 = (psiR**2).sum()*H*H
    z = np.zeros(ns+1); P2 = np.zeros(ns+1)
    P2[0] = abs((psiR*Ak).sum()*H*H)**2/(nR2*P0)
    for i in range(1, ns+1):
        Ak = Pp*Ak; Ak = sf.ifft2(D*sf.fft2(Ak, workers=1), workers=1); Ak = Pp*Ak
        z[i] = i*dz; P2[i] = abs((psiR*Ak).sum()*H*H)**2/(nR2*P0)
    kk = None
    for i in range(1, ns):
        if P2[i] > 0.05 and P2[i] >= P2[i-1] and P2[i] > P2[i+1]:
            yl, y0, yr = P2[i-1], P2[i], P2[i+1]; den = yl-2*y0+yr; off = 0.5*(yl-yr)/den if den else 0.0
            kk = (z[i]+off*dz, y0-0.25*(yl-yr)*off); break
    loss = 1-(abs(Ak)**2).sum()*H*H/P0
    out = dict(d=d, dz=dz, Lc_super_mm=Lc_super/1000, nv=[float(v) for v in nv], zmax_mm=(kk[0]/1000 if kk else None),
               P2max=(float(kk[1]) if kk else None), err_rel_vs_Lc_super=((kk[0]-Lc_super)/Lc_super if kk else None),
               err_rel_vs_Lc_r2=((kk[0]/1000-{14: 3.3305026377661915, 16: 7.735855798530757}[int(d)])/{14: 3.3305026377661915, 16: 7.735855798530757}[int(d)] if kk else None),
               loss_end=float(loss), zend_mm=zend/1000, t=time.time()-t0)
    json.dump(out, open(f"v8_g3_d{int(d)}_dz{dz:g}.json", "w"), indent=1)
    print(out, flush=True)
if __name__ == "__main__":
    main(float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]) if len(sys.argv) > 3 else None)
