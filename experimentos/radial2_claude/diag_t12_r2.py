"""Diagnostico (ronda 2): por que la busqueda de ronda 1 no encuentra la raiz a=6, t=12, dn=-0.003.
Solo lectura del solver radial2; no modifica resultados."""
import os, sys
os.environ["OMP_NUM_THREADS"] = "1"
sys.dont_write_bytecode = True
import numpy as np
import warnings
warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import radial2 as R

a, t, dn = 6e-6, 12e-6, -0.003
layers = [(0.0, a, 0.0), (a, a + t, dn)]
h = 0.005e-6
# 1) seccion de |F| en Im = 8.5 y Re alrededor de -6138 (sin usar ECS)
re = np.linspace(R.K0 * dn, -1.0, 150)
im = np.linspace(-100, 600, 141)
G = (re[:, None] + 1j * im[None, :]).ravel()
F = R.Fc(G, layers, 0, h).reshape(150, 141)
A = np.abs(F)
i, j = np.unravel_index(np.argmin(A), A.shape)
print("min |F| en malla gruesa:", A[i, j], "en Re", re[i], "Im", im[j])
# minimos locales en malla gruesa
P = np.pad(A, 1, constant_values=np.inf)
is_min = np.ones_like(A, dtype=bool)
for di in (-1, 0, 1):
    for dj in (-1, 0, 1):
        if di == 0 and dj == 0: continue
        is_min &= A <= P[1 + di:1 + di + 150, 1 + dj:1 + dj + 141]
idx = np.argwhere(is_min)
vals = A[idx[:, 0], idx[:, 1]]
o = np.argsort(vals)[:12]
print("n minimos locales gruesos:", len(idx))
for k in o:
    ii, jj = idx[k]
    print("  min local Re=%.2f Im=%.2f |F|=%.4e" % (re[ii], im[jj], vals[k]))
# 2) zoom fino alrededor del minimo grueso mas bajo (diagnostico)
rf = np.linspace(re[i] - 2 * (re[1]-re[0]), re[i] + 2 * (re[1]-re[0]), 81)
imf = np.linspace(max(-100, im[j] - 20), im[j] + 20, 81)
GF = (rf[:, None] + 1j * imf[None, :]).ravel()
FF = R.Fc(GF, layers, 0, h).reshape(81, 81)
AF = np.abs(FF)
ii, jj = np.unravel_index(np.argmin(AF), AF.shape)
print("zoom: min |F|=%.4e en Re=%.4f Im=%.4f" % (AF[ii, jj], rf[ii], imf[jj]))
# 3) secante desde el minimo del zoom
g = rf[ii] + 1j * imf[jj]
out, info = R.quasibound_roots(layers, a, 0, h, dn)
print("ronda1 quasibound_roots:", info, [(complex(o['g']), o['rF']) for o in out])
