"""Corridas de la ronda 5 (CONTRATO-bpm-r5.md). Modelo numerico escalar paraxial. Solo CPU.

Uso: OMP_NUM_THREADS=1 python -B run_bpm_r5.py <caso> [<caso> ...]
Casos:
  dz1, dz05, dz025, dz0125 : W = 40, h = 0,2, CAP base (s0 = 28, w = 12, R0 = 0,5), E0 = LP01 analitico, z = 1000 um.
  unit                     : V2, sin CAP, dz = 0,125, z <= 100 um.
  pert                     : referencia de primer orden P_pert (seccion 1 del contrato), sin propagacion.
Salida: r5_runs/<caso>.json. Propagador: bpm_r2.py (sin modificar).
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

import bpm_r2 as B

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "r5_runs"
OUT.mkdir(exist_ok=True)

H = 0.2
W = 40.0
S0, WCAP, R0 = 28.0, 12.0, 0.5
ZEND = 1000.0
DZ = {"dz1": 1.0, "dz05": 0.5, "dz025": 0.25, "dz0125": 0.125, "dz00625": 0.0625}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def lp01_solve():
    vnum = B.K0 * B.A_CORE * np.sqrt(B.N1 ** 2 - B.N2 ** 2)

    def f(u):
        w = np.sqrt(vnum ** 2 - u ** 2)
        return u * sp.j1(u) / sp.j0(u) - w * sp.k1(w) / sp.k0(w)

    u = brentq(f, 1e-6, 2.404825)
    w = np.sqrt(vnum ** 2 - u ** 2)
    neff = np.sqrt(B.N1 ** 2 - (u / (B.K0 * B.A_CORE)) ** 2)
    return float(u), float(w), float(neff), float(vnum)


def build(h=H):
    u, w, neff_an, vnum = lp01_solve()
    x = B.axis(W, h)
    n2 = B.cell_n2(x, h, [0.0])
    E0 = B.lp01_analytic(x, 0.0, u, w)
    return x, n2, E0, {"u": u, "w": w, "neff_analitico": neff_an, "VNUM": vnum}


def write(name, out):
    (OUT / f"{name}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")


def base_info(name):
    return {
        "nombre": name,
        "W_um": W,
        "h_um": H,
        "N": int(round(W / H)) * 2 + 1,
        "cap": {"s0_um": S0, "w_um": WCAP, "R0_um^-1": R0},
        "fecha_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "sha256_bpm_r2": sha256(HERE / "bpm_r2.py"),
        "sha256_run_bpm_r5": sha256(HERE / "run_bpm_r5.py"),
    }


def run_dz(name):
    dz = DZ[name]
    out = base_info(name)
    t0 = time.time()
    x, n2, E0, info = build()
    out["setup_s"] = time.time() - t0
    out["lp01"] = info
    out["dz_um"] = dz
    out["z_end_um"] = ZEND
    out["pasos"] = int(round(ZEND / dz))
    t1 = time.time()
    rec, _ = B.propagate(n2, E0, H, dz, ZEND, W, S0, WCAP, R0, {"E0": E0}, cap=True)
    out["tiempo_propagacion_s"] = time.time() - t1
    out["tiempo_por_paso_ms"] = 1e3 * out["tiempo_propagacion_s"] / out["pasos"]
    out["P0"] = float(rec.P[0])
    out["P_1mm"] = float(rec.P[rec.idx(ZEND)])
    out["perdida_1mm"] = float(rec.loss_at(ZEND))
    out["ov2_1mm"] = float(rec.ov2_at("E0", ZEND))
    out["perdida_vs_z"] = {str(int(zq)): float(rec.loss_at(zq))
                           for zq in np.arange(50.0, ZEND + 1e-9, 50.0)}
    write(name, out)
    print(f"[{name}] dz={dz} perdida(1mm)={out['perdida_1mm']:.6e} ov2={out['ov2_1mm']:.9f} "
          f"t_prop={out['tiempo_propagacion_s']:.1f}s ({out['tiempo_por_paso_ms']:.2f} ms/paso)", flush=True)


def run_unit():
    name = "unit"
    out = base_info(name)
    x, n2, E0, info = build()
    out["dz_um"] = 0.125
    out["z_end_um"] = 100.0
    t1 = time.time()
    rec, _ = B.propagate(n2, E0, H, 0.125, 100.0, W, S0, WCAP, R0, {}, cap=False)
    out["tiempo_propagacion_s"] = time.time() - t1
    dev = [abs(p / rec.P[0] - 1.0) for p in rec.P]
    out["max_abs_P_over_P0_minus_1"] = float(max(dev))
    out["n_registros"] = len(rec.P)
    write(name, out)
    print(f"[unit] max|P/P0-1| sin CAP (z<=100, dz=0,125) = {out['max_abs_P_over_P0_minus_1']:.3e}", flush=True)


def run_pert():
    name = "pert"
    out = base_info(name)
    res = {}
    for h in (0.2, 0.1):
        u, w, neff_an, vnum = lp01_solve()
        x = B.axis(W, h)
        E0 = B.lp01_analytic(x, 0.0, u, w)
        X, Y = np.meshgrid(x, x, indexing="ij")
        s = np.maximum(np.abs(X), np.abs(Y))
        t = np.clip((s - S0) / WCAP, 0.0, 1.0)
        I = np.abs(E0) ** 2
        t2 = float(np.sum(t * t * I) / np.sum(I))
        res[f"h{h}"] = {"h_um": h, "t2_medio_P_E0": t2,
                        "P_pert_1mm": float(1.0 - np.exp(-2.0 * R0 * t2 * ZEND))}
    out["referencias"] = res
    out["P_pert_1mm_h0.2"] = res["h0.2"]["P_pert_1mm"]
    write(name, out)
    print(f"[pert] P_pert(1 mm) h=0,2: {res['h0.2']['P_pert_1mm']:.6e}; h=0,1: {res['h0.1']['P_pert_1mm']:.6e}",
          flush=True)


if __name__ == "__main__":
    for nm in sys.argv[1:]:
        if nm in DZ:
            run_dz(nm)
        elif nm == "unit":
            run_unit()
        elif nm == "pert":
            run_pert()
        else:
            raise SystemExit(f"caso desconocido: {nm}")
