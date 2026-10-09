"""Corrected modal decomposition, exact bound-analogue case (CONTRATO-DESCOMPOSICION-V2.md).

Orthonormal guided basis {LP01, LP11 cos, LP11 sin} of the step guide
(a = 6 um, dn = 0.005, lambda = 1550 nm, V = 2.9202). Modes from the exact scalar
eigen-equations of experimentos/vectorial_claude/vector_step.py.
Writes descomposicion_v2.json and prints criteria C1-C3 and predictions P1-P3.
"""
import json
import math
import pathlib
import sys

import numpy as np
from scipy.special import j0, j1, k0, k1

HERE = pathlib.Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE.parent / "vectorial_claude"))
from vector_step import Guide, top_root, v_number  # noqa: E402

LAM, N1, DN, A = 1.55e-6, 1.444, 0.005, 6e-6
N2 = N1 - DN
V = v_number(LAM, N1, N2, A)
W0 = 6.0  # um, input waist
L, NG = 30.0, 601  # half-width (um) and grid size

g = Guide(N1, N2, V)
b01 = top_root(g.lp01)[0]
b11 = top_root(g.lp11)[0]
U01, W01 = V * math.sqrt(1 - b01), V * math.sqrt(b01)
U11, W11 = V * math.sqrt(1 - b11), V * math.sqrt(b11)
a_um = A * 1e6

x = np.linspace(-L, L, NG)
dx = x[1] - x[0]
X, Y = np.meshgrid(x, x, indexing="xy")
R = np.hypot(X, Y)
Rs = np.where(R < 1e-12, 1e-12, R)
COS, SIN = X / Rs, Y / Rs


def radial_lp01(r):
    xi = r / a_um
    return np.where(xi < 1, j0(U01 * xi) / j0(U01), k0(W01 * xi) / k0(W01))


def radial_lp11(r):
    xi = r / a_um
    return np.where(xi < 1, j1(U11 * xi) / j1(U11), k1(W11 * xi) / k1(W11))


basis = {
    "LP01": radial_lp01(R),
    "LP11c": radial_lp11(R) * COS,
    "LP11s": radial_lp11(R) * SIN,
}
for k in basis:  # numerical normalisation on the grid
    basis[k] = basis[k] / math.sqrt((basis[k] ** 2).sum() * dx * dx)
names = list(basis)
Phi = np.stack([basis[k] for k in names])
G = np.einsum("iab,jab->ij", Phi, Phi) * dx * dx  # Gram matrix
C2 = float(np.max(np.abs(G - np.eye(len(names)))))


def decompose(psi):
    c = np.einsum("iab,ab->i", Phi, psi) * dx * dx
    p_tot = float((psi ** 2).sum() * dx * dx)
    p_g = float((np.abs(c) ** 2).sum())
    resid = psi - np.einsum("i,iab->ab", c, Phi)
    p_r = float((resid ** 2).sum() * dx * dx)
    return c, p_tot, p_g, p_r


def gauss(x0):
    return np.exp(-(((X - x0) ** 2) + Y ** 2) / W0 ** 2)


psi0 = gauss(0.0)
psi2 = gauss(2.0)
psi4 = gauss(4.0)
psiA = gauss(-3.0)
psiB = gauss(3.0)

out = {"V": V, "b_LP01": b01, "b_LP11": b11, "grid_um": [-L, L, NG], "W0_um": W0,
       "Gram_max_offdiag_or_diag_error": C2, "C2_pass": C2 < 1e-4, "cases": {}}

rows = {}
for label, psi in (("x0=0", psi0), ("x0=2", psi2), ("x0=4", psi4)):
    c, p_tot, p_g, p_r = decompose(psi)
    closure = abs(p_tot - p_g - p_r) / p_tot
    rows[label] = {"c": dict(zip(names, map(float, c))), "P_tot": p_tot, "P_guided": p_g,
                   "P_rest": p_r, "C1_closure_rel": closure, "C1_pass": closure < 1e-4}
out["cases"] = rows

cA, ptA, pgA, _ = decompose(psiA)
cB, ptB, pgB, _ = decompose(psiB)
cAB, ptAB, pgAB, _ = decompose(psiA + psiB)
cross_numeric = pgAB - pgA - pgB
cross_formula = 2.0 * float(np.real(np.sum(np.conj(cA) * cB)))
overlap_tot = float(((psiA * psiB).sum()) * dx * dx)
interference = {"P_guided_AB": pgAB, "P_guided_A": pgA, "P_guided_B": pgB,
                "cross_term_numeric": cross_numeric, "cross_term_formula": cross_formula,
                "C3_abs_diff": abs(cross_numeric - cross_formula),
                "C3_pass": abs(cross_numeric - cross_formula) < 1e-6 * ptAB,
                "P_total_AB": ptAB, "P_total_A_plus_B_plus_2overlap": ptA + ptB + 2 * overlap_tot,
                "P3_cross_term_nonzero": abs(cross_formula) > 1e-6}
out["interference_AB_pm3um"] = interference

out["P1_symmetry_x0_0"] = {"c_LP11c": rows["x0=0"]["c"]["LP11c"], "c_LP11s": rows["x0=0"]["c"]["LP11s"],
                           "pass": abs(rows["x0=0"]["c"]["LP11c"]) < 1e-10 and abs(rows["x0=0"]["c"]["LP11s"]) < 1e-10}
out["P2_guided_fraction_centred"] = {"value": rows["x0=0"]["P_guided"] / rows["x0=0"]["P_tot"],
                                     "pass": rows["x0=0"]["P_guided"] / rows["x0=0"]["P_tot"] > 0.5}

out_path = HERE / "descomposicion_v2.json"
out_path.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
print(json.dumps({"C2": out["C2_pass"], "C1": {k: v["C1_pass"] for k, v in rows.items()},
                  "C3": interference["C3_pass"], "P1": out["P1_symmetry_x0_0"]["pass"],
                  "P2": out["P2_guided_fraction_centred"]["pass"], "P3": interference["P3_cross_term_nonzero"],
                  "P_guided_fraction": {k: round(v["P_guided"] / v["P_tot"], 6) for k, v in rows.items()},
                  "cross_term_formula": cross_formula}, ensure_ascii=False))
