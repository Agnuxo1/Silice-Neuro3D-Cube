"""Tarea H3: re-propagacion de 009d (Cd, T96d) con el mismo solver y perfil de 009d; de cada campo
final se calculan tres observables de potencia en el nucleo:
  P16  = convencion de 009d (submuestreo 16x16 en la celda; reproduce resultados009d.json: R0)
  P64  = cobertura de H1 (celdas de frontera 64x64)
  Pc   = original (indicador en el centro de la celda)
Uso: python -B h3_run_009d.py PERFIL DX_um [trozo]   PERFIL in Cd, T96d. Un hijo por invocacion.
Solo cambia el observable; el perfil, el solver (adi2d.py de glass009_claude, sin copiar) y la malla no cambian.
"""
import os, sys, json, time, math, hashlib
os.environ["OMP_NUM_THREADS"] = "1"; os.environ["OPENBLAS_NUM_THREADS"] = "1"
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "glass009_claude"))
import numpy as np
from adi2d import gaussian, sigma_map, Stepper
import observable_cobertura as oc

T0 = time.time()
kind = sys.argv[1]; dx = float(sys.argv[2]) * 1e-6
chunk = int(sys.argv[3]) if len(sys.argv) > 3 else 0
N = int(round(128e-6 / dx)); dz = 2.5e-6; DN = -0.003
tag = f"{kind}_dx{int(round(dx * 1e7))}"
outdir = os.path.join(HERE, "out")
os.makedirs(outdir, exist_ok=True)

cov = oc.modified_mask_cov(N, dx, kind, ss=16)     # perfil de 009d por cobertura (ss16)
dn = DN * cov
sig = sigma_map(N, dx)
st = Stepper(dn, sig, dx, dz)
per = 400 if dx < 0.45e-6 else 800
sf = os.path.join(outdir, f"state_{tag}.npy")
A = gaussian(N, dx, 6e-6) if chunk == 0 else np.load(sf)
for _ in range(per):
    A = st.step(A)
np.save(sf, A)
fin = (chunk + 1) * per >= 800
d = dict(kind=kind, dx_um=dx * 1e6, N=N, domain_um=N * dx * 1e6, chunk=chunk,
         steps_done=(chunk + 1) * per, final=fin,
         adi2d_sha256=hashlib.sha256(open(os.path.join(HERE, "..", "glass009_claude", "adi2d.py"), "rb").read()).hexdigest(),
         observable_cobertura_sha256=hashlib.sha256(open(os.path.join(HERE, "observable_cobertura.py"), "rb").read()).hexdigest())
if fin:
    w16 = oc.disk_coverage_uniform(N, dx, ss=16)
    w64 = oc.disk_coverage(N, dx, ss=64)
    d["P16_009d_convention"] = oc.obs_cov(A, w16, dx)
    d["P64_cobertura_H1"] = oc.obs_cov(A, w64, dx)
    d["Pc_centro_original"] = oc.obs_center(A, dx)
    d["int_abs_dn_over_abs_DN_dx2"] = float(np.abs(dn).sum() * dx * dx / abs(DN))   # diagnostico (no es Q1)
    d["P_total_remaining_sum_abs2_dx2"] = float((np.abs(A) ** 2).sum() * dx * dx)   # potencia total tras la esponja
d["elapsed_s"] = round(time.time() - T0, 3)
name = os.path.join(outdir, f"h3_{tag}" + (f"_c{chunk}" if dx < 0.45e-6 else "") + ".json")
json.dump(d, open(name, "w"), indent=1)
print(json.dumps(d))
