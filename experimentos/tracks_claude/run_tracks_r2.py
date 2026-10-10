"""Tarea F2 (ronda 2): camisa continua frente a trazos; dependencia con la caja y ligadura del modo.

Modelo numerico escalar ideal. No es dispositivo, no es medida, no es fabricacion.
Contrato: CONTRATO-tracks-r2.md (escrito antes de calcular; umbrales fijados ahi).

Uso (desde esta carpeta, CPU):
    OMP_NUM_THREADS=1 python -B run_tracks_r2.py run A B C D
    OMP_NUM_THREADS=1 python -B run_tracks_r2.py run E          (bloque opcional)
    OMP_NUM_THREADS=1 python -B run_tracks_r2.py eval
Usa run_tracks.py (ronda 1) como modulo: geometria, solver de caja (solve_near, select_core)
y referencia analitica (leaky_roots). No modifica los archivos de la ronda 1.
"""
import sys
import os
import json
import math
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_tracks as rt  # noqa: E402  (ronda 1: geometria, solver de caja, analitica)

OUT = os.path.join(HERE, "resultados_tracks_r2.json")
LOG = os.path.join(HERE, "log_run_r2.txt")

K_MODES = 30        # modos mas cercanos a sigma (ronda 1 usaba 12)
WIN = 0.002         # ventana |n_eff - sigma| para modo de nucleo (ronda 1)
P_THR = 0.5         # umbral de potencia en r <= 12 um (ronda 1)
TOL_HCHECK = 1e-5   # umbral de malla (ronda 1, C1)
TOL_L = 1e-6        # umbral de caja (tarea F2.1)
TOL_TASK = 1e-5     # umbral de la pregunta principal (ronda 1, C6)
TOL_ANALYTIC = 1e-4 # umbral analitico (ronda 1, C3)
NS = list(rt.NS)    # [8, 16, 24, 32, 48, 64, 96]

R = {"meta": {}, "analytic": {}, "fracs": {}, "runs": {}, "criteria": [], "status": None,
     "summary": {}}
SIGMA = None        # n_eff analitico del caso i (se fija en run_all)

CASES_F22 = ["i"] + [f"ii_N{N}" for N in NS] + [f"iii_N{N}" for N in NS]

BLOCKS = {
    "A": [("i", 40, 0.25), ("i", 60, 0.25), ("i", 80, 0.25), ("i", 40, 0.125)],
    "B": [(c, 40, 0.25) for c in CASES_F22],
    "C": [(c, 60, 0.25) for c in CASES_F22],
    "D": [("ii_N8", 40, 0.125), ("ii_N48", 40, 0.125)],
    "E": [(c, 80, 0.25) for c in CASES_F22],
}


def log(msg):
    stamp = time.strftime("%H:%M:%S", time.gmtime())
    line = f"[{stamp}Z] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def save():
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(R, fh, indent=2, ensure_ascii=False, default=float)


def load_existing():
    """Reanuda: conserva corridas y analitica ya guardadas (si el script se interrumpe)."""
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as fh:
            old = json.load(fh)
        R["runs"] = old.get("runs", {})
        R["analytic"] = old.get("analytic", {})
        R["fracs"] = old.get("fracs", {})


# ---------------- geometria de cada caso ----------------
def shapes_for(case):
    if case == "i":
        return rt.shapes_cont()
    if case.startswith("ii_N"):
        return rt.shapes_tracks(int(case[4:]))
    if case.startswith("iii_N"):
        N = int(case[5:])
        return rt.shapes_cont(rt.n_eq_of_f(rt.f_formula(N)))
    raise ValueError(f"caso desconocido: {case}")


def key_of(case, L, h):
    return f"{case}|L{L:g}|h{h:g}"


def get_run(case, L, h):
    return R["runs"].get(key_of(case, L, h))


def run_ok(case, L, h):
    r = get_run(case, L, h)
    return r is not None and bool(r.get("ok"))


def is_bound(case, L, h):
    """True/False si la corrida existe y tiene resultado; None si falta."""
    r = get_run(case, L, h)
    if r is None or not r.get("ok"):
        return None
    return bool(r["bound"])


def n_bound(case, L, h):
    """n_eff del modo de nucleo si esta ligado; None si no esta ligado o falta."""
    r = get_run(case, L, h)
    if r is None or not r.get("ok") or not r.get("bound"):
        return None
    return float(r["n_core"])


# ---------------- ejecucion de un caso ----------------
def run_one(case, L, h):
    key = key_of(case, L, h)
    if run_ok(case, L, h):
        log(f"omitido (existe): {key}")
        return R["runs"][key]
    t0 = time.time()
    try:
        res = rt.solve_near(shapes_for(case), L, h, SIGMA, k=K_MODES, s_sub=8)
    except Exception as exc:  # el fallo queda registrado, no se oculta
        rec = {"case": case, "L_um": L, "h_um": h, "ok": False, "error": repr(exc)[:300]}
        R["runs"][key] = rec
        save()
        log(f"{key}: ERROR {exc!r}")
        return rec
    el = time.time() - t0
    sel = rt.select_core(res)           # P(r<=12) y P(r<=6) por modo (ronda 1)
    neffs = res["neff"]
    P_in = sel["P_in_all"]
    cands = [m for m in range(len(neffs))
             if P_in[m] >= P_THR and abs(neffs[m] - SIGMA) <= WIN]
    idx = max(cands, key=lambda m: neffs[m]) if cands else None
    imaxP = int(np.argmax(P_in))
    rec = {
        "case": case, "L_um": L, "h_um": h, "K": K_MODES, "ok": True,
        "sigma_neff": SIGMA, "win": WIN, "p_thr": P_THR,
        "N_grid": int(res["N"]), "unknowns": int(res["unknowns"]), "s_sub": 8,
        "time_s": round(el, 2),
        "bound": idx is not None,
        "n_core": float(neffs[idx]) if idx is not None else None,
        "sel_index": idx,
        "P_in_core": float(P_in[idx]) if idx is not None else None,
        "P_r6_core": float(sel["P_core_all"][idx]) if idx is not None else None,
        "n_maxP": float(neffs[imaxP]),
        "P_in_maxP": float(P_in[imaxP]),
        "n_top8": [float(v) for v in neffs[:8]],
        "P_in_all": [float(v) for v in P_in],
    }
    R["runs"][key] = rec
    save()
    log(f"{key}: bound={rec['bound']} n_core={rec['n_core']} P_in_core={rec['P_in_core']} "
        f"n_maxP={rec['n_maxP']:.10f} P_maxP={rec['P_in_maxP']:.3e} unk={rec['unknowns']} t={el:.1f}s")
    return rec


# ---------------- referencia analitica (ronda 1 G_leaky / leaky_roots) ----------------
def analytic_block():
    cases = {"i": (rt.N_BG, rt.N_JAC, rt.N_BG, rt.A_CORE, rt.R_OUT)}
    for N in NS:
        cases[f"iii_N{N}"] = (rt.N_BG, rt.n_eq_of_f(rt.f_formula(N)), rt.N_BG, rt.A_CORE, rt.R_OUT)
    out = {}
    for name, (nc, nr, no, r1, r2) in cases.items():
        roots, _ = rt.leaky_roots(nc, nr, no, r1, r2)
        cand = [z for z in roots if abs(z.imag) < 0.02
                and min(nr, nc) - 1e-3 <= z.real <= max(nr, nc) + 1e-3]
        best = max(cand, key=lambda z: z.real) if cand else None
        out[name] = {"n_ring": nr, "Re_neff": float(best.real) if best is not None else None,
                     "Im_neff": float(best.imag) if best is not None else None,
                     "n_roots": len(roots)}
        log(f"analitica {name}: n_ring={nr:.6f} Re={out[name]['Re_neff']} Im={out[name]['Im_neff']}")
    R["analytic"] = out


# ---------------- fraccion de area de union (ronda 1, malla fina) ----------------
def fracs_block():
    out = {}
    for N in NS:
        f_form = rt.f_formula(N)
        d = rt.min_center_distance(N)
        overlap = d < 2 * rt.R_T
        f_exact = None if overlap else N * math.pi * rt.R_T ** 2 / rt.RING_AREA
        g = rt.union_fraction_grid(N)
        out[f"N{N}"] = {"f_formula": f_form, "min_center_dist": d, "overlap": overlap,
                        "f_union_exact_if_disjoint": f_exact,
                        "f_union_grid": g["f_union_grid"],
                        "n_eq_formula": rt.n_eq_of_f(f_form)}
        log(f"fracs N={N}: f={f_form:.5f} f_union_grid={g['f_union_grid']:.5f} overlap={overlap}")
    R["fracs"] = out


# ---------------- criterios y evaluacion ----------------
def add(crit, cid, desc, value, passed, evaluable=True, note="", informative=False):
    crit.append({
        "id": cid, "description": desc, "value": value,
        "pass": None if informative else (bool(passed) if evaluable else False),
        "evaluable": True if informative else bool(evaluable),
        "informative": bool(informative), "note": note,
    })


def marks_missing(L, h):
    return [c for c in CASES_F22 if not run_ok(c, L, h)]


def evaluate():
    crit = []
    an_i = R["analytic"]["i"]["Re_neff"]

    # F21: dependencia con la caja (caso i, h = 0.25)
    a, b = n_bound("i", 80, 0.25), n_bound("i", 60, 0.25)
    if a is None or b is None:
        add(crit, "F21-C1", "|n(L=80,h=0.25)-n(L=60,h=0.25)| < 1e-6 (caso i)",
            {"n_L80": a, "n_L60": b}, False, False, "falta modo ligado en L=60 o L=80")
    else:
        d = abs(a - b)
        add(crit, "F21-C1", "|n(L=80,h=0.25)-n(L=60,h=0.25)| < 1e-6 (caso i)", d, d < TOL_L)

    flags21 = {L: is_bound("i", L, 0.25) for L in (40, 60, 80)}
    ev21 = all(v is not None for v in flags21.values())
    add(crit, "F21-C2", "caso i ligado (P>=0,5 y |n-sigma|<=0,002) en L=40,60,80 (h=0.25)",
        {str(L): v for L, v in flags21.items()}, all(v is True for v in flags21.values()), ev21)

    n40_125, n40_25 = n_bound("i", 40, 0.125), n_bound("i", 40, 0.25)
    if n40_125 is None:
        add(crit, "F21-C3", "|Re n(i;L=40,h=0.125) - Re n_an(i)| <= 1e-4", None, False, False,
            "caso i no ligado o no calculado a h=0.125")
    else:
        d = abs(n40_125 - an_i)
        add(crit, "F21-C3", "|Re n(i;L=40,h=0.125) - Re n_an(i)| <= 1e-4", d, d <= TOL_ANALYTIC)

    if n40_25 is None or n40_125 is None:
        add(crit, "F21-C4", "|n(i;L=40,h=0.25) - n(i;L=40,h=0.125)| <= 1e-5", None, False, False,
            "falta una malla")
    else:
        d = abs(n40_25 - n40_125)
        add(crit, "F21-C4", "|n(i;L=40,h=0.25) - n(i;L=40,h=0.125)| <= 1e-5", d, d <= TOL_HCHECK)

    # F22: marcado de ligadura y trazos en caja 40 (primaria) y 60 (secundaria)
    miss40 = marks_missing(40, 0.25)
    add(crit, "F22-C1", "15 casos (i, ii_N, iii_N) con resultado y bandera de ligado, L=40, h=0.25",
        {"faltan": miss40}, len(miss40) == 0, len(miss40) == 0,
        "" if not miss40 else f"faltan: {miss40}")

    fl_ii40 = {N: is_bound(f"ii_N{N}", 40, 0.25) for N in NS}
    add(crit, "F22-C2", "7 casos ii_N ligados, L=40, h=0.25",
        {str(N): v for N, v in fl_ii40.items()},
        all(v is True for v in fl_ii40.values()),
        all(v is not None for v in fl_ii40.values()))

    fl_iii40 = {N: is_bound(f"iii_N{N}", 40, 0.25) for N in NS}
    add(crit, "F22-C3", "7 casos iii_N ligados, L=40, h=0.25",
        {str(N): v for N, v in fl_iii40.items()},
        all(v is True for v in fl_iii40.values()),
        all(v is not None for v in fl_iii40.values()))

    hd = {}
    ev_hd = True
    ok_hd = True
    for N in (8, 48):
        a, b = n_bound(f"ii_N{N}", 40, 0.25), n_bound(f"ii_N{N}", 40, 0.125)
        if a is None or b is None:
            ev_hd = False
            hd[str(N)] = None
        else:
            d = abs(a - b)
            hd[str(N)] = d
            ok_hd = ok_hd and d <= TOL_HCHECK
    add(crit, "F22-C4", "|n(ii_N;h=0.25)-n(ii_N;h=0.125)| <= 1e-5, N=8 y 48 (si ligados)",
        hd, ok_hd and ev_hd, ev_hd)

    miss60 = marks_missing(60, 0.25)
    add(crit, "F22-C5", "15 casos con resultado y bandera de ligado, L=60, h=0.25",
        {"faltan": miss60}, len(miss60) == 0, len(miss60) == 0,
        "" if not miss60 else f"faltan: {miss60}")
    fl_ii60 = {N: is_bound(f"ii_N{N}", 60, 0.25) for N in NS}
    add(crit, "F22-C6", "7 casos ii_N ligados, L=60, h=0.25",
        {str(N): v for N, v in fl_ii60.items()},
        all(v is True for v in fl_ii60.values()),
        all(v is not None for v in fl_ii60.values()))

    # F23: separacion ii - iii en caja 40 y 60 (umbral de la pregunta principal)
    for L, cid in ((40, "F23-C1"), (60, "F23-C2")):
        vals = {}
        ok = True
        ev = True
        for N in (48, 64, 96):
            a, b = n_bound(f"ii_N{N}", L, 0.25), n_bound(f"iii_N{N}", L, 0.25)
            if a is None or b is None:
                ev = False
                vals[str(N)] = None
            else:
                d = a - b
                vals[str(N)] = {"delta": d, "abs": abs(d)}
                ok = ok and abs(d) < TOL_TASK
        add(crit, cid, f"|n_ii(N)-n_iii(N)| < 1e-5 para N=48,64,96, L={L}, h=0.25 (si ligados)",
            vals, ok and ev, ev,
            "N=64 y 96: f>1, interpretacion fisica no valida" if ev else "faltan casos ligados")

    # F23: geometria (ronda 1, C5)
    fe8 = R["fracs"]["N8"]["f_union_exact_if_disjoint"]
    fe16 = R["fracs"]["N16"]["f_union_exact_if_disjoint"]
    ok_g1 = (fe8 is not None and fe16 is not None
             and abs(fe8 - rt.f_formula(8)) <= 1e-6 and abs(fe16 - rt.f_formula(16)) <= 1e-6)
    add(crit, "F23-G1", "f_union exacta = f(N) para N=8,16 (error <= 1e-6)",
        {"f_union_8": fe8, "f_union_16": fe16}, ok_g1, fe8 is not None and fe16 is not None)
    g16 = R["fracs"]["N16"]["f_union_grid"]
    err16 = abs(g16 - rt.f_formula(16)) / rt.f_formula(16)
    add(crit, "F23-G2", "estimador de malla: error relativo <= 0,5 % en N=16", err16, err16 <= 0.005)

    # Bloque E (caja 80), solo si se ejecuto
    ran80 = any("|L80|" in k for k in R["runs"])
    if ran80:
        miss80 = marks_missing(80, 0.25)
        add(crit, "F22-C7", "15 casos con bandera de ligado, L=80, h=0.25",
            {"faltan": miss80}, len(miss80) == 0, len(miss80) == 0,
            "" if not miss80 else f"faltan: {miss80}")
        vals = {}
        ok = True
        ev = True
        for N in (48, 64, 96):
            a, b = n_bound(f"ii_N{N}", 80, 0.25), n_bound(f"iii_N{N}", 80, 0.25)
            if a is None or b is None:
                ev = False
                vals[str(N)] = None
            else:
                d = a - b
                vals[str(N)] = {"delta": d, "abs": abs(d)}
                ok = ok and abs(d) < TOL_TASK
        add(crit, "F23-C3", "|n_ii(N)-n_iii(N)| < 1e-5 para N=48,64,96, L=80, h=0.25 (si ligados)",
            vals, ok and ev, ev)

    # Informativos (pass = null): caja, malla, Delta(N), geometria
    box_info = {}
    for L in (40, 60, 80):
        for h in (0.25, 0.125):
            r = get_run("i", L, h)
            if r is not None:
                box_info[f"i|L{L}|h{h}"] = {"n_core": r.get("n_core"), "bound": r.get("bound"),
                                            "P_in_core": r.get("P_in_core"),
                                            "n_maxP": r.get("n_maxP"),
                                            "P_in_maxP": r.get("P_in_maxP")}
    add(crit, "INF-caja", "n(i) y P(r<=12) frente a L y h (informativo)", box_info, None, informative=True)

    delta_info = {}
    for L in (40, 60, 80):
        rows = {}
        xs, ys = [], []
        for N in NS:
            a, b = n_bound(f"ii_N{N}", L, 0.25), n_bound(f"iii_N{N}", L, 0.25)
            if a is None or b is None:
                rows[str(N)] = {"n_ii": a, "n_iii": b, "delta": None}
            else:
                rows[str(N)] = {"n_ii": a, "n_iii": b, "delta": a - b}
                xs.append(N)
                ys.append(a - b)
        slope = float(np.polyfit(xs, ys, 1)[0]) if len(xs) >= 2 else None
        delta_info[f"L{L}"] = {"filas": rows, "pendiente_delta_por_N": slope, "n_puntos": len(xs)}
    add(crit, "INF-delta", "Delta(N)=n_ii-n_iii y pendiente frente a N, por caja (informativo)",
        delta_info, None, informative=True)

    fu_info = {}
    for N in NS:
        fr = R["fracs"].get(f"N{N}")
        if fr is None:
            continue
        fu = fr["f_union_grid"]
        fu_info[f"N{N}"] = {"f_formula": fr["f_formula"], "f_union_grid": fu,
                            "n_eq_formula": fr["n_eq_formula"],
                            "n_eq_prime_fu": math.sqrt(fu * rt.N_JAC ** 2 + (1 - fu) * rt.N_BG ** 2),
                            "overlap": fr["overlap"]}
    add(crit, "INF-fracciones", "f_union(N) frente a f(N)=N/48 y n_eq' (diagnostico, sin umbral)",
        fu_info, None, informative=True)

    crit_req = [c for c in crit if not c["informative"]]
    evaluated_all = all(c["evaluable"] for c in crit_req)
    any_run_ok = any(r.get("ok") for r in R["runs"].values())
    if not any_run_ok:
        status = "blocked"
    else:
        status = "done" if evaluated_all else "partial"
    R["criteria"] = crit
    R["status"] = status
    R["summary"] = {
        "sigma_neff": SIGMA,
        "n_runs_ok": sum(1 for r in R["runs"].values() if r.get("ok")),
        "n_runs_error": sum(1 for r in R["runs"].values() if not r.get("ok")),
        "criterios_evaluados": sum(1 for c in crit_req if c["evaluable"]),
        "criterios_totales": len(crit_req),
        "criterios_pass": sum(1 for c in crit_req if c["pass"] is True),
    }
    for c in crit:
        log(f"CRIT {c['id']}: pass={c['pass']} evaluable={c['evaluable']} value={c['value']}")
    log(f"status={status}")


def run_all(blocks):
    global SIGMA
    load_existing()
    R["meta"] = {
        "utc_start": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "contrato": "CONTRATO-tracks-r2.md",
        "modulo_base": "run_tracks.py (ronda 1): geometria, solver de caja, analitica",
        "solver": "experimentos/solver2d_claude/solver2d.py (Tarea A), via solve_near",
        "K": K_MODES, "win": WIN, "p_thr": P_THR, "s_sub": 8,
        "box_convention": "L = semilado; caja [-L,L]^2 (lado 2L)",
        "bloques_pedidos": blocks,
        "no_ejecutado_memoria": "L=80 y L=60 con h=0.125 (1,6 M y 0,9 M incognitas; RAM libre 3,9 GB de 23,7 GB a 04:52 UTC)",
        "python": sys.version.split()[0],
        "omp_num_threads": os.environ.get("OMP_NUM_THREADS"),
        "nota": "Modelo escalar ideal. No es dispositivo ni medida.",
    }
    log(f"inicio r2 bloques={blocks}")
    analytic_block()
    SIGMA = R["analytic"]["i"]["Re_neff"]
    R["meta"]["sigma_neff"] = SIGMA
    log(f"sigma_neff (raiz analitica i) = {SIGMA}")
    fracs_block()
    save()
    for b in blocks:
        for case, L, h in BLOCKS[b]:
            run_one(case, L, h)
    evaluate()
    save()
    log("fin")


if __name__ == "__main__":
    args = sys.argv[1:]
    mode = args[0] if args else "run"
    if mode == "run":
        blocks = args[1:] or ["A", "B", "C", "D"]
        for b in blocks:
            if b not in BLOCKS:
                raise SystemExit(f"bloque desconocido: {b}")
        run_all(blocks)
    elif mode == "eval":
        load_existing()
        SIGMA = R["analytic"]["i"]["Re_neff"]
        evaluate()
        save()
    else:
        raise SystemExit("uso: run [A B C D E] | eval")
