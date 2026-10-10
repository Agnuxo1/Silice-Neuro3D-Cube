import numpy as np, json
import v8_bpm as B
out = {}
for W, s0 in ((40.0, 28.0), (60.0, 48.0)):
    h = 0.2; M = int(round(W/h)); x = (np.arange(2*M+1)-M)*h
    n2 = B.cell_n2(x, h); pa, na, u, w, V = B.lp01(x); pf, nf = B.fd_mode(n2, h)
    G = B.cap(x, s0, 12.0, 0.5)
    r = {}
    for nm, ps in (("an", pa), ("fd", pf)):
        g = float((G*ps**2).sum()/(ps**2).sum()/(B.K0*B.NREF))
        r[nm] = dict(rate_per_um=g, loss_1mm=1-np.exp(-g*1000))
    X, Y = np.meshgrid(x, x, indexing="ij"); s = np.maximum(abs(X), abs(Y))
    r["tail28_frac_an"] = float((pa**2*(s > s0)).sum()/(pa**2).sum()); r["tail28_frac_fd"] = float((pf**2*(s > s0)).sum()/(pf**2).sum())
    r["neff_an"] = na; r["neff_fd"] = nf; r["dneff"] = nf-na
    r["ov2"] = float((pa*pf).sum()**2/((pa**2).sum()*(pf**2).sum())); r["u"] = u; r["w"] = w; r["V"] = V
    out[f"W{W:g}_s0{s0:g}"] = r; print(W, r, flush=True)
json.dump(out, open("v8_pert.json", "w"), indent=1)
