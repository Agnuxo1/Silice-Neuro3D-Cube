#!/usr/bin/env python3
"""Convergencia del Monte Carlo de la fraccion media (apoyo a V-K3 de registro_k.py).

Repite las 12 celdas de d = 20 um con R = 20000 realizaciones y otra semilla, y compara con el
valor analitico. Criterio de esta verificacion (fijado antes de ejecutar): |E_MC - E_ana| < 3 * SE,
con SE = sd(f_chip) / sqrt(R). Escribe verif_mc_convergencia.json.
Ejecucion: OMP_NUM_THREADS=1 python -B verif_mc_convergencia.py
"""
import json
import pathlib
import sys

import numpy as np

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import registro_k as K  # noqa: E402  (mismas tablas, mismas funciones de cumplimiento)

R_BIG = 20000
SEED_BIG = 20261111
Z = np.random.default_rng(SEED_BIG).standard_normal((R_BIG, K.N_CH))
rows = []
ok = True
for s in K.SIGMAS:
    for l in K.LS:
        A = K.factor(l, "exp")
        dl = s * (Z @ A.T)
        counts = K.passes(K.D0 + dl).sum(axis=1)
        f = counts / K.N_CH
        E_mc = float(f.mean())
        se = float(f.std(ddof=1) / np.sqrt(R_BIG))
        E_a = K.E_ana(K.D0, s)
        passed = abs(E_mc - E_a) < 3 * se
        ok = ok and passed
        rows.append({"sigma_um": s, "l_celdas": l, "R": R_BIG, "E_mc": E_mc, "SE": se,
                     "E_ana": E_a, "dif": E_mc - E_a, "dif_en_SE": (E_mc - E_a) / se, "pass": bool(passed)})
        print(f"sig={s:<4} l={l:<3} R={R_BIG} E_mc={E_mc:.5f} SE={se:.5f} E_ana={E_a:.5f} "
              f"dif/SE={(E_mc - E_a) / se:+.2f} {'ok' if passed else 'NO'}")
out = {"criterio": "|E_mc - E_ana| < 3 SE en las 12 celdas, R = 20000, semilla 20261111",
       "todas_pass": bool(ok), "celdas": rows}
(HERE / "verif_mc_convergencia.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                                                 encoding="utf-8", newline="\n")
print("todas_pass =", ok)
