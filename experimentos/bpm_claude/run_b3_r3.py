"""B3 de la ronda 3: dato inicial discreto (CONTRATO-bpm-r3.md, secciones 2-3).

Uso: python -B run_b3_r3.py <nombre> [<nombre> ...]
     python -B run_b3_r3.py --smoke <nombre>     (z_end = 5 um, salida en D:/tmp/jev_bpm_r3/smoke/)
Nombres: an_cap_dz1, fd_cap_dz1, an_cap_dz05, fd_cap_dz05, an_sin_dz1, fd_sin_dz1
Salida: r3_runs/<nombre>.json. Modelo numerico escalar paraxial. Solo CPU.
"""
import datetime
import hashlib
import json
import pathlib
import sys
import time

import numpy as np
from scipy import special as sp
from scipy.optimize import brentq

HERE = pathlib.Path(__file__).resolve().parent
EXP = HERE.parent
sys.path.insert(0, str(EXP / "solver2d_claude"))
sys.path.insert(0, str(HERE))
import solver2d as S2  # noqa: E402  (solo lectura de experimentos/solver2d_claude)
import bpm_r2 as B  # noqa: E402  (propagador propio de la ronda 2, sin cambios)

H = 0.2
W = 40.0
S0, WCAP = 28.0, 12.0
SUB = 16
Z_END = 1000.0
SMOKE_DIR = pathlib.Path("D:/tmp/jev_bpm_r3/smoke")

CONFIGS = {
    "an_cap_dz1": dict(E0="analitico", R0=0.5, dz=1.0, cap=True),
    "fd_cap_dz1": dict(E0="fd", R0=0.5, dz=1.0, cap=True),
    "an_cap_dz05": dict(E0="analitico", R0=0.5, dz=0.5, cap=True),
    "fd_cap_dz05": dict(E0="fd", R0=0.5, dz=0.5, cap=True),
    "an_sin_dz1": dict(E0="analitico", R0=0.0, dz=1.0, cap=False),
    "fd_sin_dz1": dict(E0="fd", R0=0.0, dz=1.0, cap=False),
}


def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def lp01_solve():
    """Mismo calculo que run_b2_r2.lp01_solve (ecuacion de autovalores de la fibra de salto)."""
    VNUM = B.K0 * B.A_CORE * np.sqrt(B.N1 ** 2 - B.N2 ** 2)

    def f(u):
        w = np.sqrt(VNUM ** 2 - u ** 2)
        return u * sp.j1(u) / sp.j0(u) - w * sp.k1(w) / sp.k0(w)

    u = brentq(f, 1e-6, 2.404825)
    w = np.sqrt(VNUM ** 2 - u ** 2)
    neff = np.sqrt(B.N1 ** 2 - (u / (B.K0 * B.A_CORE)) ** 2)
    return float(u), float(w), float(neff), float(VNUM)


def fd_mode():
    """Modo guiado discreto de solver2d (diferencias finitas 5 puntos, Dirichlet), misma malla que el BPM.

    solver2d devuelve psi[iy, ix]; el BPM usa psi[ix, iy]: se transpone (como en la ronda 2).
    """
    shapes = [{"kind": "disk", "x0": 0.0, "y0": 0.0, "r": B.A_CORE, "n": B.N1}]
    res = S2.solve(shapes, B.N2, B.LAM, W, H, n_modes=1, s_sub=SUB)
    psi = np.asarray(res["psi"][0], dtype=float).T.copy()
    x_s = np.asarray(res["x"], dtype=float)
    x_b = B.axis(W, H)
    if x_s.shape != x_b.shape or not np.allclose(x_s, x_b):
        raise RuntimeError("la malla de solver2d no coincide con la malla del BPM")
    return psi, float(res["neff"][0]), int(res["N"]), float(res["sigma_um2"])


def overlap2(f, g, h):
    """|<f|g>|^2 / (<f|f><g|g>) con producto h^2."""
    num = abs(np.sum(np.conj(f) * g) * h * h) ** 2
    den = (np.sum(np.abs(f) ** 2) * h * h) * (np.sum(np.abs(g) ** 2) * h * h)
    return float(num / den)


def main(name, smoke=False):
    cfg = CONFIGS[name]
    zend = 5.0 if smoke else Z_END
    t0 = time.time()
    u, w, neff_an, VNUM = lp01_solve()
    x = B.axis(W, H)
    n2 = B.cell_n2(x, H, [0.0])
    E0a = B.lp01_analytic(x, 0.0, u, w)
    out = {
        "nombre": name,
        "config": dict(cfg, W=W, s0=S0, w=WCAP, h_um=H, z_end_um=zend, SUB=SUB, lam_um=B.LAM),
        "smoke": smoke,
        "fecha_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "N": int(len(x)),
        "neff_analitico": neff_an,
        "sha256": {
            "solver2d.py": sha256(EXP / "solver2d_claude" / "solver2d.py"),
            "bpm_r2.py": sha256(HERE / "bpm_r2.py"),
            "run_b3_r3.py": sha256(HERE / "run_b3_r3.py"),
        },
    }
    if cfg["E0"] == "fd":
        psi0, neff_fd, Ns, sigma = fd_mode()
        psi_spec, neff_spec = B.discrete_ground_state(n2, H, E0a)
        out["neff_solver2d"] = neff_fd
        out["delta_neff_solver2d_vs_analitico"] = neff_fd - neff_an
        out["solver2d_N"] = Ns
        out["solver2d_sigma_um2"] = sigma
        out["neff_espectral_control"] = neff_spec
        out["overlap2_solver2d_vs_LP01"] = overlap2(E0a, psi0, H)
        out["overlap2_solver2d_vs_espectral_control"] = overlap2(psi_spec, psi0, H)
        out["E0_nota"] = "modo guiado discreto de solver2d (FD 5 puntos, Dirichlet), malla BPM h=0,2 um, s_sub=16"
        psi0 = psi0.astype(complex)
    else:
        psi0 = E0a
        out["overlap2_solver2d_vs_LP01"] = None
        out["E0_nota"] = "LP01 analitico muestreado (ronda 1 y 2)"
    out["norma_P0"] = float(np.sum(np.abs(psi0) ** 2) * H * H)

    R0 = cfg["R0"]
    dz = cfg["dz"]
    rec, Afin = B.propagate(n2, psi0, H, dz, zend, W, S0, WCAP, R0, {"E0": psi0}, cap=cfg["cap"])
    P = np.array(rec.P)
    out["unitariedad_max_abs_P_over_P0_minus_1"] = float(np.max(np.abs(P / P[0] - 1.0)))
    curve = {}
    zq = 50.0
    while zq <= zend + 1e-9:
        curve[str(int(zq))] = rec.loss_at(zq)
        zq += 50.0
    out["perdida_vs_z"] = curve
    out["z_medida_um"] = zend
    out["perdida_1mm"] = rec.loss_at(zend)
    out["P_final_sobre_P0"] = float(P[-1] / P[0])
    X, Y = np.meshgrid(x, x, indexing="ij")
    s = np.maximum(np.abs(X), np.abs(Y))
    Pout = float(np.sum(np.abs(Afin) ** 2 * (s > 28.0)) * H * H)
    out["fraccion_P_s_mayor_28_en_z_medida"] = Pout / float(P[-1])
    out["fraccion_P_s_mayor_28_sobre_P0"] = Pout / float(P[0])
    out["ov2_E0_en_z_medida"] = rec.ov2_at("E0", zend)
    out["tiempo_s"] = time.time() - t0
    out["fin_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")

    dest = SMOKE_DIR if smoke else (HERE / "r3_runs")
    dest.mkdir(parents=True, exist_ok=True)
    (dest / f"{name}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[{name}] perdida({zend:g}um)={out['perdida_1mm']:.4e} "
          f"unit={out['unitariedad_max_abs_P_over_P0_minus_1']:.2e} "
          f"P_s>28/P0={out['fraccion_P_s_mayor_28_sobre_P0']:.4e} "
          f"t={out['tiempo_s']:.1f}s", flush=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    smoke = False
    if args and args[0] == "--smoke":
        smoke = True
        args = args[1:]
    for nm in args:
        if nm not in CONFIGS:
            raise SystemExit(f"nombre desconocido: {nm}")
        main(nm, smoke=smoke)
