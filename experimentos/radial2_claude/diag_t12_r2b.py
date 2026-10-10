"""Diagnostico (ronda 2b): secante compleja desde varios semillas en la zona t=12, dn=-0.003. Solo lectura."""
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

def secant(g0, g1, n=200):
    F0 = R.Fc(np.array([g0]), layers, 0, h)[0]
    F1 = R.Fc(np.array([g1]), layers, 0, h)[0]
    hist = []
    for it in range(n):
        den = F1 - F0
        if den == 0: break
        g2 = g1 - F1 * (g1 - g0) / den
        g0, F0 = g1, F1
        g1 = g2
        F1 = R.Fc(np.array([g1]), layers, 0, h)[0]
        hist.append(abs(g1 - g0))
        if abs(g1 - g0) < 1e-10 * abs(g1) + 1e-9:
            break
    return g1, F1, it, (hist[-1] if hist else None)

seeds = [-6146.3 + 9j, -6138.1 + 8.56j, -6144 + 8j, -6130 + 12j, -6160 + 6j]
for s in seeds:
    for d in [(1.0, 1.0), (5.0, 3.0), (-5.0, 2.0)]:
        g, Fv, it, last = secant(s, s + complex(*d))
        _, F, psi, dpsi, f, fp = R.mismatch(np.array([g]), layers, 0, 'P', h, real_bound=False)
        rF = abs(F[0]) / (abs(dpsi[0] / psi[0]) + abs(fp[0] / f[0]))
        print("seed %s d=%s -> g=%.6f%+.6fj it=%d last_step=%s rF=%.3e" % (s, d, g.real, g.imag, it, last, rF))
