"""Una corrida FD de T6 r5 en su propio proceso (para medir el pico de memoria de esa corrida).

Escribe un JSON con n_eff, residuo relativo, fraccion de energia en el nucleo, tiempo y pico de memoria.
Ejemplo: python -B fd_vectorial_run.py --geom jump --h 0.0625 --out t6_corridas/x.json
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys
import time

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import numpy as np  # noqa: E402
import fd_vectorial_core as C  # noqa: E402

LAM = 1.55          # um
N1 = 1.444          # nucleo
N2 = 1.439          # revestimiento (salto)
A = 6.0             # radio del nucleo, um
DN_TRENCH = -0.005  # trinchera n0 + dn
T_TRENCH = 6.0      # espesor de la trinchera, um


def core_mask(M: int, h: float, a: float) -> np.ndarray:
    """Mascara plana (indice i*M+j) de celdas del cuadrante con centro en r < a."""
    c = (np.arange(M) + 0.5) * h
    X, Y = np.meshgrid(c, c, indexing="ij")
    return (np.hypot(X, Y) < a).ravel()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--geom", choices=["jump", "trench", "uniform"], required=True)
    p.add_argument("--semi", type=int, default=1, help="1: semivectorial H_y; 0: escalar")
    p.add_argument("--h", type=float, required=True)
    p.add_argument("--L", type=float, default=30.0)
    p.add_argument("--sx", type=int, default=1, help="+1 Neumann (par) / -1 Dirichlet (impar) en x=0")
    p.add_argument("--sy", type=int, default=1, help="+1 Neumann (par) / -1 Dirichlet (impar) en y=0")
    p.add_argument("--full", type=int, default=0, help="1: malla completa [-L,L]^2 (comprobacion de simetria)")
    p.add_argument("--k", type=int, default=3)
    p.add_argument("--select", choices=["top", "core"], default="top")
    p.add_argument("--sigma_neff", type=float, default=None, help="n_eff de referencia para el shift")
    p.add_argument("--out", required=True)
    args = p.parse_args()

    h = args.h
    M = int(round(args.L / h))
    if abs(M * h - args.L) > 1e-12:
        raise SystemExit("L/h debe ser entero")
    k0 = 2.0 * math.pi / LAM

    if args.geom == "jump":
        Eq = C.eps_quadrant(M, h, A, N1, N2)
    elif args.geom == "trench":
        Eq = C.eps_quadrant(M, h, A, N1, N1, b=A + T_TRENCH, n_tr=N1 + DN_TRENCH)
    else:
        Eq = C.eps_quadrant(M, h, A, N1, N1)  # medio uniforme n = N1

    sx, sy = args.sx, args.sy
    if args.full:
        E = C.eps_full_from_quadrant(Eq)
        sx, sy = -1, -1  # caja completa: pared de Dirichlet en -L
    else:
        E = Eq

    semi = bool(args.semi)
    sigma_neff = args.sigma_neff if args.sigma_neff is not None else N1
    sigma = k0 * k0 * sigma_neff * sigma_neff

    t0 = time.perf_counter()
    Amat = C.assemble(E, k0, h, sx, sy, semi)
    vals, vecs = C.top_eigs(Amat, sigma, k=args.k, symmetric=not semi)
    elapsed = time.perf_counter() - t0

    n_full = E.shape[0]
    mask = core_mask(M, h, A) if not args.full else None
    fr = []
    neffs = []
    resid = []
    for m in range(vals.size):
        v = vecs[:, m]
        if mask is not None:
            w = np.abs(v) ** 2
            fr.append(float(w[mask].sum() / w.sum()))
        else:
            fr.append(float("nan"))
        neffs.append(math.sqrt(float(np.real(vals[m]))) / k0)
        resid.append(C.residual_rel(Amat, vals[m], v))

    if args.select == "core" and mask is not None:
        sel = int(np.argmax(fr))
    else:
        sel = 0
    lam = vals[sel]
    out = {
        "geom": args.geom, "semi": int(semi), "h_um": h, "L_um": args.L, "M_cells_per_side": int(n_full),
        "sx": sx, "sy": sy, "full": args.full, "k": args.k, "select": args.select,
        "sigma_neff": sigma_neff, "unknowns": int(Amat.shape[0]),
        "selected_index": sel,
        "neff": float(np.real(neffs[sel])),
        "neff_imag_beta2": float(np.imag(lam)),
        "neff_list": [float(x) for x in neffs],
        "frac_core_list": fr,
        "resid_rel_list": resid,
        "resid_rel_selected": resid[sel],
        "elapsed_solve_s": elapsed,
        "peak_mem_bytes": C.peak_memory_bytes(),
        "numpy": np.__version__,
    }
    outp = pathlib.Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: out[k] for k in ("geom", "semi", "h_um", "unknowns", "neff", "resid_rel_selected",
                                          "elapsed_solve_s", "peak_mem_bytes")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
