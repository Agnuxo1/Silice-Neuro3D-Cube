"""G3 de la ronda 5 (CONTRATO-bpm-r5.md, seccion 6). Solo si B3-r5 pasa. Modelo numerico escalar. Solo CPU.

Uso: OMP_NUM_THREADS=1 python -B run_g3_r5.py <d14|d16> --dz <dz_um> [--h <h_um>]
Dos nucleos a x = -d/2 y +d/2 (a = 6 um). E0 = LP01 de un nucleo en -d/2. psi_R = LP01 de un nucleo en +d/2.
P2m(z) = |<psi_R|A(z)>|^2 / (<psi_R|psi_R> <A0|A0>). z_max = primer maximo local de P2m (parabola de 3 puntos).
kappa_FD: experimentos/acoplador_claude/resultados_g1_g2.json (G1_main_h0125, kappa_FD_per_um). L_c = pi/(2 kappa).
z_end = 1,1 L_c. Salida: r5_runs/g3_<d14|d16>.json.
"""
import argparse
import datetime
import hashlib
import json
import pathlib
import time

import numpy as np

import bpm_r2 as B
from run_bpm_r5 import lp01_solve, sha256, W

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "r5_runs"
OUT.mkdir(exist_ok=True)
KAPPA_FILE = HERE.parent / "acoplador_claude" / "resultados_g1_g2.json"
S0, WCAP, R0 = 28.0, 12.0, 0.5


def kappa_from_g1(d):
    data = json.loads(KAPPA_FILE.read_text(encoding="utf-8"))
    return float(data["G1_main_h0125"][f"{d:.1f}"]["kappa_FD_per_um"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("caso", choices=["d14", "d16"])
    ap.add_argument("--dz", type=float, required=True)
    ap.add_argument("--h", type=float, default=0.2)
    args = ap.parse_args()
    d = 14.0 if args.caso == "d14" else 16.0
    h, dz = args.h, args.dz

    t0 = time.time()
    u, w, neff_an, vnum = lp01_solve()
    x = B.axis(W, h)
    n2 = B.cell_n2(x, h, [-d / 2.0, +d / 2.0])
    A0 = B.lp01_analytic(x, -d / 2.0, u, w)
    psiR = B.lp01_analytic(x, +d / 2.0, u, w)
    setup_s = time.time() - t0

    kappa = kappa_from_g1(d)
    Lc = np.pi / (2.0 * kappa)
    z_end = 1.1 * Lc
    nsteps = int(round(z_end / dz))

    t1 = time.time()
    rec, _ = B.propagate(n2, A0, h, dz, nsteps * dz, W, S0, WCAP, R0,
                         {"R": psiR, "E0": A0}, cap=True)
    t_prop = time.time() - t1

    z = np.array(rec.z)
    p2 = np.abs(np.array(rec.ip["R"])) ** 2 / (rec.norms["R"] * rec.norms["E0"])
    p2 = np.asarray(p2, dtype=float)
    ptot = np.asarray(rec.P, dtype=float) / rec.P[0]

    kmax = None
    for k in range(1, len(p2) - 1):
        if p2[k] > p2[k - 1] and p2[k] >= p2[k + 1]:
            kmax = k
            break
    if kmax is None:
        zmax, p2max, interior = float("nan"), float("nan"), False
    else:
        a, b, c = p2[kmax - 1], p2[kmax], p2[kmax + 1]
        den = a - 2.0 * b + c
        delta = 0.5 * (a - c) / den if den != 0.0 else 0.0
        zmax = float(z[kmax] + delta * dz)
        p2max = float(b - 0.25 * (a - c) * delta)
        interior = True
    rel = abs(zmax - Lc) / Lc if interior else float("nan")
    out = {
        "nombre": f"g3_{args.caso}",
        "d_um": d,
        "h_um": h,
        "W_um": W,
        "N": int(len(x)),
        "dz_um": dz,
        "kappa_FD_per_um": kappa,
        "L_c_um": float(Lc),
        "z_end_um": float(nsteps * dz),
        "z_end_sobre_Lc": float(nsteps * dz / Lc),
        "z_max_um": zmax,
        "P2max_m": p2max,
        "max_interior": bool(interior),
        "error_relativo_zmax_Lc": rel,
        "criterio_max_rel": 0.10,
        "pass": bool(interior and rel <= 0.10),
        "P_total_sobre_P0_final": float(ptot[-1]),
        "perdida_final": float(1.0 - ptot[-1]),
        "setup_s": setup_s,
        "tiempo_propagacion_s": t_prop,
        "pasos": nsteps,
        "tiempo_por_paso_ms": 1e3 * t_prop / max(nsteps, 1),
        "neff_analitico_un_nucleo": neff_an,
        "fecha_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "sha256_bpm_r2": sha256(HERE / "bpm_r2.py"),
        "sha256_run_g3_r5": sha256(HERE / "run_g3_r5.py"),
    }
    # Curva P2m submuestreada cada 10 um para el informe.
    sub = {}
    for zq in np.arange(0.0, nsteps * dz + 1e-9, 10.0):
        k = int(np.argmin(np.abs(z - zq)))
        sub[f"{z[k]:.3f}"] = float(p2[k])
    out["P2m_vs_z_cada_10um"] = sub
    (OUT / f"g3_{args.caso}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[g3_{args.caso}] Lc={Lc:.2f} um z_max={zmax:.2f} um rel={rel:.4f} "
          f"pass={out['pass']} t_prop={t_prop:.1f}s ({out['tiempo_por_paso_ms']:.2f} ms/paso)", flush=True)


if __name__ == "__main__":
    main()
