"""V7-B2: recalcula la longitud de transferencia (G3 de B2) con otro dz. Usa bpm_r2 (solo lectura) y kappa_FD de resultados_g1_g2.json.
Uso: python -B v7_b2.py <d> <dz>"""
import json, pathlib, sys, time
import numpy as np
EXP = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(EXP / "bpm_claude")); sys.path.insert(0, str(EXP / "solver2d_claude"))
import bpm_r2 as B
import run_g3_r2 as G
d = float(sys.argv[1]); dz = float(sys.argv[2])
t0 = time.time()
kap = json.loads((EXP / "acoplador_claude" / "resultados_g1_g2.json").read_text(encoding="utf-8"))
kappa = float(kap["G1_main_h0125"][f"{d}"]["kappa_FD_per_um"])
Lc = np.pi / (2 * kappa)
psiL, _ = G.mode_single(-d / 2, d); psiR, _ = G.mode_single(d / 2, d)
x = B.axis(G.W, G.H)
n2 = B.cell_n2(x, G.H, [-d / 2, d / 2])
zend = 1.1 * Lc
rec, _ = B.propagate(n2, psiL, G.H, dz, zend, G.W, G.S0, G.WCAP, G.R0, {"R": psiR, "A0": psiL}, cap=True)
z = np.array(rec.z)
P2 = np.abs(np.array(rec.ip["R"])) ** 2 / (rec.norms["R"] * rec.P[0])
fm = G.first_local_max(z, P2)
err = (fm["z_um"] - Lc) / Lc
out = dict(d=d, dz=dz, kappa_FD_per_um=kappa, Lc_um=Lc, zmax_um=fm["z_um"], P2max=fm["P2_max"], err_rel=err,
           pass_10pct=bool(abs(err) <= 0.10), loss_end=rec.loss_at(zend), t_s=time.time() - t0)
pathlib.Path(__file__).with_name(f"v7_b2_d{int(d)}_dz{dz}.json").write_text(json.dumps(out, indent=1))
print(out, flush=True)
