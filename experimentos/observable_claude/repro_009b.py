"""Reproduccion independiente de los casos continuos (Cw) y de 96 trazos escalonados (T96w) de 009b,
con el perfil escalonado de 009b (mascara de centros de pixel, sin ponderar) y el solver de 009
(adi2d.py, sin copiar). Calcula el observable de 009b (ponderado 16x16) y el original (centro).
Sirve para comprobar las cifras de out de 009b (campos weighted y unweighted) y para la sensibilidad
al observable de P2 y P3 de 009b. Uso: python -B repro_009b.py Cw|T96w DX_um [trozo]
"""
import os, sys, json, time, math, hashlib
os.environ["OMP_NUM_THREADS"] = "1"; os.environ["OPENBLAS_NUM_THREADS"] = "1"
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "glass009_claude"))
import numpy as np
from adi2d import gaussian, sigma_map, Stepper, coords
import observable_cobertura as oc

T0 = time.time(); A0 = 6e-6
kind = sys.argv[1]; dx = float(sys.argv[2]) * 1e-6; chunk = int(sys.argv[3]) if len(sys.argv) > 3 else 0
N = int(round(128e-6 / dx)); dz = 2.5e-6
tag = f"{kind}_dx{int(round(dx * 1e7))}"
outdir = os.path.join(HERE, "out")
os.makedirs(outdir, exist_ok=True)

def centres():
    cs = []
    for k, rad in enumerate([7.25e-6, 9e-6, 10.75e-6]):
        off = math.pi / 32 if k % 2 else 0
        for j in range(32):
            an = 2 * math.pi * j / 32 + off
            cs.append((rad * math.cos(an), rad * math.sin(an)))
    return cs

x, y = coords(N, dx); r = np.hypot(x, y); ring = (r >= A0) & (r < A0 + 6e-6)
if kind == "Cw":
    dn = np.where(ring, -0.003, 0.0)
else:
    m = np.zeros_like(x, bool)
    for cx, cy in centres():
        m |= (x - cx) ** 2 + (y - cy) ** 2 <= (1.25e-6) ** 2
    dn = np.where(m & ring, -0.003, 0.0)

sig = sigma_map(N, dx); st = Stepper(dn, sig, dx, dz)
per = 400 if dx < 0.45e-6 else 800
sf = os.path.join(outdir, f"repro_state_{tag}.npy")
A = gaussian(N, dx, 6e-6) if chunk == 0 else np.load(sf)
for _ in range(per):
    A = st.step(A)
np.save(sf, A)
fin = (chunk + 1) * per >= 800
d = dict(case=kind, dx_um=dx * 1e6, N=N, chunk=chunk, steps_done=(chunk + 1) * per, final=fin,
         adi2d_sha256=hashlib.sha256(open(os.path.join(HERE, "..", "glass009_claude", "adi2d.py"), "rb").read()).hexdigest())
if fin:
    w16 = oc.disk_coverage_uniform(N, dx, ss=16)
    d["weighted_16x16"] = oc.obs_cov(A, w16, dx)
    d["unweighted_center"] = oc.obs_center(A, dx)
d["elapsed_s"] = round(time.time() - T0, 3)
name = os.path.join(outdir, f"repro009b_{tag}" + (f"_c{chunk}" if dx < 0.45e-6 else "") + ".json")
json.dump(d, open(name, "w"), indent=1)
print(json.dumps(d))
