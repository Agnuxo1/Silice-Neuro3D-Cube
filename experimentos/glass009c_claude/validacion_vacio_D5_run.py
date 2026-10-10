"""GLASS-009c-VACIO D5. Runner de una corrida en vacio (dn=0), theta=0, con w0 y absorbente parametrizados.

Uso: python -B validacion_vacio_D5_run.py W0_um THETA DOM_um DX_um FRAC P DZ_um TOTAL EVERY TAG
Ej.:  python -B validacion_vacio_D5_run.py 6 0 256 0.5 0.2 4 2.5 800 40 W6_d256_base

- Mismo codigo fisico que validacion_vacio_D3_run.py (CONTRATO-HAZ-COLA-D5-r5.md): solver adi2d.py de
  ../glass009_claude sin cambios, absorbente sigma = 4e4 * max((e-(1-FRAC))/FRAC, 0)**P, e = max(|x|,|y|)/(N dx/2).
- Referencia analitica sin frontera: la de 009c (CONTRATO.md), con w0 del argumento.
- Muestreo cada EVERY pasos, instante z = step*dz. Una sola corrida por proceso.
- Solo escribe en D5_out/ de esta carpeta. Temporales en D:.
"""
import os, sys, json, time, hashlib
os.environ["OMP_NUM_THREADS"] = "1"; os.environ["OPENBLAS_NUM_THREADS"] = "1"
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "glass009_claude"))
import numpy as np
import adi2d as S  # solver bajo prueba (009c), sin cambios

T0 = time.time()
w0 = float(sys.argv[1]) * 1e-6; theta = float(sys.argv[2])
dom = float(sys.argv[3]) * 1e-6; dx = float(sys.argv[4]) * 1e-6
frac = float(sys.argv[5]); p = float(sys.argv[6]); dz = float(sys.argv[7]) * 1e-6
total = int(sys.argv[8]); every = int(sys.argv[9]); tag = sys.argv[10]
SMAX = 4e4; RU = 40e-6
assert total % every == 0

N = int(round(dom / dx)); kt = S.b0 * theta; d2 = dx * dx; zR = S.b0 * w0 ** 2 / 2
x, y = S.coords(N, dx); R = np.hypot(x, y); useful = R < RU
e = np.maximum(np.abs(x), np.abs(y)) / (N * dx / 2)
band = e > (1 - frac)
sig = SMAX * np.maximum((e - (1 - frac)) / frac, 0) ** p

A0 = S.gaussian(N, dx, w0, 0.0, kt); N0 = A0[N // 2, N // 2].real
P0 = float((np.abs(A0) ** 2).sum() * d2)


def analytic(z):
    zeta = z / zR; xs = kt * z / S.b0
    return N0 / (1 + 1j * zeta) * np.exp(-(((x - xs) ** 2 + y * y) / (w0 ** 2 * (1 + 1j * zeta)))) \
        * np.exp(1j * kt * x) * np.exp(-1j * kt ** 2 * z / (2 * S.b0))


# K0b: sigma del runner frente a adi2d.sigma_map (p = 4)
sig_ref = S.sigma_map(N, dx, SMAX, frac)
sigma_diff_rel = float(np.abs(sig - sig_ref).max() / SMAX) if int(round(p)) == 4 else None
# K0c: el analitico en z=0 coincide con A(0)
k0c = float(np.abs(analytic(0.0) - A0).max() / np.abs(A0).max())

st = S.Stepper(np.zeros((N, N)), sig, dx, dz)
rows = []


def record(step, A):
    z = step * dz; Aa = analytic(z); na = np.linalg.norm(Aa[useful])
    rows.append(dict(z_m=z, step=step,
                     E=float(np.linalg.norm((A - Aa)[useful]) / na),
                     Pu_num=float((np.abs(A[useful]) ** 2).sum() * d2),
                     Pu_an=float((np.abs(Aa[useful]) ** 2).sum() * d2),
                     P_total_num=float((np.abs(A) ** 2).sum() * d2),
                     P_band_an=float((np.abs(Aa[band]) ** 2).sum() * d2),
                     P_band_num=float((np.abs(A[band]) ** 2).sum() * d2)))


A = A0.copy()
record(0, A)
for s in range(1, total + 1):
    A = st.step(A)
    if s % every == 0:
        record(s, A)

outd = os.path.join(HERE, "D5_out"); os.makedirs(outd, exist_ok=True)
res = dict(tag=tag, w0_um=w0 * 1e6, theta_rad=theta, domain_um=N * dx * 1e6, dx_um=dx * 1e6, dz_um=dz * 1e6,
           N=N, frac=frac, p=p, smax=SMAX, band_start_e=1 - frac, useful_radius_um=RU * 1e6,
           total_steps=total, every=every, zR_um=zR * 1e6, P0=P0, b0=S.b0,
           K0b_sigma_maxdiff_rel=sigma_diff_rel, K0c_analytic0_rel=k0c, rows=rows,
           adi2d_sha256=hashlib.sha256(open(os.path.join(HERE, "..", "glass009_claude", "adi2d.py"), "rb").read()).hexdigest(),
           runner_sha256=hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest(),
           runtime_s=round(time.time() - T0, 2))
json.dump(res, open(os.path.join(outd, f"{tag}.json"), "w"), indent=1)
print(tag, "ok", res["runtime_s"], "s", "N", N, flush=True)
