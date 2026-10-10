"""GLASS-009c-VACIO. Runner de una corrida en vacio (dn=0) con absorbente parametrizado.

Uso: python -B validacion_vacio_run.py THETA DOM_um DX_um FRAC P DZ_um TOTAL PASOS_TROZO TROZO
Ej.:  python -B validacion_vacio_run.py 0.02 128 0.5 0.2 4 2.5 800 400 0

- Solver bajo prueba: adi2d.py de ../glass009_claude (el mismo que 009c), sin copiar src/silice/.
- Absorbente: sigma = SMAX * max((e-(1-FRAC))/FRAC, 0)**P, e = max(|x|,|y|)/(N dx/2). Con FRAC=0.2, P=4 es el de 009c.
- Referencia analitica sin frontera: la misma de 009c (CONTRACT.md).
- Un hijo ejecuta PASOS_TROZO pasos (<30 s); el estado va a vacio_estados/ entre trozos.
- Muestreo cada 40 pasos (dz=2,5 um -> 20 instantes), como 009c.
"""
import os, sys, json, time, math, hashlib
os.environ["OMP_NUM_THREADS"] = "1"; os.environ["OPENBLAS_NUM_THREADS"] = "1"
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "glass009_claude"))
import numpy as np
import adi2d as S  # solver bajo prueba (009c)

T0 = time.time()
theta = float(sys.argv[1]); dom = float(sys.argv[2]) * 1e-6; dx = float(sys.argv[3]) * 1e-6
frac = float(sys.argv[4]); p = float(sys.argv[5]); dz = float(sys.argv[6]) * 1e-6
total = int(sys.argv[7]); per = int(sys.argv[8]); chunk = int(sys.argv[9])
SMAX = float(os.environ.get("VACIO_SMAX", "4e4")); w0 = 6e-6; RU = 40e-6; every = 40  # VACIO_SMAX=0 -> control sin esponja
assert total % per == 0 and per % every == 0
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

tag = f"th{int(round(theta * 1000)):03d}_dom{int(round(dom * 1e6))}_dx{int(round(dx * 1e8)):03d}_f{int(round(frac * 100)):02d}_p{int(round(p))}"  # dxNNN = NNN x 0,01 um
if SMAX == 0:
    tag += "_sin_esponja"
est = os.path.join(HERE, "vacio_estados"); outd = os.path.join(HERE, "vacio_out")
os.makedirs(est, exist_ok=True); os.makedirs(outd, exist_ok=True)
sf = os.path.join(est, f"state_{tag}.npy"); rf = os.path.join(est, f"rows_{tag}.json")

if chunk == 0:
    assert np.abs(analytic(0.0) - A0).max() < 1e-9 * np.abs(A0).max()  # K0c
    A = A0; rows = []
else:
    A = np.load(sf); rows = json.load(open(rf))

st = S.Stepper(np.zeros((N, N)), sig, dx, dz)

def record(step, A):
    z = step * dz; Aa = analytic(z); na = np.linalg.norm(Aa[useful])
    rows.append(dict(z_m=z, step=step,
                     E=float(np.linalg.norm((A - Aa)[useful]) / na),
                     Pu_num=float((np.abs(A[useful]) ** 2).sum() * d2),
                     Pu_an=float((np.abs(Aa[useful]) ** 2).sum() * d2),
                     P_total_num=float((np.abs(A) ** 2).sum() * d2),
                     P_band_an=float((np.abs(Aa[band]) ** 2).sum() * d2),
                     P_band_num=float((np.abs(A[band]) ** 2).sum() * d2)))

base = chunk * per
if chunk == 0:
    record(0, A)
for s in range(1, per + 1):
    A = st.step(A)
    if (base + s) % every == 0:
        record(base + s, A)
np.save(sf, A); json.dump(rows, open(rf, "w"))
fin = (chunk + 1) * per >= total
if fin:
    arr = [r["z_m"] for r in rows if r["P_band_an"] > 1e-4 * P0]
    z_arr = min(arr) if arr else None
    res = dict(theta_rad=theta, domain_um=N * dx * 1e6, dx_um=dx * 1e6, dz_um=dz * 1e6, N=N, frac=frac, p=p, smax=SMAX,
               band_start_e=1 - frac, useful_radius_um=RU * 1e6, P0=P0, z_arr_m=z_arr, rows=rows,
               adi2d_sha256=hashlib.sha256(open(os.path.join(HERE, "..", "glass009_claude", "adi2d.py"), "rb").read()).hexdigest(),
               runner_sha256=hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest(),
               state_file=os.path.relpath(sf, HERE))
    json.dump(res, open(os.path.join(outd, f"{tag}.json"), "w"), indent=1)
print(tag, "trozo", chunk, "fin", fin, round(time.time() - T0, 2), "s")
