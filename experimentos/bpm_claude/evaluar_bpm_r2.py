"""Evalua los criterios de CONTRATO-bpm-r2.md a partir de r2_runs/*.json y escribe resultados_bpm_r2.json.

pass se calcula aqui, con los umbrales fijados en el contrato. Si falta una corrida, su criterio queda sin evaluar.
Solo lectura de r2_runs/ y escritura de resultados_bpm_r2.json. Modelo numerico. Solo CPU.
"""
import datetime
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
RUNS = HERE / "r2_runs"
THR_V0, THR_C0, THR_D6, THR_LOSS, THR_REL = 1e-9, 1e-6, 1e-5, 1e-5, 0.10


def load(name):
    p = RUNS / f"{name}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


runs = {k: load(k) for k in ["v0", "base", "G0", "s0", "disc", "dz05", "W60", "W60c", "W80"]}
g3 = {d: load(f"g3_d{d}") for d in (14, 16)}

crit = []
sin_evaluar = []


def add(cid, desc, value, thr, passed):
    if passed is None:
        sin_evaluar.append(cid)
    crit.append({"id": cid, "description": desc, "value": value, "threshold": thr,
                 "pass": None if passed is None else bool(passed)})


def loss(name):
    r = runs.get(name)
    return None if r is None else r["perdida_1mm"]


def rel(a, ref):
    if a is None or ref is None or ref == 0:
        return None
    return abs(a - ref) / abs(ref)


# C0 y V0
neff_an = next((runs[k]["neff_analitico"] for k in runs if runs[k] is not None), None)
if neff_an is not None:
    c0 = abs(neff_an - 1.4421922)
    add("C0", "n_eff analitico |dif| vs 1,4421922 <= 1e-6", f"{c0:.3e} (n_eff={neff_an:.10f})", "1e-6", c0 <= THR_C0)
else:
    add("C0", "n_eff analitico |dif| vs 1,4421922 <= 1e-6", "no evaluado", "1e-6", None)
v0 = runs["v0"]
add("V0", "unitariedad sin CAP (200 um): max|P/P0-1| <= 1e-9",
    None if v0 is None else f"{v0['unitariedad_max_abs_P_over_P0_minus_1']:.3e}", "1e-9",
    None if v0 is None else v0["unitariedad_max_abs_P_over_P0_minus_1"] <= THR_V0)

# D6 autoestado discreto
disc = runs["disc"]
if disc is not None:
    d6 = abs(disc["neff_discreto"] - disc["neff_analitico"])
    add("D6", "autoestado discreto: |n_eff,disc - n_eff,analitico| <= 1e-5", f"{d6:.3e} (n_eff,disc={disc['neff_discreto']:.10f})",
        "1e-5", d6 <= THR_D6)
else:
    add("D6", "autoestado discreto: |n_eff,disc - n_eff,analitico| <= 1e-5", "no evaluado", "1e-5", None)

# D1 contorno
b, g0, s0c, dz5, w60, w60c, w80 = (runs[k] for k in ["base", "G0", "s0", "dz05", "W60", "W60c", "W80"])
L = {k: loss(k) for k in ["base", "G0", "s0", "disc", "dz05", "W60", "W60c", "W80"]}
d1_rel = rel(L["W80"], L["W60"]) if L["W80"] is not None and L["W60"] is not None else None
d1_val = None if d1_rel is None else abs(L["W80"] - L["W60"]) / L["W80"]
d1 = None if d1_val is None else d1_val <= THR_REL
add("D1", "contorno: |P_perd(W=80)-P_perd(W=60)|/P_perd(W=80) <= 0,10 (CAP relativo)",
    None if d1_val is None else f"{d1_val:.4f} (W60={L['W60']:.4e}, W80={L['W80']:.4e})", "0,10", d1)

d2_val = rel(L["G0"], L["base"])
d2 = None if d2_val is None else d2_val <= THR_REL
add("D2", "CAP amplitud: |P_perd(R0=0,05)-P_perd(R0=0,5)|/P_perd(R0=0,5) <= 0,10",
    None if d2_val is None else f"{d2_val:.4f} (G0 corto={L['G0']:.4e}, base={L['base']:.4e})", "0,10", d2)

d3_val = rel(L["s0"], L["base"])
d3 = None if d3_val is None else d3_val <= THR_REL
add("D3", "CAP posicion/ancho: |P_perd(s0=34,w=6)-P_perd(base)|/P_perd(base) <= 0,10",
    None if d3_val is None else f"{d3_val:.4f} (s0={L['s0']:.4e})", "0,10", d3)

d4_val = rel(L["dz05"], L["base"])
d4 = None if d4_val is None else d4_val <= THR_REL
add("D4", "paso dz: |P_perd(dz=0,5)-P_perd(dz=1)|/P_perd(dz=1) <= 0,10",
    None if d4_val is None else f"{d4_val:.4f} (dz=0,5: {L['dz05']:.4e})", "0,10", d4)

d5 = None if L["disc"] is None else L["disc"] <= THR_LOSS
add("D5", "dato discreto: P_perd(1 mm) <= 1e-5 (W=40, CAP base)",
    None if L["disc"] is None else f"{L['disc']:.4e}", "1e-5", d5)

# Regla R y B2.2
if d5:
    sel, sel_loss = "disc", L["disc"]
elif d1:
    sel, sel_loss = "W80", L["W80"]
else:
    sel, sel_loss = "base", L["base"]
b22 = None if sel_loss is None else sel_loss <= THR_LOSS
add("B2.2", f"B3 repetido con umbral 1e-5 en la configuracion seleccionada ({sel})",
    None if sel_loss is None else f"{sel_loss:.4e}", "1e-5", b22)

# Clasificacion de hipotesis
hip = []
if d2 is False or d3 is False:
    hip.append("H-CAP (la perdida depende de G0 o de s0/w)")
if d1 is False:
    hip.append("H-CONTORNO (la perdida depende del semiancho W)")
if d5 is True:
    hip.append("H-DATO (el dato discreto elimina la perdida)")
if d4 is False:
    hip.append("H-DZ (la perdida depende de dz)")
if d2 is True and d3 is True and d1 is True and d5 is not True and d4 is True:
    hip.append("ninguna de las cuatro explica la perdida con los datos actuales")

# G3
kap_info = {}
for d in (14, 16):
    r = g3[d]
    if r is None or r.get("z_max_mm") is None:
        add(f"G3.d{d}", f"G3 d={d} um: |z_max(P2)-L_c|/L_c <= 0,10",
            "no evaluado" if r is None else "no se detecto maximo en la ventana de propagacion", "0,10",
            None if r is None else False)
        continue
    e = r["error_rel_zmax_vs_Lc"]
    add(f"G3.d{d}", f"G3 d={d} um: |z_max(P2)-L_c|/L_c <= 0,10",
        f"z_max={r['z_max_mm']:.4f} mm, L_c={r['Lc_mm']:.4f} mm, error={e:+.4f}, P2max={r['P2_max_detectado']['P2_max']:.4f}",
        "0,10", abs(e) <= THR_REL)
    kap_info[str(d)] = {"Lc_mm": r["Lc_mm"], "z_max_mm": r["z_max_mm"], "error_rel": e}

g3_pass = None
if all(g3[d] is not None and g3[d].get("z_max_mm") is not None for d in (14, 16)):
    g3_pass = all(abs(g3[d]["error_rel_zmax_vs_Lc"]) <= THR_REL for d in (14, 16))
add("G3", "G3 global: ambos d (14 y 16) cumplen el 10 %", "ver G3.d14 y G3.d16", "0,10", g3_pass)

# Resumen de perdidas (informativo)
resumen = {k: (None if v is None else v) for k, v in L.items()}
status = "done" if not sin_evaluar else "partial"

out = {
    "fecha_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    "status": status,
    "sin_evaluar": sin_evaluar,
    "perdida_1mm_por_corrida": resumen,
    "regla_R_seleccion": sel,
    "hipotesis_con_evidencia": hip,
    "B2_2_pass": b22,
    "G3_zmax_vs_Lc": kap_info,
    "criterios": crit,
}
(HERE / "resultados_bpm_r2.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
for c in crit:
    print(f"{c['id']:>6} | pass={c['pass']} | {c['value']} | umbral {c['threshold']}")
print("status:", status, "seleccion:", sel, "sin_evaluar:", sin_evaluar)
