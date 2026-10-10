"""Tarea F3 (ronda 3): tracks con fraccion de area real y caja convergida.

Modelo numerico escalar ideal. No es dispositivo, no es medida, no es fabricacion.
Contrato: CONTRATO-tracks-r3.md (escrito antes de calcular; umbrales fijados ahi).

Uso (desde esta carpeta, CPU, un proceso a la vez):
    OMP_NUM_THREADS=1 python -B run_tracks_r3.py run F31
    OMP_NUM_THREADS=1 python -B run_tracks_r3.py run F32 [N ...]   (por defecto 48 64 96 32 24 16 8)
    OMP_NUM_THREADS=1 python -B run_tracks_r3.py eval
Usa run_tracks.py (ronda 1) como modulo: geometria, solve_near, select_core, n_eq_of_f, shapes.
No modifica los archivos de la ronda 1 ni de la ronda 2 (solo lee resultados_tracks_r2.json).
"""
import sys
import os
import json
import math
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_tracks as rt  # noqa: E402  (ronda 1: geometria, solver de caja, seleccion)

TMP = "D:/PROJECTS/.cognition/tmp/tracks_r3"
os.makedirs(TMP, exist_ok=True)
OUT = os.path.join(HERE, "resultados_tracks_r3.json")
LOG = os.path.join(HERE, "log_run_r3.txt")
MD = os.path.join(HERE, "RESULTADOS-tracks-r3.md")
R2_JSON = os.path.join(HERE, "resultados_tracks_r2.json")
PSI_I = os.path.join(TMP, "psi_i_L80_h0.25.npy")  # modo recto (caso i, L = 80), temporal en D:

SIGMA = 1.44219587036024   # raiz analitica del caso i (ronda 1, resultados.json: analytic.i.Re_neff)
K_MODES = 30               # igual que la ronda 2
WIN = 0.002                # ventana |n - sigma| (ronda 1 / ronda 2)
P_THR = 0.5                # umbral de potencia en r <= 12 um (ronda 1 / ronda 2)
S_THR = 0.9                # umbral de solape con el modo recto (contrato r3, seccion 4)
TOL_L = 1e-6               # F31-C1
TOL_AN = 1e-4              # F31-C3 (umbral de ronda 1 C3)
TOL_DIFF = 1e-5            # F33-C1 y F33-C2 (umbral de la tarea)
H = 0.25                   # um, en toda la ronda 3
L_SMALL, L_BIG = 60.0, 80.0
NS = [8, 16, 24, 32, 48, 64, 96]
ORDER_F32 = [48, 64, 96, 32, 24, 16, 8]

R = {"meta": {}, "runs": {}, "fracs": {}, "criteria": [], "status": None, "summary": {}}


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
    """Reanuda: conserva corridas ya guardadas (si el proceso se interrumpe)."""
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as fh:
            old = json.load(fh)
        R["runs"] = old.get("runs", {})


def load_fracs():
    """Fraccion de area real medida en la malla (ronda 2, campo f_union_grid, precision completa)."""
    with open(R2_JSON, encoding="utf-8") as fh:
        r2 = json.load(fh)
    out = {}
    for N in NS:
        out[N] = float(r2["fracs"][f"N{N}"]["f_union_grid"])
    return out


F_REAL = load_fracs()


def n_eq_real(N):
    return rt.n_eq_of_f(F_REAL[N])


def shapes_for(case):
    if case == "i":
        return rt.shapes_cont()
    if case.startswith("ii_N"):
        return rt.shapes_tracks(int(case[4:]))
    if case.startswith("iii_N"):
        return rt.shapes_cont(n_eq_real(int(case[5:])))
    raise ValueError(f"caso desconocido: {case}")


def key_of(case, L):
    return f"{case}|L{L:g}|h{H:g}"


def get(case, L):
    return R["runs"].get(key_of(case, L))


def have(case, L):
    """True si existe una corrida con resultado del solver (ok)."""
    r = get(case, L)
    return r is not None and bool(r.get("ok"))


def n_counted(case, L):
    """n_eff del modo de nucleo si CUENTA (ligado y, para ii/iii, S > S_THR); None en otro caso."""
    r = get(case, L)
    if r is None or not r.get("ok") or not r.get("counted"):
        return None
    return float(r["n_core"])


def run_one(case, L):
    key = key_of(case, L)
    if have(case, L):
        log(f"omitido (existe): {key}")
        return R["runs"][key]
    psi_i = None
    if case != "i":
        if not os.path.exists(PSI_I):
            raise SystemExit("falta el modo recto psi_i (ejecutar 'run F31' antes)")
        psi_i = np.load(PSI_I)
    t0 = time.time()
    try:
        res = rt.solve_near(shapes_for(case), L, H, SIGMA, k=K_MODES, s_sub=8)
    except Exception as exc:  # el fallo queda registrado, no se oculta
        rec = {"case": case, "L_um": L, "h_um": H, "ok": False, "error": repr(exc)[:300]}
        R["runs"][key] = rec
        save()
        log(f"{key}: ERROR {exc!r}")
        return rec
    el = time.time() - t0
    sel = rt.select_core(res)
    neffs = res["neff"]
    P_in = sel["P_in_all"]
    cands = [m for m in range(len(neffs)) if P_in[m] >= P_THR and abs(neffs[m] - SIGMA) <= WIN]
    idx = max(cands, key=lambda m: neffs[m]) if cands else None
    imaxP = int(np.argmax(P_in))
    bound = idx is not None
    S = None
    if case == "i" and L == L_BIG and bound:
        np.save(PSI_I, res["psi"][idx])   # modo recto para el solape de F3.2
        S = 1.0
    elif bound and psi_i is not None:
        ov = float(np.sum(res["psi"][idx] * psi_i) * H * H)
        S = ov * ov                       # solape de potencia |<psi_N, psi_i>|^2
    if case == "i":
        counted = bound
    else:
        counted = bool(bound and S is not None and S > S_THR)
    N = int(case.split("_N")[1]) if "_N" in case else None
    rec = {
        "case": case, "L_um": L, "h_um": H, "K": K_MODES, "ok": True,
        "sigma_neff": SIGMA, "win": WIN, "p_thr": P_THR, "s_thr": S_THR,
        "N_grid": int(res["N"]), "unknowns": int(res["unknowns"]), "s_sub": 8,
        "time_s": round(el, 2),
        "f_real": F_REAL[N] if (N is not None and case.startswith(("ii_", "iii_"))) else None,
        "n_eq_real": n_eq_real(N) if case.startswith("iii_") else None,
        "bound": bool(bound), "counted": bool(counted), "S_overlap": S,
        "n_core": float(neffs[idx]) if bound else None,
        "sel_index": idx,
        "P_in_core": float(P_in[idx]) if bound else None,
        "P_r6_core": float(sel["P_core_all"][idx]) if bound else None,
        "n_maxP": float(neffs[imaxP]), "P_in_maxP": float(P_in[imaxP]),
        "n_top8": [float(v) for v in neffs[:8]],
        "P_in_first8": [float(v) for v in P_in[:8]],
    }
    R["runs"][key] = rec
    save()
    log(f"{key}: bound={bound} counted={counted} n_core={rec['n_core']} P_in={rec['P_in_core']} "
        f"S={S} n_maxP={rec['n_maxP']:.10f} P_maxP={rec['P_in_maxP']:.3e} unk={rec['unknowns']} "
        f"t={el:.1f}s")
    return rec


def block_F31():
    for L in (L_SMALL, L_BIG):
        run_one("i", L)


def block_F32(ns):
    for N in ns:
        run_one(f"ii_N{N}", L_BIG)
        run_one(f"iii_N{N}", L_BIG)


def add(crit, cid, desc, value, passed, evaluable=True, note="", informative=False):
    crit.append({
        "id": cid, "description": desc, "value": value,
        "pass": None if informative else (bool(passed) if evaluable else False),
        "evaluable": True if informative else bool(evaluable),
        "informative": bool(informative), "note": note,
    })


def evaluate():
    crit = []

    # F3.1: caja de la camisa continua (caso i), h = 0,25
    ev31 = have("i", L_BIG) and have("i", L_SMALL)
    na, nb = n_counted("i", L_BIG), n_counted("i", L_SMALL)
    if not ev31:
        add(crit, "F31-C1", "|n(i;L=80)-n(i;L=60)| < 1e-6 (h=0,25)", None, False, False,
            "falta una corrida de caso i")
    elif na is None or nb is None:
        add(crit, "F31-C1", "|n(i;L=80)-n(i;L=60)| < 1e-6 (h=0,25)",
            {"n_L80": na, "n_L60": nb}, False, True, "caso i no ligado en L=60 o L=80")
    else:
        d = abs(na - nb)
        add(crit, "F31-C1", "|n(i;L=80)-n(i;L=60)| < 1e-6 (h=0,25)", d, d < TOL_L)

    flags31 = {str(L): (get("i", L)["bound"] if have("i", L) else None) for L in (L_SMALL, L_BIG)}
    add(crit, "F31-C2", "caso i ligado (P>=0,5 y |n-sigma|<=0,002) en L=60 y L=80 (h=0,25)",
        flags31, all(v is True for v in flags31.values()),
        all(v is not None for v in flags31.values()))

    if not have("i", L_BIG):
        add(crit, "F31-C3", "|Re n(i;L=80,h=0,25) - Re n_an(i)| <= 1e-4", None, False, False,
            "falta la corrida de caso i a L=80")
    elif na is None:
        add(crit, "F31-C3", "|Re n(i;L=80,h=0,25) - Re n_an(i)| <= 1e-4", None, False, True,
            "caso i no ligado a L=80")
    else:
        d = abs(na - SIGMA)
        add(crit, "F31-C3", "|Re n(i;L=80,h=0,25) - Re n_an(i)| <= 1e-4", d, d <= TOL_AN)

    # F3.2: trazos y continua equivalente, L = 80, h = 0,25
    keys32 = [(f"ii_N{N}", L_BIG) for N in NS] + [(f"iii_N{N}", L_BIG) for N in NS]
    miss = [k for k in keys32 if not have(*k)]
    ev_all = all(get(c, L) is not None for c, L in keys32)
    add(crit, "F32-C1", "14 casos (ii_N, iii_N) con resultado del solver, L=80, h=0,25",
        {"faltan_o_fallan": [key_of(c, L) for c, L in keys32 if not have(c, L)]},
        len(miss) == 0, ev_all)

    cnt_ii = {N: bool(get(f"ii_N{N}", L_BIG) and get(f"ii_N{N}", L_BIG).get("counted")) for N in NS}
    ev_ii = all(have(f"ii_N{N}", L_BIG) for N in NS)
    add(crit, "F32-C2", "7 trazos ii_N cuentan (ligados y S>0,9), L=80, h=0,25",
        {str(N): v for N, v in cnt_ii.items()}, all(cnt_ii.values()), ev_ii)

    cnt_iii = {N: bool(get(f"iii_N{N}", L_BIG) and get(f"iii_N{N}", L_BIG).get("counted")) for N in NS}
    ev_iii = all(have(f"iii_N{N}", L_BIG) for N in NS)
    add(crit, "F32-C3", "7 continuas equivalentes iii_N cuentan (ligadas y S>0,9), L=80, h=0,25",
        {str(N): v for N, v in cnt_iii.items()}, all(cnt_iii.values()), ev_iii)

    # F3.3: separacion Delta(N) = n_ii(N) - n_iii(N), L = 80, h = 0,25
    def pair(N):
        a, b = n_counted(f"ii_N{N}", L_BIG), n_counted(f"iii_N{N}", L_BIG)
        ev = have(f"ii_N{N}", L_BIG) and have(f"iii_N{N}", L_BIG)
        return a, b, ev

    vals = {}
    ok_all = True
    ev_all33 = True
    for N in (48, 64, 96):
        a, b, ev = pair(N)
        ev_all33 = ev_all33 and ev
        if a is None or b is None:
            vals[str(N)] = {"delta": None, "abs": None, "nota": "par no contado (no ligado o S<=0,9)"}
            ok_all = False
        else:
            d = a - b
            vals[str(N)] = {"delta": d, "abs": abs(d)}
            ok_all = ok_all and abs(d) < TOL_DIFF
    add(crit, "F33-C1", "|Delta(N)| < 1e-5 para N=48, 64 y 96, L=80, h=0,25 (ambos casos contados)",
        vals, ok_all and ev_all33, ev_all33,
        "N=64 y 96: f_real<1 (valido), pero el par debe contar" if ev_all33 else "faltan corridas")

    a, b, ev = pair(48)
    if not ev:
        add(crit, "F33-C2", "|Delta(48)| < 1e-5, L=80, h=0,25", None, False, False, "faltan corridas N=48")
    elif a is None or b is None:
        add(crit, "F33-C2", "|Delta(48)| < 1e-5, L=80, h=0,25", None, False, True,
            "par N=48 no contado (no ligado o S<=0,9)")
    else:
        d = a - b
        add(crit, "F33-C2", "|Delta(48)| < 1e-5, L=80, h=0,25", d, abs(d) < TOL_DIFF)

    # Informativos (pass = null)
    ov_info = {}
    for N in NS:
        for fam in ("ii", "iii"):
            r = get(f"{fam}_N{N}", L_BIG)
            if r is not None:
                ov_info[f"{fam}_N{N}"] = {"S": r.get("S_overlap"), "bound": r.get("bound"),
                                          "counted": r.get("counted"), "n_core": r.get("n_core"),
                                          "P_in_core": r.get("P_in_core"), "f_real": r.get("f_real"),
                                          "n_eq_real": r.get("n_eq_real")}
    add(crit, "INF-solape", "S = |<psi_N, psi_i>|^2 y cuenta por caso (informativo)", ov_info, None,
        informative=True)

    dl_rows, xs, ys = {}, [], []
    for N in NS:
        a, b, _ = pair(N)
        if a is None or b is None:
            dl_rows[str(N)] = {"n_ii": a, "n_iii": b, "delta": None}
        else:
            dl_rows[str(N)] = {"n_ii": a, "n_iii": b, "delta": a - b}
            xs.append(N)
            ys.append(a - b)
    slope = float(np.polyfit(xs, ys, 1)[0]) if len(xs) >= 2 else None
    add(crit, "INF-delta", "Delta(N) frente a N y pendiente sobre pares contados (informativo)",
        {"filas": dl_rows, "pendiente_delta_por_N": slope, "n_pares": len(xs)}, None, informative=True)

    caja = {}
    for L in (L_SMALL, L_BIG):
        r = get("i", L)
        if r is not None and r.get("ok"):
            caja[f"L{L:g}"] = {"n_core": r.get("n_core"), "P_in_core": r.get("P_in_core"),
                               "n_maxP": r.get("n_maxP"), "P_in_maxP": r.get("P_in_maxP"),
                               "unknowns": r.get("unknowns"), "time_s": r.get("time_s")}
    add(crit, "INF-caja", "caso i: n y P(r<=12) frente a L (informativo)", caja, None, informative=True)

    R["criteria"] = crit
    any_ok = any(r.get("ok") for r in R["runs"].values())
    crit_req = [c for c in crit if not c["informative"]]
    evaluated_all = all(c["evaluable"] for c in crit_req)
    if not any_ok:
        status = "blocked"
    else:
        status = "done" if evaluated_all else "partial"
    R["status"] = status
    R["summary"] = {
        "sigma_neff": SIGMA,
        "n_runs_ok": sum(1 for r in R["runs"].values() if r.get("ok")),
        "n_runs_error": sum(1 for r in R["runs"].values() if not r.get("ok")),
        "n_runs_counted": sum(1 for r in R["runs"].values() if r.get("ok") and r.get("counted")),
        "criterios_evaluados": sum(1 for c in crit_req if c["evaluable"]),
        "criterios_totales": len(crit_req),
        "criterios_pass": sum(1 for c in crit_req if c["pass"] is True),
    }
    for c in crit:
        log(f"CRIT {c['id']}: pass={c['pass']} evaluable={c['evaluable']} value={c['value']}")
    log(f"status={status}")


def write_md():
    lines = []
    lines.append("# RESULTADOS tracks ronda 3 (F3)")
    lines.append("")
    lines.append("Modelo numerico escalar ideal. No es dispositivo, medida ni fabricacion. "
                 "Contrato: `CONTRATO-tracks-r3.md`. Pass calculado por `run_tracks_r3.py eval`.")
    lines.append("")
    s = R.get("summary", {})
    lines.append(f"Estado: **{R.get('status')}**. Corridas ok: {s.get('n_runs_ok')}, "
                 f"con error: {s.get('n_runs_error')}, que cuentan: {s.get('n_runs_counted')}. "
                 f"Criterios evaluados: {s.get('criterios_evaluados')}/{s.get('criterios_totales')}, "
                 f"pass: {s.get('criterios_pass')}.")
    lines.append("")
    lines.append("## Corridas (L = 80 um salvo caso i a L = 60; h = 0,25 um)")
    lines.append("")
    lines.append("| caso | L (um) | incognitas | ligado | S (solape con modo recto) | cuenta | n_eff | P(r<=12) | f_real | n_eq | t (s) |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for key in sorted(R["runs"].keys(), key=lambda k: (k.split("|")[0], k)):
        r = R["runs"][key]
        if not r.get("ok"):
            lines.append(f"| {r['case']} | {r['L_um']:g} | - | ERROR | - | - | - | - | - | - | - |")
            continue
        S = "-" if r.get("S_overlap") is None else f"{r['S_overlap']:.4f}"
        nc = "-" if r.get("n_core") is None else f"{r['n_core']:.10f}"
        pin = "-" if r.get("P_in_core") is None else f"{r['P_in_core']:.4f}"
        fr = "-" if r.get("f_real") is None else f"{r['f_real']:.5f}"
        neq = "-" if r.get("n_eq_real") is None else f"{r['n_eq_real']:.6f}"
        lines.append(f"| {r['case']} | {r['L_um']:g} | {r['unknowns']} | {'si' if r['bound'] else 'no'} | {S} | "
                     f"{'si' if r['counted'] else 'no ligado'} | {nc} | {pin} | {fr} | {neq} | {r['time_s']} |")
    lines.append("")
    lines.append("## Criterios (pass calculado por el codigo)")
    lines.append("")
    lines.append("| id | descripcion | pass | evaluable | valor |")
    lines.append("|---|---|---|---|---|")
    for c in R.get("criteria", []):
        pz = "null (informativo)" if c["pass"] is None else str(c["pass"]).lower()
        val = json.dumps(c["value"], ensure_ascii=False, default=float)
        if len(val) > 400:
            val = val[:400] + "..."
        lines.append(f"| {c['id']} | {c['description']} | {pz} | {str(c['evaluable']).lower()} | `{val}` |")
    lines.append("")
    lines.append("## Limites y estado (fijados antes de calcular)")
    lines.append("")
    lines.append("- Solo CPU, un proceso a la vez, un hilo (OMP_NUM_THREADS=1). RAM libre 4,9 GB de 23,7 GB a 07:15 UTC.")
    lines.append("- h = 0,125 a L = 80 no se ejecuta (1,6 M incognitas no caben con la RAM disponible). No hay convergencia en h a L = 80.")
    lines.append("- La ronda 2 no completo sus bloques (un solo resultado, status null). Esta ronda no reutiliza sus corridas.")
    lines.append("- Fracciones f_real: area de union medida en malla fina (ronda 2). No es f = N/48 (descartado).")
    lines.append("- Modo recto: modo de nucleo del caso i a L = 80, h = 0,25 (interpretacion fijada en el contrato, seccion 4).")
    lines.append("- JEV: la consulta devolvio error de esquema local (`remote_decision` false). Decisiones con fallback local explicito (contrato, seccion 10).")
    lines.append("- Lo calculado: n_eff, P, S y las diferencias de la tabla. Lo supuesto: sigma de la ronda 1, modo recto, f_real, geometria, umbrales.")
    lines.append("- No afirmo vectorial, perdidas, fabricacion ni convergencia mas alla de L = 80.")
    lines.append("")
    with open(MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def main():
    args = sys.argv[1:]
    mode = args[0] if args else "eval"
    load_existing()
    R["meta"] = {
        "utc_last_start": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "contrato": "CONTRATO-tracks-r3.md",
        "modulo_base": "run_tracks.py (ronda 1): geometria, solve_near, select_core, n_eq_of_f",
        "solver": "experimentos/solver2d_claude/solver2d.py (Tarea A), via solve_near",
        "K": K_MODES, "win": WIN, "p_thr": P_THR, "s_thr": S_THR, "s_sub": 8, "h_um": H,
        "box_convention": "L = semilado; caja [-L,L]^2 (lado 2L)",
        "sigma_neff": SIGMA,
        "f_real_fuente": "resultados_tracks_r2.json, fracs.N*.f_union_grid (precision completa)",
        "python": sys.version.split()[0],
        "omp_num_threads": os.environ.get("OMP_NUM_THREADS"),
        "nota": "Modelo escalar ideal. No es dispositivo ni medida.",
    }
    R["fracs"] = {f"N{N}": F_REAL[N] for N in NS}
    if mode == "run":
        blocks = args[1:2]
        if not blocks:
            raise SystemExit("uso: run F31 | run F32 [N ...]")
        log(f"inicio bloque {blocks[0]} (sigma={SIGMA})")
        if blocks[0] == "F31":
            block_F31()
        elif blocks[0] == "F32":
            ns = [int(v) for v in args[2:]] or ORDER_F32
            for N in ns:
                if N not in NS:
                    raise SystemExit(f"N fuera de la lista: {N}")
            block_F32(ns)
        else:
            raise SystemExit(f"bloque desconocido: {blocks[0]}")
        save()
        log("fin bloque")
    elif mode == "eval":
        pass
    else:
        raise SystemExit("uso: run F31 | run F32 [N ...] | eval")
    evaluate()
    save()
    write_md()
    log("md escrito")


if __name__ == "__main__":
    main()
