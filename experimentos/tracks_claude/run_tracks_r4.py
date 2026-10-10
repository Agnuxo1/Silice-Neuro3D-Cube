"""Tarea F4 (ronda 4): convergencia de caja de la camisa continua (caso i).

Modelo numerico escalar ideal. No es dispositivo, no es medida, no es fabricacion.
Contrato: CONTRATO-tracks-r4.md (escrito antes de calcular; umbrales fijados ahi).

Uso (desde esta carpeta, CPU, un proceso a la vez):
    OMP_NUM_THREADS=1 python -B run_tracks_r4.py run A   (h = 0,25: L = 60, 80, 100, 120; K = 30; check K = 60 en L = 60)
    OMP_NUM_THREADS=1 python -B run_tracks_r4.py run B   (h = 0,2: L = 60, 80)
    OMP_NUM_THREADS=1 python -B run_tracks_r4.py run C   (h = 0,2: L = 100, 120; solo si cabe)
    OMP_NUM_THREADS=1 python -B run_tracks_r4.py eval
Usa run_tracks.py (ronda 1) como modulo: geometria, solve_near, select_core, shapes_cont.
No modifica los archivos de rondas anteriores.
"""
import sys
import os
import json
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_tracks as rt  # noqa: E402  (ronda 1: geometria, solver de caja, seleccion)

OUT = os.path.join(HERE, "resultados_tracks_r4.json")
LOG = os.path.join(HERE, "log_run_r4.txt")

SIGMA = 1.44219587036024   # raiz analitica del caso i (ronda 1)
N_AN = 1.44219587036       # Re n_an(i), ronda 1 (G_leaky), control
K_MAIN = 30
WIN = 0.002                # ventana |n - sigma| (ronda 1)
P_THR = 0.5                # umbral de potencia en r <= 12 um (ronda 1)
TOL_C1 = 1e-6              # F4-C1
TOL_C3 = 1e-4              # F4-C3
TOL_C5 = 1e-9              # F4-C5 (fijado en el contrato r4)
L_LIST = [60.0, 80.0, 100.0, 120.0]

R = {"meta": {}, "runs": {}, "criteria": [], "status": None, "summary": {}}


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
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as fh:
            old = json.load(fh)
        R["runs"] = old.get("runs", {})


def key_of(L, h, K):
    return f"i|L{L:g}|h{h:g}|K{K}"


def run_case(L, h, K):
    key = key_of(L, h, K)
    if key in R["runs"]:
        log(f"omitido (ya existe): {key}")
        return R["runs"][key]
    t0 = time.time()
    res = rt.solve_near(rt.shapes_cont(), L, h, SIGMA, k=K, s_sub=8)
    el = time.time() - t0
    sel = rt.select_core(res)
    idx = sel["sel_index"]
    n_core = res["neff"][idx] if idx is not None else None
    P_sel = sel["P_in_all"][idx] if idx is not None else None
    bound = (n_core is not None) and (P_sel >= P_THR) and (abs(n_core - SIGMA) <= WIN)
    rec = {
        "L_um": L, "h_um": h, "K": K, "N_grid": res["N"], "unknowns": res["unknowns"],
        "time_s": round(el, 2), "n_top8": res["neff"][:8], "sel_index": idx,
        "n_core": n_core, "P_in_sel": P_sel, "ligado": bool(bound),
        "P_in_first_K": sel["P_in_all"],
    }
    R["runs"][key] = rec
    save()
    log(f"{key}: n_core={n_core} idx={idx} P_in={P_sel} ligado={bound} unk={res['unknowns']} t={el:.1f}s")
    return rec


def get(L, h, K=K_MAIN):
    rec = R["runs"].get(key_of(L, h, K))
    return rec["n_core"] if rec else None


def evaluate():
    crit = []

    def add(cid, desc, value, passed, evaluable=True, note="", informative=False):
        crit.append({"id": cid, "description": desc, "value": value,
                     "pass": (None if informative else bool(passed and evaluable)),
                     "evaluable": bool(evaluable), "informative": informative, "note": note})

    # F4-C1: convergencia de caja, L=120 frente a L=100 (h=0,25)
    n100, n120 = get(100.0, 0.25), get(120.0, 0.25)
    if n100 is not None and n120 is not None:
        d = n120 - n100
        add("F4-C1", "|n(i;L=120)-n(i;L=100)| < 1e-6 (h=0,25)", d, abs(d) < TOL_C1)
    else:
        add("F4-C1", "|n(i;L=120)-n(i;L=100)| < 1e-6 (h=0,25)", None, False, False, "falta una corrida")

    # F4-C2: caso i ligado en las cuatro cajas (h=0,25)
    vals = {}
    ok = True
    for L in L_LIST:
        rec = R["runs"].get(key_of(L, 0.25, K_MAIN))
        if rec is None:
            vals[f"{L:g}"] = None
            ok = False
        else:
            vals[f"{L:g}"] = {"ligado": rec["ligado"], "P_in_sel": rec["P_in_sel"], "n_core": rec["n_core"]}
            ok = ok and rec["ligado"]
    add("F4-C2", "caso i ligado (P>=0,5 y |n-sigma|<=0,002) en L=60,80,100,120 (h=0,25)",
        vals, ok, all(v is not None for v in vals.values()))

    # F4-C3: control analitico con L=120
    if n120 is not None:
        d = n120 - N_AN
        add("F4-C3", "|Re n(i;L=120,h=0,25) - Re n_an(i)| <= 1e-4", d, abs(d) <= TOL_C3)
    else:
        add("F4-C3", "|Re n(i;L=120,h=0,25) - Re n_an(i)| <= 1e-4", None, False, False, "falta L=120")

    # F4-C4 (informativo): malla h=0,2 frente a h=0,25, por L
    rows = {}
    for L in L_LIST:
        a = get(L, 0.25)
        b = get(L, 0.2)
        if a is not None and b is not None:
            rows[f"{L:g}"] = {"n_h025": a, "n_h02": b, "delta": b - a}
        else:
            rows[f"{L:g}"] = {"n_h025": a, "n_h02": b, "delta": None,
                              "nota": "h=0,2 no calculada" if b is None else "h=0,25 no calculada"}
    add("F4-C4", "malla: n(h=0,2)-n(h=0,25) por L (informativo, sin umbral de paso)", rows, None,
        informative=True)

    # F4-C5: independencia de K en L=60 (h=0,25)
    k30 = get(60.0, 0.25, 30)
    k60 = get(60.0, 0.25, 60)
    if k30 is not None and k60 is not None:
        d = k60 - k30
        add("F4-C5", "L=60,h=0,25: |n(K=60)-n(K=30)| < 1e-9", d, abs(d) < TOL_C5)
    else:
        add("F4-C5", "L=60,h=0,25: |n(K=60)-n(K=30)| < 1e-9", None, False, False, "falta una corrida")

    # F4-C6 (trazos, F4(d)): no se ejecuta en esta corrida; solo aplicable si F4-C1 pasa
    c1 = [c for c in crit if c["id"] == "F4-C1"][0]
    if c1["pass"]:
        add("F4-C6", "trazos N=48,64,96: |Delta(N)| < 1e-5 (F4(d) no ejecutado)", None, False, False,
            "F4(d) no ejecutado en esta ronda")
    else:
        add("F4-C6", "trazos (no aplicable: F4-C1 no pasa, F4(d) no se ejecuta)", None, None, False,
            "no aplicable", informative=True)

    R["criteria"] = crit
    main_ids = ("F4-C1", "F4-C2", "F4-C3", "F4-C5")
    all_eval = all(c["evaluable"] for c in crit if c["id"] in main_ids)
    if not all_eval:
        R["status"] = "partial"
    elif c1["pass"]:
        R["status"] = "partial"   # F4-C1 pasa pero F4(d) (trazos) no se ejecuto
    else:
        R["status"] = "partial"   # F4-C1 no pasa: se declara el limite; F4(d) no se ejecuta
    R["summary"] = {c["id"]: c["pass"] for c in crit}
    save()
    return crit


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    R["meta"] = {"contrato": "CONTRATO-tracks-r4.md", "modulo_base": "run_tracks.py (ronda 1)",
                 "sigma_neff": SIGMA, "K_main": K_MAIN, "win": WIN, "p_thr": P_THR, "s_sub": 8,
                 "box_convention": "L = semilado; caja [-L,L]^2", "python": sys.version.split()[0],
                 "omp_num_threads": os.environ.get("OMP_NUM_THREADS"),
                 "nota": "Modelo escalar ideal. No es dispositivo ni medida."}
    load_existing()
    if cmd == "run":
        block = sys.argv[2] if len(sys.argv) > 2 else "A"
        log(f"inicio bloque {block} (sigma={SIGMA})")
        if block == "A":
            for L in L_LIST:
                run_case(L, 0.25, K_MAIN)
            run_case(60.0, 0.25, 60)
        elif block == "B":
            run_case(60.0, 0.2, K_MAIN)
            run_case(80.0, 0.2, K_MAIN)
        elif block == "C":
            run_case(100.0, 0.2, K_MAIN)
            run_case(120.0, 0.2, K_MAIN)
        elif block == "D":
            # diagnostico informativo (desviacion de protocolo declarada): L=100 con K=60
            run_case(100.0, 0.25, 60)
        log(f"fin bloque {block}")
    if cmd in ("run", "eval"):
        crit = evaluate()
        for c in crit:
            log(f"CRIT {c['id']}: pass={c['pass']} evaluable={c['evaluable']} value={c['value']}")
        log(f"status={R['status']}")


if __name__ == "__main__":
    main()
