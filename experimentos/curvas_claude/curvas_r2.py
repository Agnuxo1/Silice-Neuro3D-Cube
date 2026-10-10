# -*- coding: utf-8 -*-
"""Tarea I2 (ronda 2, curvas): convergencia de dominio de la guia curvada por indice equivalente.

Modelo numerico. No es un dispositivo ni una medida.
    n_eq(X, Y) = n_xy(X, Y) * (1 + X / R),  X hacia el exterior de la curva.
Ejecutar: OMP_NUM_THREADS=1 python -B curvas_r2.py
Criterios y umbrales: CONTRATO-curvas-r2.md (fijados antes de ejecutar).
Dominio de solver2d: [-L, +L] (L = semidimension). n_modes = 40.
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
S_SUB = 8
NM = 40
CORTE_MARGEN = 3          # caso no fiable si indice del nucleo >= NM - CORTE_MARGEN
RADII_MM = [10.0, 20.0, 50.0]
LS = [40.0, 60.0, 80.0, 100.0]
H_MAIN = 0.25
H_INFO = 0.125
L_INFO = [40.0, 60.0]     # solo informativo, fuera de criterios
ROUND1_R10_L40_H025 = 1.442266248115  # ronda 1, n_modes = 12, para consistencia (informativo)

# Configuracion por entorno (por defecto = ejecucion completa). Permite repartir L entre procesos
# en paralelo por limite de RAM; cada proceso escribe su parte y los criterios se evaluan al final.
LS_RUN = [float(v) for v in os.environ.get("CURVAS_LS", "40,60,80,100").split(",")]
PATH_JSON = os.environ.get("CURVAS_JSON") or os.path.join(HERE, "resultados_curvas_r2.json")
LOG_PATH = os.environ.get("CURVAS_LOG") or os.path.join(HERE, "log_curvas_r2.txt")
RUN_PHASE2 = os.environ.get("CURVAS_PHASE2", "1") == "1"
LOG = open(LOG_PATH, "w", encoding="utf-8")
T_START = time.time()


def log(msg=""):
    print(msg, flush=True)
    LOG.write(msg + "\n")
    LOG.flush()


def key_case(R_mm, L, h):
    return "R%g_L%g_h%g" % (R_mm, L, h)


def key_recto(L, h):
    return "recto_L%g_h%g" % (L, h)


# ---------------------------------------------------------------- analitica
def lp01_analytic():
    """LP01 de fibra de salto (Snyder-Love), raiz por brentq. Misma formula que curvas.py."""
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
    return {"V": V, "U": U, "W": W, "neff": neff}


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


def solve_case(L, h, R_mm):
    t0 = time.time()
    res = solver2d.solve(
        shapes=[], n_bg=N2, lam_um=LAM, L_um=L, h_um=h,
        n_modes=NM, s_sub=S_SUB, index_fn=make_index(R_mm),
    )
    res["_t_s"] = time.time() - t0
    return res


def grid_xy(res):
    x = np.asarray(res["x"], dtype=float)
    N = res["N"]
    X = np.tile(x[None, :], (N, 1))  # X[iy, ix] = x[ix]
    Y = np.tile(x[:, None], (1, N))  # Y[iy, ix] = y[iy]
    return X, Y


def overlap(psi, ref_psi, h):
    return float((np.sum(psi * ref_psi) * h * h) ** 2)


def metrics_of(res, m, R_mm, ref_psi):
    h = res["h_um"]
    psi = res["psi"][m]
    neff = float(res["neff"][m])
    X, Y = grid_xy(res)
    P = psi * psi * h * h
    r = np.hypot(X, Y)
    out = {
        "mode_index": int(m),
        "neff": neff,
        "S": overlap(psi, ref_psi, h),
        "norm_err": float(abs(P.sum() - 1.0)),
        "centroid_um": float((X * P).sum()),
        "P_core": float(P[r < A].sum()),
        "y_mirror_rel": float(np.max(np.abs(psi - psi[::-1, :])) / np.max(np.abs(psi))),
    }
    if R_mm is None:
        out["x_t_um"] = None
        out["P_out"] = None
    else:
        x_t = 1000.0 * float(R_mm) * (neff / N2 - 1.0)
        out["x_t_um"] = x_t
        out["P_out"] = float(P[X > x_t].sum())
    return out


def select_core(res, ref_psi, R_mm):
    """Modo nucleo = mayor solapamiento S con el LP01 recto de la misma caja y malla."""
    h = res["h_um"]
    S_all = [overlap(psi, ref_psi, h) for psi in res["psi"]]
    m_best = int(np.argmax(S_all))
    sel = metrics_of(res, m_best, R_mm, ref_psi)
    sel["flag_corte"] = bool(m_best >= NM - CORTE_MARGEN)
    sel["S_all"] = [float(v) for v in S_all]
    sel["spectrum_neff"] = [float(v) for v in res["neff"]]
    return sel


# ----------------------------------------------------------------- persistencia
R_OUT = {
    "meta": {
        "lam_um": LAM, "a_um": A, "n1": N1, "n2": N2, "s_sub": S_SUB, "n_modes": NM,
        "corte_margen": CORTE_MARGEN, "radii_mm": RADII_MM, "L_um": LS, "h_um": H_MAIN,
        "dominio": "solver2d: [-L, +L] (L semidimension)",
        "modelo": "n_eq = n_xy (1 + X/R), X exterior, solver2d scalar FD, Dirichlet",
        "nota": "MODELO NUMERICO. Perdida por radiacion NO calculada. I2.4 no evaluado (decision JEV Q4).",
        "contrato": "CONTRATO-curvas-r2.md",
    },
    "analitica": None,
    "recto": {},
    "casos": {},
    "criterios": {},
    "informativo": {},
    "estado": "parcial",
}


def save(estado):
    R_OUT["estado"] = estado
    R_OUT["tiempo_total_s"] = time.time() - T_START
    tmp = PATH_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(R_OUT, fh, indent=2, ensure_ascii=False, default=float)
    os.replace(tmp, PATH_JSON)


# ----------------------------------------------------------------- criterios
def evaluar_criterios(ana):
    C = {}
    casos = R_OUT["casos"]
    rec = R_OUT["recto"]

    # I2.0 verificacion: recto frente a analitica en cada L (h = 0,25) y normalizacion
    errs = {L: rec[key_recto(L, H_MAIN)]["err_vs_analitica"] for L in LS}
    max_err = max(abs(v) for v in errs.values())
    norm_max = max(c["norm_err"] for c in casos.values())
    C["I2.0"] = {
        "desc": "|n_recto(L,h=0,25) - n_analitica| <= 1e-6 para todo L y |sum psi^2 h^2 - 1| <= 1e-10 (nucleo)",
        "value": {"max_abs_err_recto": max_err, "err_recto_por_L": {str(L): errs[L] for L in LS},
                  "max_norm_err": norm_max},
        "pass": bool(max_err <= 1e-6 and norm_max <= 1e-10),
        "evaluado": True,
    }

    # I2.1 convergencia de dominio: |n(L=100) - n(L=80)| < 1e-6 a h = 0,25 con S > 0,9
    conv = {}
    ok_R = {}
    for R in RADII_MM:
        c80 = casos[key_case(R, 80.0, H_MAIN)]
        c100 = casos[key_case(R, 100.0, H_MAIN)]
        d = abs(c100["neff"] - c80["neff"])
        ok = bool(d < 1e-6 and c80["S"] > 0.90 and c100["S"] > 0.90
                  and not c80["flag_corte"] and not c100["flag_corte"])
        ok_R[R] = ok
        pares = {}
        for L1, L2 in ((40.0, 60.0), (60.0, 80.0), (80.0, 100.0)):
            pares["%g-%g" % (L1, L2)] = casos[key_case(R, L1, H_MAIN)]["neff"] - casos[key_case(R, L2, H_MAIN)]["neff"]
        conv["R%g" % R] = {
            "d_80_100": d, "pass_R": ok, "S_L80": c80["S"], "S_L100": c100["S"],
            "neff_L80": c80["neff"], "neff_L100": c100["neff"],
            "diferencias_informativas_neff_Li_minus_Lj": pares,
            "indice_nucleo_L80": c80["mode_index"], "indice_nucleo_L100": c100["mode_index"],
        }
    C["I2.1"] = {
        "desc": "|n_eff(L=100) - n_eff(L=80)| < 1e-6 a h=0,25 con S>0,90 para R = 10, 20, 50 mm",
        "value": conv,
        "pass": bool(all(ok_R.values())),
        "evaluado": True,
    }

    # I2.2 identificacion del nucleo: S > 0,90 y sin corte espectral en los 12 pares
    fallos = []
    S_min = 1.0
    for R in RADII_MM:
        for L in LS:
            c = casos[key_case(R, L, H_MAIN)]
            S_min = min(S_min, c["S"])
            if not (c["S"] > 0.90 and not c["flag_corte"]):
                fallos.append({"R_mm": R, "L_um": L, "S": c["S"], "indice": c["mode_index"],
                               "flag_corte": c["flag_corte"]})
    C["I2.2"] = {
        "desc": "S > 0,90 y sin corte espectral para los 12 pares (R, L), h=0,25",
        "value": {"S_min": S_min, "n_pares": len(RADII_MM) * len(LS), "fallos": fallos},
        "pass": bool(len(fallos) == 0),
        "evaluado": True,
    }

    # I2.3 tendencia con incertidumbre de dominio: solo si I2.1 pasa para R = 10
    if ok_R[10.0]:
        u = max(conv["R%g" % R]["d_80_100"] for R in RADII_MM)
        n10 = casos[key_case(10.0, 100.0, H_MAIN)]["neff"]
        n20 = casos[key_case(20.0, 100.0, H_MAIN)]["neff"]
        n50 = casos[key_case(50.0, 100.0, H_MAIN)]["neff"]
        D1 = n50 - n20
        D2 = n20 - n10
        C["I2.3"] = {
            "desc": "n(50)-n(20) > u y n(20)-n(10) > u a L=100, h=0,25; u = max_R |n(100)-n(80)|",
            "value": {"u_dominio": u, "n10": n10, "n20": n20, "n50": n50, "D_50_20": D1, "D_20_10": D2},
            "pass": bool(D1 > u and D2 > u),
            "evaluado": True,
        }
    else:
        C["I2.3"] = {
            "desc": "n(50)-n(20) > u y n(20)-n(10) > u a L=100, h=0,25 (solo si I2.1 pasa para R=10)",
            "value": None, "pass": None, "evaluado": False,
            "motivo": "I2.1 no converge para R = 10 mm (condicion del contrato)",
        }

    # I2.4 radio critico: no evaluado en esta ronda (decision JEV Q4, opcion C)
    C["I2.4"] = {
        "desc": "radio critico (C7 ronda 1 citado, no evaluado en ronda 2)",
        "value": None, "pass": None, "evaluado": False,
        "motivo": "No ejecutado en esta ronda por decision JEV Q4 (opcion C, confianza 0,89).",
    }
    return C


def resumen(C):
    ev = [k for k, v in C.items() if v["evaluado"]]
    ps = [k for k in ev if C[k]["pass"]]
    return {"n_criterios": len(C), "n_evaluados": len(ev), "n_pass": len(ps),
            "pass_list": ps, "fail_list": [k for k in ev if not C[k]["pass"]],
            "no_evaluados": [k for k in C if not C[k]["evaluado"]]}


# ---------------------------------------------------------------------- main
def main():
    ana = lp01_analytic()
    R_OUT["analitica"] = ana
    log("Tarea I2 ronda 2 (curvas): NM=%d h=%g Ls=%s radios=%s" % (NM, H_MAIN, LS, RADII_MM))
    log("Analitica LP01: V=%.6f U=%.10f neff=%.16f" % (ana["V"], ana["U"], ana["neff"]))
    log("OMP_NUM_THREADS=%s solver2d desde %s" % (os.environ.get("OMP_NUM_THREADS"), SOLVER_DIR))
    save("parcial")

    # ---- fase 1: criterio principal, h = 0,25, L = 40, 60, 80, 100
    for L in LS_RUN:
        res = solve_case(L, H_MAIN, None)
        ref = np.array(res["psi"][0], copy=True)
        neff_rec = float(res["neff"][0])
        R_OUT["recto"][key_recto(L, H_MAIN)] = {
            "neff": neff_rec, "err_vs_analitica": neff_rec - ana["neff"],
            "N": res["N"], "unknowns": res["unknowns"], "t_s": res["_t_s"],
            "spectrum_top5": [float(v) for v in res["neff"][:5]],
        }
        log("[recto] L=%g h=%g N=%d neff=%.12f err=%+.3e t=%.1fs"
            % (L, H_MAIN, res["N"], neff_rec, neff_rec - ana["neff"], res["_t_s"]))
        del res
        save("parcial")
        for R in RADII_MM:
            res = solve_case(L, H_MAIN, R)
            sel = select_core(res, ref, R)
            sel.update({"R_mm": R, "L_um": L, "h_um": H_MAIN, "N": res["N"],
                        "unknowns": res["unknowns"], "t_s": res["_t_s"], "n_modes": NM})
            sel["D_vs_recto"] = sel["neff"] - neff_rec
            R_OUT["casos"][key_case(R, L, H_MAIN)] = sel
            save("parcial")
            log("[R=%g L=%g h=%g] neff=%.12f S=%.6f idx=%d corte=%s x_t=%.2f P_out=%.3e P_core=%.4f <x>=%+.4f D=%+.3e t=%.1fs"
                % (R, L, H_MAIN, sel["neff"], sel["S"], sel["mode_index"], sel["flag_corte"],
                   sel["x_t_um"], sel["P_out"], sel["P_core"], sel["centroid_um"], sel["D_vs_recto"],
                   sel["t_s"] if "t_s" in sel else res["_t_s"]))
            log("   top-5 neff: %s" % ", ".join("%.8f" % v for v in sel["spectrum_neff"][:5]))
            del res
        del ref

    # ---- criterios de la fase 1
    C = evaluar_criterios(ana) if set(LS).issubset(set(LS_RUN)) else {}
    R_OUT["criterios"] = C
    R_OUT["resumen"] = resumen(C)
    for k in sorted(C):
        log("%s evaluado=%s pass=%s  %s" % (k, C[k]["evaluado"], C[k]["pass"], C[k]["desc"]))
    log("Resumen fase 1: %s" % json.dumps(R_OUT["resumen"], ensure_ascii=False))
    save("fase1_completa")

    # ---- fase 2: informativa, h = 0,125 (solo L = 40 y 60; fuera de criterios)
    info = {}
    for L in (L_INFO if RUN_PHASE2 else []):
        res = solve_case(L, H_INFO, None)
        ref = np.array(res["psi"][0], copy=True)
        neff_rec = float(res["neff"][0])
        info[key_recto(L, H_INFO)] = {"neff": neff_rec, "err_vs_analitica": neff_rec - ana["neff"],
                                      "dif_vs_h025": neff_rec - R_OUT["recto"][key_recto(L, H_MAIN)]["neff"]}
        log("[info recto] L=%g h=%g neff=%.12f err=%+.3e" % (L, H_INFO, neff_rec, neff_rec - ana["neff"]))
        del res
        radios_info = RADII_MM if L == 40.0 else [10.0]
        for R in radios_info:
            res = solve_case(L, H_INFO, R)
            sel = select_core(res, ref, R)
            sel.pop("S_all", None)
            sel.pop("spectrum_neff", None)
            sel["dif_vs_h025"] = sel["neff"] - R_OUT["casos"][key_case(R, L, H_MAIN)]["neff"]
            sel["R_mm"] = R
            sel["L_um"] = L
            info[key_case(R, L, H_INFO)] = sel
            log("[info R=%g L=%g h=%g] neff=%.12f S=%.6f idx=%d dif_vs_h025=%+.3e"
                % (R, L, H_INFO, sel["neff"], sel["S"], sel["mode_index"], sel["dif_vs_h025"]))
            del res
            R_OUT["informativo"] = info
            save("fase2_parcial")
        del ref
    R_OUT["informativo"] = info
    if key_case(10.0, 40.0, H_MAIN) in R_OUT["casos"]:
      R_OUT["informativo"]["consistencia_ronda1_R10_L40_h025"] = {
        "neff_ronda2": R_OUT["casos"][key_case(10.0, 40.0, H_MAIN)]["neff"],
        "neff_ronda1_nmodes12": ROUND1_R10_L40_H025,
        "dif": R_OUT["casos"][key_case(10.0, 40.0, H_MAIN)]["neff"] - ROUND1_R10_L40_H025,
    }
    if "consistencia_ronda1_R10_L40_h025" in R_OUT["informativo"]:
        log("Consistencia ronda1 (R=10, L=40, h=0,25): dif=%+.3e" % R_OUT["informativo"]["consistencia_ronda1_R10_L40_h025"]["dif"])
    save("completo")
    log("Escrito %s. Tiempo total %.1f s." % (PATH_JSON, time.time() - T_START))


if __name__ == "__main__":
    main()
