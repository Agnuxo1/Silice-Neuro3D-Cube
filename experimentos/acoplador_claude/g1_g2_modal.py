"""TAREA G, G1 y G2: base modal (supermodos par/impar) y contraste del prefactor de T8.

Modelo numerico escalar. No es un dispositivo ni una medida. Un hilo, CPU.
Contrato: CONTRATO-acoplador.md (secciones 3 y 7). Umbrales fijados antes de calcular.

Importa (no copia): solver2d (experimentos/solver2d_claude), analitico_lp01 (idem),
acoplo_paralelo (experimentos/acoplo_claude). Salida: resultados_g1_g2.json (en esta carpeta).
"""
import datetime
import hashlib
import json
import pathlib
import sys
import time

import numpy as np

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
EXP = HERE.parent
for sub in ("solver2d_claude", "acoplo_claude"):
    sys.path.insert(0, str(EXP / sub))
import solver2d as S2          # noqa: E402  (experimentos/solver2d_claude/solver2d.py)
import analitico_lp01 as AN    # noqa: E402  (experimentos/solver2d_claude/analitico_lp01.py)
import acoplo_paralelo as AP   # noqa: E402  (experimentos/acoplo_claude/acoplo_paralelo.py)

LAM, A, N1, N2 = 1.55, 6.0, 1.444, 1.439
K0 = 2.0 * np.pi / LAM
D_LIST = [14.0, 16.0, 20.0]
L_MAIN, H_MAIN, H_CONV = 40.0, 0.125, 0.25
L_ENM, H_BPM = 40.4, 0.2          # enmienda E-1 para el caso de un nucleo (G1.5)
L_DOM = 50.0                      # G1.4

TOL_PARITY, TOL_H, TOL_DOM, TOL_NEFF1, TOL_G2 = 1e-5, 0.05, 0.05, 1e-5, 0.10


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def two_core(d):
    return [
        {"kind": "disk", "x0": -d / 2.0, "y0": 0.0, "r": A, "n": N1},
        {"kind": "disk", "x0": +d / 2.0, "y0": 0.0, "r": A, "n": N1},
    ]


def parity_errs(psi):
    """Errores relativos de paridad par e impar en x (psi[iy, ix], espejo = columnas invertidas)."""
    m = float(np.max(np.abs(psi)))
    mir = psi[:, ::-1]
    e_even = float(np.max(np.abs(psi - mir)) / m)
    e_odd = float(np.max(np.abs(psi + mir)) / m)
    return e_even, e_odd


def supermodes(d, h, L):
    """Dos modos mas guiados del par de nucleos. Devuelve par/impar segun paridad medida."""
    t0 = time.time()
    res = S2.solve(two_core(d), N2, LAM, L, h, n_modes=2, s_sub=8)
    dt = time.time() - t0
    modes = []
    for m in range(2):
        e_e, e_o = parity_errs(res["psi"][m])
        modes.append({"index_solver": m, "neff": res["neff"][m], "err_even": e_e, "err_odd": e_o})
    # el modo par es el que tiene menor error de paridad par (asignacion por paridad medida)
    if modes[0]["err_even"] <= modes[1]["err_even"]:
        par, imp = modes[0], modes[1]
    else:
        par, imp = modes[1], modes[0]
    kappa = K0 * (par["neff"] - imp["neff"]) / 2.0
    return {
        "d_um": d, "h_um": h, "L_um": L, "N": int(res["N"]), "unknowns": int(res["unknowns"]),
        "neff_par": par["neff"], "neff_imp": imp["neff"],
        "err_parity_par_even": par["err_even"], "err_parity_imp_odd": imp["err_odd"],
        "par_has_higher_neff": bool(par["neff"] > imp["neff"]),
        "kappa_FD_per_um": kappa, "time_s": round(dt, 2),
    }


def main():
    t_start = utc()
    print(f"[{t_start}] inicio G1/G2", flush=True)
    out = {
        "task": "G1 base modal + G2 prefactor T8",
        "started_utc": t_start,
        "files_sha256": {
            "solver2d.py": sha256(EXP / "solver2d_claude" / "solver2d.py"),
            "analitico_lp01.py": sha256(EXP / "solver2d_claude" / "analitico_lp01.py"),
            "acoplo_paralelo.py": sha256(EXP / "acoplo_claude" / "acoplo_paralelo.py"),
        },
        "params": {"lam_um": LAM, "a_um": A, "n1": N1, "n2": N2, "k0_per_um": K0,
                   "s_sub": 8, "d_list_um": D_LIST, "L_main_um": L_MAIN, "h_main_um": H_MAIN,
                   "h_conv_um": H_CONV, "L_dom_um": L_DOM},
        "thresholds": {"G1.1_parity": TOL_PARITY, "G1.2_sign": "n_par - n_imp > 0",
                       "G1.3_h": TOL_H, "G1.4_domain": TOL_DOM, "G1.5_neff_single": TOL_NEFF1,
                       "G2.1_ratio": TOL_G2},
    }

    an = AN.lp01_analytic()
    out["analytic_lp01"] = {"neff": an["neff"], "U": an["U"], "W": an["W"]}

    # G1.5: un nucleo centrado (referencia analitica), h = 0,2, L = 40,4 (enmienda E-1)
    t0 = time.time()
    single = S2.solve([{"kind": "disk", "x0": 0.0, "y0": 0.0, "r": A, "n": N1}], N2, LAM,
                      L_ENM, H_BPM, n_modes=1, s_sub=8)
    g15_diff = abs(single["neff"][0] - an["neff"])
    out["G1_5_single_core"] = {"neff_FD": single["neff"][0], "neff_analytic": an["neff"],
                               "abs_diff": g15_diff, "h_um": H_BPM, "L_um": L_ENM,
                               "N": int(single["N"]), "time_s": round(time.time() - t0, 2),
                               "pass": bool(g15_diff <= TOL_NEFF1)}
    print("G1.5", out["G1_5_single_core"], flush=True)

    # G1.1, G1.2: supermodos a h = 0,125, L = 40 (principal)
    main_runs = {}
    for d in D_LIST:
        r = supermodes(d, H_MAIN, L_MAIN)
        main_runs[str(d)] = r
        print("main", d, r, flush=True)
    out["G1_main_h0125"] = main_runs

    # G1.3: convergencia en h, a h = 0,25 (mismo dominio)
    conv_runs = {}
    for d in D_LIST:
        r = supermodes(d, H_CONV, L_MAIN)
        conv_runs[str(d)] = r
        print("conv", d, r, flush=True)
    out["G1_conv_h0250"] = conv_runs

    # G1.4: dominio, d = 20, h = 0,25, L = 40 frente a L = 50
    dom40 = conv_runs["20.0"]
    dom50 = supermodes(20.0, H_CONV, L_DOM)
    print("dom50", dom50, flush=True)
    out["G1_domain_d20_h0250"] = {"L40": dom40, "L50": dom50}

    # G2: prefactor frente a kappa(d) de acoplo_paralelo (um^-1)
    g2 = {}
    for d in D_LIST:
        k_fd = main_runs[str(d)]["kappa_FD_per_um"]
        k_fd_c = conv_runs[str(d)]["kappa_FD_per_um"]
        k_mod = float(AP.kappa(float(d)))
        ratio = k_fd / k_mod
        ratio_lit2 = k_fd / (2.0 * k_mod)
        Lc_fd_mm = float(np.pi / (2.0 * k_fd) / 1000.0)
        P2_fd_10mm = float(np.sin(k_fd * 10000.0) ** 2)
        P2_model_10mm = float(np.sin(k_mod * 10000.0) ** 2)
        g2[str(d)] = {
            "kappa_FD_per_um": k_fd, "kappa_FD_h0250_per_um": k_fd_c,
            "kappa_model_per_um": k_mod,
            "ratio_FD_over_model": ratio, "ratio_FD_over_2model_informativo": ratio_lit2,
            "rel_dev_G2_1": abs(ratio - 1.0),
            "kappa_FD_per_mm": k_fd * 1000.0, "kappa_model_per_mm": k_mod * 1000.0,
            "Lc_FD_mm": Lc_fd_mm, "Lc_model_mm": float(np.pi / (2.0 * k_mod) / 1000.0),
            "P2_FD_at_10mm": P2_fd_10mm, "P2_model_at_10mm": P2_model_10mm,
            "pass_G2_1": bool(abs(ratio - 1.0) < TOL_G2),
        }
        print("G2", d, g2[str(d)], flush=True)
    out["G2_prefactor"] = g2

    # Criterios G1 evaluados por el codigo
    par_ok = all(max(main_runs[k]["err_parity_par_even"], main_runs[k]["err_parity_imp_odd"]) <= TOL_PARITY
                 for k in main_runs)
    sign_ok = all(main_runs[k]["neff_par"] - main_runs[k]["neff_imp"] > 0 for k in main_runs)
    h_ok = all(abs(main_runs[k]["kappa_FD_per_um"] - conv_runs[k]["kappa_FD_per_um"])
               / abs(main_runs[k]["kappa_FD_per_um"]) <= TOL_H for k in main_runs)
    dom_rel = abs(dom50["kappa_FD_per_um"] - dom40["kappa_FD_per_um"]) / abs(dom40["kappa_FD_per_um"])
    dom_ok = dom_rel <= TOL_DOM
    g15_ok = out["G1_5_single_core"]["pass"]
    g21_ok = all(g2[k]["pass_G2_1"] for k in g2)

    out["criteria"] = {
        "G1.1_parity": {"value_max": max(max(main_runs[k]["err_parity_par_even"],
                                             main_runs[k]["err_parity_imp_odd"]) for k in main_runs),
                        "threshold": TOL_PARITY, "pass": bool(par_ok)},
        "G1.2_sign": {"values": {k: main_runs[k]["neff_par"] - main_runs[k]["neff_imp"] for k in main_runs},
                      "pass": bool(sign_ok)},
        "G1.3_h": {"values_rel": {k: abs(main_runs[k]["kappa_FD_per_um"] - conv_runs[k]["kappa_FD_per_um"])
                                  / abs(main_runs[k]["kappa_FD_per_um"]) for k in main_runs},
                   "threshold": TOL_H, "pass": bool(h_ok)},
        "G1.4_domain_d20": {"value_rel": dom_rel, "threshold": TOL_DOM, "pass": bool(dom_ok)},
        "G1.5_single_core": {"value_abs": g15_diff, "threshold": TOL_NEFF1, "pass": bool(g15_ok)},
        "G2.1_prefactor": {"values": {k: g2[k]["ratio_FD_over_model"] for k in g2},
                           "threshold_rel_dev": TOL_G2, "pass": bool(g21_ok)},
    }
    out["G1_all_pass"] = bool(par_ok and sign_ok and h_ok and dom_ok and g15_ok)
    out["G2_all_pass"] = bool(g21_ok)
    out["finished_utc"] = utc()
    (HERE / "resultados_g1_g2.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                                                encoding="utf-8", newline="\n")
    print("G1_all_pass", out["G1_all_pass"], "G2_all_pass", out["G2_all_pass"], flush=True)
    print("escrito resultados_g1_g2.json", flush=True)


if __name__ == "__main__":
    main()
