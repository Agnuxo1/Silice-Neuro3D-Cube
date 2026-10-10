"""FD propio (no importa solver2d) para supermodos: kappa = k0 (n_par - n_imp)/2. Barrido de h, s_sub, centros fuera de nodo."""
import json, sys, time, numpy as np
import scipy.sparse as sp, scipy.sparse.linalg as sla
sys.dont_write_bytecode = True
LAM, A, N1, N2 = 1.55, 6.0, 1.444, 1.439
k0 = 2*np.pi/LAM
KMOD = {14.0: 0.000471258390313316, 16.0: 0.00020308102495955916, 20.0: 3.8495830330116794e-05}  # de v_kappa_modelo (dblquad propio coincide a 1e-13)

def n2map(d, h, L, s, xshift=0.0):
    nh = int(round(L/h)); N = 2*nh+1
    x = (np.arange(N)-nh)*h
    sub = (np.arange(s)+0.5)/s*h - 0.5*h
    acc = np.zeros((N, N))
    # acumula por sub-posicion (bucle sobre s x s para ahorrar memoria)
    X0, Y0 = np.meshgrid(x, x, indexing="ij")  # [ix, iy]
    for a in range(s):
        for b in range(s):
            X = X0+sub[a]; Y = Y0+sub[b]
            inside = (np.hypot(X+d/2+xshift, Y) <= A) | (np.hypot(X-d/2+xshift, Y) <= A)
            acc += np.where(inside, N1**2, N2**2)
    return acc/(s*s), N

def supermodes(d, h, L, s, xshift=0.0):
    t0 = time.time()
    n2, N = n2map(d, h, L, s, xshift)
    M = N-2; ni = n2[1:-1, 1:-1]
    T = sp.diags([np.ones(M-1), -2*np.ones(M), np.ones(M-1)], [-1, 0, 1], format="csr")/h**2
    I = sp.identity(M, format="csr")
    P = (sp.kron(I, T)+sp.kron(T, I)+sp.diags(k0**2*ni.ravel())).tocsc()
    sigma = k0**2*N1**2*1.0005
    vals, vecs = sla.eigsh(P, k=2, sigma=sigma, which="LM")
    o = np.argsort(vals)[::-1]; vals = vals[o]
    neff = np.sqrt(vals)/k0
    # paridad en x (indice 0 del array = x): par si psi(x)=psi(-x)
    par = []
    for m in range(2):
        v = vecs[:, o[m]].reshape(M, M)   # [ix, iy]
        par.append(float(np.max(np.abs(v-v[::-1, :]))/np.max(np.abs(v))))  # error de paridad par
    return neff, par, time.time()-t0

if __name__ == "__main__":
    out = []
    cases = []
    for d in (14.0, 16.0, 20.0):
        for h, s in ((0.2, 16), (0.15, 16), (0.1, 16), (0.2, 4), (0.2, 1)):
            cases.append((d, h, 40.0, s, 0.0))
        cases.append((d, 0.2, 40.0, 16, 0.07))   # centros desplazados 0.07 um respecto de nodos (rompe simetria x->-x del dominio? no: dominio simetrico, estructura desplazada)
    for d, h, L, s, xs in cases:
        neff, par, dt = supermodes(d, h, L, s, xs)
        # modo par = el de mayor neff si el primer modo tiene paridad par
        dn = neff[0]-neff[1]
        kap = k0*dn/2
        rec = {"d": d, "h": h, "L": L, "s_sub": s, "xshift": xs, "neff0": neff[0], "neff1": neff[1],
               "parity_err_even_mode0": par[0], "parity_err_even_mode1": par[1],
               "kappa_FD": kap, "kappa_model": KMOD[d], "ratio": kap/KMOD[d], "time_s": round(dt, 1)}
        out.append(rec); print(rec, flush=True)
        json.dump(out, open("v_fd_propio.json", "w"), indent=1)
