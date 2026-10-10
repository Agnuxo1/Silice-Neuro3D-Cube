"""Veredictos P2 y P3 de 009b (criterios sin cambios: |dP|<0,005 y <10 %) con el observable ponderado
16x16 (el de 009b) y con el original (centro). Lee las reproducciones de repro_009b.py y las compara
con resultados de 009b (leidos de su JSON, no recalculados).
"""
import os, sys, json, hashlib
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
ref = json.load(open(os.path.join(HERE, "..", "glass009b_claude", "resultados009b.json")))

def rp(case, dxtag, chunk=None):
    name = f"repro009b_{case}_dx{dxtag}" + (f"_c{chunk}" if chunk is not None else "") + ".json"
    return json.load(open(os.path.join(OUT, name)))

def pair(case):
    p5 = rp(case, 5)
    p4 = rp(case, 4, 1)
    assert p5["final"] and p4["final"]
    return {"0.5": {"w": p5["weighted_16x16"], "c": p5["unweighted_center"]},
            "0.4": {"w": p4["weighted_16x16"], "c": p4["unweighted_center"]}}

def verdict(p05, p04):
    d = abs(p04 - p05)
    return dict(P05=p05, P04=p04, diff=d, rel=d / p05, PASS=bool(d < 0.005 and d / p05 < 0.10))

res = {}
for case, key in [("Cw", "P2_continuo"), ("T96w", "P3_96trazos")]:
    p = pair(case)
    res[key] = dict(
        weighted_16x16=verdict(p["0.5"]["w"], p["0.4"]["w"]),
        center_original=verdict(p["0.5"]["c"], p["0.4"]["c"]),
        recorded_009b_weighted=ref[key]["PASS"],
        recorded_009b_weighted_diff=ref[key]["diff_w"],
        recorded_009b_center_diff=ref[key]["diff_u"],
        recorded_009b_center_PASS=bool(ref[key]["diff_u"] < 0.005 and ref[key]["diff_u"] / ref[key]["dx05_u"] < 0.10),
    )
out = dict(
    nota="Reproducciones propias (repro_009b.py) de los campos finales de 009b; criterios de 009b sin cambios.",
    observable_cobertura_sha256=hashlib.sha256(open(os.path.join(HERE, "observable_cobertura.py"), "rb").read()).hexdigest(),
    resultados=res,
)
json.dump(out, open(os.path.join(OUT, "analisis_009b.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
