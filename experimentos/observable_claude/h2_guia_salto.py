"""Tarea H2: convergencia con h del observable original (centro) y de cobertura frente a la
integral analitica del nucleo de un LP01 de guia de salto (a=6 um, lam=1,55 um, n1=1,444, n2=1,439).

Uso: python -B h2_guia_salto.py   (salida: out/h2_guia_salto.json)
Modelo escalar, sin solver de propagacion. Solo CPU, un hilo.
"""
import os, sys, json, math, time, hashlib
os.environ["OMP_NUM_THREADS"] = "1"; os.environ["OPENBLAS_NUM_THREADS"] = "1"
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from scipy import special as sp, integrate, optimize
import observable_cobertura as oc

T0 = time.time()
a = 6e-6; lam = 1.55e-6; n1 = 1.444; n2 = 1.439; k0 = 2 * math.pi / lam
V = k0 * a * math.sqrt(n1 * n1 - n2 * n2)

# ---- referencia analitica: LP01 de guia de salto -------------------------------------
def eig(u):
    w = math.sqrt(V * V - u * u)
    return u * sp.j1(u) / sp.j0(u) - w * sp.k1(w) / sp.k0(w)

u = optimize.brentq(eig, 1e-6, 2.4048255576957727 - 1e-9, xtol=1e-15, rtol=1e-15, maxiter=500)
w = math.sqrt(V * V - u * u)
resid = abs(eig(u))
J = (sp.j1(u) / sp.j0(u)) ** 2          # J1^2/J0^2 (en el nucleo)
K = (sp.k1(w) / sp.k0(w)) ** 2          # K1^2/K0^2 (en la camisa)
Gamma = (1 + J) / (J + K)                # fraccion de potencia en el nucleo (cerrada)
P_closed = math.pi * a * a * (J + K)     # potencia total sin normalizar (psi(a)=1)

# verificacion por cuadratura de las dos integrales (rho = r/a)
core_q = integrate.quad(lambda p: (sp.j0(u * p) / sp.j0(u)) ** 2 * p, 0, 1, epsabs=1e-15, epsrel=1e-13, limit=400)[0]
clad_q = integrate.quad(lambda p: (sp.k0(w * p) / sp.k0(w)) ** 2 * p, 1, np.inf, epsabs=1e-15, epsrel=1e-13, limit=400)[0]
Gamma_quad = core_q / (core_q + clad_q)
G0 = {
    "V": V, "u": u, "w": w, "eig_residual": resid,
    "Gamma_closed": Gamma, "Gamma_quad": Gamma_quad,
    "rel_core_closed_vs_quad": abs(2 * core_q - (1 + J)) / (1 + J),
    "rel_clad_closed_vs_quad": abs(2 * clad_q - (K - 1)) / (K - 1),
    "rel_Gamma_closed_vs_quad": abs(Gamma - Gamma_quad) / Gamma,
}
G0["PASS"] = bool(resid < 1e-10 and G0["rel_Gamma_closed_vs_quad"] < 1e-8
                  and G0["rel_core_closed_vs_quad"] < 1e-8 and G0["rel_clad_closed_vs_quad"] < 1e-8)

def psi_on_grid(N, h):
    x, y = oc.grid(N, h)
    r = np.hypot(x, y)
    inner = sp.j0(u * r / a) / sp.j0(u)
    outer = sp.k0(w * r / a) / sp.k0(w)
    return np.where(r < a, inner, outer) / math.sqrt(P_closed)

# ---- malla y observables -------------------------------------------------------------
HS_UM = [0.8, 0.4, 0.2, 0.1, 0.05]
L_HALF_UM = 40.0                # semidominio 40 um: cola de K0 despreciable (ver G0 y sumas de potencia)
rows = []
for hu in HS_UM:
    h = hu * 1e-6
    N = int(round(2 * L_HALF_UM / hu))
    t = time.time()
    psi = psi_on_grid(N, h)
    w64 = oc.disk_coverage(N, h, ss=64)
    w16 = oc.disk_coverage_uniform(N, h, ss=16)
    O_w = oc.obs_cov(psi, w64, h)
    O_w16 = oc.obs_cov(psi, w16, h)
    O_c = oc.obs_center(psi, h)
    S_tot = float((np.abs(psi) ** 2).sum() * h * h)
    area64 = float(w64.sum() * h * h); area16 = float(w16.sum() * h * h)
    Ap = math.pi * a * a
    rows.append(dict(
        h_um=hu, N=N, domain_um=N * hu,
        O_cov=O_w, O_cov_ss16=O_w16, O_center=O_c,
        err_cov=O_w - Gamma, err_cov_ss16=O_w16 - Gamma, err_center=O_c - Gamma,
        ratio_cov_to_discrete_total=O_w / S_tot,
        S_discrete_total_minus_1=S_tot - 1.0,
        area_rel_err_ss64=(area64 - Ap) / Ap, area_rel_err_ss16=(area16 - Ap) / Ap,
        H1_G3_area_ss16_vs_ss64_rel=abs(area16 - area64) / Ap,
        H1_G2_w_in_01=bool(w64.min() >= 0 and w64.max() <= 1),
        max_abs_dw_ss16_vs_ss64=float(np.abs(w16 - w64).max()),
        elapsed_s=round(time.time() - t, 3),
    ))
    print(json.dumps({k: rows[-1][k] for k in ["h_um", "N", "err_cov", "err_center", "area_rel_err_ss64"]}), flush=True)

# ---- robustez (no es gate): mallas no conmensurables con a=6 um --------------------------
# Anadida tras la primera pasada: en HS_UM los nodos caen sobre la circunferencia en los ejes
# (6/h entero) salvo h=0,8. Se comprueba con 6/17,3 ... 6/138,4 um (razon 2 entre mallas).
rob_rows = []
for hu in [6 / 17.3, 6 / 34.6, 6 / 69.2, 6 / 138.4]:
    h = hu * 1e-6
    N = int(round(2 * L_HALF_UM / hu))
    psi = psi_on_grid(N, h)
    w64 = oc.disk_coverage(N, h, ss=64)
    O_w = oc.obs_cov(psi, w64, h); O_c = oc.obs_center(psi, h)
    rob_rows.append(dict(h_um=hu, N=N, err_cov=O_w - Gamma, err_center=O_c - Gamma))
rh = np.array([r["h_um"] for r in rob_rows])
rob = dict(
    h_um=[round(float(v), 5) for v in rh],
    err_cov=[r["err_cov"] for r in rob_rows], err_center=[r["err_center"] for r in rob_rows],
    order_cov_LS=float(np.polyfit(np.log(rh), np.log(np.abs([r["err_cov"] for r in rob_rows])), 1)[0]),
    order_center_LS=float(np.polyfit(np.log(rh), np.log(np.abs([r["err_center"] for r in rob_rows])), 1)[0]),
    nota="robustez, no gate",
)

# ---- criterios ------------------------------------------------------------------------
hs = np.array([r["h_um"] for r in rows])
e_w = np.array([abs(r["err_cov"]) for r in rows])
e_c = np.array([abs(r["err_center"]) for r in rows])
mask = np.isin(hs, [0.4, 0.2, 0.1, 0.05])
def ls_order(e):
    return float(np.polyfit(np.log(hs[mask]), np.log(e[mask]), 1)[0])
p_w = ls_order(e_w); p_c = ls_order(e_c)
pair_w = float(math.log(e_w[3] / e_w[4]) / math.log(0.1 / 0.05))
pair_c = float(math.log(e_c[3] / e_c[4]) / math.log(0.1 / 0.05))

H1 = {
    "H1_G1_area_ss64_max_rel": max(abs(r["area_rel_err_ss64"]) for r in rows),
    "H1_G1_PASS": all(abs(r["area_rel_err_ss64"]) < 1e-4 for r in rows),
    "H1_G2_PASS": all(r["H1_G2_w_in_01"] for r in rows),
    "H1_G3_max_rel": max(r["H1_G3_area_ss16_vs_ss64_rel"] for r in rows),
    "H1_G3_PASS": all(r["H1_G3_area_ss16_vs_ss64_rel"] < 1e-4 for r in rows),
}
H2 = {
    "H2_G1_order_cov_LS_0p4to0p05": p_w,
    "H2_G1_order_center_LS_0p4to0p05": p_c,
    "H2_order_cov_pair_0p1_0p05": pair_w,
    "H2_order_center_pair_0p1_0p05": pair_c,
    "H2_G1_PASS": bool(p_w >= 1.8),
    "err_cov_at_0p05": float(e_w[4]),
    "err_center_at_0p05": float(e_c[4]),
}
out = dict(
    tarea="H2", contrato_sha256_CONTRATO_OBSERVABLE_COBERTURA=hashlib.sha256(open(os.path.join(HERE, "CONTRATO-OBSERVABLE-COBERTURA.md"), "rb").read()).hexdigest(),
    observable_cobertura_sha256=hashlib.sha256(open(os.path.join(HERE, "observable_cobertura.py"), "rb").read()).hexdigest(),
    referencia=G0, malla=rows, H1=H1, H2=H2, robustez_no_gate=rob, elapsed_total_s=round(time.time() - T0, 2),
)
os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "out", "h2_guia_salto.json"), "w"), indent=1)
print(json.dumps(dict(G0=G0["PASS"], H1=H1, H2=H2), indent=1))
