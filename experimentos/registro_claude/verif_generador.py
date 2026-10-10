#!/usr/bin/env python3
"""Convergencia del generador gaussiano correlacionado (apoyo a V-K2 de registro_k.py).

Compara la correlacion empirica por retardo con exp(-k/l) para R = 2000 (semilla principal)
y R = 20000 (semilla distinta). Si el error es de muestreo, debe caer aproximadamente como 1/sqrt(R).
Ejecucion: OMP_NUM_THREADS=1 python -B verif_generador.py -> verif_generador.json
"""
import json
import pathlib
import sys

import numpy as np

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
N_CH = 200
LAGS = [1, 2, 3, 5, 10]


def factor(l):
    k = np.abs(np.subtract.outer(np.arange(N_CH), np.arange(N_CH))).astype(float)
    C = np.exp(-k / l)
    w, V = np.linalg.eigh(C)
    A = V * np.sqrt(np.clip(w, 0.0, None))
    return A, float(np.max(np.abs(A @ A.T - C)))


def lag_stats(rho, l):
    rows = {}
    for k in LAGS:
        emp = float(np.mean(rho[:, :-k] * rho[:, k:]))
        rows[k] = {"emp": emp, "obj": float(np.exp(-k / l)), "err": emp - float(np.exp(-k / l))}
    return rows, float(np.std(rho))


out = {"N_chip": N_CH, "nota": "err = emp - exp(-k/l); si es muestreo, |err| baja con R"}
for l in [1, 3, 10]:
    A, rec = factor(l)
    res = {"reconstruccion_max": rec}
    for R, seed in [(2000, 20261010), (20000, 20261109)]:
        Z = np.random.default_rng(seed).standard_normal((R, N_CH))
        rho = Z @ A.T
        rows, sd = lag_stats(rho, l)
        res[f"R{R}"] = {"sd_rho": sd, "lags": rows, "max_abs_err": max(abs(r["err"]) for r in rows.values())}
    out[f"l{l}"] = res
path = HERE / "verif_generador.json"
path.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
for l in [1, 3, 10]:
    r = out[f"l{l}"]
    print(f"l={l:<3} rec={r['reconstruccion_max']:.1e} | R=2000 max|err|={r['R2000']['max_abs_err']:.4f} sd={r['R2000']['sd_rho']:.4f}"
          f" | R=20000 max|err|={r['R20000']['max_abs_err']:.4f} sd={r['R20000']['sd_rho']:.4f}")
print("->", path)
