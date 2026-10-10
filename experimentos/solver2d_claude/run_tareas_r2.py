"""Tarea A2, ronda 2: ejecuta A1-A4 de CONTRATO-solver2d-r2.md y evalua los criterios fijados en el contrato.

Ejecucion: OMP_NUM_THREADS=1 python -B run_tareas_r2.py > log_run_r2.txt
Salida: resultados_solver2d.json (pass calculado por este codigo).
Modelo numerico escalar: no es un dispositivo ni una medida.
run_tareas.py (ronda 1) no se modifica.
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import ctypes
import datetime
import json
import pathlib
import time

import numpy as np

from analitico_lp01 import A_UM, LAM_UM, N1, N2, lp01_analytic, lp01_field
from solver2d import cell_average, solve

HERE = pathlib.Path(__file__).resolve().parent
REF_JSON = HERE.parent / "vectorial_claude" / "fd_escalar_convergencia.json"
OUT_JSON = HERE / "resultados_solver2d.json"
UTC = datetime.timezone.utc

H_LIST = [0.5, 0.25, 0.125]
L_MAIN = 40.0   # dominio principal A1, A2, A3
L_REF = 30.0    # reproduccion de la referencia escalonada (C1.5)
L_DOM = 50.0    # control de dominio (C1.6)
L_A4 = 80.0     # dos nucleos a +-8 um
S_SUB = 8

# Umbrales del CONTRATO-solver2d-r2.md (seccion 3). No se editan tras ver resultados.
UMB_C12 = 1.0e-6
UMB_C13 = 1.8
UMB_C13B_LO, UMB_C13B_HI = 1.8, 2.2
UMB_C14_LO, UMB_C14_HI = 1.2, 1.6
UMB_C15 = 1e-9
UMB_C16 = 1e-7
UMB_C17_NEFF = 1.4421921654570133
UMB_C17_TOL = 1e-12
UMB_C21 = 1e-10
UMB_C22 = 1e-6
UMB_C23 = 1e-6
UMB_C25 = -1e-9
UMB_C31 = 1e-8
UMB_C32 = 1e-3
UMB_C33 = 1.5
UMB_C33_MIN_ERR = 1e-9
UMB_C41_DN = 0.0
UMB_C42 = 1e-5
RAM_MIN_GB = 4.0
HORA_LIMITE_A4_H0125 = (5, 20)   # 05:20 UTC

RUNS = {}
RUN_LOG = []
CRITERIA = []


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def free_ram_gb():
    """RAM fisica libre en GB (Windows, API de sistema; sin dependencias)."""
    try:
        st = MEMORYSTATUSEX()
        st.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st)):
            return None
        return st.ullAvailPhys / 1e9
    except Exception:
        return None


def utc_now():
    return datetime.datetime.now(UTC)


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


def criterio(cid, desc, valor, umbral, op="<=", evaluable=True, rol="vinculante"):
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
    CRITERIA.append({"id": cid, "descripcion": desc, "rol": rol,
                     "valor": None if valor is None else float(valor),
                     "umbral": list(umbral) if isinstance(umbral, (list, tuple)) else float(umbral),
                     "operador": op, "evaluable": bool(evaluable), "pass": ok})
    log(f"  {cid} [{rol}]: valor={valor} umbral={umbral} op={op} evaluable={evaluable} -> pass={ok}")
    return ok


def criterio_banda_ambos(cid, desc, valores, lo, hi, rol="adicional_brief"):
    """Banda [lo, hi] que deben cumplir TODOS los valores (p.ej. los dos pares de orden)."""
    ok = all(np.isfinite(v) and (lo <= v <= hi) for v in valores)
    CRITERIA.append({"id": cid, "descripcion": desc, "rol": rol,
                     "valor": [float(v) for v in valores], "umbral": [lo, hi],
                     "operador": "banda_en_todos", "evaluable": True, "pass": bool(ok)})
    log(f"  {cid} [{rol}]: valores={valores} banda=[{lo}, {hi}] -> pass={ok}")
    return ok


def a4_eval(rr, h):
    """Par = modo con menor asimetria bajo x -> -x. Impar = el otro (2 modos)."""
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
    return {"h_um": h, "neff_par": n_par, "neff_impar": n_imp, "delta_n": dn,
            "kappa_FD_um_inv": kappa, "asim_par_x": ev[ie], "asim_impar_x": od[io],
            "neff_lista": rr["neff"], "L_um": L_A4, "s_sub": S_SUB,
            "incognitas": rr["unknowns"]}


def build_out(t_start, ana, ref_err_125, res_A1, res_A2, res_A3, res_A4, kappa_diff, extra_h0125):
    status = "done" if all(c["evaluable"] for c in CRITERIA) else "partial"
    n_pass = sum(1 for c in CRITERIA if c["pass"])
    return {
        "tarea": "A2 ronda 2",
        "contrato": "CONTRATO-solver2d-r2.md",
        "naturaleza": "modelo numerico escalar; no es dispositivo ni medida",
        "estado": status,
        "inicio_utc": t_start.isoformat(),
        "fin_utc": utc_now().isoformat(),
        "referencia_json": str(REF_JSON),
        "analitico_lp01": ana,
        "A1": res_A1 | {"ref_error_stair_125": ref_err_125},
        "A2": res_A2,
        "A3": res_A3,
        "A4": {"resultados": res_A4, "kappa_diff_0.25_menos_0.5_um_inv": kappa_diff,
               "h_0.125": extra_h0125},
        "supuestos": [
            "Solver escalar, no vectorial; solve() de solver2d.py sin cambios.",
            "Analitica LP01 escalar exacta para n por tramos; no es modo vectorial TE/TM.",
            "Dirichlet en contorno de L = 40 um (A1-A3) y L = 80 um (A4); el error de dominio se controla con C1.6 (L=40 frente a L=50 a h=0,25), no se demuestra.",
            "Subpixel s = 8 fijado; no se optimiza.",
            "C1.1 usa el error escalonado del JSON de referencia de la ronda previa (no recalculado); C1.5 si recalcula el escalonado L=30.",
            "No hay medidas: ninguna cifra es dato de laboratorio.",
        ],
        "runs": RUN_LOG,
        "criterios": CRITERIA,
        "resumen": {"n_criterios": len(CRITERIA), "n_pass": n_pass, "n_fail": len(CRITERIA) - n_pass,
                    "n_evaluables": sum(1 for c in CRITERIA if c["evaluable"])},
    }


def main():
    t_start = utc_now()
    log(f"Inicio UTC {t_start.isoformat()}")
    ref = json.loads(REF_JSON.read_text(encoding="utf-8"))
    ref_by_h = {round(float(r["h_um"]), 6): r for r in ref["rows"]}
    ref_err_125 = float(ref_by_h[0.125]["err_abs"])
    log(f"Referencia: err_abs(0.125) escalonado = {ref_err_125:.10e}")

    ana = lp01_analytic()
    neff_ana = ana["neff"]
    U, W = ana["U"], ana["W"]
    log(f"Analitico: V={ana['V']:.10f} U={U:.12f} W={W:.12f} neff={neff_ana:.16f} "
        f"Gamma_closed={ana['gamma_core_closed']:.12f} Gamma_quad={ana['gamma_core_quad']:.12f}")

    shapes_A1 = [{"kind": "disk", "x0": 0.0, "y0": 0.0, "r": A_UM, "n": N1}]

    # ---------------- A1 ----------------
    log("== A1: LP01 frente a analitica ==")
    for h in H_LIST:
        run(f"A1_sub_L40_h{hkey(h)}", shapes_A1, N2, L_MAIN, h, S_SUB)
        run(f"A1_stair_L40_h{hkey(h)}", shapes_A1, N2, L_MAIN, h, 1)
        run(f"A1_stair_L30_h{hkey(h)}", shapes_A1, N2, L_REF, h, 1)
    run("A1_sub_L50_h0.25", shapes_A1, N2, L_DOM, 0.25, S_SUB)

    e_sub = {h: abs(RUNS[f"A1_sub_L40_h{hkey(h)}"]["neff"][0] - neff_ana) for h in H_LIST}
    e_st = {h: abs(RUNS[f"A1_stair_L40_h{hkey(h)}"]["neff"][0] - neff_ana) for h in H_LIST}
    e_st30 = {h: abs(RUNS[f"A1_stair_L30_h{hkey(h)}"]["neff"][0] - neff_ana) for h in H_LIST}
    p_sub_a = float(np.log2(e_sub[0.5] / e_sub[0.25]))     # 0,5 -> 0,25
    p_sub_b = float(np.log2(e_sub[0.25] / e_sub[0.125]))   # 0,25 -> 0,125
    p_st_a = float(np.log2(e_st[0.5] / e_st[0.25]))
    p_st_b = float(np.log2(e_st[0.25] / e_st[0.125]))
    repro = {h: abs(RUNS[f"A1_stair_L30_h{hkey(h)}"]["neff"][0] - ref_by_h[h]["neff_fd"]) for h in H_LIST}
    repro_max = max(repro.values())
    dom_diff = abs(RUNS["A1_sub_L40_h0.25"]["neff"][0] - RUNS["A1_sub_L50_h0.25"]["neff"][0])

    log(f"  e_sub={e_sub}")
    log(f"  e_stair_L40={e_st}")
    log(f"  e_stair_L30={e_st30}")
    log(f"  ordenes subpixel: p(0.5->0.25)={p_sub_a:.6f} p(0.25->0.125)={p_sub_b:.6f}")
    log(f"  ordenes escalonado L40: p(0.5->0.25)={p_st_a:.6f} p(0.25->0.125)={p_st_b:.6f}")
    log(f"  reproduccion referencia max|dif|={repro_max:.3e}; dominio |L40-L50|(h=0.25)={dom_diff:.3e}")

    criterio("C1.1", "e_sub(h=0.125) <= error escalonado de referencia (4.2164e-6) [r1]",
             e_sub[0.125], ref_err_125, rol="vinculante")
    criterio("C1.2", "e_sub(h=0.125) <= 1.0e-6 (estricto) [r1]", e_sub[0.125], UMB_C12)
    criterio("C1.3", "orden subpixel (0.25->0.125) >= 1.8 [r1, VINCULANTE]", p_sub_b, UMB_C13, op=">=")
    criterio_banda_ambos("C1.3b", "orden subpixel en [1.8, 2.2] en AMBOS pares (0.5->0.25 y 0.25->0.125) [brief, adicional]",
                         [p_sub_a, p_sub_b], UMB_C13B_LO, UMB_C13B_HI)
    criterio("C1.4", "orden escalonado L=40 (0.25->0.125) en [1.2, 1.6] [r1]", p_st_b,
             [UMB_C14_LO, UMB_C14_HI], op="in")
    criterio("C1.5", "reproduccion escalonado L=30 frente a JSON de referencia, max|dif| <= 1e-9 [r1]",
             repro_max, UMB_C15)
    criterio("C1.6", "dominio: |neff(L=40) - neff(L=50)| a h=0.25 <= 1e-7 [r1]", dom_diff, UMB_C16)
    criterio("C1.7", "analitica: |neff - 1.4421921654570133| <= 1e-12 [r1]",
             abs(neff_ana - UMB_C17_NEFF), UMB_C17_TOL)

    res_A1 = {
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
    }

    # ---------------- A2 ----------------
    log("== A2: normalizacion, simetria y forma del modo (L=40, h=0.125, subpixel) ==")
    r125 = RUNS["A1_sub_L40_h0.125"]
    psi = r125["psi"][0]
    norm_val = float(np.sum(psi ** 2) * 0.125 ** 2)
    norm_err = abs(norm_val - 1.0)
    scale = float(np.max(np.abs(psi)))
    xsym = float(np.max(np.abs(psi - psi[:, ::-1])) / scale)
    ysym = float(np.max(np.abs(psi - psi[::-1, :])) / scale)
    border_max = float(max(np.max(np.abs(psi[0, :])), np.max(np.abs(psi[-1, :])),
                           np.max(np.abs(psi[:, 0])), np.max(np.abs(psi[:, -1]))))
    min_rel = float(np.min(psi) / np.max(psi))
    log(f"  sum|psi|^2 h^2 = {norm_val:.16f}; asim_x={xsym:.3e}; asim_y={ysym:.3e}; "
        f"borde={border_max:.3e}; min/max={min_rel:.3e}")
    criterio("C2.1", "|sum |psi|^2 h^2 - 1| <= 1e-10 [r1]", norm_err, UMB_C21)
    criterio("C2.2", "asimetria en x relativa <= 1e-6 [r1]", xsym, UMB_C22)
    criterio("C2.3", "asimetria en y relativa <= 1e-6 [r1]", ysym, UMB_C23)
    criterio("C2.4", "max |psi| en contorno = 0 [r1]", border_max, 0.0)
    criterio("C2.5", "min(psi)/max(psi) >= -1e-9 (LP01 sin cambios de signo) [nuevo r2, diagnostico]",
             min_rel, UMB_C25, op=">=")
    res_A2 = {"norm_sum_psi2_h2": norm_val, "asim_x_rel": xsym, "asim_y_rel": ysym,
              "borde_max_abs": border_max, "min_sobre_max": min_rel}

    # ---------------- A3 ----------------
    log("== A3: observable de potencia en el nucleo ==")
    gc = ana["gamma_core_closed"]
    gq = ana["gamma_core_quad"]
    err_c_q = abs(gc - gq) / gq
    criterio("C3.1", "|Gamma_cerrada - Gamma_quad| / Gamma_quad <= 1e-8 [r1]", err_c_q, UMB_C31)

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

    g_fd, g_an, err_fd, err_an = {}, {}, {}, {}
    for h in [0.25, 0.125]:
        rr = RUNS[f"A1_sub_L40_h{hkey(h)}"]
        g_fd[h] = gamma_fd(rr, h)
        g_an[h] = gamma_analytic_nodes(rr, h)
        err_fd[h] = abs(g_fd[h] - gc) / gc
        err_an[h] = abs(g_an[h] - gc) / gc
        log(f"  h={h}: Gamma_FD={g_fd[h]:.12f} Gamma_obs(psi_analitica)={g_an[h]:.12f} "
            f"err_rel_FD={err_fd[h]:.3e} err_rel_observable={err_an[h]:.3e}")
    log(f"  Gamma_exacta={gc:.12f}")
    evaluable3 = err_fd[0.25] > UMB_C33_MIN_ERR and err_fd[0.125] > UMB_C33_MIN_ERR
    p3 = float(np.log2(err_fd[0.25] / err_fd[0.125])) if evaluable3 else None
    criterio("C3.2", "error relativo Gamma_FD(h=0.125) frente a Gamma exacta <= 1e-3 [r1, criterio principal]",
             err_fd[0.125], UMB_C32)
    criterio("C3.3", "orden del error relativo (0.25->0.125) >= 1.5 (evaluable si ambos > 1e-9) [r1]",
             p3, UMB_C33, op=">=", evaluable=evaluable3)
    res_A3 = {
        "gamma_exacta_cerrada": gc, "gamma_exacta_quad": gq, "err_rel_cerrada_vs_quad": err_c_q,
        "gamma_FD": {hkey(h): g_fd[h] for h in g_fd},
        "gamma_observable_psi_analitica_nodos": {hkey(h): g_an[h] for h in g_an},
        "err_rel_FD": {hkey(h): err_fd[h] for h in err_fd},
        "err_rel_observable_solo": {hkey(h): err_an[h] for h in err_an},
        "orden_err_FD_0.25_0.125": p3,
    }

    # ---------------- A4 ----------------
    log("== A4: dos nucleos a +-8 um (h=0.5 y 0.25 vinculantes) ==")
    shapes_A4 = [{"kind": "disk", "x0": -8.0, "y0": 0.0, "r": A_UM, "n": N1},
                 {"kind": "disk", "x0": 8.0, "y0": 0.0, "r": A_UM, "n": N1}]
    a4 = {}
    for h in [0.5, 0.25]:
        rr = run(f"A4_sub_L80_h{hkey(h)}", shapes_A4, N2, L_A4, h, S_SUB, n_modes=2)
        a4[hkey(h)] = a4_eval(rr, h)
        ev = a4[hkey(h)]
        log(f"  h={h}: n_par={ev['neff_par']:.10f} n_impar={ev['neff_impar']:.10f} dn={ev['delta_n']:.6e} "
            f"kappa_FD={ev['kappa_FD_um_inv']:.6e} 1/um asim_par={ev['asim_par_x']:.2e} "
            f"asim_impar={ev['asim_impar_x']:.2e}")
        criterio(f"C4.1_h{hkey(h)}", f"n_par - n_impar > 0 (h={h}) [r1]", ev["delta_n"], UMB_C41_DN, op=">")
        criterio(f"C4.2_h{hkey(h)}", f"paridad: asim par <= 1e-5 y asim impar <= 1e-5 (h={h}) [r1]",
                 max(ev["asim_par_x"], ev["asim_impar_x"]), UMB_C42)
    kappa_diff = a4["0.25"]["kappa_FD_um_inv"] - a4["0.5"]["kappa_FD_um_inv"]
    log(f"  kappa(0.25)-kappa(0.5) = {kappa_diff:.6e} 1/um (solo informativo)")

    # Salida intermedia: los criterios vinculantes ya estan escritos.
    extra_h0125 = {"ejecutado": False, "motivo": "pendiente de comprobacion de RAM y hora"}
    out = build_out(t_start, ana, ref_err_125, res_A1, res_A2, res_A3,
                    a4, kappa_diff, extra_h0125)
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False, default=float), encoding="utf-8")
    log(f"Salida intermedia escrita: {OUT_JSON}")

    # ---------------- A4 opcional con h = 0.125 (JEV q_alcance_A4, respuesta B) ----------------
    free_gb = free_ram_gb()
    now = utc_now()
    hora_ok = (now.hour, now.minute) < HORA_LIMITE_A4_H0125
    ram_ok = free_gb is not None and free_gb >= RAM_MIN_GB
    log(f"== A4 opcional h=0.125: RAM libre={free_gb} GB (min {RAM_MIN_GB}); hora UTC {now.strftime('%H:%M')} "
        f"(limite 05:20); condicion={ram_ok and hora_ok} ==")
    if ram_ok and hora_ok:
        try:
            rr = run("A4_sub_L80_h0.125", shapes_A4, N2, L_A4, 0.125, S_SUB, n_modes=2)
            ev = a4_eval(rr, 0.125)
            a4["0.125"] = ev
            kappa_diff_125 = ev["kappa_FD_um_inv"] - a4["0.25"]["kappa_FD_um_inv"]
            extra_h0125 = {"ejecutado": True, "ram_libre_gb_inicio": free_gb, "hora_inicio_utc": now.isoformat(),
                           "resultado": ev, "kappa(0.125)-kappa(0.25)_um_inv": kappa_diff_125,
                           "nota": "informativo; no es criterio vinculante"}
            log(f"  h=0.125: n_par={ev['neff_par']:.10f} n_impar={ev['neff_impar']:.10f} "
                f"dn={ev['delta_n']:.6e} kappa={ev['kappa_FD_um_inv']:.6e}")
        except Exception as exc:  # error de memoria u otro: se declara limite, no se oculta
            extra_h0125 = {"ejecutado": False, "motivo": f"error al ejecutar: {type(exc).__name__}: {exc}",
                           "ram_libre_gb_inicio": free_gb, "hora_inicio_utc": now.isoformat()}
            log(f"  h=0.125 no completado: {type(exc).__name__}: {exc}")
    else:
        extra_h0125 = {"ejecutado": False,
                       "motivo": "no cumple la condicion de JEV (RAM libre >= 4 GB y hora < 05:20 UTC)",
                       "ram_libre_gb_inicio": free_gb, "hora_inicio_utc": now.isoformat()}

    out = build_out(t_start, ana, ref_err_125, res_A1, res_A2, res_A3,
                    a4, kappa_diff, extra_h0125)
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False, default=float), encoding="utf-8")
    n_pass = out["resumen"]["n_pass"]
    log(f"Criterios: {n_pass}/{out['resumen']['n_criterios']} pass; evaluables {out['resumen']['n_evaluables']}; "
        f"estado={out['estado']}. Salida: {OUT_JSON}")
    log(f"Fin UTC {utc_now().isoformat()}")


if __name__ == "__main__":
    main()
