"""Verificacion independiente de kappa_modelo(d): implementacion propia (no importa acoplo_paralelo salvo para comparar al final)."""
import json, sys, numpy as np
sys.dont_write_bytecode = True
from scipy.special import jv, kv
from scipy.optimize import root_scalar
from scipy.integrate import quad, dblquad

LAM, A, N1, N2 = 1.55, 6.0, 1.444, 1.439
k0 = 2*np.pi/LAM
V = k0*A*np.sqrt(N1**2-N2**2)
def f(u):
    w = np.sqrt(V*V-u*u)
    return u*jv(1,u)/jv(0,u) - w*kv(1,w)/kv(0,w)
us = np.linspace(0.2, V-1e-3, 4000); fs = [f(u) for u in us]
br = [(us[i], us[i+1]) for i in range(len(us)-1) if fs[i]*fs[i+1] < 0 and abs(fs[i])<50 and abs(fs[i+1])<50]
u = root_scalar(f, bracket=br[0], xtol=1e-14, rtol=1e-14).root
w = np.sqrt(V*V-u*u)
beta = np.sqrt((k0*N1)**2-(u/A)**2)
def psi(r):
    r = np.asarray(r, float)
    return np.where(r <= A, jv(0,u*r/A)/jv(0,u), kv(0,w*np.maximum(r,1e-12)/A)/kv(0,w))
nr, _ = quad(lambda r: 2*np.pi*r*float(psi(r))**2, 0, A, epsabs=1e-13, epsrel=1e-13)
nc, _ = quad(lambda r: 2*np.pi*r*float(psi(r))**2, A, 40*A, epsabs=1e-13, epsrel=1e-13, limit=400)
Norm = nr+nc
print("V,u,w,beta,neff", V, u, w, beta, beta/k0, "bracketsfound", len(br), "Norm", Norm)

def overlap_cart(d, hh):
    # rejilla cartesiana de punto medio sobre el disco del nucleo 2 (centrado en x=d): psi1 centrado en 0
    n = int(round(2*A/hh)); xs = (np.arange(n)+0.5)*hh - A
    X, Y = np.meshgrid(xs, xs, indexing="ij")
    m = np.hypot(X, Y) <= A
    r1 = np.hypot(X+d, Y)   # distancia al centro de la guia 1 (a -d respecto del centro 2)
    r2 = np.hypot(X, Y)
    return float(np.sum(psi(r1)[m]*psi(r2)[m])*hh*hh/Norm)
def overlap_dbl(d):
    g = lambda r, ph: float(psi(np.hypot(d+r*np.cos(ph), r*np.sin(ph))))*float(psi(r))*r
    val, err = dblquad(g, 0, 2*np.pi, 0, A, epsabs=1e-13, epsrel=1e-11)
    return val/Norm
def kappa(I): return (k0**2/(2*beta))*(N1**2-N2**2)*I
out = {"V": V, "U": u, "W": w, "beta": beta, "Norm": Norm, "d": {}}
sys.path.insert(0, "../acoplo_claude")
import acoplo_paralelo as AP
for d in (14.0, 16.0, 20.0):
    Ic1 = overlap_cart(d, 0.02); Ic2 = overlap_cart(d, 0.01); Id = overlap_dbl(d)
    k_c = kappa(Ic2); k_d = kappa(Id); k_ap = float(AP.kappa(d))
    out["d"][str(d)] = {"I_cart_0.02": Ic1, "I_cart_0.01": Ic2, "I_dblquad": Id,
        "kappa_cart_per_um": k_c, "kappa_dbl_per_um": k_d, "kappa_AP_per_um": k_ap,
        "rel_dbl_vs_AP": abs(k_d/k_ap-1), "rel_cart_vs_AP": abs(k_c/k_ap-1),
        "kappa_with_literal_factor2": 2*k_d}
    print(d, out["d"][str(d)], flush=True)
json.dump(out, open("v_kappa_modelo.json","w"), indent=1)
