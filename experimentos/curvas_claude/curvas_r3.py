# -*- coding: utf-8 -*-
"""Tarea I3 (curvas, ronda 3): seguimiento del modo de nucleo por continuacion en R.

Modelo numerico. No es un dispositivo ni una medida.
    n_eq(X, Y) = n_xy(X, Y) * (1 + X/R),  X hacia el exterior de la curva.
Paso 0 = recto. Cadena R = 50, 30, 20, 15, 10 mm. Cada paso: shift-invert con
sigma = (k0 n_eff_prev)^2, n_modes = 12, y se elige el modo de mayor solape con el
modo del paso anterior (S = (sum psi psi_prev h^2)^2 > 0,9).
solver2d no se modifica: se importan solver2d.cell_average y solver2d.solve (solo para
verificacion). Umbrales y reglas: CONTRATO-curvas-r3.md (fijados antes de ejecutar).

Ejecutar: OMP_NUM_THREADS=1 python -B curvas_r3.py
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

import numpy as np  # noqa: E402
import scipy.sparse as sp  # noqa: E402
import scipy.sparse.linalg as sla  # noqa: E402
import scipy.special as sps  # noqa: E402
from scipy.optimize import brentq  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SOLVER_DIR = os.path.normpath(os.path.join(HERE, "..", "solver2d_claude"))
sys.path.insert(0, SOLVER_DIR)
import solver2d  # noqa: E402

LAM = 1.55
A = 6.0
N1 = 1.444
N2 = 1.439
S_SUB = 8
K0 = 2.0 * np.pi / LAM
H = 0.25
NMODES = 12
CHAIN_MM = [50.0, 30.0, 20.0, 15.0, 10.0]
LS = [40.0, 60.0, 80.0, 100.0]
S_MIN = 0.9
THR_POUT = 0.01
TOL_DN = 1e-6
N_R2_L40 = {10.0: 1.442266248115, 20.0: 1.442210322525, 50.0: 1.442194819527}  # RESULTADOS-curvas-r2.md, L=40, h=0.25

LOG_PATH = os.path.join(HERE, "log_curvas_r3.txt")
LOG = open(LOG_PATH, "w", encoding="utf-8")


def log(msg=""):
    print(msg, flush=True)
    LOG.write(msg + "\n")
    LOG.flush()


# ---------------------------------------------------------------- analitica (misma formula que curvas.py)
def lp01_analytic():
    V = K0 * A * math.sqrt(N1 ** 2 - N2 ** 2)

    def f(U):
        W = math.sqrt(V ** 2 - U ** 2)
        return U * sps.j1(U) * sps.k0(W) - W * sps.k1(W) * sps.j0(U)

    Us = np.linspace(1e-6, V - 1e-6, 4000)
    fv = np.array([f(u) for u in Us])
    idx = np.where(np.sign(fv[:-1]) != np.sign(fv[1:]))[0]
    i = int(idx[0])
    U = brentq(f, Us[i], Us[i + 1], xtol=1e-15, rtol=1e-15, maxiter=500)
    neff = math.sqrt(N1 ** 2 - (U / (K0 * A)) ** 2)
    return {"V": float(V), "U": float(U), "neff": float(neff)}


ANA = lp01_analytic()
ANA_NEFF = ANA["neff"]


# ---------------------------------------------------------------- indice
def n_xy(X, Y):
    r = np.hypot(X, Y)
    return np.where(r < A, N1, N2)


def index_fn_for(R_mm):
    if R_mm is None:
        return n_xy
    R_um = 1000.0 * float(R_mm)

    def n_eq(X, Y):
        return n_xy(X, Y) * (1.0 + X / R_um)

    return n_eq


# ---------------------------------------------------------------- malla y operador (misma convencion que solver2d.solve)
class Grid:
    def __init__(self, L, h):
        nh = int(round(L / h))
        self.N = 2 * nh + 1
        self.h = float(h)
        self.L = float(L)
        self.x = (np.arange(self.N) - (self.N - 1) / 2.0) * self.h
        self.X = np.tile(self.x[None, :], (self.N, 1))  # X[iy, ix] = x[ix]
        self.Y = np.tile(self.x[:, None], (1, self.N))  # Y[iy, ix] = y[iy]
        self.R2 = np.hypot(self.X, self.Y)


def cell_n2(grid, index_fn):
    def f(X, Y):
        return np.asarray(index_fn(X, Y), dtype=float) ** 2

    return solver2d.cell_average(f, grid.x, grid.h, S_SUB)


def build_P(grid, cn2):
    M = grid.N - 2
    h = grid.h
    T = sp.diags([np.ones(M - 1), -2.0 * np.ones(M), np.ones(M - 1)], [-1, 0, 1], format="csr") / h ** 2
    I = sp.identity(M, format="csr")
    n2_int = cn2[1:-1, 1:-1]
    P = (sp.kron(I, T) + sp.kron(T, I) + sp.diags(K0 ** 2 * n2_int.ravel())).tocsc()
    return P, M


def eig_sigma(grid, cn2, sigma):
    """NMODES autovalores mas cercanos a sigma (en beta^2, um^-2), shift-invert, which='LM'."""
    P, M = build_P(grid, cn2)
    vals, vecs = sla.eigsh(P, k=NMODES, sigma=sigma, which="LM")
    modes = []
    for m in range(len(vals)):
        beta2 = float(np.real(vals[m]))
        v = np.real(vecs[:, m])
        resid = P @ v - beta2 * v
        rel = float(np.linalg.norm(resid) / (abs(beta2) * np.linalg.norm(v)))
        full = np.zeros((grid.N, grid.N), dtype=float)
        full[1:-1, 1:-1] = v.reshape(M, M)
        norm = math.sqrt(float(np.sum(full * full)) * grid.h * grid.h)
        full = full / norm
        imax = np.unravel_index(int(np.argmax(np.abs(full))), full.shape)
        if full[imax] < 0.0:
            full = -full
        modes.append({"neff": math.sqrt(beta2) / K0, "psi": full, "resid_rel": rel})
    return modes


def eig_shift_neff(grid, cn2, neff_sigma):
    return eig_sigma(grid, cn2, (K0 * neff_sigma) ** 2)


def overlap_S(grid, psi, psi_ref):
    return float((np.sum(psi * psi_ref) * grid.h * grid.h) ** 2)


def metrics(grid, psi, neff, R_mm):
    h = grid.h
    Pw = psi * psi * h * h
    out = {
        "neff": float(neff),
        "norm_err": float(abs(Pw.sum() - 1.0)),
        "centroid_um": float((grid.X * Pw).sum()),
        "P_core": float(Pw[grid.R2 < A].sum()),
        "y_mirror_rel": float(np.max(np.abs(psi - psi[::-1, :])) / np.max(np.abs(psi))),
    }
    if R_mm is None:
        out["x_t_um"] = None
        out["P_out"] = None
    else:
        x_t = 1000.0 * float(R_mm) * (neff / N2 - 1.0)
        out["x_t_um"] = float(x_t)
        out["P_out"] = float(Pw[grid.X > x_t].sum())
    return out


# ---------------------------------------------------------------- una longitud L: recto + cadena
def run_L(L):
    t0 = time.time()
    grid = Grid(L, H)
    cn2_rec = cell_n2(grid, n_xy)
    modes0 = eig_shift_neff(grid, cn2_rec, ANA_NEFF)
    best0 = min(modes0, key=lambda md: abs(md["neff"] - ANA_NEFF))
    psi_rec = best0["psi"]
    rec = metrics(grid, psi_rec, best0["neff"], None)
    rec.update({
        "dist_a_analitica": float(best0["neff"] - ANA_NEFF),
        "resid_rel": best0["resid_rel"],
        "aceptado": bool(abs(best0["neff"] - ANA_NEFF) <= 1e-5),
        "neff_12": [float(m["neff"]) for m in modes0],
    })
    log("[L=%g] N=%d incognitas=%d recto neff=%.12f err_analitica=%+.3e resid=%.2e t=%.1fs"
        % (L, grid.N, (grid.N - 2) ** 2, rec["neff"], rec["neff"] - ANA_NEFF, rec["resid_rel"], time.time() - t0))

    pasos = {}
    prev_neff, prev_psi = best0["neff"], psi_rec
    chain_ok = True
    for R_mm in CHAIN_MM:
        key = "R%g" % R_mm
        if not chain_ok:
            pasos[key] = {"evaluado": False, "motivo": "cadena detenida en un radio mayor"}
            log("[L=%g] R=%g mm: no evaluado (cadena detenida)" % (L, R_mm))
            continue
        ts = time.time()
        cn2 = cell_n2(grid, index_fn_for(R_mm))
        modes = eig_shift_neff(grid, cn2, prev_neff)
        S_prev_list = [overlap_S(grid, md["psi"], prev_psi) for md in modes]
        k = int(np.argmax(S_prev_list))
        md = modes[k]
        S_prev = S_prev_list[k]
        # rango del modo elegido por cercania a sigma (n_eff del paso anterior)
        order = sorted(range(len(modes)), key=lambda j: abs(modes[j]["neff"] - prev_neff))
        rank = int(order.index(k))
        met = metrics(grid, md["psi"], md["neff"], R_mm)
        S_rec = overlap_S(grid, md["psi"], psi_rec)
        step = dict(met)
        step.update({
            "R_mm": float(R_mm),
            "S_prev": float(S_prev),
            "S_rec": float(S_rec),
            "resid_rel": float(md["resid_rel"]),
            "rank_por_cercania": rank,
            "neff_prev": float(prev_neff),
            "neff_12": [float(m["neff"]) for m in modes],
            "S_prev_12": [float(s) for s in S_prev_list],
            "t_s": float(time.time() - ts),
            "N": int(grid.N),
        })
        if S_prev > S_MIN:
            step["evaluado"] = True
            pasos[key] = step
            prev_neff, prev_psi = md["neff"], md["psi"]
            log("[L=%g] R=%g mm neff=%.12f S_prev=%.6f S_rec=%.6f x_t=%.3f P_out=%.4e P_core=%.4f <x>=%+.4f rank=%d resid=%.1e t=%.1fs"
                % (L, R_mm, step["neff"], S_prev, S_rec, step["x_t_um"], step["P_out"], step["P_core"],
                   step["centroid_um"], rank, step["resid_rel"], step["t_s"]))
        else:
            step["evaluado"] = False
            step["motivo"] = "S_prev <= 0,9: cadena detenida"
            pasos[key] = step
            chain_ok = False
            log("[L=%g] R=%g mm FALLO: S_prev=%.6f <= 0,9 (neff=%.12f, S_rec=%.6f). Cadena detenida."
                % (L, R_mm, S_prev, md["neff"], S_rec))
    log("[L=%g] fin: %.1f s" % (L, time.time() - t0))
    return {"L_um": float(L), "h_um": H, "N": int(grid.N), "unknowns": int((grid.N - 2) ** 2),
            "recto": rec, "pasos": pasos, "t_s": float(time.time() - t0)}


# ---------------------------------------------------------------- criterios
def conv_test(res, R_mm):
    """Prueba de convergencia en L de I3.1 para un radio: |dn(100-80)| < 1e-6, S_rec > 0,9 en ambos L."""
    key = "R%g" % R_mm
    s80 = res[80.0]["pasos"].get(key)
    s100 = res[100.0]["pasos"].get(key)
    if s80 is None or s100 is None or not s80.get("evaluado") or not s100.get("evaluado"):
        return {"R_mm": float(R_mm), "evaluado": False, "pass": None,
                "motivo": "cadena incompleta en L=80 o L=100"}
    d = abs(s100["neff"] - s80["neff"])
    ok_S = bool(s80["S_rec"] > S_MIN and s100["S_rec"] > S_MIN)
    ok = bool(d < TOL_DN and ok_S)
    return {"R_mm": float(R_mm), "evaluado": True, "pass": ok,
            "neff_L80": s80["neff"], "neff_L100": s100["neff"], "abs_diff": float(d),
            "S_rec_L80": s80["S_rec"], "S_rec_L100": s100["S_rec"],
            "x_t_L100_um": s100["x_t_um"], "P_out_L100": s100["P_out"]}


def tendencia(res, L):
    """I3.2 (informativo): signo de n(R_{k+1}) - n(R_k) a lo largo de la cadena decreciente en R."""
    pts = []
    for R_mm in CHAIN_MM:
        s = res[L]["pasos"].get("R%g" % R_mm)
        if s is None or not s.get("evaluado"):
            break
        pts.append((R_mm, s["neff"]))
    if len(pts) < 2:
        return {"L_um": float(L), "puntos": pts, "diferencias": [], "observado": "no evaluado"}
    diffs = [pts[i + 1][1] - pts[i][1] for i in range(len(pts) - 1)]
    if all(d > 0 for d in diffs):
        obs = "crece al bajar R"
    elif all(d < 0 for d in diffs):
        obs = "decrece al bajar R"
    else:
        obs = "mixto"
    return {"L_um": float(L), "puntos_R_neff": [[float(a), float(b)] for a, b in pts],
            "diferencias_neff": [float(d) for d in diffs], "observado": obs,
            "completa": bool(len(pts) == len(CHAIN_MM)),
            "coincide_con_expectativa_r1_C2": bool(obs == "decrece al bajar R")}


def radio_critico(res, conv):
    """I3.3: primer tramo desde R=50 hacia abajo con P_out(R_{k-1}) < 1 % <= P_out(R_k) a L=100.
    Interpolacion log-log en R (criterio C7 de la ronda 1, citado)."""
    pts = []
    for R_mm in CHAIN_MM:
        s = res[100.0]["pasos"].get("R%g" % R_mm)
        if s is not None and s.get("evaluado"):
            pts.append((R_mm, s["P_out"]))
        else:
            break
    Rc = None
    metodo = None
    for k in range(1, len(pts)):
        R_prev, p_prev = pts[k - 1]
        R_cur, p_cur = pts[k]
        if p_prev < THR_POUT <= p_cur:
            if p_prev > 0.0:
                t = (math.log(THR_POUT) - math.log(p_prev)) / (math.log(p_cur) - math.log(p_prev))
                Rc = math.exp(math.log(R_prev) + t * (math.log(R_cur) - math.log(R_prev)))
                metodo = "interpolacion log-log"
            else:
                Rc = float(R_cur)
                metodo = "P_out previo = 0: se toma el radio de la cadena que supera el umbral"
            break
    if Rc is None:
        return {"R_c_mm": None, "metodo": "sin cruce P_out >= 1 % en la cadena evaluada a L = 100",
                "puntos_P_out_L100": [[float(a), float(b)] for a, b in pts],
                "convergencia_hasta_Rc": None, "pass": False}
    above = [R for R in CHAIN_MM if R >= Rc]
    conv_flags = []
    for R in above:
        c = conv.get(R)
        conv_flags.append({"R_mm": R, "pass": (None if c is None else c["pass"])})
    all_conv = all(f["pass"] is True for f in conv_flags)
    return {"R_c_mm": float(Rc), "metodo": metodo,
            "puntos_P_out_L100": [[float(a), float(b)] for a, b in pts],
            "convergencia_R_mayores_o_iguales": conv_flags,
            "pass": bool(all_conv)}


def main():
    t_start = time.time()
    log("Tarea I3 (curvas, ronda 3) - OMP_NUM_THREADS=%s h=%g NMODES=%d" % (os.environ.get("OMP_NUM_THREADS"), H, NMODES))
    log("solver2d desde: %s (solo cell_average y verificacion; no modificado)" % SOLVER_DIR)
    log("Analitica LP01: V=%.6f U=%.10f neff=%.12f" % (ANA["V"], ANA["U"], ANA_NEFF))

    # ------------- verificacion del operador (I3.0 a, b)
    gv = Grid(40.0, 0.5)
    cnv = cell_n2(gv, n_xy)
    sigma_def = K0 ** 2 * float(cnv.max())
    mine = sorted([m["neff"] for m in eig_sigma(gv, cnv, sigma_def)], reverse=True)
    ref = solver2d.solve(shapes=[], n_bg=N2, lam_um=LAM, L_um=40.0, h_um=0.5, n_modes=NMODES, s_sub=S_SUB, index_fn=n_xy)
    refn = sorted(ref["neff"], reverse=True)
    da = float(max(abs(a - b) for a, b in zip(mine, refn)))
    shift_m = eig_shift_neff(gv, cnv, ANA_NEFF)
    best_shift = min(shift_m, key=lambda md: abs(md["neff"] - ANA_NEFF))
    db = float(abs(best_shift["neff"] - refn[0]))
    log("[I3.0a] |wrapper - solver2d| max sobre 12 autovalores (L=40,h=0.5,recto) = %.3e" % da)
    log("[I3.0b] |nucleo por sigma en analitica - solver2d top| (L=40,h=0.5,recto) = %.3e" % db)

    # ------------- L = 40 primero (verificacion rapida frente a la ronda 2)
    res = {}
    for L in LS:
        res[L] = run_L(L)
        with open(os.path.join(HERE, "ckpt_curvas_r3_L%g.json" % L), "w", encoding="utf-8") as fh:
            json.dump(res[L], fh, indent=1, ensure_ascii=False)
        if L == 40.0:
            cr = {}
            for R_mm in (50.0, 20.0, 10.0):
                s = res[40.0]["pasos"].get("R%g" % R_mm)
                if s is not None and s.get("evaluado"):
                    cr[str(R_mm)] = float(abs(s["neff"] - N_R2_L40[R_mm]))
                else:
                    cr[str(R_mm)] = None
            log("[I3.0c] |n_eff(L=40,h=0.25) - n_r2| por radio = %s" % json.dumps(cr))

    # ------------- verificacion del recto (I3.0 d) y de eigenpares (I3.0 e)
    d_rec = {str(L): float(abs(res[L]["recto"]["neff"] - ANA_NEFF)) for L in LS}
    resid_all = [res[L]["recto"]["resid_rel"] for L in LS]
    norm_all = [res[L]["recto"]["norm_err"] for L in LS]
    for L in LS:
        for key, s in res[L]["pasos"].items():
            if s.get("evaluado"):
                resid_all.append(s["resid_rel"])
                norm_all.append(s["norm_err"])
    max_resid = float(max(resid_all))
    max_norm = float(max(norm_all))

    c_a = {"max_abs_diff": da, "umbral": 1e-10, "pass": bool(da <= 1e-10)}
    c_b = {"abs_diff": db, "umbral": 1e-10, "pass": bool(db <= 1e-10)}
    dc = [v for v in [res[40.0]["pasos"]["R%g" % R]["neff"] - N_R2_L40[R] if res[40.0]["pasos"]["R%g" % R].get("evaluado") else None for R in (50.0, 20.0, 10.0)]]
    if all(v is not None for v in dc):
        max_c = float(max(abs(v) for v in dc))
        c_c = {"max_abs_diff": max_c, "umbral": 1e-9, "pass": bool(max_c <= 1e-9)}
    else:
        c_c = {"max_abs_diff": None, "umbral": 1e-9, "pass": False, "motivo": "cadena incompleta a L=40"}
    c_d = {"abs_diff_por_L": d_rec, "umbral": 1e-6, "pass": bool(max(d_rec.values()) <= 1e-6)}
    c_e = {"max_resid_rel": max_resid, "umbral_resid": 1e-8, "max_norm_err": max_norm, "umbral_norm": 1e-10,
           "pass": bool(max_resid <= 1e-8 and max_norm <= 1e-10)}
    I30 = bool(c_a["pass"] and c_b["pass"] and c_c["pass"] and c_d["pass"] and c_e["pass"])

    # ------------- I3.1
    conv = {}
    for R_mm in (10.0, 20.0, 50.0):
        conv[R_mm] = conv_test(res, R_mm)
    # R intermedios (30 y 15) para I3.3, sin criterio propio en I3.1
    conv_extra = {R_mm: conv_test(res, R_mm) for R_mm in (30.0, 15.0)}
    vals31 = [conv[R]["pass"] for R in (10.0, 20.0, 50.0)]
    if any(v is False for v in vals31):
        I31 = False
    elif any(v is None for v in vals31):
        I31 = None
    else:
        I31 = True

    # ------------- I3.2 (informativo)
    tend = {str(L): tendencia(res, L) for L in LS}

    # ------------- I3.3
    conv_all = dict(conv)
    conv_all.update(conv_extra)
    rc = radio_critico(res, conv_all)
    I33 = bool(rc["pass"])

    rcA = A * N2 / (res[100.0]["recto"]["neff"] - N2) / 1000.0

    criterios = {
        "I3.0": {"descripcion": "verificacion del metodo (a: operador; b: seleccion por sigma; c: contraste r2 L=40; d: recto vs analitica; e: eigenpares)",
                 "a": c_a, "b": c_b, "c": c_c, "d": c_d, "e": c_e, "pass": I30},
        "I3.1": {"descripcion": "|n(L=100)-n(L=80)| < 1e-6 a h=0,25 con S_rec > 0,9 para R in {10,20,50} mm",
                 "por_radio": [conv[R] for R in (10.0, 20.0, 50.0)], "pass": I31},
        "I3.2": {"descripcion": "informativo: signo de n_eff frente a R (cadena 50->10); ronda 1 C2 esperaba decrece",
                 "por_L": tend, "pass": None},
        "I3.3": {"descripcion": "radio critico P_out = 1 % a L=100, establecido solo si I3.1 pasa para todos los R >= R_c",
                 "resultado": rc, "pass": I33},
    }
    evaluados = [I30, I31, I33]
    n_pass = int(sum(1 for c in (I30, I31, I33) if c is True))
    estado = "done" if all(v is not None for v in evaluados) and all(
        tend[str(L)]["observado"] != "no evaluado" for L in (80.0, 100.0)) else "partial"

    out = {
        "meta": {"lam_um": LAM, "a_um": A, "n1": N1, "n2": N2, "s_sub": S_SUB, "h_um": H,
                 "n_modes": NMODES, "chain_mm": CHAIN_MM, "L_um": LS, "S_min": S_MIN,
                 "S_def": "(sum psi psi_ref h^2)^2 (potencia, definicion ronda 2)",
                 "shift": "sigma = (k0 n_eff_prev)^2, which=LM, k=12",
                 "modelo": "n_eq = n_xy (1 + X/R), X exterior; solver2d (cell_average) scalar FD",
                 "nota": "MODELO NUMERICO. Perdida por radiacion NO calculada."},
        "analitica": ANA,
        "por_L": {str(L): res[L] for L in LS},
        "criterios": criterios,
        "R_cA_mm_ronda1_formula": float(rcA),
        "estado": estado,
        "n_pass": n_pass,
        "n_criterios_evaluados": int(sum(1 for c in (I30, I31, I33) if c is not None)),
        "n_criterios": 4,
        "tiempo_total_s": float(time.time() - t_start),
    }
    for name, val in (("I3.0", I30), ("I3.1", I31), ("I3.3", I33)):
        log("%s pass=%s" % (name, val))
    log("I3.2 informativo (pass=null): %s" % json.dumps({k: v["observado"] for k, v in tend.items()}))
    log("I3.3 radio critico: %s" % json.dumps(rc, default=float)[:600])
    log("estado=%s n_pass=%d tiempo=%.1f s" % (estado, n_pass, out["tiempo_total_s"]))
    out_path = os.path.join(HERE, "resultados_curvas_r3.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, default=float)
    log("Escrito: %s" % out_path)


if __name__ == "__main__":
    main()
