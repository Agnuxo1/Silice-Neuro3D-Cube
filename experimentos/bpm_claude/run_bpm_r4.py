"""Corridas de la ronda 4 (CONTRATO-bpm-r4.md, seccion 3). Modelo numerico. Solo CPU.

Uso: OMP_NUM_THREADS=1 python -B run_bpm_r4.py <nombre> [<nombre> ...]
Salida: r4_runs/<nombre>.json (perdida a 1 mm, solapes, curva de perdida, huella del propagador).
Propagador: bpm_r2.py (sin modificar). Implementacion del paso P-EIG en este archivo.
"""
import datetime
import hashlib
import json
import pathlib
import sys
import time

import numpy as np
import scipy.fft as sfft
from scipy.sparse.linalg import LinearOperator, eigs
from scipy import special as sp
from scipy.optimize import brentq

import bpm_r2 as B

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "r4_runs"
OUT.mkdir(exist_ok=True)

H = 0.2
CONFIGS = {
    "r4_W40_dz1": dict(W=40, s0=28, w=12, R0=0.5, dz=1.0, E0="analitico", z_end=1000.0),
    "r4_W60_dz1": dict(W=60, s0=48, w=12, R0=0.5, dz=1.0, E0="analitico", z_end=1000.0),
    "r4_W80_dz1": dict(W=80, s0=68, w=12, R0=0.5, dz=1.0, E0="analitico", z_end=1000.0),
    "r4_W40_dz05": dict(W=40, s0=28, w=12, R0=0.5, dz=0.5, E0="analitico", z_end=1000.0),
    "r4_PEIG_W40_dz1": dict(W=40, s0=28, w=12, R0=0.5, dz=1.0, E0="peig", z_end=1000.0),
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def lp01_solve():
    VNUM = B.K0 * B.A_CORE * np.sqrt(B.N1 ** 2 - B.N2 ** 2)

    def f(u):
        w = np.sqrt(VNUM ** 2 - u ** 2)
        return u * sp.j1(u) / sp.j0(u) - w * sp.k1(w) / sp.k0(w)

    u = brentq(f, 1e-6, 2.404825)
    w = np.sqrt(VNUM ** 2 - u ** 2)
    neff = np.sqrt(B.N1 ** 2 - (u / (B.K0 * B.A_CORE)) ** 2)
    return float(u), float(w), float(neff), float(VNUM)


def peig(n2, E0a, h, dz, s0, w, R0, W):
    """Autovector guiado del operador de un paso U = P D P (con CAP), por ARPACK (mayor |lambda|)."""
    N = n2.shape[0]
    x = (np.arange(N) - (N - 1) // 2) * h
    V = B.K0 * B.K0 * (n2 - B.NREF * B.NREF).astype(complex)
    V = V - 1j * B.gamma_cap(x, s0, w, R0)
    kx = 2.0 * np.pi * np.fft.fftfreq(N, d=h)
    K2 = kx[:, None] ** 2 + kx[None, :] ** 2
    D = np.exp(1j * dz * K2 / (2.0 * B.K0 * B.NREF))
    P = np.exp(-1j * dz * V / (4.0 * B.K0 * B.NREF))

    def step(A):
        A = P * A
        A = sfft.ifft2(D * sfft.fft2(A, workers=1), workers=1)
        return P * A

    def mv(v):
        return step(np.asarray(v).reshape(N, N)).ravel()

    op = LinearOperator((N * N, N * N), matvec=mv, dtype=complex)
    vals, vecs = eigs(op, k=1, which="LM", v0=E0a.ravel().astype(complex), tol=1e-10, maxiter=5000)
    lam = complex(vals[0])
    E = vecs[:, 0].reshape(N, N)
    E = E / np.sqrt(np.sum(np.abs(E) ** 2) * h * h)
    ph = np.angle(np.sum(E))
    E = E * np.exp(-1j * ph)
    resid = float(np.linalg.norm(step(E) - lam * E) / np.linalg.norm(E))
    return E, lam, resid


def main(name):
    cfg = CONFIGS[name]
    t0 = time.time()
    u, w, neff_an, VNUM = lp01_solve()
    x = B.axis(cfg["W"], H)
    n2 = B.cell_n2(x, H, [0.0])
    E0a = B.lp01_analytic(x, 0.0, u, w)
    out = {
        "nombre": name,
        "config": cfg,
        "h_um": H,
        "N": int(len(x)),
        "fecha_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "neff_analitico": neff_an,
        "sha256_bpm_r2": sha256(HERE / "bpm_r2.py"),
        "sha256_run_bpm_r4": sha256(HERE / "run_bpm_r4.py"),
    }
    dz = cfg["dz"]
    zend = cfg["z_end"]
    if cfg["E0"] == "peig":
        E, lam, resid = peig(n2, E0a, H, dz, cfg["s0"], cfg["w"], cfg["R0"], cfg["W"])
        psi0 = E
        out["lam_abs"] = float(abs(lam))
        out["lam_fase_por_paso"] = float(np.angle(lam))
        out["residuo_relativo_U"] = resid
        out["neff_propagador_implicito"] = float(B.NREF - np.angle(lam) / (B.K0 * dz))
        out["delta_neff_propagador_vs_analitico"] = out["neff_propagador_implicito"] - neff_an
        out["perdida_eigen_teorica_1mm"] = float(1.0 - abs(lam) ** (2.0 * zend / dz))
        n_norm_a = float(np.sum(np.abs(E0a) ** 2) * H * H)
        out["ov2_LP01_analitico"] = float(abs(np.sum(np.conj(E0a) * E) * H * H) ** 2 / (n_norm_a * np.sum(np.abs(E) ** 2) * H * H))
    else:
        psi0 = E0a
    rec, Afin = B.propagate(n2, psi0, H, dz, zend, cfg["W"], cfg["s0"], cfg["w"], cfg["R0"],
                            {"E0": psi0}, cap=True)
    P = np.array(rec.P)
    out["unitariedad_max_abs_P_over_P0_minus_1"] = float(np.max(np.abs(P / P[0] - 1.0)))
    curve = {}
    for zq in np.arange(50.0, zend + 1e-9, 50.0):
        curve[str(int(zq))] = rec.loss_at(zq)
    out["perdida_vs_z"] = curve
    out["z_medida_um"] = zend
    out["perdida_1mm"] = rec.loss_at(zend)
    out["ov2_1mm"] = rec.ov2_at("E0", zend)
    out["tiempo_s"] = time.time() - t0
    (OUT / f"{name}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[{name}] perdida(1mm)={out['perdida_1mm']:.4e} ov2={out['ov2_1mm']:.9f} "
          f"t={out['tiempo_s']:.1f}s", flush=True)


if __name__ == "__main__":
    for nm in sys.argv[1:]:
        main(nm)
