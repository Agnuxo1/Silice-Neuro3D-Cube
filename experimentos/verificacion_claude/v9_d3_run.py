"""V9: replica del runner de D3 con otro dato inicial (anchura w0 distinta y/o centro desplazado).
Uso: python -B v9_d3_run.py TAG W0_um X0_um Y0_um DOM_um FRAC [DX_um]
Solo importa adi2d (lectura, sin modificar) de ../glass009_claude. theta=0, dz=2.5 um, 800 pasos, muestreo cada 40.
"""
import os, sys, json, time
os.environ["OMP_NUM_THREADS"] = "1"; os.environ["OPENBLAS_NUM_THREADS"] = "1"
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "glass009_claude"))
import numpy as np
import adi2d as S
T0 = time.time()
tag = sys.argv[1]; w0 = float(sys.argv[2]) * 1e-6; x0 = float(sys.argv[3]) * 1e-6; y0 = float(sys.argv[4]) * 1e-6
dom = float(sys.argv[5]) * 1e-6; frac = float(sys.argv[6]); dx = (float(sys.argv[7]) if len(sys.argv) > 7 else 0.5) * 1e-6
dz = 2.5e-6; total = 800; every = 40; SMAX = 4e4; RU = 40e-6; p = 4.0
N = int(round(dom / dx)); d2 = dx * dx; zR = S.b0 * w0 ** 2 / 2
x, y = S.coords(N, dx); R = np.hypot(x, y); useful = R < RU
e = np.maximum(np.abs(x), np.abs(y)) / (N * dx / 2); band = e > (1 - frac)
sig = SMAX * np.maximum((e - (1 - frac)) / frac, 0) ** p
f = np.exp(-(((x - x0) ** 2 + (y - y0) ** 2) / w0 ** 2)); c = 1.0 / np.sqrt((f ** 2).sum() * d2)
A0 = (f * c).astype(complex); P0 = float((np.abs(A0) ** 2).sum() * d2)
def analytic(z):
    zeta = z / zR
    return c / (1 + 1j * zeta) * np.exp(-(((x - x0) ** 2 + (y - y0) ** 2) / (w0 ** 2 * (1 + 1j * zeta))))
k0c = float(np.abs(analytic(0.0) - A0).max() / np.abs(A0).max())
st = S.Stepper(np.zeros((N, N)), sig, dx, dz); rows = []
def record(step, A):
    z = step * dz; Aa = analytic(z); na = np.linalg.norm(Aa[useful])
    rows.append(dict(z_m=z, E=float(np.linalg.norm((A - Aa)[useful]) / na),
        Pu_num=float((np.abs(A[useful]) ** 2).sum() * d2), Pu_an=float((np.abs(Aa[useful]) ** 2).sum() * d2),
        P_total_num=float((np.abs(A) ** 2).sum() * d2), P_band_an=float((np.abs(Aa[band]) ** 2).sum() * d2)))
A = A0.copy(); record(0, A)
for s in range(1, total + 1):
    A = st.step(A)
    if s % every == 0: record(s, A)
od = os.path.join(HERE, "v9_d3_out"); os.makedirs(od, exist_ok=True)
json.dump(dict(tag=tag, w0_um=w0 * 1e6, x0_um=x0 * 1e6, y0_um=y0 * 1e6, dom_um=dom * 1e6, frac=frac, dx_um=dx * 1e6, N=N,
               P0=P0, k0c=k0c, rows=rows, runtime_s=round(time.time() - T0, 1)), open(os.path.join(od, tag + ".json"), "w"))
print(tag, "ok", round(time.time() - T0, 1), flush=True)
