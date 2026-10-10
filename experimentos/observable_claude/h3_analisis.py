"""Tarea H3: lee out/h3_*.json (campos finales de 009d re-propagados) y evalua Q2, Q3, Q4 de 009d con
tres observables: P16 (convencion 009d), P64 (cobertura H1) y Pc (original, centro).
Criterios de 009d sin cambios. R0: P16 debe reproducir resultados009d.json.
Salida: out/h3_analisis.json y tabla por consola.
"""
import os, sys, json, hashlib
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
ref = json.load(open(os.path.join(HERE, "..", "glass009d_claude", "resultados009d.json")))

def load(kind, dxtag, chunk=None):
    name = f"h3_{kind}_dx{dxtag}" + (f"_c{chunk}" if chunk is not None else "") + ".json"
    return json.load(open(os.path.join(OUT, name)))

def P(kind, key):
    """key in P16_009d_convention, P64_cobertura_H1, Pc_centro_original"""
    out = {}
    for lab, dxtag, ch in [("0.5", "5", None), ("0.625", "6", None), ("0.4", "4", 1)]:
        d = load(kind, dxtag, ch)
        assert d["final"], (kind, lab)
        out[lab] = d[key]
    return out

def verdicts(p):
    d45 = abs(p["0.4"] - p["0.5"]); rel = d45 / p["0.5"]
    d50_625 = abs(p["0.5"] - p["0.625"])
    q2 = bool(d45 < 0.005 and rel < 0.10)
    q4 = bool(d50_625 >= d45)
    return dict(P=p, diff_04_05=d45, rel_04_05=rel, diff_05_0625=d50_625, Q_threshold_pass=q2, Q4_monotone=q4)

res = {}
for kind, qname in [("Cd", "Q2_continuo"), ("T96d", "Q3_96trazos")]:
    ref_k = ref[kind]
    refP = {"0.5": ref_k["P_dx0p5"], "0.625": ref_k["P_dx0p625"], "0.4": ref_k["P_dx0p4"]}
    row = {}
    for key, lab in [("P16_009d_convention", "P16"), ("P64_cobertura_H1", "P64"), ("Pc_centro_original", "Pc")]:
        row[lab] = verdicts(P(kind, key))
    row["R0_repro_P16_minus_009d"] = {k: row["P16"]["P"][k] - refP[k] for k in refP}
    row["ref_009d_recorded"] = dict(P=refP, Q_threshold_pass=bool(ref_k["Q23_PASS"]), Q4_monotone=bool(ref_k["Q4_monotone"]),
                                    diff_04_05=ref_k["diff_04_05"], diff_05_0625=ref_k["diff_05_0625"])
    res[kind] = row

# verdicts for Q2 (Cd) and Q3 (T96d) use the same threshold check; Q4 monotone for both
summary = {}
for kind, qname in [("Cd", "Q2_continuo"), ("T96d", "Q3_96trazos")]:
    summary[qname] = {lab: res[kind][lab]["Q_threshold_pass"] for lab in ["P16", "P64", "Pc"]}
    summary[qname]["009d_recorded"] = res[kind]["ref_009d_recorded"]["Q_threshold_pass"]
for kind, qname in [("Cd", "Q4_continuo"), ("T96d", "Q4_96trazos")]:
    summary[qname] = {lab: res[kind][lab]["Q4_monotone"] for lab in ["P16", "P64", "Pc"]}
    summary[qname]["009d_recorded"] = res[kind]["ref_009d_recorded"]["Q4_monotone"]

R0_max = max(abs(v) for kind in ["Cd", "T96d"] for v in res[kind]["R0_repro_P16_minus_009d"].values())
out = dict(
    tarea="H3",
    observable_cobertura_sha256=hashlib.sha256(open(os.path.join(HERE, "observable_cobertura.py"), "rb").read()).hexdigest(),
    R0_max_abs_diff_P16_vs_009d=R0_max,
    R0_PASS=bool(R0_max < 1e-9),
    detalle=res,
    resumen_veredictos=summary,
)
json.dump(out, open(os.path.join(OUT, "h3_analisis.json"), "w"), indent=1)

print("R0 max |P16 - 009d| =", R0_max, "PASS" if R0_max < 1e-9 else "FAIL")
for kind in ["Cd", "T96d"]:
    for lab in ["P16", "P64", "Pc"]:
        r = res[kind][lab]
        print(kind, lab, {k: round(v, 9) for k, v in r["P"].items()},
              "d45=%.4e rel=%.4e d50_625=%.4e Qthr=%s Q4=%s" % (r["diff_04_05"], r["rel_04_05"], r["diff_05_0625"], r["Q_threshold_pass"], r["Q4_monotone"]))
    print(kind, "009d recorded", res[kind]["ref_009d_recorded"]["P"], "Qthr", res[kind]["ref_009d_recorded"]["Q_threshold_pass"], "Q4", res[kind]["ref_009d_recorded"]["Q4_monotone"])
print(json.dumps(summary, indent=1))
