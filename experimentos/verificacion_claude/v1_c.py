"""V1-C: re-ejecucion de C1 de radial2 (solo lectura de radial2.py) + raices cerradas propias. Ver CONTRATO-V1.md."""
import os, sys, json, time
os.environ["OMP_NUM_THREADS"] = "1"
sys.dont_write_bytecode = True
sys.path.insert(0, "D:/PROJECTS/.cognition/audit/silice-origin-main/experimentos/radial2_claude")
import warnings; warnings.filterwarnings("ignore")
import numpy as np
from scipy.special import jv, kv
from scipy.optimize import brentq
import radial2 as R

REF = json.load(open("D:/PROJECTS/.cognition/audit/silice-origin-main/experimentos/radial2_claude/resultados_radial2.json"))
a = 6e-6
LAM, N0 = 1550e-9, 1.444
k0 = 2*np.pi/LAM

def my_roots_E(Delta, l):
    """Raices de la ecuacion LP_lm: U J_{l-1}(U) K_l(W) + W K_{l-1}(W) J_l(U) = 0 (forma generica, propia)."""
    n1 = N0+Delta
    Vn = a*k0*np.sqrt(n1**2-N0**2)
    F = lambda u: u*jv(l-1, u)*kv(l, np.sqrt(Vn**2-u**2))+np.sqrt(Vn**2-u**2)*kv(l-1, np.sqrt(Vn**2-u**2))*jv(l, u)
    us = np.linspace(1e-6, Vn*(1-1e-9), 20001)
    vals = F(us)
    out = []
    for i in range(len(us)-1):
        if vals[i]*vals[i+1] < 0:
            u = brentq(F, us[i], us[i+1], xtol=1e-16, rtol=1e-15)
            # descartar polos (J_l(u)=0 con W-termino finito no son polos aqui: F es entera en u)
            out.append(np.sqrt(n1**2-(u/(k0*a))**2))
    return sorted(out, reverse=True)

def my_roots_P(Delta, l):
    VP = a*k0*np.sqrt(2*N0*Delta)
    F = lambda u: u*jv(l-1, u)*kv(l, np.sqrt(VP**2-u**2))+np.sqrt(VP**2-u**2)*kv(l-1, np.sqrt(VP**2-u**2))*jv(l, u)
    us = np.linspace(1e-6, VP*(1-1e-9), 20001)
    vals = F(us)
    out = []
    for i in range(len(us)-1):
        if vals[i]*vals[i+1] < 0:
            u = brentq(F, us[i], us[i+1], xtol=1e-16, rtol=1e-15)
            w = np.sqrt(VP**2-u**2)
            out.append(N0+w**2/(2*k0**2*N0*a**2))
    return sorted(out, reverse=True)

H0 = 0.005e-6
res = {"casos": []}
t0 = time.time()
maxdiff_json = 0.0
for ci, Delta in enumerate((0.003, 0.005, 0.010)):
    n1, n2 = N0+Delta, N0
    case = {"Delta": Delta}
    for l in (0, 1):
        ref = REF["C1"][ci]["modes"][f"l{l}"]
        closed = sorted(R.closed_roots(a, n1, n2, l), reverse=True)
        xsE = np.linspace(N0+1e-9, n1-1e-9, 400)
        rE = sorted(R.real_roots(xsE, [(0.0, a, Delta)], l, "E", H0), reverse=True)
        gsP = np.linspace(1e-9, R.K0*Delta*(1-1e-9), 400)
        rP = sorted([N0+g/R.K0 for g in R.real_roots(gsP, [(0.0, a, Delta)], l, "P", H0)], reverse=True)
        myE = my_roots_E(Delta, l); myP = my_roots_P(Delta, l)
        d = {"n_roots": dict(closed=len(closed), E=len(rE), P=len(rP), myE=len(myE), myP=len(myP)),
             "ref_counts": dict(closed=ref["n_closed"], E=ref["n_E"], P=ref["n_P"])}
        def mx(x, y): return float(max(abs(np.array(x)-np.array(y)))) if (len(x) == len(y) and len(x) > 0) else (0.0 if len(x) == len(y) else float("nan"))
        d["rerun_vs_json"] = dict(closed=mx(closed, ref["closed_neff"]), E=mx(rE, ref["solver_E_neff"]), P=mx(rP, ref["solver_P_neff"]))
        d["mi_cerrada_vs_su_cerrada"] = mx(myE, ref["closed_neff"])
        d["solverE_vs_mi_cerrada"] = mx(rE, myE)
        d["solverP_vs_mi_cerrada_P"] = mx(rP, myP)
        d["errP_over_Delta_vs_cerrada_E_mia"] = [abs(x-y)/Delta for x, y in zip(rP, myE)]
        for v in d["rerun_vs_json"].values():
            if np.isfinite(v): maxdiff_json = max(maxdiff_json, v)
        case[f"l{l}"] = d
        print(Delta, l, json.dumps(d), flush=True)
    res["casos"].append(case)
res["max_rerun_vs_json"] = maxdiff_json
# VC1d: orden RK4 (E, Delta=0.010, LP01), referencia = mi cerrada
Delta = 0.010; n1 = N0+Delta
ref_ne = my_roots_E(Delta, 0)[0]
ords = {}
errs = []
hs = [100e-9, 50e-9, 25e-9, 12.5e-9]
for h in hs:
    xs = np.linspace(N0+1e-9, n1-1e-9, 400)
    rts = sorted(R.real_roots(xs, [(0.0, a, Delta)], 0, "E", h), reverse=True)
    errs.append(abs(rts[0]-ref_ne))
ords["h_nm"] = [h*1e9 for h in hs]; ords["err"] = errs
ords["orden_obs"] = [float(np.log2(errs[i]/errs[i+1])) if errs[i+1] > 0 and errs[i] > 0 else None for i in range(len(errs)-1)]
res["VC1d"] = ords
print("VC1d", json.dumps(ords), flush=True)
res["tiempo_s"] = time.time()-t0
json.dump(res, open("v1_c_resultados.json", "w"), indent=1, default=float)
