"""V9: aplica la metrica M y el K2 del contrato D3 (mismas formulas) a otros datos iniciales. Solo lee v9_d3_out/ y D3_out/."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
def load(p): return json.load(open(p))
def M_of(d, zmin_late=None):
    rows = d["rows"]; P0 = d["P0"]
    arr = [r["z_m"] for r in rows if r["P_band_an"] > 1e-4 * P0]
    if not arr: return None
    zarr = min(arr)
    W = [r for r in rows if r["z_m"] >= zarr - 1e-15]
    dp = [abs(r["Pu_num"] - r["Pu_an"]) / P0 for r in W]
    late = [abs(r["Pu_num"] - r["Pu_an"]) / P0 for r in rows if r["z_m"] * 1e3 >= 1.0 - 1e-9]
    return dict(M=max(dp), z_arr=zarr * 1e3, M_late=max(late), M_at_zarr=dp[0])
def gm(rs): return math.exp(sum(math.log(r) for r in rs) / len(rs))
def factors(M, w_lo, w_hi, key="M"):
    rA = [M[(w_hi, dom, ab)][key] / M[(w_lo, dom, ab)][key] for dom in (128, 256) for ab in ("base", "ancho")]
    rB = [M[(w, 256, ab)][key] / M[(w, 128, ab)][key] for w in (w_lo, w_hi) for ab in ("base", "ancho")]
    rC = [M[(w, dom, "ancho")][key] / M[(w, dom, "base")][key] for w in (w_lo, w_hi) for dom in (128, 256)]
    out = {}
    for n, rs in (("A", rA), ("B", rB), ("C", rC)):
        g = gm(rs); cons = all(r > 1 for r in rs) or all(r < 1 for r in rs)
        out[n] = dict(r=[round(r, 4) for r in rs], GM=round(g, 4), consistent=cons, strong=bool(cons and (g >= 2 or g <= .5)))
    st = [k for k, v in out.items() if v["strong"]]
    out["dominante"] = max(st, key=lambda k: abs(math.log(out[k]["GM"]))) if st else "ninguno"
    return out
res = {}
for grp, wl, wh, pre in (("S0_original", 2, 4, None), ("S1_w3_w5", 3, 5, "s1_w{w}_d{d}_{a}"), ("S2_desplazado_w2_w4", 2, 4, "s2_w{w}_d{d}_{a}")):
    M = {}
    for w in (wl, wh):
        for d in (128, 256):
            for a in ("base", "ancho"):
                p = os.path.join(HERE, "..", "glass009c_claude", "D3_out", f"w{w}_d{d}_{a}.json") if pre is None else os.path.join(HERE, "v9_d3_out", pre.format(w=w, d=d, a=a) + ".json")
                if not os.path.exists(p): M = None; break
                M[(w, d, a)] = M_of(load(p))
            if M is None: break
        if M is None: break
    if M is None:
        res[grp] = "incompleto"; continue
    res[grp] = dict(M={f"w{k[0]}_d{k[1]}_{k[2]}": {kk: (round(vv, 6) if kk == 'z_arr' else float(f"{vv:.4e}")) for kk, vv in v.items()} for k, v in M.items()},
                    K2_pre_declarado_M=factors(M, wl, wh, "M"), K2_tardio_z_ge_1mm=factors(M, wl, wh, "M_late"),
                    K2_en_z_arr=factors(M, wl, wh, "M_at_zarr"))
json.dump(res, open(os.path.join(HERE, "v9_d3_resumen.json"), "w"), indent=1)
for g, v in res.items():
    if v == "incompleto": print(g, v); continue
    print(g); 
    for k in ("K2_pre_declarado_M", "K2_tardio_z_ge_1mm", "K2_en_z_arr"):
        f = v[k]; print("  ", k, "A GM", f["A"]["GM"], f["A"]["strong"], "| B GM", f["B"]["GM"], f["B"]["strong"], "| C GM", f["C"]["GM"], f["C"]["strong"], "| dominante", f["dominante"])
    print("   M:", {k: x["M"] for k, x in v["M"].items()})
