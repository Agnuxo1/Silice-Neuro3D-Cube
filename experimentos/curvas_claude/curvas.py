# -*- coding: utf-8 -*-
"""Tarea I (curvas): guia curvada por indice equivalente de Marcuse con solver2d.

Modelo numerico. No es un dispositivo ni una medida.
    n_eq(X, Y) = n_xy(X, Y) * (1 + X / R),  X hacia el exterior de la curva.
Ejecutar: python -B curvas.py   (con OMP_NUM_THREADS=1)
Criterios y umbrales: CONTRATO-curvas.md (fijados antes de ejecutar).
"""
import json
import math
import os
import sys
import time

import numpy as np
import scipy.special as sps
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
SOLVER_DIR = os.path.normpath(os.path.join(HERE, "..", "solver2d_claude"))
sys.path.insert(0, SOLVER_DIR)
import solver2d  # noqa: E402  uso directo del modulo; no se copia codigo

LAM = 1.55
A = 6.0
N1 = 1.444
N2 = 1.439
K0 = 2.0 * np.pi / LAM
RADII_MM = [5.0, 10.0, 20.0, 50.0]
L_MAIN = 40.0
NMODES = 12
S_SUB = 8
SCAN_MM = [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 7.5, 10.0, 20.0, 50.0]

LOG_PATH = os.path.join(HERE, "log_run.txt")
LOG = open(LOG_PATH, "w", encoding="utf-8")


def log(msg=""):
    print(msg, flush=True)
    LOG.write(msg + "\n")
    LOG.flush()


def fnum(v):
    if v is None:
        return None
    return float(v)


# ---------------------------------------------------------------- analitica
def lp01_analytic():
    """LP01 de fibra de salto (ecuacion caracteristica de Snyder-Love), raiz por brentq."""
    V = K0 * A * math.sqrt(N1 ** 2 - N2 ** 2)

    def f(U):
        W = math.sqrt(V ** 2 - U ** 2)
        return U * sps.j1(U) * sps.k0(W) - W * sps.k1(W) * sps.j0(U)

    Us = np.linspace(1e-6, V - 1e-6, 4000)
    fv = np.array([f(u) for u in Us])
    idx = np.where(np.sign(fv[:-1]) != np.sign(fv[1:]))[0]
    if idx.size == 0:
        raise RuntimeError("sin raiz LP01 en (0, V)")
    i = int(idx[0])
    U = brentq(f, Us[i], Us[i + 1], xtol=1e-15, rtol=1e-15, maxiter=500)
    W = math.sqrt(V ** 2 - U ** 2)
    neff = math.sqrt(N1 ** 2 - (U / (K0 * A)) ** 2)
    return {"V": V, "U": U, "W": W, "neff": neff, "U_below_2p405": bool(U < 2.4048)}


# ------------------------------------------------------------- indice y solver
def n_xy(X, Y):
    r = np.hypot(X, Y)
    return np.where(r < A, N1, N2)


def make_index(R_mm):
    if R_mm is None:
        return n_xy
    R_um = 1000.0 * float(R_mm)

    def n_eq(X, Y):
        return n_xy(X, Y) * (1.0 + X / R_um)

    return n_eq


def solve_case(R_mm, L, h):
    t0 = time.time()
    res = solver2d.solve(
        shapes=[], n_bg=N2, lam_um=LAM, L_um=L, h_um=h,
        n_modes=NMODES, s_sub=S_SUB, index_fn=make_index(R_mm),
    )
    res["_t_s"] = time.time() - t0
    return res


def grid_xy(res):
    x = np.asarray(res["x"], dtype=float)
    N = res["N"]
    X = np.tile(x[None, :], (N, 1))  # X[iy, ix] = x[ix]
    Y = np.tile(x[:, None], (1, N))  # Y[iy, ix] = y[iy]
    return X, Y


def mode_metrics(res, m, R_mm, ref_psi):
    h = res["h_um"]
    psi = res["psi"][m]
    neff = res["neff"][m]
    X, Y = grid_xy(res)
    P = psi * psi * h * h
    norm_err = float(abs(P.sum() - 1.0))
    centroid = float((X * P).sum())
    r = np.hypot(X, Y)
    p_core = float(P[r < A].sum())
    if R_mm is None:
        x_t = None
        p_out = None
    else:
        x_t = 1000.0 * float(R_mm) * (neff / N2 - 1.0)
        p_out = float(P[X > x_t].sum())
    S = float((np.sum(psi * ref_psi) * h * h) ** 2)
    ymir = float(np.max(np.abs(psi - psi[::-1, :])) / np.max(np.abs(psi)))
    return {
        "neff": float(neff),
        "centroid_um": centroid,
        "P_core": p_core,
        "P_out": p_out,
        "x_t_um": x_t,
        "overlap_S": S,
        "norm_err": norm_err,
        "y_mirror_rel": ymir,
    }


def run_point(R_mm, L, h, ref_psi=None):
    """Resuelve un caso y selecciona el modo fundamental por solapamiento con el LP01 recto.

    ref_psi: LP01 recto en la misma malla (L, h). Si es None (caso recto), se usa el propio modo 0.
    """
    res = solve_case(R_mm, L, h)
    if ref_psi is None:
        ref_psi = res["psi"][0]
    rows = []
    for m in range(len(res["psi"])):
        rows.append(mode_metrics(res, m, R_mm, ref_psi))
    best = max(range(len(rows)), key=lambda m: rows[m]["overlap_S"])
    sel = dict(rows[best])
    sel["mode_index"] = int(best)
    sel["h_um"] = float(h)
    sel["L_um"] = float(L)
    sel["N"] = int(res["N"])
    sel["unknowns"] = int(res["unknowns"])
    sel["t_s"] = float(res["_t_s"])
    sel["R_mm"] = None if R_mm is None else float(R_mm)
    sel["spectrum_neff_top"] = [float(v) for v in res["neff"]]
    sel["spectrum_S"] = [r_["overlap_S"] for r_ in rows]
    return sel, res


def critical_crossings(pairs, thr=0.01):
    """pairs: [(R_mm, P_out)]. Interpolacion log-log del cruce P_out = thr."""
    pts = sorted(pairs, key=lambda t: t[0])
    out = []
    for (r1, p1), (r2, p2) in zip(pts[:-1], pts[1:]):
        if p1 is None or p2 is None or p1 <= 0 or p2 <= 0:
            continue
        if (p1 - thr) * (p2 - thr) <= 0 and p1 != p2:
            t = (math.log(thr) - math.log(p1)) / (math.log(p2) - math.log(p1))
            out.append(math.exp(math.log(r1) + t * (math.log(r2) - math.log(r1))))
    return out


def main():
    t_start = time.time()
    log("Tarea I (curvas) - ejecucion; OMP_NUM_THREADS=%s" % os.environ.get("OMP_NUM_THREADS"))
    log("solver2d desde: %s" % SOLVER_DIR)

    ana = lp01_analytic()
    log("Analitica LP01: V=%.6f U=%.10f W=%.10f neff=%.16f U<2.4048=%s"
        % (ana["V"], ana["U"], ana["W"], ana["neff"], ana["U_below_2p405"]))

    results = {
        "meta": {
            "lam_um": LAM, "a_um": A, "n1": N1, "n2": N2, "s_sub": S_SUB,
            "n_modes": NMODES, "L_main_um": L_MAIN, "radii_mm": RADII_MM,
            "scan_mm": SCAN_MM, "modelo": "n_eq = n_xy (1 + X/R), X exterior, solver2d scalar FD",
            "nota": "MODELO NUMERICO. Perdida por radiacion NO calculada.",
        },
        "analitica": ana,
        "convergencia_recto": {},
        "casos": {},
        "dominio": {},
        "scan_radio": {},
        "criterios": {},
    }

    # ---------------- barrido principal: recto y curvas a h = 0,5; 0,25; 0,125
    refs = {}
    for h in (0.5, 0.25, 0.125):
        ref_sel, ref_res = run_point(None, L_MAIN, h, None)
        refs[h] = ref_res["psi"][0]
        results["convergencia_recto"]["h_%g" % h] = {
            "neff_recto": ref_sel["neff"],
            "err_vs_analitica": ref_sel["neff"] - ana["neff"],
            "unknowns": ref_sel["unknowns"],
            "t_s": ref_sel["t_s"],
        }
        log("[recto] h=%g N=%d unknowns=%d neff=%.12f err=%+.3e t=%.1fs"
            % (h, ref_sel["N"], ref_sel["unknowns"], ref_sel["neff"],
               ref_sel["neff"] - ana["neff"], ref_sel["t_s"]))
        for R_mm in RADII_MM:
            sel, _ = run_point(R_mm, L_MAIN, h, refs[h])
            results["casos"]["R%g_h%g" % (R_mm, h)] = sel
            log("[R=%g mm] h=%g neff=%.12f D=%+.6e <x>=%+.5f um P_out=%.3e P_core=%.4f S=%.4f modo=%d t=%.1fs"
                % (R_mm, h, sel["neff"], sel["neff"] - results["convergencia_recto"]["h_%g" % h]["neff_recto"],
                   sel["centroid_um"], sel["P_out"], sel["P_core"], sel["overlap_S"],
                   sel["mode_index"], sel["t_s"]))
        log("  espectro top (recto, h=%g): %s" % (h, ", ".join("%.8f" % v for v in ref_sel["spectrum_neff_top"][:4])))

    # ---------------- dominio (C6): L = 40 frente a L = 80 a h = 0,5
    big_ref_sel, big_ref_res = run_point(None, 80.0, 0.5, None)
    results["dominio"]["recto_L80_h0.5"] = big_ref_sel
    sel_R10_L80, _ = run_point(10.0, 80.0, 0.5, big_ref_res["psi"][0])
    results["dominio"]["R10_L80_h0.5"] = sel_R10_L80
    log("[dominio] recto L=80 h=0.5 neff=%.12f ; R=10 L=80 h=0.5 neff=%.12f"
        % (big_ref_sel["neff"], sel_R10_L80["neff"]))

    # ---------------- barrido de radio critico: h = 0,25, L = 40
    scan = []
    for R_mm in SCAN_MM:
        if R_mm in RADII_MM:
            sel = results["casos"]["R%g_h0.25" % R_mm]
        else:
            sel, _ = run_point(R_mm, L_MAIN, 0.25, refs[0.25])  # noqa: E501
        scan.append(sel)
        log("[scan] R=%.2f mm neff=%.10f x_t=%.3f um P_out=%.4e P_core=%.4f S=%.4f"
            % (R_mm, sel["neff"], sel["x_t_um"], sel["P_out"], sel["P_core"], sel["overlap_S"]))
    results["scan_radio"] = [
        {"R_mm": s["R_mm"], "neff": s["neff"], "x_t_um": s["x_t_um"], "P_out": s["P_out"],
         "P_core": s["P_core"], "S": s["overlap_S"], "centroid_um": s["centroid_um"]}
        for s in scan
    ]

    # ---------------- criterios
    neff_rec = {h: results["convergencia_recto"]["h_%g" % h]["neff_recto"] for h in (0.5, 0.25, 0.125)}
    C = {}

    def D(R_mm, h):
        return results["casos"]["R%g_h%g" % (R_mm, h)]["neff"] - neff_rec[h]

    d125 = {R: D(R, 0.125) for R in RADII_MM}
    d025 = {R: D(R, 0.25) for R in RADII_MM}

    c0 = abs(neff_rec[0.125] - ana["neff"])
    C["C0"] = {"desc": "|neff_recto(h=0,125) - neff_analitica| <= 1e-6", "value": c0, "pass": bool(c0 <= 1e-6)}

    c1 = abs(d125[50.0])
    C["C1"] = {"desc": "|neff(R=50 mm,h=0,125) - neff_recto| <= 1e-6", "value": c1, "pass": bool(c1 <= 1e-6)}

    n5 = results["casos"]["R5_h0.125"]["neff"]
    n10 = results["casos"]["R10_h0.125"]["neff"]
    n20 = results["casos"]["R20_h0.125"]["neff"]
    n50 = results["casos"]["R50_h0.125"]["neff"]
    c2 = bool(n50 > n20 > n10 > n5)
    C["C2"] = {"desc": "n_eff decrece al bajar R en h=0,125: n(50)>n(20)>n(10)>n(5)",
               "value": {"n50": n50, "n20": n20, "n10": n10, "n5": n5}, "pass": c2}

    c3_vals = {}
    c3_ok = True
    for R in (5.0, 10.0):
        rel = abs(d025[R] - d125[R]) / abs(d125[R]) if d125[R] != 0 else float("inf")
        c3_vals["R%g" % R] = {"D_h025": d025[R], "D_h0125": d125[R], "rel_change": rel}
        c3_ok = c3_ok and (rel <= 0.10)
    C["C3"] = {"desc": "|D(h=0,25)-D(h=0,125)| <= 0,10 |D(h=0,125)| para R=5 y 10 mm",
               "value": c3_vals, "pass": bool(c3_ok)}

    x5 = results["casos"]["R5_h0.125"]["centroid_um"]
    x10 = results["casos"]["R10_h0.125"]["centroid_um"]
    ratio_x = x5 / x10 if x10 != 0 else float("nan")
    C["C4"] = {"desc": "<x>(5 mm) > 0 y 1,8 <= <x>(5)/<x>(10) <= 2,2 (h=0,125)",
               "value": {"x5_um": x5, "x10_um": x10, "ratio": ratio_x},
               "pass": bool(x5 > 0 and 1.8 <= ratio_x <= 2.2)}

    ratio_D = d125[5.0] / d125[10.0] if d125[10.0] != 0 else float("nan")
    C["C5"] = {"desc": "D(5 mm)>0, D(10 mm)>0 y 3,6 <= D(5)/D(10) <= 4,4 (h=0,125)",
               "value": {"D5": d125[5.0], "D10": d125[10.0], "ratio": ratio_D},
               "pass": bool(d125[5.0] > 0 and d125[10.0] > 0 and 3.6 <= ratio_D <= 4.4)}

    dom_rec = abs(results["dominio"]["recto_L80_h0.5"]["neff"] - results["convergencia_recto"]["h_0.5"]["neff_recto"])
    dom_r10 = abs(results["dominio"]["R10_L80_h0.5"]["neff"] - results["casos"]["R10_h0.5"]["neff"])
    C["C6"] = {"desc": "|L40-L80| <= 1e-7 (recto) y <= 1e-6 (R=10 mm), h=0,5",
               "value": {"recto": dom_rec, "R10": dom_r10},
               "pass": bool(dom_rec <= 1e-7 and dom_r10 <= 1e-6)}

    R_cA = A * N2 / (neff_rec[0.125] - N2)
    kappa = K0 * math.sqrt(neff_rec[0.125] ** 2 - N2 ** 2)
    R_cA2 = (A + 1.0 / kappa) * N2 / (neff_rec[0.125] - N2)
    crossings = critical_crossings([(s["R_mm"], s["P_out"]) for s in scan], thr=0.01)
    R_num = crossings[0] if crossings else None
    ok_range = R_num is not None and 2.0 <= R_num <= 5.0 and 2.0 <= R_cA / 1000.0 <= 5.0
    ratio_c = (R_num / (R_cA / 1000.0)) if R_num is not None else float("nan")
    C["C7"] = {"desc": "R_c,num/R_c,A en [0,67; 1,5] y ambos en [2; 5] mm",
               "value": {"R_cA_mm": R_cA / 1000.0, "R_cA_sens_mm": R_cA2 / 1000.0,
                         "R_c_num_mm": R_num, "all_crossings_mm": crossings, "ratio": ratio_c},
               "pass": bool(R_num is not None and 0.67 <= ratio_c <= 1.5 and ok_range)}

    c8_ok = True
    c8_vals = {}
    for key, s in results["casos"].items():
        if key.endswith("h0.125"):
            ok = s["norm_err"] <= 1e-10 and s["y_mirror_rel"] <= 1e-6
            c8_ok = c8_ok and ok
            c8_vals[key] = {"norm_err": s["norm_err"], "y_mirror_rel": s["y_mirror_rel"]}
    C["C8"] = {"desc": "norma |sum|psi|^2 h^2 -1| <= 1e-10 y simetria y: max|psi(x,y)-psi(x,-y)|/max|psi| <= 1e-6 (curvas, h=0,125)",
               "value": c8_vals, "pass": bool(c8_ok)}

    c9_vals = {k: s["overlap_S"] for k, s in results["casos"].items() if k.endswith("h0.125")}
    c9_vals["recto"] = 1.0
    C["C9"] = {"desc": "solapamiento S >= 0,90 con el LP01 recto (h=0,125)",
               "value": c9_vals, "pass": bool(all(v >= 0.90 for v in c9_vals.values()))}

    # ---------------- informativo: orden de convergencia del recto frente a la analitica
    e = {h: abs(results["convergencia_recto"]["h_%g" % h]["err_vs_analitica"]) for h in (0.5, 0.25, 0.125)}
    p_rec = math.log2(e[0.25] / e[0.125]) if e[0.125] > 0 and e[0.25] > 0 else float("nan")
    results["convergencia_recto"]["orden_p_0.25_0.125"] = p_rec
    results["convergencia_recto"]["errores_abs"] = {str(k): v for k, v in e.items()}

    results["D_bent_minus_recto_h0.125"] = {str(R): d125[R] for R in RADII_MM}
    results["D_bent_minus_recto_h0.25"] = {str(R): d025[R] for R in RADII_MM}
    results["x_t_um_h0.125"] = {str(R): results["casos"]["R%g_h0.125" % R]["x_t_um"] for R in RADII_MM}
    results["R_cA_mm"] = R_cA / 1000.0
    results["R_cA_sens_mm"] = R_cA2 / 1000.0
    results["R_c_num_mm"] = R_num
    results["criterios"] = C
    results["n_pass"] = sum(1 for c in C.values() if c["pass"])
    results["n_criterios"] = len(C)
    results["tiempo_total_s"] = time.time() - t_start

    for k in sorted(C):
        log("%s pass=%s  %s  value=%s" % (k, C[k]["pass"], C[k]["desc"], json.dumps(C[k]["value"], default=float)[:400]))
    log("Resumen: %d/%d criterios pass=true. Tiempo %.1f s." % (results["n_pass"], results["n_criterios"], results["tiempo_total_s"]))

    out_path = os.path.join(HERE, "resultados.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False, default=float)
    log("Escrito: %s" % out_path)


if __name__ == "__main__":
    main()
