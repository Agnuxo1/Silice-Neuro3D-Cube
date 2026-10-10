# -*- coding: utf-8 -*-
"""Tarea I4 (curvas, ronda 4): signo de Delta n_eff y radio critico por continuacion.

Modelo numerico. No es un dispositivo ni una medida.
    n_eq(X, Y) = n_xy(X, Y) * (1 + X/R),  X hacia el exterior, R en um.
Uso:
    OMP_NUM_THREADS=1 python -B curvas_r4.py 40     (cadena + perturbacion a L = 40)
    OMP_NUM_THREADS=1 python -B curvas_r4.py 80     (cadena a L = 80)
    OMP_NUM_THREADS=1 python -B curvas_r4.py 100    (cadena a L = 100)
    OMP_NUM_THREADS=1 python -B curvas_r4.py report (criterios y resultados_curvas_r4.json)
Umbrales y reglas: CONTRATO-curvas-r4.md (fijados antes de ejecutar).
curvas_r3.py NO se importa (abre y sobrescribe log_curvas_r3.txt): sus funciones se copian aqui.
solver2d no se modifica; se importa solver2d.cell_average.
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")

import json  # noqa: E402
import math  # noqa: E402
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
CHAIN_MM = [50.0, 20.0, 10.0, 7.0, 5.0, 4.0, 3.0, 2.5, 2.0]
S_MIN = 0.9
TOL_DN = 1e-6

LOGF = None


def log(msg=""):
    print(msg, flush=True)
    if LOGF is not None:
        LOGF.write(msg + "\n")
        LOGF.flush()


# ---------------------------------------------------------------- analitica (misma formula que curvas.py / curvas_r3.py)
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


ANA_NEFF = lp01_analytic()["neff"]


def n_xy(X, Y):
    r = np.hypot(X, Y)
    return np.where(r < A, N1, N2)


def index_fn_for(R_mm):
    R_um = 1000.0 * float(R_mm)

    def n_eq(X, Y):
        return n_xy(X, Y) * (1.0 + X / R_um)

    return n_eq


class Grid:
    def __init__(self, L, h):
        nh = int(round(L / h))
        self.N = 2 * nh + 1
        self.h = float(h)
        self.L = float(L)
        self.x = (np.arange(self.N) - (self.N - 1) / 2.0) * self.h
        self.X = np.tile(self.x[None, :], (self.N, 1))  # X[iy, ix] = x[ix]
        self.Y = np.tile(self.x[:, None], (1, self.N))  # Y[iy, ix] = y[iy]


def cell_n2(grid, index_fn):
    def f(X, Y):
        return np.asarray(index_fn(X, Y), dtype=float) ** 2

    return solver2d.cell_average(f, grid.x, grid.h, S_SUB)


def build_P(grid, cn2):
    """Operador P = Laplaciano 5 puntos + k0^2 n^2 en el interior (convencion de solver2d.solve)."""
    M = grid.N - 2
    h = grid.h
    T = sp.diags([np.ones(M - 1), -2.0 * np.ones(M), np.ones(M - 1)], [-1, 0, 1], format="csr") / h ** 2
    I = sp.identity(M, format="csr")
    n2_int = cn2[1:-1, 1:-1]
    P = (sp.kron(I, T) + sp.kron(T, I) + sp.diags(K0 ** 2 * n2_int.ravel())).tocsc()
    return P, M


def eig_sigma(grid, cn2, sigma):
    """NMODES autovalores mas cercanos a sigma (en beta^2, um^-2), shift-invert, which = LM."""
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
        norm_err = float(abs(float(np.sum(full * full)) * grid.h * grid.h - 1.0))
        imax = np.unravel_index(int(np.argmax(np.abs(full))), full.shape)
        if full[imax] < 0.0:
            full = -full
        modes.append({"beta2": beta2, "neff": math.sqrt(beta2) / K0, "psi": full,
                      "resid_rel": rel, "norm_err": norm_err})
    return modes


def overlap_S(grid, psi, psi_ref):
    return float((np.sum(psi * psi_ref) * grid.h * grid.h) ** 2)


# ---------------------------------------------------------------- perturbacion a segundo orden (L fijo, recto)
def pert_coeffs(grid, psi_rec, neff0):
    """P(lam) = P0 + lam D1 + lam^2 D2 exacto en el operador discreto (cavg lineal en el integrando).
    D1 = 2 k0^2 cavg(n^2 X), D2 = k0^2 cavg(n^2 X^2). mu(lam) = mu0 + lam <D1> + lam^2 (<D2> + S2),
    S2 = <g_perp | (mu0 - P0)^-1_perp | g_perp>, g = D1 u0. Sistema bordeado para el resolvente."""
    c1 = solver2d.cell_average(lambda X, Y: n_xy(X, Y) ** 2 * X, grid.x, grid.h, S_SUB)
    c2a = solver2d.cell_average(lambda X, Y: n_xy(X, Y) ** 2 * X ** 2, grid.x, grid.h, S_SUB)
    P0, M = build_P(grid, cell_n2(grid, n_xy))
    u = psi_rec[1:-1, 1:-1].ravel().astype(float)
    u = u / np.linalg.norm(u)
    mu0 = (K0 * neff0) ** 2
    D1d = 2.0 * K0 ** 2 * c1[1:-1, 1:-1].ravel()
    D2d = K0 ** 2 * c2a[1:-1, 1:-1].ravel()
    g = D1d * u
    first = float(u @ g)
    D2term = float(u @ (D2d * u))
    gp = g - u * first
    I = sp.identity(M * M, format="csc")
    Amat = (mu0 * I - P0).tocsc()
    B = sp.bmat([[Amat, sp.csc_matrix(u.reshape(-1, 1))],
                 [sp.csc_matrix(u.reshape(1, -1)), None]]).tocsc()
    rhs = np.concatenate([gp, [0.0]])
    sol = sla.spsolve(B, rhs)
    chi = sol[:-1]
    S2 = float(gp @ chi)
    res_bord = float(np.linalg.norm(B @ sol - rhs) / max(np.linalg.norm(rhs), 1e-300))
    c2 = (D2term + S2) / (2.0 * K0 ** 2 * neff0)
    return {"mu0": float(mu0), "first_order_u_D1_u": first, "D2_term": D2term, "S2": S2,
            "c2_um2": float(c2), "residuo_bordeado_rel": res_bord}


# ---------------------------------------------------------------- una longitud L
def run_chain(L, with_pert):
    t0 = time.time()
    grid = Grid(L, H)
    cn2_rec = cell_n2(grid, n_xy)
    modes0 = eig_sigma(grid, cn2_rec, (K0 * ANA_NEFF) ** 2)
    best0 = min(modes0, key=lambda md: abs(md["neff"] - ANA_NEFF))
    psi_rec = best0["psi"]
    neff_rec = best0["neff"]
    out = {"L_um": float(L), "h_um": H, "N": int(grid.N),
           "recto": {"neff": neff_rec, "dist_analitica": neff_rec - ANA_NEFF,
                     "resid_rel": best0["resid_rel"], "norm_err": best0["norm_err"]},
           "pasos": {}}
    log("[L=%g] N=%d recto neff=%.12f err_analitica=%+.3e resid=%.2e t=%.1fs"
        % (L, grid.N, neff_rec, neff_rec - ANA_NEFF, best0["resid_rel"], time.time() - t0))
    if with_pert:
        out["pert"] = pert_coeffs(grid, psi_rec, neff_rec)
        log("[L=%g] perturbacion: %s" % (L, json.dumps(out["pert"])))
        log("[L=%g] prediccion c2/R^2 en R=50,20,10 mm: %s"
            % (L, json.dumps({str(R): out["pert"]["c2_um2"] / (1000.0 * R) ** 2 for R in (50.0, 20.0, 10.0)})))
    prev_neff, prev_psi = neff_rec, psi_rec
    ok_chain = True
    ckpt = os.path.join(HERE, "ckpt_curvas_r4_L%g.json" % L)
    for R in CHAIN_MM:
        key = "R%g" % R
        if not ok_chain:
            out["pasos"][key] = {"evaluado": False, "motivo": "cadena detenida en un radio mayor"}
            continue
        ts = time.time()
        cn2 = cell_n2(grid, index_fn_for(R))
        modes = eig_sigma(grid, cn2, (K0 * prev_neff) ** 2)
        Sp = [overlap_S(grid, md["psi"], prev_psi) for md in modes]
        k = int(np.argmax(Sp))
        md = modes[k]
        Srec = overlap_S(grid, md["psi"], psi_rec)
        step = {"R_mm": R, "neff": md["neff"], "dn": md["neff"] - neff_rec,
                "S_prev": Sp[k], "S_rec": Srec, "resid_rel": md["resid_rel"], "norm_err": md["norm_err"],
                "x_t_um": 1000.0 * R * (md["neff"] / N2 - 1.0), "neff_prev": prev_neff,
                "S_prev_12_max_otro": float(sorted(Sp)[-2]) if len(Sp) > 1 else None,
                "N": int(grid.N)}
        if Sp[k] > S_MIN:
            step["evaluado"] = True
            prev_neff, prev_psi = md["neff"], md["psi"]
        else:
            step["evaluado"] = False
            step["motivo"] = "S_prev <= 0,9: modo perdido por continuacion"
            ok_chain = False
        step["t_s"] = time.time() - ts
        out["pasos"][key] = step
        log("[L=%g] R=%g mm neff=%.12f dn=%+.4e S_prev=%.6f S_rec=%.6f x_t=%.2f resid=%.1e t=%.1fs %s"
            % (L, R, step["neff"], step["dn"], step["S_prev"], step["S_rec"], step["x_t_um"],
               step["resid_rel"], step["t_s"], "" if step["evaluado"] else "FALLO: " + step["motivo"]))
        with open(ckpt, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1, ensure_ascii=False)
    out["t_s"] = time.time() - t0
    with open(ckpt, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    log("[L=%g] fin: %.1f s" % (L, out["t_s"]))
    return out


# ---------------------------------------------------------------- informe y criterios
def load(L):
    p = os.path.join(HERE, "ckpt_curvas_r4_L%g.json" % L)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def report():
    ck = {L: load(L) for L in (40.0, 80.0, 100.0)}
    with open(os.path.join(HERE, "ckpt_curvas_r3_L40.json"), encoding="utf-8") as fh:
        r3_40 = json.load(fh)
    crit = {}

    # I4.0 (a): contraste con r3 a L = 40
    if ck[40.0] is not None:
        diffs = {}
        for R in (50.0, 20.0, 10.0):
            s = ck[40.0]["pasos"].get("R%g" % R)
            if s and s.get("evaluado"):
                diffs[str(R)] = abs(s["neff"] - r3_40["pasos"]["R%g" % R]["neff"])
            else:
                diffs[str(R)] = None
        diffs["recto"] = abs(ck[40.0]["recto"]["neff"] - r3_40["recto"]["neff"])
        vals = [v for v in diffs.values() if v is not None]
        a_ok = bool(len(vals) == 4 and max(vals) <= 1e-10)
        a_res = {"abs_diff_por_radio": diffs, "umbral": 1e-10, "pass": a_ok}
    else:
        a_res = {"pass": None, "motivo": "sin ckpt L=40"}

    # I4.0 (b): coeficiente de perturbacion frente a la cadena numerica a L = 40
    b_res = {"pass": None}
    if ck[40.0] is not None and "pert" in ck[40.0]:
        c2 = ck[40.0]["pert"]["c2_um2"]
        rel = {}
        for R in (50.0, 20.0, 10.0):
            s = ck[40.0]["pasos"].get("R%g" % R)
            if s and s.get("evaluado"):
                pred = c2 / (1000.0 * R) ** 2
                rel[str(R)] = {"dn_num": s["dn"], "dn_pred": pred, "cociente_num_pred": s["dn"] / pred,
                               "dif_rel": abs(s["dn"] / pred - 1.0)}
        dif10 = rel.get("10.0", {}).get("dif_rel")
        b_res = {"c2_um2": c2, "por_radio": rel, "umbral_dif_rel_R10": 0.02,
                 "pass": bool(dif10 is not None and dif10 <= 0.02)}

    # I4.0 (c): eigenpares de todos los modos seleccionados
    resid, normerr = [], []
    for L in (40.0, 80.0, 100.0):
        if ck[L] is None:
            continue
        resid.append(ck[L]["recto"]["resid_rel"])
        normerr.append(ck[L]["recto"]["norm_err"])
        for s in ck[L]["pasos"].values():
            if s.get("evaluado"):
                resid.append(s["resid_rel"])
                normerr.append(s["norm_err"])
    c_res = {"max_resid_rel": max(resid) if resid else None, "umbral_resid": 1e-8,
             "max_norm_err": max(normerr) if normerr else None, "umbral_norm": 1e-10,
             "pass": bool(resid and max(resid) <= 1e-8 and max(normerr) <= 1e-10)}
    I40 = bool(a_res.get("pass") is True and b_res.get("pass") is True and c_res["pass"])
    crit["I4.0"] = {"descripcion": "verificacion: (a) contraste con r3 L=40 <= 1e-10; (b) c2 perturbativo vs numerico R=10 mm L=40 <= 2 %; (c) eigenpares",
                    "a": a_res, "b": b_res, "c": c_res, "pass": I40}

    # I4.1 (i): signo; (ii) simetria y c2 > 0; (iii) pendiente log-log L = 100 entre 50 y 10 mm
    signo = {}
    for L in (40.0, 80.0, 100.0):
        if ck[L] is None:
            signo[str(L)] = None
            continue
        vals = [s["dn"] for s in ck[L]["pasos"].values() if s.get("evaluado")]
        signo[str(L)] = {"n_puntos": len(vals), "todos_positivos": bool(vals and all(v > 0 for v in vals)),
                         "dn_por_R": {k: s["dn"] for k, s in ck[L]["pasos"].items() if s.get("evaluado")}}
    if any(v is None or v["n_puntos"] < 1 for v in signo.values()):
        i_ok = None
    else:
        i_ok = bool(all(v["todos_positivos"] for v in signo.values()))
    ii = {"pass": None}
    if ck[40.0] is not None and "pert" in ck[40.0]:
        p = ck[40.0]["pert"]
        ii = {"first_order_u_D1_u": p["first_order_u_D1_u"], "D2_term": p["D2_term"], "S2": p["S2"],
              "c2_um2": p["c2_um2"], "umbral_first_order": 1e-10,
              "pass": bool(abs(p["first_order_u_D1_u"]) <= 1e-10 and p["c2_um2"] > 0 and p["D2_term"] > 0 and p["S2"] >= 0)}
    slope = None
    iii = {"pass": None}
    if ck[100.0] is not None:
        s50 = ck[100.0]["pasos"].get("R50")
        s10 = ck[100.0]["pasos"].get("R10")
        if s50 and s10 and s50.get("evaluado") and s10.get("evaluado") and s50["dn"] > 0 and s10["dn"] > 0:
            slope = math.log(s10["dn"] / s50["dn"]) / math.log(10.0 / 50.0)
            iii = {"pendiente_log_log_L100_50_10": slope, "intervalo": [-2.05, -1.95],
                   "pass": bool(-2.05 <= slope <= -1.95)}
    parts41 = [i_ok, ii.get("pass"), iii.get("pass")]
    if any(p is False for p in parts41):
        I41 = False
    elif any(p is None for p in parts41):
        I41 = None
    else:
        I41 = True
    crit["I4.1"] = {"descripcion": "signo: Delta n > 0 en toda la cadena; (ii) primer orden nulo, c2 > 0; (iii) pendiente log-log en [-2,05; -1,95] a L = 100",
                    "i_signo_por_L": signo, "i_pass": i_ok, "ii": ii, "iii": iii, "pass": I41}

    # I4.2: radio critico por solape (L = 100) y convergencia en L (80-100) para R >= R_a
    I42 = None
    rc = {"motivo": "sin datos L=100"}
    if ck[100.0] is not None:
        pts = [(R, ck[100.0]["pasos"].get("R%g" % R)) for R in CHAIN_MM]
        k_b = None
        for idx, (R, s) in enumerate(pts):
            if s is None or not (s.get("evaluado") and s["S_rec"] > S_MIN):
                k_b = idx
                break
        if k_b is None or k_b == 0 or pts[k_b][1] is None:
            if k_b is None:
                rc = {"motivo": "no se encuentra cruce de S_rec = 0,9 en la cadena evaluada", "chain_completa": True}
                I42 = False
            elif k_b == 0:
                rc = {"motivo": "S_rec(R = 50 mm) ya <= 0,9 o paso no evaluado"}
                I42 = None
            else:
                rc = {"motivo": "cadena L=100 incompleta (no alcanzada el radio siguiente)", "chain_completa": False}
                I42 = None
        else:
            R_a, s_a = pts[k_b - 1][0], pts[k_b - 1][1]
            R_b, s_b = pts[k_b][0], pts[k_b][1]
            if s_b is not None and s_b.get("evaluado") and s_b["S_rec"] <= S_MIN:
                t = (math.log(S_MIN) - math.log(s_a["S_rec"])) / (math.log(s_b["S_rec"]) - math.log(s_a["S_rec"]))
                Rc = math.exp(math.log(R_a) + t * (math.log(R_b) - math.log(R_a)))
                tipo = "interpolado (log S_rec frente a log R)"
            else:
                Rc = None
                tipo = "cota: paso fallido en R_b, sin interpolar; R_c en [R_b; R_a]"
            conv = []
            for idx in range(0, k_b):
                R = CHAIN_MM[idx]
                c80 = ck[80.0]["pasos"].get("R%g" % R) if ck[80.0] is not None else None
                c100 = ck[100.0]["pasos"].get("R%g" % R)
                if c80 is None or not c80.get("evaluado") or not c100.get("evaluado"):
                    conv.append({"R_mm": R, "pass": None})
                    continue
                d = abs(c100["neff"] - c80["neff"])
                ok = bool(d < TOL_DN and c80["S_rec"] > S_MIN and c100["S_rec"] > S_MIN)
                conv.append({"R_mm": R, "abs_diff_L100_L80": d, "S_rec_L80": c80["S_rec"],
                             "S_rec_L100": c100["S_rec"], "pass": ok})
            # puntos con R >= R_a (todos los de la cadena por encima de R_b)
            ok_list = [c["pass"] for c in conv]
            if any(v is None for v in ok_list):
                I42 = None
            else:
                I42 = bool(all(ok_list))
            rc = {"R_a_mm": R_a, "R_b_mm": R_b, "R_c_mm": Rc, "cota_mm": ([R_b, R_a] if Rc is None else None), "tipo": tipo,
                  "S_rec_R_a_L100": s_a["S_rec"], "S_rec_R_b_L100": (s_b["S_rec"] if s_b else None),
                  "motivo_paso_fallido": (s_b.get("motivo") if s_b and not s_b.get("evaluado") else None),
                  "convergencia_R_mayores_o_iguales_R_a": conv}
    crit["I4.2"] = {"descripcion": "radio critico R_c(S) con S_rec = 0,9 (L = 100); convergencia |dn(100-80)| < 1e-6 y S_rec > 0,9 para R >= R_a",
                    "resultado": rc, "pass": I42}

    crit["I4.3"] = {"descripcion": "perdida por radiacion: NO calculada en esta ronda", "pass": None}

    evaluados = [I40, I41, I42]
    llega_2mm = {str(L): bool(ck[L] is not None and ck[L]["pasos"].get("R2", {}).get("evaluado") is True)
                 for L in (80.0, 100.0)}
    estado = "done" if (all(v is not None for v in evaluados) and all(llega_2mm.values())) else "partial"
    n_pass = int(sum(1 for v in evaluados if v is True))
    rcA = A * N2 / (ANA_NEFF - N2) / 1000.0
    Rx = A / (ck[100.0]["recto"]["neff"] - N2) / 1000.0 if False else None
    out = {
        "meta": {"lam_um": LAM, "a_um": A, "n1": N1, "n2": N2, "s_sub": S_SUB, "h_um": H, "n_modes": NMODES,
                 "chain_mm": CHAIN_MM, "L_um_ejecutadas": [L for L in (40.0, 80.0, 100.0) if ck[L] is not None],
                 "S_min": S_MIN, "S_def": "(sum psi psi_ref h^2)^2", "TOL_DN": TOL_DN,
                 "modelo": "n_eq = n_xy (1 + X/R), X exterior; solver2d.cell_average; P = nabla^2 + k0^2 n^2",
                 "nota": "MODELO NUMERICO. Perdida por radiacion NO calculada."},
        "analitica_neff": ANA_NEFF,
        "por_L": {str(L): ck[L] for L in (40.0, 80.0, 100.0) if ck[L] is not None},
        "criterios": crit,
        "informativo": {"R_cA_mm_ronda1": rcA,
                        "pendiente_log_log_L100": slope},
        "estado": estado,
        "n_pass": n_pass,
        "n_criterios_evaluados": int(sum(1 for v in evaluados if v is not None)),
        "n_criterios": 4,
    }
    out_path = os.path.join(HERE, "resultados_curvas_r4.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, default=float)
    log("I4.0 pass=%s | I4.1 pass=%s | I4.2 pass=%s | I4.3 null | estado=%s" % (I40, I41, I42, estado))
    log("Escrito: %s" % out_path)


def main():
    global LOGF
    arg = sys.argv[1] if len(sys.argv) > 1 else "report"
    if arg == "report":
        LOGF = open(os.path.join(HERE, "log_curvas_r4_report.txt"), "w", encoding="utf-8")
        report()
        return
    L = float(arg)
    LOGF = open(os.path.join(HERE, "log_curvas_r4_L%g.txt" % L), "w", encoding="utf-8")
    log("Tarea I4 (curvas, ronda 4) L=%g h=%g NMODES=%d OMP=%s" % (L, H, NMODES, os.environ.get("OMP_NUM_THREADS")))
    log("Analitica LP01 neff=%.12f" % ANA_NEFF)
    run_chain(L, with_pert=(L == 40.0))


if __name__ == "__main__":
    main()
