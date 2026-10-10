"""G3 de la ronda 2: longitud de transferencia de un acoplador de dos nucleos con BPM (bpm_r2.py).

Uso: python -B run_g3_r2.py <d_um>   (d en {14, 16})
E0 = modo de un nucleo en x = -d/2 (solver2d, n_bg = n2, ventana L = 40 um, h = 0,2 um).
psi_R = modo de un nucleo en x = +d/2 (solver2d). P2(z) = |<psi_R|A(z)>|^2 / (<psi_R|psi_R> <A0|A0>).
CAP base de la ronda 2 (W = 40, s0 = 28, w = 12, R0 = 0.5 um^-1), dz = 1 um, hasta 1,1 L_c.
L_c = pi/(2 kappa_FD) con kappa_FD de experimentos/acoplador_claude/resultados_g1_g2.json (solo lectura).
Salida: r2_runs/g3_d<d>.json. Modelo numerico escalar. Solo CPU.
"""
import datetime
import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
EXP = HERE.parent
sys.path.insert(0, str(EXP / "solver2d_claude"))
import solver2d as S2  # noqa: E402  (modelo 2D de experimentos/solver2d_claude, interfaz solve)
import bpm_r2 as B  # noqa: E402

H = 0.2
W = 40.0
S0, WCAP, R0 = 28.0, 12.0, 0.5
DZ = 1.0


def mode_single(xc, d):
    """Modo guiado de un nucleo en x = xc (solver2d), en la convencion [ix, iy] del BPM."""
    shapes = [{"kind": "disk", "x0": float(xc), "y0": 0.0, "r": B.A_CORE, "n": B.N1}]
    res = S2.solve(shapes, B.N2, B.LAM, W, H, n_modes=1, s_sub=8)
    psi = np.asarray(res["psi"][0]).T.copy()   # solver2d: [iy, ix] -> BPM: [ix, iy]
    return psi, float(res["neff"][0])


def first_local_max(z, p2, floor=0.05):
    for k in range(1, len(p2) - 1):
        if p2[k] > floor and p2[k] >= p2[k - 1] and p2[k] > p2[k + 1]:
            yl, y0, yr = p2[k - 1], p2[k], p2[k + 1]
            den = yl - 2.0 * y0 + yr
            off = 0.5 * (yl - yr) / den if den != 0 else 0.0
            dzs = z[k + 1] - z[k]
            return {"z_um": float(z[k] + off * dzs), "P2_max": float(y0 - 0.25 * (yl - yr) * off),
                    "k": int(k)}
    return None


def main(d):
    t0 = time.time()
    kap = json.loads((EXP / "acoplador_claude" / "resultados_g1_g2.json").read_text(encoding="utf-8"))
    kappa_um = float(kap["G1_main_h0125"][f"{float(d)}"]["kappa_FD_per_um"])
    Lc_um = np.pi / (2.0 * kappa_um)
    psiL, neff_L = mode_single(-d / 2.0, d)
    psiR, neff_R = mode_single(+d / 2.0, d)
    x = B.axis(W, H)
    n2 = B.cell_n2(x, H, [-d / 2.0, +d / 2.0])
    zend = 1.1 * Lc_um
    rec, _ = B.propagate(n2, psiL, H, DZ, zend, W, S0, WCAP, R0, {"R": psiR, "A0": psiL}, cap=True)
    z = np.array(rec.z)
    P2 = np.abs(np.array(rec.ip["R"])) ** 2 / (rec.norms["R"] * rec.P[0])
    fm = first_local_max(z, P2)
    out = {
        "d_um": float(d), "W_um": W, "h_um": H, "dz_um": DZ, "N": int(len(x)),
        "cap": {"s0": S0, "w": WCAP, "R0_um^-1": R0},
        "kappa_FD_um^-1": kappa_um, "kappa_FD_mm^-1": kappa_um * 1000.0,
        "Lc_mm": Lc_um / 1000.0, "z_end_mm": zend / 1000.0,
        "neff_solver2d_nucleo": neff_L, "norma_E0": rec.norms["A0"], "norma_psiR": rec.norms["R"],
        "P2_inicial": float(P2[0]), "P2_max_detectado": fm,
        "z_max_mm": (fm["z_um"] / 1000.0) if fm else None,
        "error_rel_zmax_vs_Lc": ((fm["z_um"] - Lc_um) / Lc_um) if fm else None,
        "perdida_al_final": rec.loss_at(zend),
        "curva_P2_cada_20um": {str(int(round(zz))): float(P2[k]) for k, zz in enumerate(z)
                               if abs(zz / 20.0 - round(zz / 20.0)) < 1e-9},
        "fecha_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "tiempo_s": time.time() - t0,
    }
    (HERE / "r2_runs" / f"g3_d{int(d)}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False),
                                                         encoding="utf-8")
    print(f"[G3 d={d}] Lc={Lc_um/1000:.4f} mm, z_max={out['z_max_mm']}, "
          f"err_rel={out['error_rel_zmax_vs_Lc']}, P2max={fm['P2_max'] if fm else None}, "
          f"t={out['tiempo_s']:.1f}s", flush=True)


if __name__ == "__main__":
    main(float(sys.argv[1]))
