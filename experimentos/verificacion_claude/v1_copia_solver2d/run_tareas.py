"""Tarea A: ejecuta A1 a A4 de CONTRATO-solver2d.md y evalua los criterios fijados en el contrato.

Ejecucion: OMP_NUM_THREADS=1 python -B run_tareas.py > log_run.txt
Salida: resultados.json (pass calculado por este codigo) y log por consola.
Modelo numerico: no es un dispositivo ni una medida.
"""
import datetime
import json
import pathlib
import time

import numpy as np

from analitico_lp01 import A_UM, LAM_UM, N1, N2, lp01_analytic, lp01_field
from solver2d import cell_average, solve

HERE = pathlib.Path(__file__).resolve().parent
REF_JSON = pathlib.Path("D:/PROJECTS/.cognition/audit/silice-origin-main/experimentos/vectorial_claude/fd_escalar_convergencia.json")
OUT_JSON = HERE / "resultados.json"

H_LIST = [0.5, 0.25, 0.125]
L_MAIN = 40.0   # dominio principal A1 y A3
L_REF = 30.0    # reproduccion de la referencia escalonada
L_DOM = 50.0    # control de dominio (C1.6)
L_A4 = 80.0     # dos nucleos a +-8 um
S_SUB = 8

RUNS = {}
RUN_LOG = []
CRITERIA = []


def hkey(h):
    return f"{h:g}"


def log(msg):
    print(msg, flush=True)


def run(key, shapes, n_bg, L, h, s, n_modes=1):
    t0 = time.time()
    r = solve(shapes, n_bg, LAM_UM, L, h, n_modes=n_modes, s_sub=s)
    dt = time.time() - t0
    RUNS[key] = r
    RUN_LOG.append({"key": key, "L_um": L, "h_um": h, "s_sub": s, "N": r["N"], "incognitas": r["unknowns"],
                    "neff": r["neff"], "beta_um": r["beta_um"], "wall_s": round(dt, 2)})
    log(f"[{key}] L={L} h={h} s={s} N={r['N']} incognitas={r['unknowns']} "
        f"neff={['%.13f' % v for v in r['neff']]} t={dt:.1f}s")
    return r


def criterio(cid, desc, valor, umbral, op="<=", evaluable=True):
    if not evaluable or valor is None or not np.isfinite(valor):
        ok = False
    elif op == "<=":
        ok = bool(valor <= umbral)
    elif op == ">=":
        ok = bool(valor >= umbral)
    elif op == "in":
        ok = bool(umbral[0] <= valor <= umbral[1])
    elif op == ">":
        ok = bool(valor > umbral)
    else:
        raise ValueError(op)
    CRITERIA.append({"id": cid, "descripcion": desc, "valor": None if valor is None else float(valor),
                     "umbral": umbral if isinstance(umbral, (list, tuple)) else float(umbral),
                     "operador": op, "evaluable": bool(evaluable), "pass": ok})
    log(f"  {cid}: valor={valor} umbral={umbral} op={op} evaluable={evaluable} -> pass={ok}")
    return ok


def main():
    t_start = datetime.datetime.now(datetime.timezone.utc)
    log(f"Inicio UTC {t_start.isoformat()}")
    ref = json.loads(REF_JSON.read_text(encoding="utf-8"))
    ref_by_h = {round(float(r["h_um"]), 6): r for r in ref["rows"]}
    ref_err_125 = float(ref_by_h[0.125]["err_abs"])

    ana = lp01_analytic()
    neff_ana = ana["neff"]
    U, W = ana["U"], ana["W"]
    log(f"Analitico: V={ana['V']:.10f} U={U:.12f} W={W:.12f} neff={neff_ana:.16f} "
        f"Gamma_closed={ana['gamma_core_closed']:.12f} Gamma_quad={ana['gamma_core_quad']:.12f}")

    shapes_A1 = [{"kind": "disk", "x0": 0.0, "y0": 0.0, "r": A_UM, "n": N1}]

    # ---------------- A1: convergencia frente a analitica ----------------
    log("== A1: LP01 frente a analitica ==")
    for h in H_LIST:
        run(f"A1_sub_L40_h{hkey(h)}", shapes_A1, N2, L_MAIN, h, S_SUB)
        run(f"A1_stair_L40_h{hkey(h)}", shapes_A1, N2, L_MAIN, h, 1)
        run(f"A1_stair_L30_h{hkey(h)}", shapes_A1, N2, L_REF, h, 1)
    run("A1_sub_L50_h0.25", shapes_A1, N2, L_DOM, 0.25, S_SUB)

    e_sub = {h: abs(RUNS[f"A1_sub_L40_h{hkey(h)}"]["neff"][0] - neff_ana) for h in H_LIST}
    e_st = {h: abs(RUNS[f"A1_stair_L40_h{hkey(h)}"]["neff"][0] - neff_ana) for h in H_LIST}
    e_st30 = {h: abs(RUNS[f"A1_stair_L30_h{hkey(h)}"]["neff"][0] - neff_ana) for h in H_LIST}
    p_sub_b = float(np.log2(e_sub[0.25] / e_sub[0.125]))
    p_sub_a = float(np.log2(e_sub[0.5] / e_sub[0.25]))
    p_st_b = float(np.log2(e_st[0.25] / e_st[0.125]))
    p_st_a = float(np.log2(e_st[0.5] / e_st[0.25]))
    repro = {h: abs(RUNS[f"A1_stair_L30_h{hkey(h)}"]["neff"][0] - ref_by_h[h]["neff_fd"]) for h in H_LIST}
    repro_max = max(repro.values())
    dom_diff = abs(RUNS["A1_sub_L40_h0.25"]["neff"][0] - RUNS["A1_sub_L50_h0.25"]["neff"][0])
    e_sub_125 = e_sub[0.125]

    log(f"  e_sub: {e_sub}")
    log(f"  e_stair_L40: {e_st}")
    log(f"  e_stair_L30: {e_st30} ref_err_125={ref_err_125:.10e}")
    log(f"  ordenes: p_sub(0.5->0.25)={p_sub_a:.4f} p_sub(0.25->0.125)={p_sub_b:.4f} "
        f"p_stair40(0.5->0.25)={p_st_a:.4f} p_stair40(0.25->0.125)={p_st_b:.4f}")
    log(f"  reproduccion referencia max|dif|={repro_max:.3e}; dominio |L40-L50|(h=0.25)={dom_diff:.3e}")

    criterio("C1.1", "e_sub(h=0.125) <= error escalonado de referencia (4.2164e-6)", e_sub_125, ref_err_125)
    criterio("C1.2", "e_sub(h=0.125) <= 1.0e-6 (estricto)", e_sub_125, 1.0e-6)
    criterio("C1.3", "orden observado subpixel (0.25->0.125) >= 1.8", p_sub_b, 1.8, op=">=")
    criterio("C1.4", "orden observado escalonado L=40 (0.25->0.125) en [1.2, 1.6]", p_st_b, [1.2, 1.6], op="in")
    criterio("C1.5", "reproduccion escalonado L=30 frente a JSON de referencia, max|dif| <= 1e-9", repro_max, 1e-9)
    criterio("C1.6", "dominio: |neff(L=40) - neff(L=50)| a h=0.25 <= 1e-7", dom_diff, 1e-7)
    criterio("C1.7", "analitica: |neff - 1.4421921654570133| <= 1e-12",
             abs(neff_ana - 1.4421921654570133), 1e-12)

    # ---------------- A2: normalizacion y simetria ----------------
    log("== A2: normalizacion y simetria (L=40, h=0.125, subpixel) ==")
    r125 = RUNS["A1_sub_L40_h0.125"]
    psi = r125["psi"][0]
    h125 = 0.125
    x125 = r125["x"]
    norm_val = float(np.sum(psi ** 2) * h125 ** 2)
    norm_err = abs(norm_val - 1.0)
    scale = float(np.max(np.abs(psi)))
    xsym = float(np.max(np.abs(psi - psi[:, ::-1])) / scale)
    ysym = float(np.max(np.abs(psi - psi[::-1, :])) / scale)
    border_max = float(max(np.max(np.abs(psi[0, :])), np.max(np.abs(psi[-1, :])),
                           np.max(np.abs(psi[:, 0])), np.max(np.abs(psi[:, -1]))))
    log(f"  sum|psi|^2 h^2 = {norm_val:.16f}; asim_x={xsym:.3e}; asim_y={ysym:.3e}; borde={border_max:.3e}")
    criterio("C2.1", "|sum |psi|^2 h^2 - 1| <= 1e-10", norm_err, 1e-10)
    criterio("C2.2", "asimetria en x relativa <= 1e-6", xsym, 1e-6)
    criterio("C2.3", "asimetria en y relativa <= 1e-6", ysym, 1e-6)
    criterio("C2.4", "max |psi| en contorno = 0", border_max, 0.0)

    # ---------------- A3: observable de potencia en el nucleo ----------------
    log("== A3: observable de potencia en el nucleo ==")
    gc = ana["gamma_core_closed"]
    gq = ana["gamma_core_quad"]
    err_c_q = abs(gc - gq) / gq
    criterio("C3.1", "|Gamma_cerrada - Gamma_quad| / Gamma_quad <= 1e-8", err_c_q, 1e-8)

    def indicator(X, Y):
        return (np.hypot(X, Y) < A_UM).astype(float)

    def gamma_fd(run_r, h):
        cov = cell_average(indicator, run_r["x"], h, S_SUB)
        p = run_r["psi"][0]
        return float(np.sum(cov * p ** 2) / np.sum(p ** 2))

    def gamma_analytic_nodes(run_r, h):
        cov = cell_average(indicator, run_r["x"], h, S_SUB)
        X, Y = np.meshgrid(run_r["x"], run_r["y"])
        pa = lp01_field(X, Y, U, W, a=A_UM)
        return float(np.sum(cov * pa ** 2) / np.sum(pa ** 2))

    g_fd = {}
    g_an = {}
    err_fd = {}
    err_an = {}
    for h in [0.25, 0.125]:
        rr = RUNS[f"A1_sub_L40_h{hkey(h)}"]
        g_fd[h] = gamma_fd(rr, h)
        g_an[h] = gamma_analytic_nodes(rr, h)
        err_fd[h] = abs(g_fd[h] - gc) / gc
        err_an[h] = abs(g_an[h] - gc) / gc
        log(f"  h={h}: Gamma_FD={g_fd[h]:.12f} Gamma_obs(psi_analitica)={g_an[h]:.12f} "
            f"err_rel_FD={err_fd[h]:.3e} err_rel_observable={err_an[h]:.3e}")
    log(f"  Gamma_exacta={gc:.12f}")
    p3 = float(np.log2(err_fd[0.25] / err_fd[0.125])) if (err_fd[0.25] > 1e-9 and err_fd[0.125] > 1e-9) else None
    evaluable3 = p3 is not None
    criterio("C3.2", "error relativo Gamma_FD(h=0.125) frente a Gamma exacta <= 1e-3",
             err_fd[0.125], 1e-3)
    criterio("C3.3", "orden del error relativo (0.25->0.125) >= 1.5 (evaluable si ambos > 1e-9)",
             p3 if evaluable3 else None, 1.5, op=">=", evaluable=evaluable3)

    # ---------------- A4: dos nucleos (informativa, con criterios de signo y paridad) ----------------
    log("== A4: dos nucleos a +-8 um (solo informa; criterios de signo y paridad) ==")
    shapes_A4 = [{"kind": "disk", "x0": -8.0, "y0": 0.0, "r": A_UM, "n": N1},
                 {"kind": "disk", "x0": 8.0, "y0": 0.0, "r": A_UM, "n": N1}]
    a4 = {}
    for h in [0.5, 0.25]:
        rr = run(f"A4_sub_L80_h{hkey(h)}", shapes_A4, N2, L_A4, h, S_SUB, n_modes=2)
        ev, od = [], []
        for p in rr["psi"]:
            sc = float(np.max(np.abs(p)))
            ev.append(float(np.max(np.abs(p - p[:, ::-1])) / sc))
            od.append(float(np.max(np.abs(p + p[:, ::-1])) / sc))
        ie = int(np.argmin(ev))
        io = 1 - ie
        n_par = rr["neff"][ie]
        n_imp = rr["neff"][io]
        dn = n_par - n_imp
        kappa = rr["k0_um"] * dn / 2.0
        a4[hkey(h)] = {"neff_par": n_par, "neff_impar": n_imp, "delta_n": dn, "kappa_FD_um_inv": kappa,
                       "asim_par_x": ev[ie], "asim_impar_x": od[io],
                       "neff_lista": rr["neff"], "L_um": L_A4, "s_sub": S_SUB}
        log(f"  h={h}: n_par={n_par:.10f} n_impar={n_imp:.10f} dn={dn:.6e} kappa_FD={kappa:.6e} 1/um "
            f"asim_par={ev[ie]:.2e} asim_impar={od[io]:.2e}")
        criterio(f"C4.1_h{hkey(h)}", f"n_par - n_impar > 0 (h={h})", dn, 0.0, op=">")
        criterio(f"C4.2_h{hkey(h)}", f"paridad: asim par <= 1e-5 y asim impar <= 1e-5 (h={h})",
                 max(ev[ie], od[io]), 1e-5)
    kappa_diff = a4["0.25"]["kappa_FD_um_inv"] - a4["0.5"]["kappa_FD_um_inv"]
    log(f"  kappa(0.25)-kappa(0.5) = {kappa_diff:.6e} 1/um (solo informativo)")

    # ---------------- salida ----------------
    n_pass = sum(1 for c in CRITERIA if c["pass"])
    out = {
        "tarea": "A",
        "contrato": "CONTRATO-solver2d.md",
        "naturaleza": "modelo numerico escalar; no es dispositivo ni medida",
        "inicio_utc": t_start.isoformat(),
        "fin_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "referencia_json": str(REF_JSON),
        "analitico_lp01": ana,
        "A1": {
            "n_eff_sub_L40": {hkey(h): RUNS[f"A1_sub_L40_h{hkey(h)}"]["neff"][0] for h in H_LIST},
            "error_abs_sub_L40": {hkey(h): e_sub[h] for h in H_LIST},
            "error_abs_stair_L40": {hkey(h): e_st[h] for h in H_LIST},
            "error_abs_stair_L30": {hkey(h): e_st30[h] for h in H_LIST},
            "orden_sub_0.5_0.25": p_sub_a,
            "orden_sub_0.25_0.125": p_sub_b,
            "orden_stair_L40_0.5_0.25": p_st_a,
            "orden_stair_L40_0.25_0.125": p_st_b,
            "reproduccion_max_dif_vs_ref": repro_max,
            "reproduccion_dif_por_h": {hkey(h): repro[h] for h in H_LIST},
            "dominio_dif_L40_L50_h025": dom_diff,
            "ref_error_stair_125": ref_err_125,
        },
        "A2": {
            "norm_sum_psi2_h2": norm_val,
            "asim_x_rel": xsym,
            "asim_y_rel": ysym,
            "borde_max_abs": border_max,
        },
        "A3": {
            "gamma_exacta_cerrada": gc,
            "gamma_exacta_quad": gq,
            "err_rel_cerrada_vs_quad": err_c_q,
            "gamma_FD": {hkey(h): g_fd[h] for h in g_fd},
            "gamma_observable_psi_analitica_nodos": {hkey(h): g_an[h] for h in g_an},
            "err_rel_FD": {hkey(h): err_fd[h] for h in err_fd},
            "err_rel_observable_solo": {hkey(h): err_an[h] for h in err_an},
            "orden_err_FD_0.25_0.125": p3,
        },
        "A4": {"resultados": a4, "kappa_diff_0.25_menos_0.5_um_inv": kappa_diff,
               "h_0.125_no_ejecutado": "1,6 M incognitas; RAM libre ~2,1 GB a las 03:30 UTC"},
        "runs": RUN_LOG,
        "criterios": CRITERIA,
        "resumen": {"n_criterios": len(CRITERIA), "n_pass": n_pass, "n_fail": len(CRITERIA) - n_pass},
    }
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False, default=float), encoding="utf-8")
    log(f"Criterios: {n_pass}/{len(CRITERIA)} pass. Salida: {OUT_JSON}")
    log(f"Fin UTC {datetime.datetime.now(datetime.timezone.utc).isoformat()}")


if __name__ == "__main__":
    main()
