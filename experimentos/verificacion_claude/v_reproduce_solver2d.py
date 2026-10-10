import sys, json, numpy as np
sys.dont_write_bytecode = True
sys.path.insert(0, "../solver2d_claude"); sys.path.insert(0, "../acoplo_claude")
import solver2d as S2, acoplo_paralelo as AP
k0 = 2*np.pi/1.55
out = []
for d, h, L, s in ((14.0, 0.125, 40.0, 8), (20.0, 0.125, 40.0, 8), (14.0, 0.2, 40.0, 16), (16.0, 0.15, 40.0, 16), (20.0, 0.1, 40.0, 16), (20.0, 0.2, 40.0, 1)):
    sh = [{"kind":"disk","x0":-d/2,"y0":0.0,"r":6.0,"n":1.444},{"kind":"disk","x0":d/2,"y0":0.0,"r":6.0,"n":1.444}]
    r = S2.solve(sh, 1.439, 1.55, L, h, n_modes=2, s_sub=s)
    k = k0*(r["neff"][0]-r["neff"][1])/2; km = AP.kappa(d)
    rec = {"d": d, "h": h, "s_sub": s, "kappa_FD": k, "ratio": k/km}
    out.append(rec); print(rec, flush=True)
json.dump(out, open("v_reproduce_solver2d.json","w"), indent=1)
