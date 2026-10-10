"""Barrido B2.1 y corridas de diagnostico de la ronda 2 (CONTRATO-bpm-r2.md, seccion 3).

Uso: python -B run_b2_r2.py <nombre> [<nombre> ...]
Salida: r2_runs/<nombre>.json (perdida a 1 mm, solapes, n_eff implicito, curva de perdida).
Modelo numerico. Solo CPU.
"""
import datetime
import json
import pathlib
import sys
import time

import numpy as np
from scipy import special as sp
from scipy.optimize import brentq

import bpm_r2 as B

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "r2_runs"
OUT.mkdir(exist_ok=True)

H = 0.2
CONFIGS = {
    "v0": dict(W=40, s0=28, w=12, R0=0.5, dz=1.0, E0="analitico", cap=False, z_end=200.0),
    "base": dict(W=40, s0=28, w=12, R0=0.5, dz=1.0, E0="analitico", cap=True, z_end=1000.0),
    "G0": dict(W=40, s0=28, w=12, R0=0.05, dz=1.0, E0="analitico", cap=True, z_end=1000.0),
    "s0": dict(W=40, s0=34, w=6, R0=0.5, dz=1.0, E0="analitico", cap=True, z_end=1000.0),
    "disc": dict(W=40, s0=28, w=12, R0=0.5, dz=1.0, E0="discreto", cap=True, z_end=1000.0),
    "dz05": dict(W=40, s0=28, w=12, R0=0.5, dz=0.5, E0="analitico", cap=True, z_end=1000.0),
    "W60": dict(W=60, s0=48, w=12, R0=0.5, dz=1.0, E0="analitico", cap=True, z_end=1000.0),
    "W60c": dict(W=60, s0=28, w=12, R0=0.5, dz=1.0, E0="analitico", cap=True, z_end=1000.0),
    "W80": dict(W=80, s0=68, w=12, R0=0.5, dz=1.0, E0="analitico", cap=True, z_end=1000.0),
}


def lp01_solve():
    VNUM = B.K0 * B.A_CORE * np.sqrt(B.N1 ** 2 - B.N2 ** 2)

    def f(u):
        w = np.sqrt(VNUM ** 2 - u ** 2)
        return u * sp.j1(u) / sp.j0(u) - w * sp.k1(w) / sp.k0(w)

    u = brentq(f, 1e-6, 2.404825)
    w = np.sqrt(VNUM ** 2 - u ** 2)
    neff = np.sqrt(B.N1 ** 2 - (u / (B.K0 * B.A_CORE)) ** 2)
    return float(u), float(w), float(neff), float(VNUM)


def main(name):
    cfg = CONFIGS[name]
    t0 = time.time()
    u, w, neff_an, VNUM = lp01_solve()
    x = B.axis(cfg["W"], H)
    n2 = B.cell_n2(x, H, [0.0])
    E0a = B.lp01_analytic(x, 0.0, u, w)
    out = {"nombre": name, "config": cfg, "h_um": H, "N": int(len(x)),
           "fecha_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           "neff_analitico": neff_an}
    if cfg["E0"] == "discreto":
        psi0, neff_disc = B.discrete_ground_state(n2, H, E0a)
        out["neff_discreto"] = neff_disc
        out["delta_neff_discreto_vs_analitico"] = neff_disc - neff_an
        out["E0_nota"] = "autoestado discreto de -(lap+V_real), W=40, h=0.2"
    else:
        psi0 = E0a
    dz = cfg["dz"]
    zend = cfg["z_end"]
    rec, Afin = B.propagate(n2, psi0, H, dz, zend, cfg["W"], cfg["s0"], cfg["w"], cfg["R0"],
                            {"E0": psi0}, cap=cfg["cap"])
    P = np.array(rec.P)
    out["unitariedad_max_abs_P_over_P0_minus_1"] = float(np.max(np.abs(P / P[0] - 1.0)))
    curve = {}
    for zq in np.arange(50.0, zend + 1e-9, 50.0):
        curve[str(int(zq))] = rec.loss_at(zq)
    out["perdida_vs_z"] = curve
    z1 = min(1000.0, zend)
    out["z_medida_um"] = z1
    out["perdida_1mm"] = rec.loss_at(z1)
    out["ov2_1mm"] = rec.ov2_at("E0", z1)
    out["neff_impl_1mm"] = rec.neff_impl_at("E0", z1)
    out["delta_neff_impl_vs_analitico"] = out["neff_impl_1mm"] - neff_an
    out["tiempo_s"] = time.time() - t0
    (OUT / f"{name}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[{name}] perdida(1mm)={out['perdida_1mm']:.4e} ov2={out['ov2_1mm']:.10f} "
          f"neff_impl={out['neff_impl_1mm']:.10f} unit={out['unitariedad_max_abs_P_over_P0_minus_1']:.2e} "
          f"t={out['tiempo_s']:.1f}s", flush=True)


if __name__ == "__main__":
    for nm in sys.argv[1:]:
        main(nm)
