#!/usr/bin/env python3
"""Tarea K: registro entre caras y tolerancias correlacionadas (modelo numerico).

Contrato: CONTRATO-REGISTRO.md (enmiendas E-1 y E-2, fijadas antes de calcular).
Ejecucion: OMP_NUM_THREADS=1 python -B registro_k.py
Salida:    registro_resultados.json (esta carpeta). Solo modelo; sin medidas.
kappa(d) se importa de experimentos/acoplo_claude/acoplo_paralelo.py sin modificarlo.
"""
import importlib.util
import json
import pathlib
import sys
import time

import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
ACO = HERE.parent / "acoplo_claude" / "acoplo_paralelo.py"
_spec = importlib.util.spec_from_file_location("acoplo_paralelo", ACO)
AP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(AP)  # kappa(d) en um^-1

# ---------------- parametros (fijados en el contrato) ----------------
L_UM = 10_000.0                       # 10 mm
P2T = 0.10                            # umbral de diafonia
XT = float(np.arcsin(np.sqrt(P2T)))   # kappa*L en el umbral, rad
D0 = 20.0                             # separacion de diseno, um
N_CH = 200                            # acopladores por chip (supuesto)
R = 2000                              # realizaciones
SEED = 20261010
SIGMAS = [0.5, 1.0, 2.0]              # um (supuesto)
LS = [0, 1, 3, 10]                    # celdas; l = 0 es la referencia iid
SIG_RES = 0.2                         # um, residuo tras correccion (supuesto)
Z95 = float(norm.ppf(0.95))           # 1,645
NPASS_MIN = 190                       # 0,95 * 200
D_LO, D_HI = 12.0, 40.0               # dominio de la tabla (E-1)
DGRID = np.round(np.arange(20.0, 30.0 + 1e-9, 0.05), 4)


def intervals(mask, x):
    """Intervalos contiguos de x donde mask es True."""
    if not mask.any():
        return []
    edges = np.flatnonzero(np.diff(np.concatenate(([0], mask.astype(int), [0]))))
    return [[float(x[s]), float(x[e - 1])] for s, e in zip(edges[::2], edges[1::2])]


# ---------------- kappa tabulado (interpolacion lineal en ln kappa) ----------------
GRID = np.round(np.arange(D_LO, D_HI + 1e-9, 0.01), 6)
LNK = np.log(np.array([AP.kappa(float(d)) for d in GRID]))


def kap_tab(d):
    return np.exp(np.interp(np.clip(d, D_LO, D_HI), GRID, LNK))


def passes(d):
    """True si P2 <= 0,10. Regla E-1: d < 12 um cuenta como fallo."""
    d = np.asarray(d, dtype=float)
    p2 = np.sin(kap_tab(d) * L_UM) ** 2
    return (p2 <= P2T) & (d >= D_LO)


def p2_tab(d):
    return np.sin(kap_tab(np.asarray(d, dtype=float)) * L_UM) ** 2


# ---------------- correlacion y factorizacion (E-2) ----------------
_FAC = {}


def corr_mat(l, kernel="exp"):
    k = np.abs(np.subtract.outer(np.arange(N_CH), np.arange(N_CH))).astype(float)
    if l == 0:
        return np.eye(N_CH)
    if kernel == "exp":
        return np.exp(-k / l)
    return np.exp(-(k ** 2) / (2.0 * l ** 2))


def factor(l, kernel="exp"):
    key = (l, kernel)
    if key not in _FAC:
        C = corr_mat(l, kernel)
        w, V = np.linalg.eigh(C)
        w = np.clip(w, 0.0, None)
        A = V * np.sqrt(w)
        recon = float(np.max(np.abs(A @ A.T - C)))
        _FAC[key] = {"A": A, "recon": recon, "lam_min": float(np.linalg.eigvalsh(C).min())}
    return _FAC[key]["A"]


# ---------------- analitico ----------------
U_GRID = np.linspace(-12.0, 12.0, 240001)
W_GRID = norm.pdf(U_GRID)


def E_ana(d, sigma, sign=+1):
    ind = passes(d + sign * sigma * U_GRID).astype(float)
    return float(np.trapezoid(ind * W_GRID, U_GRID))


def stats(P):
    counts = P.sum(axis=1)
    f = counts / N_CH
    return {"E_mc": float(f.mean()), "sd_f": float(f.std(ddof=1)),
            "P5_f": float(np.percentile(f, 5)), "Y95": float(np.mean(counts >= NPASS_MIN))}


def Y_curve(dl, dgrid=DGRID):
    out = []
    for d in dgrid:
        counts = passes(d + dl).sum(axis=1)
        out.append(float(np.mean(counts >= NPASS_MIN)))
    return out


def first_d_at(dgrid, yvals, thr=0.95):
    for d, y in zip(dgrid, yvals):
        if y >= thr:
            return float(d)
    return None


def main():
    t0 = time.time()
    out = {
        "tarea": "K: registro entre caras y tolerancias correlacionadas (modelo)",
        "contrato": "CONTRATO-REGISTRO.md (E-1, E-2)",
        "supuestos_no_medidos": {"sigma_um": SIGMAS, "l_celdas": LS, "kernel": "exp (sens.: gauss)",
                                 "N_acopladores_por_chip": N_CH, "R_realizaciones": R, "seed": SEED,
                                 "sigma_res_um": SIG_RES, "residuo": "iid por acoplador"},
        "modelo": {"L_um": L_UM, "P2_umbral": P2T, "kappa_L_umbral_rad": XT, "d_diseno_um": D0,
                   "fuente_kappa": "experimentos/acoplo_claude/acoplo_paralelo.py (kappa, sin cambios)"},
    }
    crit = []
    ver = {}

    def add(cid, desc, value, passed):
        crit.append({"id": cid, "description": desc, "value": value, "pass": bool(passed)})

    # ===== V-K0: interpolacion de kappa frente a la llamada directa =====
    rng_t = np.random.default_rng(SEED)
    dt = np.sort(rng_t.uniform(12.0, 35.0, 50))
    kd = np.array([AP.kappa(float(x)) for x in dt])
    err_k = float(np.max(np.abs(kap_tab(dt) / kd - 1.0)))
    ver["V-K0_err_rel_kappa"] = err_k
    add("V-K0", "Interpolacion de kappa frente a la llamada directa, error relativo max < 1e-4 "
                "en 50 puntos de d in [12,35] um",
        f"{err_k:.3e}", err_k < 1e-4)

    # ===== V-K1: raiz d* con kappa directo y cambio de signo unico =====
    def g_direct(d):
        return AP.kappa(float(d)) * L_UM - XT
    dstar = float(brentq(g_direct, 16.0, 30.0, xtol=1e-13, rtol=1e-14))
    p2_dstar = float(np.sin(AP.kappa(dstar) * L_UM) ** 2)
    xs = np.arange(16.0, 30.0 + 1e-9, 0.01)
    gv = kap_tab(xs) * L_UM - XT
    n_sc = int(np.sum(np.sign(gv[:-1]) != np.sign(gv[1:])))
    err_p2 = abs(p2_dstar - P2T)
    ver.update({"V-K1_err_P2_dstar": err_p2, "V-K1_cambios_signo": n_sc})
    add("V-K1", "P2(d*) = 0,10 con tolerancia 1e-9 y un unico cambio de signo de kappa*L-arcsin(sqrt 0,1) en [16,30] um",
        f"|P2-0,10|={err_p2:.2e}, cambios={n_sc}", (err_p2 < 1e-9) and n_sc == 1)

    # ===== K1: tolerancia del caso peor =====
    dmax = D0 - dstar
    dfav = dstar - D0
    ds_w = np.arange(0.0, 8.0 + 1e-9, 0.002)
    mask_w = passes(D0 - ds_w)
    ints_w = intervals(mask_w, ds_w)
    ds_f = np.arange(0.0, 20.0 + 1e-9, 0.01)
    mask_f = passes(D0 + ds_f)
    ints_f = intervals(mask_f, ds_f)
    P2_nom = float(p2_tab(D0))
    design_rows = []
    for d in [20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0]:
        design_rows.append({"d_um": d, "P2_nominal": float(p2_tab(d)), "delta_max_simetrico_um": float(d - dstar)})
    k1 = {"d_star_um": dstar, "kappa_D0_L": float(kap_tab(D0) * L_UM), "P2_nominal_d20": P2_nom,
          "delta_max_simetrico_um": float(dmax), "delta_min_favorable_um": float(dfav),
          "intervalos_caso_peor_delta_um_con_P2_le_0.10": ints_w,
          "intervalos_caso_favorable_delta_um_con_P2_le_0.10": ints_f,
          "tabla_diseno": design_rows}
    out["K1"] = k1
    add("K1-C1", "Tolerancia simetrica del caso peor a d = 20 um: delta_max = d - d* >= 0",
        f"delta_max = {dmax:+.3f} um (d*={dstar:.3f} um; P2(20)={P2_nom:.4f})", dmax >= 0)

    # ===== Monte Carlo: 12 celdas a d = 20 um =====
    Z0 = np.random.default_rng(SEED).standard_normal((R, N_CH))
    Zr0 = np.random.default_rng(SEED + 10).standard_normal((R, N_CH))
    cells = {}
    rec_max = 0.0
    for s in SIGMAS:
        for l in LS:
            A = factor(l, "exp")
            dl = s * (Z0 @ A.T)
            P20 = passes(D0 + dl)
            st = stats(P20)
            Ea = E_ana(D0, s)
            P20m = passes(D0 - dl)
            st_m = stats(P20m)
            n_below = int(np.sum(D0 + dl < D_LO))
            n_above = int(np.sum(D0 + dl > D_HI))
            n_pass = int(P20.sum())
            n_pass_nonmono = int(np.sum(P20 & (D0 + dl < 16.0)))
            dmin = dstar + Z95 * s
            Pdm = passes(dmin + dl)
            st_dm = stats(Pdm)
            Yc = Y_curve(dl)
            d95 = first_d_at(DGRID, Yc)
            cells[(s, l)] = {
                "sigma_um": s, "l_celdas": l, "E_mc_d20": st["E_mc"], "E_ana_d20": Ea,
                "diff_mc_ana": abs(st["E_mc"] - Ea), "sd_f_d20": st["sd_f"], "P5_f_d20": st["P5_f"],
                "Y95_d20": st["Y95"], "E_mc_signo_menos_d20": st_m["E_mc"],
                "d_min_um": dmin, "E_mc_dmin": st_dm["E_mc"], "Y95_dmin": st_dm["Y95"],
                "P5_f_dmin": st_dm["P5_f"], "d_chip95_um": d95,
                "n_eventos_d_eff_menor_12": n_below, "n_eventos_d_eff_mayor_40": n_above,
                "frac_pasos_en_rama_no_monotona_d_lt_16": (n_pass_nonmono / n_pass) if n_pass else None,
                "_Y_curve": Yc,
            }
    rec_max = max(v["recon"] for v in _FAC.values())

    # ===== V-K2: generador gaussiano, correlacion empirica =====
    gen = {}
    gen_ok = True
    for l in [1, 3, 10]:
        A = factor(l, "exp")
        rho = Z0 @ A.T
        emp = {}
        for k in range(1, 11):
            r_k = float(np.mean(rho[:, :-k] * rho[:, k:]))
            tgt = float(np.exp(-k / l))
            emp[k] = {"emp": r_k, "obj": tgt, "err": abs(r_k - tgt)}
            gen_ok = gen_ok and abs(r_k - tgt) < 0.02
        sd_rho = float(np.std(rho))
        gen_ok = gen_ok and abs(sd_rho - 1.0) < 0.02
        gen[f"l{l}"] = {"sd_rho": sd_rho, "lag_corr": emp}
    ver["V-K2_generador"] = gen
    ver["V-K2_reconstruccion_max"] = rec_max
    add("V-K2", "Generador gaussiano: |corr. empirica(k) - exp(-k/l)| < 0,02 para k=1..10, l in {1,3,10}; |sd-1| < 0,02",
        f"reconstruccion max={rec_max:.2e}; ver detalle en JSON", gen_ok and rec_max < 1e-8)

    # ===== V-K3: Monte Carlo frente a analitico (12 celdas + residuo) =====
    max_diff = max(v["diff_mc_ana"] for v in cells.values())
    # residuo iid para K3 (lo calculamos mas abajo y lo incluimos)
    dl_res0 = SIG_RES * Zr0
    P20r = passes(D0 + dl_res0)
    st_r = stats(P20r)
    Ea_r = E_ana(D0, SIG_RES)
    max_diff_all = max(max_diff, abs(st_r["E_mc"] - Ea_r))
    add("V-K3", "Monte Carlo frente a analitico: |media MC - E analitico| < 0,005 en las 12 celdas y en el residuo",
        f"max diff={max_diff_all:.4f}", max_diff_all < 0.005)

    # ===== V-K4: sensibilidad a semilla (dos semillas adicionales, d = 20 um) =====
    seed_dev = 0.0
    seed_detail = {}
    for sd_off in [1, 2]:
        Zs = np.random.default_rng(SEED + sd_off).standard_normal((R, N_CH))
        dev_here = []
        for s in SIGMAS:
            for l in LS:
                A = factor(l, "exp")
                st_s = stats(passes(D0 + s * (Zs @ A.T)))
                dev = abs(st_s["E_mc"] - cells[(s, l)]["E_mc_d20"])
                dev_here.append(dev)
                seed_dev = max(seed_dev, dev)
        seed_detail[f"seed+{sd_off}_max_dev"] = float(max(dev_here))
    add("V-K4", "Sensibilidad a semilla: cambio de la media < 0,01 con dos semillas adicionales en las 12 celdas",
        f"max cambio={seed_dev:.4f}", seed_dev < 0.01)

    # ===== K2: primario, media >= 0,95 en d = 20 =====
    tbl = []
    for s in SIGMAS:
        for l in LS:
            c = cells[(s, l)]
            tbl.append({k: v for k, v in c.items() if not k.startswith("_")})
    e_vals = {(c["sigma_um"], c["l_celdas"]): c["E_mc_d20"] for c in tbl}
    maxE = max(e_vals.values())
    minE = min(e_vals.values())
    add("K2-C1", "Primario: fraccion media de acopladores con P2<=0,10 >= 0,95 en d = 20 um, en las 12 celdas",
        f"E_mc en [{minE:.4f}, {maxE:.4f}]", minE >= 0.95)

    # K2-H-a: invarianza de la media con la correlacion
    inv_dev = {}
    for s in SIGMAS:
        inv_dev[s] = max(abs(e_vals[(s, l)] - e_vals[(s, 0)]) for l in [1, 3, 10])
    inv_max = max(inv_dev.values())
    add("K2-H-a", "La media no depende de la correlacion: |E(l) - E(0)| < 0,01 para l in {1,3,10} y cada sigma",
        f"max |E(l)-E(0)|={inv_max:.4f}", inv_max < 0.01)

    # K2-H-b: dispersion crece con l
    mono = {}
    for s in SIGMAS:
        sdv = [cells[(s, l)]["sd_f_d20"] for l in [0, 1, 3, 10]]
        mono[s] = bool(all(sdv[i] < sdv[i + 1] for i in range(3)))
    add("K2-H-b", "La dispersion de la fraccion por chip crece con l (sd(0)<sd(1)<sd(3)<sd(10)) para cada sigma",
        f"monotona por sigma: {mono}", all(mono.values()))

    # K2-C2: rendimiento por chip en d_min(sigma) = d* + 1,645 sigma
    y_dm = {(s, l): cells[(s, l)]["Y95_dmin"] for s in SIGMAS for l in LS}
    maxY = max(y_dm.values()); minY = min(y_dm.values())
    add("K2-C2", "Secundario: rendimiento por chip Y = P(f_chip >= 0,95) >= 0,95 en d_min(sigma) = d* + 1,645 sigma, en las 12 celdas",
        f"Y en [{minY:.3f}, {maxY:.3f}]", minY >= 0.95)

    # ===== K3: residuo tras correccion =====
    d_cal = dstar + Z95 * SIG_RES
    Yc_r = Y_curve(dl_res0)
    d95_cal = first_d_at(DGRID, Yc_r)
    st_cal_dm = stats(passes(d_cal + dl_res0))
    E_cal_ana_dm = E_ana(d_cal, SIG_RES)
    k3 = {"E_mc_d20": st_r["E_mc"], "E_ana_d20": Ea_r, "sd_f_d20": st_r["sd_f"], "P5_f_d20": st_r["P5_f"],
          "Y95_d20": st_r["Y95"], "d_min_cal_um": d_cal, "E_mc_dmin_cal": st_cal_dm["E_mc"],
          "E_ana_dmin_cal": E_cal_ana_dm, "Y95_dmin_cal": st_cal_dm["Y95"], "d_chip95_cal_um": d95_cal,
          "d_min_sigma_um": {str(s): dstar + Z95 * s for s in SIGMAS},
          "comparacion_en_dmin_sigma": {}}
    for s in SIGMAS:
        dm = dstar + Z95 * s
        stc = stats(passes(dm + dl_res0))
        k3["comparacion_en_dmin_sigma"][str(s)] = {"E_cal": stc["E_mc"], "Y95_cal": stc["Y95"],
                                                   "E_K2_l0": cells[(s, 0)]["E_mc_dmin"],
                                                   "Y95_K2_l0": cells[(s, 0)]["Y95_dmin"]}
    out["K3"] = k3

    add("K3-C1", "Residuo sigma_res = 0,2 um: fraccion media en d = 20 um >= 0,95",
        f"E_mc={st_r['E_mc']:.4f} (analitico {Ea_r:.4f})", st_r["E_mc"] >= 0.95)
    add("K3-C2", "Regla de diseno: E analitico en d* + 1,645*0,2 >= 0,95 - 1e-4 y |MC - analitico| < 0,005",
        f"E_ana={E_cal_ana_dm:.6f}, E_mc={st_cal_dm['E_mc']:.4f}",
        (E_cal_ana_dm >= 0.95 - 1e-4) and abs(st_cal_dm["E_mc"] - E_cal_ana_dm) < 0.005)
    min_k2_d20 = min(cells[(s, 0)]["E_mc_d20"] for s in SIGMAS)
    add("K3-C3", "Comparacion en d = 20 um: fraccion con calibracion < min sigma de la fraccion K2 (l=0)",
        f"E_cal={st_r['E_mc']:.4f} vs min K2={min_k2_d20:.4f}", st_r["E_mc"] < min_k2_d20)
    dmins = {s: dstar + Z95 * s for s in SIGMAS}
    add("K3-C4", "La calibracion reduce la separacion de guarda: d_min,cal < d_min(sigma) para cada sigma",
        f"d_min,cal={d_cal:.3f} um; d_min(sigma)={ {s: round(v, 3) for s, v in dmins.items()} } um",
        all(d_cal < dmins[s] for s in SIGMAS))
    add("K3-C5", "Rendimiento por chip con calibracion en d_min,cal: Y = P(f_chip >= 0,95) >= 0,95",
        f"Y={st_cal_dm['Y95']:.3f}", st_cal_dm["Y95"] >= 0.95)

    # ===== sensibilidad: kernel gaussiano (sigma = 1, l en {1,3,10}) =====
    sens = {}
    for l in [1, 3, 10]:
        A = factor(l, "gauss")
        dl = 1.0 * (Z0 @ A.T)
        st_g = stats(passes(D0 + dl))
        dm = dstar + Z95 * 1.0
        Yg = Y_curve(dl)
        sens[f"gauss_l{l}"] = {"E_mc_d20": st_g["E_mc"], "sd_f_d20": st_g["sd_f"],
                               "Y95_dmin_sigma1": stats(passes(dm + dl))["Y95"],
                               "d_chip95_um": first_d_at(DGRID, Yg),
                               "recon_max": _FAC[(l, "gauss")]["recon"],
                               "lam_min_gauss": _FAC[(l, "gauss")]["lam_min"]}
    out["sensibilidad_kernel_gauss_sigma1"] = sens

    # ===== resumen de celdas =====
    cells_out = []
    for s in SIGMAS:
        for l in LS:
            c = cells[(s, l)]
            cells_out.append({k: v for k, v in c.items() if not k.startswith("_")})
    out["K2_celdas"] = cells_out
    out["K2_chip_curvas_Y_d"] = {f"sigma{s}_l{l}": {"d_um": [float(x) for x in DGRID],
                                                    "Y95": cells[(s, l)]["_Y_curve"]}
                                 for s in SIGMAS for l in LS}
    out["K3_curva_Y_d"] = {"d_um": [float(x) for x in DGRID], "Y95": Yc_r}
    out["verificacion"] = {**ver, "max_diff_mc_ana": max_diff_all, "seed_dev_max": seed_dev,
                           "seed_detail": seed_detail,
                           "sign_check_max_abs_E_plus_minus": max(abs(c["E_mc_d20"] - c["E_mc_signo_menos_d20"]) for c in cells.values()),
                           "n_eventos_d_lt_12_total_d20": int(sum(c["n_eventos_d_eff_menor_12"] for c in cells.values())),
                           "n_eventos_d_gt_40_total_d20": int(sum(c["n_eventos_d_eff_mayor_40"] for c in cells.values()))}
    out["criterios"] = crit
    out["tiempo_s"] = round(time.time() - t0, 1)

    path = HERE / "registro_resultados.json"
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    # ---- resumen por consola ----
    print(f"d* = {dstar:.4f} um | delta_max(20) = {dmax:+.4f} um | P2(20) = {P2_nom:.4f} | kappa(20)L = {kap_tab(D0)*L_UM:.4f}")
    print("intervalos caso peor (delta, P2<=0.10):", ints_w)
    print("intervalos caso favorable (delta, P2<=0.10):", [[round(a, 2), round(b, 2)] for a, b in ints_f])
    for c in cells_out:
        print(f"sig={c['sigma_um']:<4} l={c['l_celdas']:<3} E_mc={c['E_mc_d20']:.4f} E_ana={c['E_ana_d20']:.4f} "
              f"sd={c['sd_f_d20']:.4f} P5={c['P5_f_d20']:.4f} Y95(d20)={c['Y95_d20']:.3f} "
              f"d_min={c['d_min_um']:.3f} E_dmin={c['E_mc_dmin']:.4f} Y95(dmin)={c['Y95_dmin']:.3f} d_chip95={c['d_chip95_um']}")
    print(f"K3: E(d20)={st_r['E_mc']:.4f} ana={Ea_r:.4f} | d_min,cal={d_cal:.4f} E={st_cal_dm['E_mc']:.4f} "
          f"Y={st_cal_dm['Y95']:.3f} d_chip95_cal={d95_cal}")
    for c in crit:
        print(f"[{'PASS' if c['pass'] else 'FAIL'}] {c['id']}: {c['value']}")
    print(f"tiempo {out['tiempo_s']} s -> {path}")


if __name__ == "__main__":
    main()
