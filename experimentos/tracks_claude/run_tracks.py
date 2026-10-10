"""Tarea F: camisa continua frente a camisa de trazos discretos (modelo ideal, escalar 2D).

Modelo numerico. No es un dispositivo, no es una medida, no es fabricacion.
Contrato: CONTRATO-camisa-trazos.md (escrito antes de ejecutar; umbrales fijados ahi).

Ejecutar desde esta carpeta:
    OMP_NUM_THREADS=1 python -B run_tracks.py
Usa solo numpy, scipy y la biblioteca estandar. Solver: ../solver2d_claude/solver2d.py (Tarea A).
"""
import sys
import os
import json
import math
import time

import numpy as np
import scipy.special as sps
from scipy.optimize import newton

HERE = os.path.dirname(os.path.abspath(__file__))
SOLVER_DIR = os.path.abspath(os.path.join(HERE, "..", "solver2d_claude"))
sys.path.insert(0, SOLVER_DIR)
import solver2d  # noqa: E402  (solver de la Tarea A)

# ---------------- geometria fijada en el contrato ----------------
A_CORE = 6.0          # radio del nucleo (um); el nucleo es el propio vidrio (n = N_BG)
T_JAC = 6.0           # espesor de camisa (um)
R_OUT = A_CORE + T_JAC            # 12 um
R_MID = A_CORE + T_JAC / 2.0      # 9 um, radio medio de la camisa
R_T = 1.5             # radio de cada trazo (um)
N_BG = 1.444          # fondo y nucleo
N_JAC = 1.439         # camisa (delta n = -0.005)
LAM = 1.55            # um
K0 = 2.0 * math.pi / LAM
NS = [8, 16, 24, 32, 48, 64, 96]
RING_AREA = math.pi * (R_OUT ** 2 - A_CORE ** 2)   # 108 pi um^2
BAND_R_IN = R_MID - R_T                             # 7.5 um
BAND_R_OUT = R_MID + R_T                            # 10.5 um
PIN_R = R_OUT          # region para la potencia del modo de nucleo (r <= 12 um)
P_THR = 0.5            # umbral de potencia para aceptar el modo de nucleo
WIN_NEFF = 0.002      # ventana |n_core - sigma| (enmienda 1: seleccion por desplazamiento)

OUT_JSON = os.path.join(HERE, "resultados.json")
LOG = os.path.join(HERE, "log_run.txt")

RESULTS = {"meta": {}, "analytic": {}, "runs": {}, "fracs": {}, "criteria": [], "status": None}


def log(msg):
    stamp = time.strftime("%H:%M:%S", time.gmtime())
    line = f"[{stamp}Z] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def save():
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(RESULTS, fh, indent=2, ensure_ascii=False, default=float)


# ---------------- formas ----------------
def shapes_cont(n=N_JAC, r_in=A_CORE, r_out=R_OUT):
    return [{"kind": "annulus", "x0": 0.0, "y0": 0.0, "r_in": r_in, "r_out": r_out, "n": n}]


def track_centers(N, phase=0.0):
    th = 2.0 * math.pi * np.arange(N) / N + phase
    return R_MID * np.cos(th), R_MID * np.sin(th)


def shapes_tracks(N, phase=0.0):
    xc, yc = track_centers(N, phase)
    return [{"kind": "disk", "x0": float(x), "y0": float(y), "r": R_T, "n": N_JAC}
            for x, y in zip(xc, yc)]


def f_formula(N):
    """Fraccion de area de la tarea: N pi r_t^2 / (2 pi (a + t/2) t) = N/48."""
    return N * R_T ** 2 / (2.0 * R_MID * T_JAC)


def n_eq_of_f(f):
    return math.sqrt(f * N_JAC ** 2 + (1.0 - f) * N_BG ** 2)


# ---------------- seleccion del modo de nucleo ----------------
def select_core(res):
    x = res["x"]
    h = res["h_um"]
    X, Y = np.meshgrid(x, x)            # psi[iy, ix], X[iy,ix] = x[ix]
    rr = np.hypot(X, Y)
    inside = rr <= PIN_R + 1e-12
    inner = rr <= A_CORE + 1e-12
    P_in, P_core = [], []
    for psi in res["psi"]:
        w = psi * psi * h * h
        P_in.append(float(w[inside].sum()))
        P_core.append(float(w[inner].sum()))
    sel = None
    for m, p in enumerate(P_in):
        if p >= P_THR:
            sel = m
            break
    return {"sel_index": sel, "P_in_all": P_in, "P_core_all": P_core}


SIGMA_NEFF = None   # fijado en main() a partir de la raiz analitica del caso (i), antes de los casos discretos


def solve_near(shapes, L, h, sigma_neff, k=12, s_sub=8):
    """Misma discretizacion que solver2d.solve (promediado subpixel, Laplaciano de 5 puntos,
    Dirichlet, dominio [-L, L]^2 con L semilado), pero con shift-invert en sigma = (k0 sigma_neff)^2
    para obtener los k autovalores mas cercanos. Usa cell_average y _index_from_shapes de solver2d."""
    import scipy.sparse as sp
    import scipy.sparse.linalg as sla
    h = float(h)
    L = float(L)
    nh = int(round(L / h))
    N = 2 * nh + 1
    x = (np.arange(N) - (N - 1) / 2.0) * h

    def f(X, Y):
        return solver2d._index_from_shapes(shapes, N_BG, X, Y) ** 2

    cell_n2 = solver2d.cell_average(f, x, h, s_sub)
    M = N - 2
    n2_int = cell_n2[1:-1, 1:-1]
    T = sp.diags([np.ones(M - 1), -2.0 * np.ones(M), np.ones(M - 1)], [-1, 0, 1], format="csr") / h ** 2
    I = sp.identity(M, format="csr")
    P = (sp.kron(I, T) + sp.kron(T, I) + sp.diags(K0 ** 2 * n2_int.ravel())).tocsc()
    sigma = (K0 * sigma_neff) ** 2
    vals, vecs = sla.eigsh(P, k=int(k), sigma=sigma, which="LM")
    order = np.argsort(vals.real)[::-1]
    beta2 = vals.real[order]
    vecs = vecs[:, order]
    neff = np.sqrt(beta2) / K0
    psi_list = []
    for m in range(int(k)):
        full = np.zeros((N, N), dtype=float)
        full[1:-1, 1:-1] = vecs[:, m].real.reshape(M, M)
        norm = math.sqrt(float(np.sum(full * full)) * h * h)
        full = full / norm
        imax = np.unravel_index(int(np.argmax(np.abs(full))), full.shape)
        if full[imax] < 0.0:
            full = -full
        psi_list.append(full)
    return {"neff": [float(v) for v in neff], "x": x, "psi": psi_list, "h_um": h,
            "N": N, "unknowns": M * M}


def run_case(case, shapes, L, h, K, phase=None, s_sub=8):
    key = f"{case}|L{L:g}|h{h:g}" + (f"|ph{phase:.4f}" if phase is not None else "")
    if key in RESULTS["runs"]:
        log(f"omitido (ya existe): {key}")
        return RESULTS["runs"][key]
    t0 = time.time()
    res = solve_near(shapes, L, h, SIGMA_NEFF, k=K, s_sub=s_sub)
    el = time.time() - t0
    sel = select_core(res)
    idx = sel["sel_index"]
    n_core = res["neff"][idx] if idx is not None else None
    rec = {
        "case": case, "L_um": L, "h_um": h, "K": K, "N_grid": res["N"],
        "unknowns": res["unknowns"], "s_sub": s_sub, "time_s": round(el, 2),
        "neff_top8": res["neff"][:8],
        "n_top_mode": res["neff"][0], "P_in_top_mode": sel["P_in_all"][0],
        "sel_index": idx, "n_core": n_core,
        "P_in_sel": sel["P_in_all"][idx] if idx is not None else None,
        "P_core_sel": sel["P_core_all"][idx] if idx is not None else None,
        "P_in_first_K": sel["P_in_all"],
    }
    RESULTS["runs"][key] = rec
    save()
    log(f"{key}: n_core={n_core} idx={idx} P_in={rec['P_in_sel']} top={rec['n_top_mode']:.10f} "
        f"P_in_top={rec['P_in_top_mode']:.3e} unk={res['unknowns']} t={el:.1f}s")
    return rec


# ---------------- referencia analitica: modo radial m=0 con radiacion ----------------
def G_leaky(neff, n_core, n_ring, n_out, r1, r2, k0=K0):
    """Funcion sin polos G = det * F, cuyo cero es el modo radial m=0 con condicion saliente.
    Interior: J0(q1 r) para r < r1; anillo: A I0(p r) + B K0(p r); exterior: C H0^(1)(q0 r) para r > r2.
    Se multiplica por el determinante de la matriz 2x2 de continuidad en r1 (elimina polos espurios).
    Devuelve (G, S) con S = escala para residuo relativo |G|/S."""
    ne = np.asarray(neff, dtype=complex)
    q1 = k0 * np.sqrt(n_core ** 2 - ne ** 2 + 0j)
    q0 = k0 * np.sqrt(n_out ** 2 - ne ** 2 + 0j)
    p = k0 * np.sqrt(ne ** 2 - n_ring ** 2 + 0j)
    j = sps.jv(0, q1 * r1)
    jp = -q1 * sps.jv(1, q1 * r1)
    u1, v1 = sps.iv(0, p * r1), sps.kv(0, p * r1)
    u1p, v1p = p * sps.iv(1, p * r1), -p * sps.kv(1, p * r1)
    a1 = j * v1p - v1 * jp           # det * A
    b1 = u1 * jp - u1p * j           # det * B
    u2, v2 = sps.iv(0, p * r2), sps.kv(0, p * r2)
    u2p, v2p = p * sps.iv(1, p * r2), -p * sps.kv(1, p * r2)
    Gg = a1 * u2 + b1 * v2           # det * g(r2)
    Ggp = a1 * u2p + b1 * v2p        # det * g'(r2)
    H0 = sps.hankel1(0, q0 * r2)
    H1 = sps.hankel1(1, q0 * r2)
    G = Ggp * H0 + Gg * q0 * H1
    S = np.abs(Ggp * H0) + np.abs(Gg * q0 * H1) + 1e-300
    return G, S


def leaky_roots(n_core, n_ring, n_out, r1, r2, im_max=0.02):
    """Busca ceros complejos de G por arranques multiples de Newton (secante compleja).
    Acepta una raiz si el residuo relativo |G|/S <= 1e-9 y Re(neff) dentro de [min, max] de los indices."""
    lo = min(n_ring, n_core) - 1e-3
    hi = max(n_ring, n_core) + 1e-3
    starts = [complex(a, b) for a in np.linspace(lo, hi, 61) for b in np.linspace(-im_max, im_max, 21)]
    roots = []
    for z0 in starts:
        try:
            with np.errstate(all="ignore"):
                rt = newton(lambda ne: complex(G_leaky(ne, n_core, n_ring, n_out, r1, r2)[0]),
                            z0, tol=1e-14, maxiter=60)
        except (RuntimeError, OverflowError, FloatingPointError, ValueError, ZeroDivisionError):
            continue
        if not np.isfinite(rt):
            continue
        Gr, Sr = G_leaky(complex(rt), n_core, n_ring, n_out, r1, r2)
        rel = float(abs(Gr) / Sr)
        if not np.isfinite(rel) or rel > 1e-9:
            continue
        if not (lo <= rt.real <= hi):
            continue
        if all(abs(rt - q) > 1e-7 for q in roots):
            roots.append(complex(rt))
    roots.sort(key=lambda z: -z.real)
    return roots, None


def analytic_block():
    out = {}
    cases = {
        "i": (N_BG, N_JAC, N_BG, A_CORE, R_OUT),
        "iv": (N_BG, N_JAC, N_BG, BAND_R_IN, BAND_R_OUT),
    }
    for N in NS:
        neq = n_eq_of_f(f_formula(N))
        cases[f"iii_N{N}"] = (N_BG, neq, N_BG, A_CORE, R_OUT)
    for name, (nc, nr, no, r1, r2) in cases.items():
        roots, min_r = leaky_roots(nc, nr, no, r1, r2)
        # modo de nucleo: raiz de mayor Re con |Im| < 0.02 dentro de [n_ring, n_core]
        cand = [z for z in roots if abs(z.imag) < 0.02 and min(nr, nc) - 1e-3 <= z.real <= max(nr, nc) + 1e-3]
        best = max(cand, key=lambda z: z.real) if cand else None
        rec = {"n_ring": nr, "r1": r1, "r2": r2,
               "all_roots": [[z.real, z.imag] for z in roots],
               "n_roots": len(roots), "min_grid_residual": min_r,
               "Re_neff": best.real if best is not None else None,
               "Im_neff": best.imag if best is not None else None}
        out[name] = rec
        log(f"analitica {name}: n_ring={nr:.6f} raices={len(roots)} "
            f"Re neff={rec['Re_neff']} Im neff={rec['Im_neff']}")
    RESULTS["analytic"] = out
    save()


# ---------------- area de union de trazos (independiente, malla fina) ----------------
def union_fraction_grid(N, phase=0.0, dx=0.01):
    xs = np.arange(-R_OUT - 0.5, R_OUT + 0.5 + dx / 2, dx)
    n = xs.size
    xc, yc = track_centers(N, phase)
    mask = np.zeros((n, n), dtype=bool)
    for x0, y0 in zip(xc, yc):
        i0 = max(0, int(math.floor((x0 - R_T - xs[0]) / dx)) - 1)
        i1 = min(n, int(math.ceil((x0 + R_T - xs[0]) / dx)) + 2)
        j0 = max(0, int(math.floor((y0 - R_T - xs[0]) / dx)) - 1)
        j1 = min(n, int(math.ceil((y0 + R_T - xs[0]) / dx)) + 2)
        X, Y = np.meshgrid(xs[i0:i1], xs[j0:j1])
        m = (X - x0) ** 2 + (Y - y0) ** 2 <= R_T ** 2
        sub = mask[j0:j1, i0:i1]
        sub |= m
    XX, YY = np.meshgrid(xs, xs)
    rr = np.hypot(XX, YY)
    ring = (rr >= A_CORE) & (rr <= R_OUT)
    area_ring_grid = ring.sum() * dx * dx
    f_grid = float((mask & ring).sum()) / float(ring.sum())
    return {"f_union_grid": f_grid, "ring_area_grid": float(area_ring_grid),
            "ring_area_exact": RING_AREA, "dx": dx}


def min_center_distance(N):
    return 2.0 * R_MID * math.sin(math.pi / N)


def fracs_block():
    out = {}
    for N in NS:
        d = min_center_distance(N)
        f_form = f_formula(N)
        # area exacta solo si no hay solapes entre trazos
        if d >= 2 * R_T:
            f_exact = N * math.pi * R_T ** 2 / RING_AREA
            overlap = False
        else:
            f_exact = None
            overlap = True
        g = union_fraction_grid(N)
        out[f"N{N}"] = {"f_formula": f_form, "min_center_dist": d, "overlap": overlap,
                        "f_union_exact_if_disjoint": f_exact, **g,
                        "n_eq_formula": n_eq_of_f(f_form)}
        log(f"fracs N={N}: f_formula={f_form:.5f} f_union_grid={g['f_union_grid']:.5f} "
            f"overlap={overlap} dmin={d:.3f}")
    # limite de banda
    gb = union_fraction_grid(96, dx=0.01)
    out["band_limit_fraction_of_ring"] = (BAND_R_OUT ** 2 - BAND_R_IN ** 2) / (R_OUT ** 2 - A_CORE ** 2)
    out["band_grid_check_N96"] = gb["f_union_grid"]
    RESULTS["fracs"] = out
    save()


# ---------------- ejecucion ----------------
def main():
    RESULTS["meta"] = {
        "utc_start": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "geometry_um": {"a": A_CORE, "t": T_JAC, "r_mid": R_MID, "r_t": R_T, "n_bg": N_BG,
                        "n_jacket": N_JAC, "lam": LAM, "k0": K0},
        "solver": "experimentos/solver2d_claude/solver2d.py (Tarea A)",
        "s_sub": 8, "P_thr": P_THR, "pin_radius_um": PIN_R, "WIN_neff": WIN_NEFF,
        "dominio": "[-L, L]^2 (L semilado, como en solver2d)",
        "note": "Modelo escalar ideal. No es dispositivo ni medida.",
    }
    open(LOG, "w", encoding="utf-8").close()
    log("inicio")
    fracs_block()
    analytic_block()
    global SIGMA_NEFF
    SIGMA_NEFF = RESULTS["analytic"]["i"]["Re_neff"]
    RESULTS["meta"]["sigma_neff"] = SIGMA_NEFF
    log(f"sigma_neff (raiz analitica del caso i) = {SIGMA_NEFF}")

    def cases_at(L, h, K, phase_ids=False):
        cs = {"i": shapes_cont(), "iv": shapes_cont(N_JAC, BAND_R_IN, BAND_R_OUT)}
        for N in NS:
            cs[f"ii_N{N}"] = shapes_tracks(N)
            cs[f"iii_N{N}"] = shapes_cont(n_eq_of_f(f_formula(N)))
        return cs

    # bloque principal: L=40, K=30, h=0.25 y h=0.125 (y 0.5 en casos de convergencia)
    cs = cases_at(40, 0.25, 30)
    for c in ["i", "iv"] + [f"ii_N{N}" for N in NS] + [f"iii_N{N}" for N in NS]:
        run_case(c, cs[c], 40, 0.25, 12)
    cs = cases_at(40, 0.125, 30)
    for c in ["i", "iv"] + [f"ii_N{N}" for N in NS] + [f"iii_N{N}" for N in NS]:
        run_case(c, cs[c], 40, 0.125, 12)
    # convergencia en h adicional (h = 0.5) en casos de prueba
    for c in ["i", "ii_N8", "ii_N48"]:
        run_case(c, cs[c], 40, 0.5, 12)
    # dominio: L=50 (K=45) y L=60 (K=60) en h=0.25
    csL = cases_at(50, 0.25, 45)
    for c in ["i", "ii_N48"]:
        run_case(c, csL[c], 50, 0.25, 12)
    csL60 = cases_at(60, 0.25, 60)
    run_case("i", csL60["i"], 60, 0.25, 12)
    # diagnostico de fase de trazos (desplazamiento pi/N), L=40, h=0.25
    for N in [8, 16]:
        run_case(f"ii_N{N}_phshift", shapes_tracks(N, phase=math.pi / N), 40, 0.25, 12,
                 phase=math.pi / N)

    evaluate()
    save()
    log("fin")


def get(case, L, h, K=None):
    for k, v in RESULTS["runs"].items():
        if v["case"] == case and abs(v["L_um"] - L) < 1e-9 and abs(v["h_um"] - h) < 1e-12:
            return v
    return None


def nval(case, L, h):
    r = get(case, L, h)
    return None if (r is None or r["n_core"] is None) else r["n_core"]


def evaluate():
    crit = []

    def add(cid, desc, value, passed, evaluable=True, note=""):
        crit.append({"id": cid, "description": desc, "value": value,
                     "pass": bool(passed) if evaluable else False,
                     "evaluable": bool(evaluable), "note": note})

    an_i = RESULTS["analytic"]["i"]["Re_neff"]

    # C1: convergencia en h
    for c in ["i", "ii_N8", "ii_N48"]:
        a, b = nval(c, 40, 0.25), nval(c, 40, 0.125)
        if a is None or b is None:
            add(f"C1_{c}", f"|n(h=0.25)-n(h=0.125)|<=1e-5 ({c})", None, False, False, "modo no hallado")
        else:
            d = abs(a - b)
            add(f"C1_{c}", f"|n(h=0.25)-n(h=0.125)|<=1e-5 ({c})", d, d <= 1e-5)
    n05, n025, n0125 = nval("i", 40, 0.5), nval("i", 40, 0.25), nval("i", 40, 0.125)
    if None in (n05, n025, n0125):
        add("C1b_i", "orden observado h en (i) >= 1,5", None, False, False, "faltan datos")
    else:
        d1, d2 = abs(n05 - n025), abs(n025 - n0125)
        if d1 > 1e-9 and d2 > 1e-9:
            p = math.log(d1 / d2, 2)
            add("C1b_i", "orden observado h en (i) >= 1,5", p, p >= 1.5)
        else:
            add("C1b_i", "orden observado h en (i) >= 1,5", None, False, False,
                "diferencias <= 1e-9: no evaluable")

    # C2: dominio L=50 vs L=40 (h=0.25)
    for c in ["i", "ii_N48"]:
        a, b = nval(c, 50, 0.25), nval(c, 40, 0.25)
        if a is None or b is None:
            add(f"C2_{c}", f"|n(L=50)-n(L=40)|<=1e-5 ({c}, h=0.25)", None, False, False, "modo no hallado")
        else:
            d = abs(a - b)
            add(f"C2_{c}", f"|n(L=50)-n(L=40)|<=1e-5 ({c}, h=0.25)", d, d <= 1e-5)

    # C3: analitica (i)
    nb = nval("i", 40, 0.125)
    if nb is None:
        add("C3", "|Re n_caja(i,L=40,h=0.125) - Re n_analitica(i)|<=1e-4", None, False, False, "modo no hallado")
    else:
        d = abs(nb - an_i)
        add("C3", "|Re n_caja(i,L=40,h=0.125) - Re n_analitica(i)|<=1e-4", d, d <= 1e-4)
    e40 = abs(nval("i", 40, 0.25) - an_i) if nval("i", 40, 0.25) is not None else None
    e60 = abs(nval("i", 60, 0.25) - an_i) if nval("i", 60, 0.25) is not None else None
    if e40 is None or e60 is None:
        add("C3b", "error analitico baja con L (L=60 < L=40, h=0.25)", None, False, False, "faltan datos")
    else:
        add("C3b", "error analitico baja con L (L=60 < L=40, h=0.25)",
            {"err_L40": e40, "err_L60": e60}, e60 < e40)

    # C4: seleccion del modo de nucleo en todas las corridas
    bad = []
    total = 0
    for k, v in RESULTS["runs"].items():
        total += 1
        ok = (v["sel_index"] is not None and v["P_in_sel"] is not None
              and v["P_in_sel"] >= P_THR and abs(v["n_core"] - SIGMA_NEFF) <= WIN_NEFF)
        if not ok:
            bad.append(k)
    add("C4", "modo de nucleo: P(r<=12)>=0,5 y |n-sigma|<=0,002 en todas las corridas", {"n_runs": total, "fallos": bad},
        len(bad) == 0 and total > 0)

    # C5: geometria de trazos (exacta para N=8,16)
    ok5 = True
    vals5 = {}
    for N in [8, 16]:
        fe = RESULTS["fracs"][f"N{N}"]["f_union_exact_if_disjoint"]
        vals5[N] = fe
        if fe is None or abs(fe - f_formula(N)) > 1e-6:
            ok5 = False
    add("C5a", "f_union exacta = f_formula para N=8,16 (sin solapes, error<=1e-6)", vals5, ok5)
    g16 = RESULTS["fracs"]["N16"]["f_union_grid"]
    err16 = abs(g16 - f_formula(16)) / f_formula(16)
    add("C5b", "estimador de malla: error relativo <=0,5 % en N=16", err16, err16 <= 0.005)

    # C6: pregunta principal (umbral de la tarea)
    for N in [48, 64, 96]:
        a, b = nval(f"ii_N{N}", 40, 0.125), nval(f"iii_N{N}", 40, 0.125)
        note = "" if N <= 48 else "f>1: la formula (iii) no es fraccion de volumen; valor calculado, interpretacion no valida"
        if a is None or b is None:
            add(f"C6_N{N}", f"|n_ii(N)-n_iii(N)|<1e-5 (N={N})", None, False, False, "modo no hallado")
        else:
            d = abs(a - b)
            add(f"C6_N{N}", f"|n_ii(N)-n_iii(N)|<1e-5 (N={N}, L=40, h=0.125)", d, d < 1e-5, True, note)

    # C7: convergencia en N hacia la banda (iv)
    a, b = nval("ii_N96", 40, 0.125), nval("iv", 40, 0.125)
    if a is None or b is None:
        add("C7", "|n_ii(96)-n_iv|<=1e-5", None, False, False, "modo no hallado")
    else:
        d = abs(a - b)
        add("C7", "|n_ii(96)-n_iv|<=1e-5 (L=40, h=0.125)", d, d <= 1e-5)

    RESULTS["criteria"] = crit
    evaluated_all = all(c["evaluable"] for c in crit)
    RESULTS["status"] = "done" if evaluated_all else "partial"
    for c in crit:
        log(f"CRIT {c['id']}: pass={c['pass']} evaluable={c['evaluable']} value={c['value']}")
    log(f"status={RESULTS['status']}")


if __name__ == "__main__":
    main()
