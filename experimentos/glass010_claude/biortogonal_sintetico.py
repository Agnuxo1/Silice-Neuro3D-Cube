"""Biorthogonal basis test on synthetic quasi-bound modes (CONTRATO-BIORT-r4.md).

Two known, non-orthogonal, complex modes phi_1, phi_2 on a 1D grid, unit norm.
Method D (proposed): dual basis chi = Phi G^-1, c = G^-1 d, eta_D = ||Phi c||^2 / ||psi||^2.
Method A (GLASS-010 style, per mode): c_m = d_m / G_mm, eta_A = sum_m |c_m|^2 G_mm / ||psi||^2.

Block 1 (pre-registered, verdict): k2 = 0.7 1/um, deltas in CONTRATO-BIORT-r4.md.
Block 2 (post hoc, declared, does not change the verdict): k2 = 0, deltas down to 0.02 um,
added after block 1 because block 1 reaches only |G12| ~ 0.61 (cond ~ 4). Same thresholds.

Writes resultados_biort.json. Pass flags are computed here, not set by hand.
CPU only, numpy only. Run with: python -B biortogonal_sintetico.py
"""
import json
import pathlib
import sys

import numpy as np

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent

X = np.linspace(-40.0, 40.0, 4001)
DX = float(X[1] - X[0])
S = 2.0
A1 = np.array([0.8 + 0.3j, -0.5 + 0.9j])
A2 = np.array([1.0 + 0.0j, -1.0 + 0.0j])
A4 = np.array([1.0 + 0.0j, 1.0 + 0.0j])
A_CASES = {"T1": A1, "T2": A2, "T4": A4}

# Thresholds fixed in CONTRATO-BIORT-r4.md (not tuned after seeing results)
TH_B1 = 1e-12
TH_B2 = 1e-12
TH_B3 = 1e-10
TH_V1 = 1e-12
TH_V2 = 1e-10
TH_V3 = 1e-12
TH_V4 = 1e-12
TH_D1 = 1e-12

BLOCK1 = {"k2": 0.7, "deltas": [10.0, 4.0, 2.0, 1.0, 0.5, 0.1]}
BLOCK2 = {"k2": 0.0, "deltas": [0.5, 0.1, 0.05, 0.02]}


def ip(u, v):
    return complex(np.sum(np.conj(u) * v) * DX)


def nrm(u):
    return float(np.sqrt(abs(ip(u, u))))


def mode(x0, k):
    return np.exp(-((X - x0) ** 2) / (2.0 * S ** 2)) * np.exp(1j * k * X)


def build_modes(delta, k2):
    cols = [mode(0.0, 0.0), mode(delta, k2)]
    cols = [c / nrm(c) for c in cols]
    return np.stack(cols, axis=1)


def gram_of(phi):
    return (phi.conj().T @ phi) * DX


def method_d(phi, gram, psi):
    d = (phi.conj().T @ psi) * DX
    c = np.linalg.solve(gram, d)
    rec = phi @ c
    return c, rec


def method_a(phi, gram, psi):
    d = (phi.conj().T @ psi) * DX
    gdiag = np.real(np.diag(gram))
    c_a = d / gdiag
    p_tot = nrm(psi) ** 2
    per = np.abs(c_a) ** 2 * gdiag / p_tot
    return c_a, per, float(np.sum(per))


RNG = np.random.default_rng(20261010)
R_RAW = RNG.standard_normal(X.size) + 1j * RNG.standard_normal(X.size)
R_UNIT = R_RAW / nrm(R_RAW)


def run_block(k2, deltas):
    rows = []
    v1_all, v2_all, b1_all, b3_all, b2_all, d1_all = [], [], [], [], [], []
    p1_sel = []
    b3_cond_ratio = []

    for delta in deltas:
        phi = build_modes(delta, k2)
        gram = gram_of(phi)
        g12 = abs(gram[0, 1])
        cond = float(np.linalg.cond(gram))
        chi = phi @ np.linalg.inv(gram)
        m_bi = (chi.conj().T @ phi) * DX
        v1 = float(np.max(np.abs(m_bi - np.eye(2))))
        v1_all.append(v1)

        base = phi @ A1
        psis = {
            "T1": base,
            "T2": phi @ A2,
            "T4": phi @ A4,
            "T3": base + 0.3 * nrm(base) * R_UNIT,
        }
        for name, psi in psis.items():
            c_d, rec = method_d(phi, gram, psi)
            c_ls = np.linalg.lstsq(phi, psi, rcond=None)[0]
            v2 = float(np.linalg.norm(c_d - c_ls) / np.linalg.norm(c_ls))
            v2_all.append(v2)

            c_a, per_a, eta_a = method_a(phi, gram, psi)
            p_tot = nrm(psi) ** 2
            p_g = nrm(rec) ** 2
            p_r = nrm(psi - rec) ** 2
            eta_d = p_g / p_tot
            b2_all.append(eta_d)
            d1 = abs(p_tot - p_g - p_r) / p_tot
            d1_all.append(d1)

            row = {
                "k2_per_um": k2,
                "delta_um": delta,
                "field": name,
                "abs_G12": float(g12),
                "cond_G": cond,
                "eta_D": float(eta_d),
                "eta_A_sum": eta_a,
                "eta_A_per_mode": [float(v) for v in per_a],
                "V2_relerr_vs_lstsq": v2,
                "D1_closure_rel": float(d1),
            }
            if name in A_CASES:
                a = A_CASES[name]
                b1 = nrm(psi - rec) / nrm(psi)
                b3 = float(np.linalg.norm(c_d - a) / np.linalg.norm(a))
                b1_all.append(b1)
                b3_all.append(b3)
                b3_cond_ratio.append(b3 / (cond * np.finfo(float).eps))
                row["B1_recon_rel"] = float(b1)
                row["B3_coef_relerr"] = b3
            if name == "T4" and g12 >= 0.6:
                p1_sel.append((delta, eta_a))
            rows.append(row)

    p1_pass = len(p1_sel) > 0 and all(eta > 1.0 for _, eta in p1_sel)
    crit = {
        "B1": {"description": "reconstruccion con base dual, T1/T2/T4 en el span, max rel err",
               "threshold": TH_B1, "value": max(b1_all), "pass": bool(max(b1_all) < TH_B1)},
        "B2": {"description": "eta_D <= 1 en todos los casos (T1..T4, todos los delta)",
               "threshold": TH_B2, "value": max(b2_all), "pass": bool(max(b2_all) <= 1.0 + TH_B2)},
        "B3": {"description": "recuperacion de coeficientes T1/T2/T4, max rel err",
               "threshold": TH_B3, "value": max(b3_all), "pass": bool(max(b3_all) < TH_B3)},
        "V1": {"description": "biortogonalidad <chi_i, phi_j> = delta_ij, max abs err",
               "threshold": TH_V1, "value": max(v1_all), "pass": bool(max(v1_all) < TH_V1)},
        "V2": {"description": "cruce c_D frente a numpy lstsq, max rel err",
               "threshold": TH_V2, "value": max(v2_all), "pass": bool(max(v2_all) < TH_V2)},
        "D1": {"description": "cierre P_tot = P_g + P_r en todos los casos, max rel err",
               "threshold": TH_D1, "value": max(d1_all), "pass": bool(max(d1_all) < TH_D1)},
        "P1": {"description": "eta_A > 1 para T4 con |G12| >= 0.6 (prediccion)",
               "threshold": None, "value": [{"delta_um": d, "eta_A_sum": e} for d, e in p1_sel],
               "pass": bool(p1_pass)},
    }
    p2 = {"min": float(min(b3_cond_ratio)), "max": float(max(b3_cond_ratio))}
    return rows, crit, p2


# Analytic check in R^2 (V3, V4), plain real dot products
P1V = np.array([1.0, 0.0])
P2V = np.array([0.6, 0.8])
PHI_R = np.stack([P1V, P2V], axis=1)
G_R = PHI_R.T @ PHI_R
PSI_DIFF = P1V - P2V
C_R = np.linalg.solve(G_R, PHI_R.T @ PSI_DIFF)
V3 = float(np.linalg.norm(C_R - np.array([1.0, -1.0])))
PSI_SUM = P1V + P2V
D_R = PHI_R.T @ PSI_SUM
ETA_A_R = float(np.sum(np.abs(D_R) ** 2 / np.diag(G_R)) / (PSI_SUM @ PSI_SUM))
ETA_A_R_EXPECTED = 1.0 + 0.6
V4 = abs(ETA_A_R - ETA_A_R_EXPECTED)

rows1, crit1, p2_1 = run_block(BLOCK1["k2"], BLOCK1["deltas"])
crit1["V3"] = {"description": "caso analitico R2: recupera a=(1,-1)",
               "threshold": TH_V3, "value": V3, "pass": bool(V3 < TH_V3)}
crit1["V4"] = {"description": "caso analitico R2: eta_A(phi1+phi2) = 1 + G12 = 1.6",
               "threshold": TH_V4, "value": V4, "pass": bool(V4 < TH_V4)}

rows2, crit2, p2_2 = run_block(BLOCK2["k2"], BLOCK2["deltas"])

pre_registered = [k for k in ("B1", "B2", "B3", "V1", "V2", "V3", "V4", "D1") if crit1[k]["pass"]]
all_evaluated = all(k in crit1 for k in ("B1", "B2", "B3", "V1", "V2", "V3", "V4", "D1", "P1"))

out = {
    "contrato": "CONTRATO-BIORT-r4.md",
    "fecha": "2026-10-10",
    "grid": {"x_um": [-40.0, 40.0], "N": int(X.size), "dx_um": DX, "s_um": S},
    "bloque_1_preregistrado": {"k2_per_um": BLOCK1["k2"], "deltas_um": BLOCK1["deltas"],
                               "criteria": crit1, "P2_B3_over_cond_eps": p2_1, "cases": rows1},
    "analytic_R2": {"coef_recovered": [float(v) for v in C_R], "eta_A_phi1_plus_phi2": ETA_A_R,
                    "eta_A_expected": ETA_A_R_EXPECTED},
    "bloque_2_post_hoc": {
        "declaracion": ("Barrido adicional decidido despues de ver el bloque 1 (|G12| maximo 0,61). "
                        "Mismos umbrales. No altera el veredicto del bloque 1."),
        "k2_per_um": BLOCK2["k2"], "deltas_um": BLOCK2["deltas"],
        "criteria": crit2, "P2_B3_over_cond_eps": p2_2, "cases": rows2},
}

out_path = HERE / "resultados_biort.json"
out_path.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

def short(c):
    return {k: {"value": v["value"], "pass": v["pass"]} for k, v in c.items() if k != "P1"}

print("BLOQUE 1 (preregistrado)")
print(json.dumps(short(crit1), ensure_ascii=False, indent=1))
print("P1:", crit1["P1"]["pass"], crit1["P1"]["value"])
print("G12 T1:", {r["delta_um"]: round(r["abs_G12"], 6) for r in rows1 if r["field"] == "T1"})
print("cond T1:", {r["delta_um"]: float(f"{r['cond_G']:.3e}") for r in rows1 if r["field"] == "T1"})
print("P2 bloque1:", p2_1)
print("BLOQUE 2 (post hoc)")
print(json.dumps(short(crit2), ensure_ascii=False, indent=1))
print("P1:", crit2["P1"]["pass"], crit2["P1"]["value"])
print("G12 T1:", {r["delta_um"]: float(f"{r['abs_G12']:.6f}") for r in rows2 if r["field"] == "T1"})
print("cond T1:", {r["delta_um"]: float(f"{r['cond_G']:.3e}") for r in rows2 if r["field"] == "T1"})
print("P2 bloque2:", p2_2)
print("analytic V3, V4:", V3, V4, "eta_A R2:", ETA_A_R)
