"""Diagnostico (NO es criterio del contrato): origen de la perdida de 2,46e-4 en B3.

Pregunta: la potencia que llega a la region exterior (s > 28 um, y s > 34 um) sin CAP,
y la perdida con CAP en funcion de z (1 mm, h = 0,2 um, dz = 1 um).
Ejecutar con: python -B diagnostico_perdida_bpm.py
"""
import json
import numpy as np
import bpm
import verificar_bpm as v

x = bpm.axis_coords(v.N_BASE, v.H_BASE)
u, w, _ = v.lp01_solve()
E0 = v.lp01_field(x, 0.0, u, w)
n_cell = v.n_xy_cell(x, v.H_BASE, [0.0])
X, Y = np.meshgrid(x, x, indexing="ij")
S = np.maximum(np.abs(X), np.abs(Y))
h2 = v.H_BASE ** 2
P0 = float(np.sum(np.abs(E0) ** 2) * h2)
out = {}

# (a) sin CAP: potencia fuera de la region del CAP y dentro del nucleo, a 1 mm
saved = bpm.propagate(n_cell, E0, v.LAM, v.H_BASE, 1.0, [1000.0], v.NREF, cap=False)
A1 = saved[1000.0]
P_s28 = float(np.sum(np.abs(A1[S > 28.0]) ** 2) * h2) / P0
P_s34 = float(np.sum(np.abs(A1[S > 34.0]) ** 2) * h2) / P0
P_core = float(np.sum(np.abs(A1[np.hypot(X, Y) <= 6.0]) ** 2) * h2) / P0
ov2_nc = float(abs(np.sum(np.conj(E0) * A1) * h2) ** 2 / (P0 * float(np.sum(np.abs(A1) ** 2) * h2)))
out["sin_CAP_1mm"] = {"fraccion_P_s>28": P_s28, "fraccion_P_s>34": P_s34,
                      "fraccion_P_nucleo_r<=6": P_core, "overlap2_con_E0": ov2_nc}
print("[diag a] sin CAP 1 mm: P(s>28)/P0 =", P_s28, " P(s>34)/P0 =", P_s34,
      " P(r<=6)/P0 =", P_core, " overlap2 =", ov2_nc, flush=True)

# (b) con CAP: perdida en funcion de z
rec_c = v.Recorder(E0, v.H_BASE)
bpm.propagate(n_cell, E0, v.LAM, v.H_BASE, 1.0, [1000.0], v.NREF, cap=True, observe=rec_c)
curva = {}
for zq in [50.0, 100.0, 200.0, 400.0, 600.0, 800.0, 1000.0]:
    lq, _ = rec_c.loss_at(zq)
    curva[str(int(zq))] = lq
out["con_CAP_perdida_vs_z"] = curva
print("[diag b] con CAP, perdida(z):", curva, flush=True)

with open("diagnostico_perdida_bpm.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=2, ensure_ascii=False)
