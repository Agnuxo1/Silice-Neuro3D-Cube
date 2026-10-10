# -*- coding: utf-8 -*-
"""Suplementario (ENMIENDA A1, informativo): busqueda del modo nucleo para R = 5 mm.

Motivo: en curvas.py con n_modes = 12 el modo seleccionado para R = 5 mm tiene solapamiento
S = 0 con el LP01 recto y P_core = 0. Es decir, el nucleo no aparece entre los 12 valores mas
altos del espectro (los estados de caja del borde exterior quedan por encima). Esta ejecucion
NO sustituye a los criterios pre-registrados; aumenta n_modes solo para localizar el modo
nucleo y reportarlo como dato informativo.
Modelo numerico. No es un dispositivo ni una medida.
Ejecutar: python -B supp_r5.py  (OMP_NUM_THREADS=1)
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "solver2d_claude")))
import solver2d  # noqa: E402  uso directo del modulo; no se copia codigo

LAM, A, N1, N2 = 1.55, 6.0, 1.444, 1.439
S_SUB = 8
R_MM = 5.0
NMODES_LIST = [40, 80]
HS = [0.5, 0.25]
L = 40.0

LOG = open(os.path.join(HERE, "supp_r5_log.txt"), "w", encoding="utf-8")


def log(msg=""):
    print(msg, flush=True)
    LOG.write(msg + "\n")
    LOG.flush()


def n_xy(X, Y):
    return np.where(np.hypot(X, Y) < A, N1, N2)


def n_eq(X, Y):
    return n_xy(X, Y) * (1.0 + X / (1000.0 * R_MM))


def grid_xy(res):
    x = np.asarray(res["x"], dtype=float)
    N = res["N"]
    return np.tile(x[None, :], (N, 1)), np.tile(x[:, None], (1, N))


def main():
    out = {"amendment": "A1 informativo: n_modes ampliado solo para localizar el modo nucleo a R=5 mm",
           "R_mm": R_MM, "L_um": L, "casos": []}
    for h in HS:
        ref = solver2d.solve(shapes=[], n_bg=N2, lam_um=LAM, L_um=L, h_um=h,
                             n_modes=1, s_sub=S_SUB, index_fn=n_xy)
        ref_psi = ref["psi"][0]
        neff_rec = ref["neff"][0]
        log("[recto] h=%g neff=%.12f" % (h, neff_rec))
        for nm in NMODES_LIST:
            t0 = time.time()
            res = solver2d.solve(shapes=[], n_bg=N2, lam_um=LAM, L_um=L, h_um=h,
                                 n_modes=nm, s_sub=S_SUB, index_fn=n_eq)
            dt = time.time() - t0
            X, Y = grid_xy(res)
            best = None
            rows = []
            for m, psi in enumerate(res["psi"]):
                P = psi * psi * h * h
                S = float((np.sum(psi * ref_psi) * h * h) ** 2)
                rows.append(S)
                if best is None or S > best[1]:
                    best = (m, S, P)
            m, S, P = best
            neff = res["neff"][m]
            r = np.hypot(X, Y)
            x_t = 1000.0 * R_MM * (neff / N2 - 1.0)
            caso = {
                "h_um": h, "n_modes": nm, "mode_index": int(m), "neff": neff,
                "D_vs_recto": neff - neff_rec, "S": S,
                "P_core": float(P[r < A].sum()), "P_out": float(P[X > x_t].sum()),
                "centroid_um": float((X * P).sum()), "x_t_um": x_t,
                "top_S_values": rows, "t_s": dt,
                "spectrum_top5": [float(v) for v in res["neff"][:5]],
            }
            out["casos"].append(caso)
            log("[R=5 mm amp.] h=%g n_modes=%d modo=%d neff=%.12f D=%+.6e S=%.4f P_core=%.4f P_out=%.3e <x>=%+.4f um t=%.1fs"
                % (h, nm, m, neff, neff - neff_rec, S, caso["P_core"], caso["P_out"], caso["centroid_um"], dt))
            log("  S de los modos (orden de n_eff): " + ", ".join("%.3f" % v for v in rows[:20]))
    with open(os.path.join(HERE, "supp_r5.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, default=float)
    log("Escrito supp_r5.json")


if __name__ == "__main__":
    main()
