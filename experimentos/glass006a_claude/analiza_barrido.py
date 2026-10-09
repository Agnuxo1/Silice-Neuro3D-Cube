"""Summary and predictions P-B1..P-B4 of CONTRATO-BARRIDO-MODAL.md (reads barrido/*.json)."""
import json, math, pathlib, sys
sys.stdout.reconfigure(encoding='utf-8')
HERE = pathlib.Path(__file__).resolve().parent
MESH = [500, 700, 900, 1100, 1400, 1800]
K = 2 * (10 / math.log(10)) * 0.01  # dB/cm per unit Im(gamma), as in run006a
recs = {}
for f in (HERE / "barrido").glob("a*_t*_dn*_N*.json"):
    r = json.loads(f.read_text(encoding="utf-8"))
    recs[(r["a_um"], r["t_um"], r["dn"], r["N"])] = r
cases = sorted({(k[0], k[1], k[2]) for k in recs}, key=lambda c: (c[0], c[2], c[1]))
summary, pb1, pb2, pb3, pb4 = [], [], [], [], []
for a, t, dn in cases:
    row = {"a_um": a, "t_um": t, "dn": dn, "selected_re": {}, "core": {}, "im": {}, "residual_max": 0.0}
    for N in MESH:
        r = recs[(a, t, dn, N)]
        s = r["selected"]
        row["selected_re"][N] = None if s is None else s["re"]
        row["core"][N] = None if s is None else s["core"]
        row["im"][N] = None if s is None else s["im"]
        if s is not None:
            row["residual_max"] = max(row["residual_max"], s["residual"])
    has_mode = all(row["selected_re"][N] is not None for N in MESH[2:])
    if (a, t) == (6.0, 3.0):
        pb1.append({"a": a, "t": t, "dn": dn, "mode_at_N>=900": any(row["selected_re"][N] is not None for N in MESH[2:]),
                    "pass": not any(row["selected_re"][N] is not None for N in MESH[2:])})
    if has_mode:
        a1, a2 = recs[(a, t, dn, 1400)]["selected"], recs[(a, t, dn, 1800)]["selected"]
        rel = abs(a2["re"] - a1["re"]) / abs(a2["re"])
        loss1, loss2 = K * a1["im"], K * a2["im"]
        absl = abs(loss2 - loss1); rell = absl / max(abs(loss2), 1e-30)
        g2 = rel < 0.01 and ((rell < 0.10) or absl < 0.005)
        pb2.append({"a": a, "t": t, "dn": dn, "re_rel_1400_1800": rel, "loss_rel": rell, "loss_abs": absl, "G2_pair": g2})
        cores = [row["core"][N] for N in MESH[2:]]
        pairs_ok = all(abs(recs[(a, t, dn, MESH[i+1])]["selected"]["re"] - recs[(a, t, dn, MESH[i])]["selected"]["re"])
                       / abs(recs[(a, t, dn, MESH[i+1])]["selected"]["re"]) < 0.01 for i in range(2, 5))
        stab = (max(cores) - min(cores) < 0.02) and pairs_ok
        pb3.append({"a": a, "t": t, "dn": dn, "core_spread_900_1800": max(cores) - min(cores), "pairs_lt_1pct": pairs_ok, "pass": stab})
    summary.append(row)
    pb4.append({"a": a, "t": t, "dn": dn, "residual_max": row["residual_max"], "pass": row["residual_max"] < 1e-8})
out = {"cases": summary, "P_B1_no_mode_t3": pb1, "P_B2_G2_pair": pb2, "P_B3_stability": pb3, "P_B4_residual": pb4}
(HERE / "barrido_resumen.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
print("P-B1 pass:", all(x["pass"] for x in pb1), [ (x['a'],x['t'],x['dn'],x['mode_at_N>=900']) for x in pb1])
print("P-B2 G2 pair: %d/%d" % (sum(x["G2_pair"] for x in pb2), len(pb2)))
print("P-B3 stability: %d/%d" % (sum(x["pass"] for x in pb3), len(pb3)))
print("P-B4 residual: %d/%d (max %.2e)" % (sum(x["pass"] for x in pb4), len(pb4), max(x["residual_max"] for x in pb4)))
for x in pb2:
    print("  a=%g t=%g dn=%g  Re rel %.3f%%  loss_rel %.2f%%  G2 %s" % (x["a"], x["t"], x["dn"], 100*x["re_rel_1400_1800"], 100*x["loss_rel"], x["G2_pair"]))
