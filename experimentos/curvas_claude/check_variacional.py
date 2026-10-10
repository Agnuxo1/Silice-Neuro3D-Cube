# -*- coding: utf-8 -*-
"""Comprobacion analitica (informativa): cota variacional del desplazamiento de n_eff.

Con psi0 (LP01 recto, misma malla) como funcion de prueba, el autovalor superior beta^2 del problema
con indice equivalente cumple beta^2(R) >= beta0^2 + k0^2 sum psi0^2 Delta(n^2_celda) h^2.
Asi, n_eff(R) - n_eff0 >= sqrt(n2^2 + B) - n_eff0 con B = sum psi0^2 Delta(n^2_celda) h^2 (con el
recto normalizado a n_eff0 en la misma malla). Se compara con el valor de solver2d.
Modelo numerico. Ejecutar: python -B check_variacional.py (OMP_NUM_THREADS=1)
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "solver2d_claude")))
import solver2d  # noqa: E402

LAM, A, N1, N2, S_SUB = 1.55, 6.0, 1.444, 1.439, 8
L, H = 40.0, 0.25


def n_xy(X, Y):
    return np.where(np.hypot(X, Y) < A, N1, N2)


def f_of(R_mm):
    def f(X, Y):
        if R_mm is None:
            return n_xy(X, Y) ** 2
        return (n_xy(X, Y) * (1.0 + X / (1000.0 * R_mm))) ** 2
    return f


def main():
    ref = solver2d.solve(shapes=[], n_bg=N2, lam_um=LAM, L_um=L, h_um=H, n_modes=1, s_sub=S_SUB, index_fn=n_xy)
    psi0 = ref["psi"][0]
    x = ref["x"]
    n0 = ref["neff"][0]
    cell0 = solver2d.cell_average(f_of(None), x, H, S_SUB)
    out = {"h_um": H, "L_um": L, "n_eff0": n0, "casos": {}}
    lines = []
    for R_mm in (50.0, 20.0, 10.0, 5.0):
        cellR = solver2d.cell_average(f_of(R_mm), x, H, S_SUB)
        dcell = cellR - cell0
        B = float(np.sum(psi0 * psi0 * dcell) * H * H)
        bound = math.sqrt(n0 ** 2 + B) - n0
        res = solver2d.solve(shapes=[], n_bg=N2, lam_um=LAM, L_um=L, h_um=H, n_modes=12, s_sub=S_SUB,
                             index_fn=(lambda R: (lambda X, Y: n_xy(X, Y) * (1.0 + X / (1000.0 * R))))(R_mm))
        top = res["neff"][0]
        out["casos"]["R%g" % R_mm] = {
            "B_um0_bound": B,
            "cota_inferior_D": bound,
            "D_top_del_solver_h0.25": top - n0,
            "cota_cumple_top": bool(top - n0 >= bound - 1e-12),
        }
        lines.append("R=%g mm  B=%.6e  cota_D=%+.6e  D_top_solver=%+.6e  cumple=%s"
                     % (R_mm, B, bound, top - n0, out["casos"]["R%g" % R_mm]["cota_cumple_top"]))
        print(lines[-1], flush=True)
    with open(os.path.join(HERE, "check_variacional.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, default=float)
    print("Escrito check_variacional.json", flush=True)


if __name__ == "__main__":
    main()
