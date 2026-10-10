"""Genera RESULTADOS-tracks-r4.md a partir de resultados_tracks_r4.json (tablas generadas por codigo)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "resultados_tracks_r4.json"), encoding="utf-8"))
runs = R.get("runs", {})
crit = R.get("criteria", [])


def fmt(x, nd=10):
    return "null" if x is None else f"{x:.{nd}f}"


L_order = [60.0, 80.0, 100.0, 120.0]
lines = []
lines.append("# RESULTADOS tracks ronda 4 (F4: convergencia de caja, caso i)")
lines.append("")
lines.append("Modelo numerico escalar ideal. No es dispositivo, medida ni fabricacion. Contrato: `CONTRATO-tracks-r4.md`. "
             "Pass calculado por `run_tracks_r4.py eval`.")
lines.append("")
n_ok = sum(1 for r in runs.values() if r.get("n_core") is not None)
n_lig = sum(1 for r in runs.values() if r.get("ligado"))
n_eval = sum(1 for c in crit if c.get("evaluable"))
n_pass = sum(1 for c in crit if c.get("pass") is True)
lines.append(f"Estado: **{R.get('status')}**. Corridas: {len(runs)}, con n_eff: {n_ok}, ligadas: {n_lig}. "
             f"Criterios evaluados: {n_eval}/{len(crit)}, pass: {n_pass}.")
lines.append("")
lines.append("## Corridas (caso i, camisa continua n = 1,439; fondo y nucleo n = 1,444; lam = 1,55 um; s_sub = 8)")
lines.append("")
lines.append("| caso | h (um) | L (um) | K | incognitas | n_eff seleccionado | P(r<=12) | ligado | "
             "Delta n frente a L anterior (mismo h, K=30) | t (s) |")
lines.append("|---|---|---|---|---|---|---|---|---|---|")
prev = {}
for key in sorted(runs, key=lambda k: (runs[k]["h_um"], runs[k]["K"], runs[k]["L_um"])):
    r = runs[key]
    dn = ""
    if r["K"] == 30:
        hk = r["h_um"]
        if hk in prev and r["n_core"] is not None and prev[hk][1] is not None and r["L_um"] > prev[hk][0]:
            dn = f"{r['n_core'] - prev[hk][1]:+.3e}"
        prev[hk] = (r["L_um"], r["n_core"])
    pin = "null" if r["P_in_sel"] is None else f"{r['P_in_sel']:.4f}"
    lines.append(f"| i | {r['h_um']:g} | {r['L_um']:g} | {r['K']} | {r['unknowns']} | {fmt(r['n_core'])} | "
                 f"{pin} | {'si' if r['ligado'] else 'no'} | {dn} | {r['time_s']} |")
lines.append("")
lines.append("## Sucesion n_eff(L) con h = 0,25 y K = 30")
lines.append("")
lines.append("| L (um) | n_eff | Delta n frente a L anterior | P(r<=12) |")
lines.append("|---|---|---|---|")
p_prev = None
for L in L_order:
    r = runs.get(f"i|L{L:g}|h0.25|K30")
    if r is None:
        lines.append(f"| {L:g} | no calculada | - | - |")
        continue
    d = "" if p_prev is None or r["n_core"] is None else f"{r['n_core'] - p_prev:+.3e}"
    pin = "null" if r["P_in_sel"] is None else f"{r['P_in_sel']:.4f}"
    lines.append(f"| {L:g} | {fmt(r['n_core'])} | {d} | {pin} |")
    p_prev = r["n_core"]
lines.append("")
lines.append("## Diagnostico de seleccion (datos guardados por corrida, sin recalcular)")
lines.append("")
lines.append("| corrida | max P(r<=12) entre los K modos | indice del max | n del modo mas cercano a sigma | P de ese modo |")
lines.append("|---|---|---|---|---|")
SIG = 1.44219587036024
for key in sorted(runs, key=lambda k: (runs[k]["h_um"], runs[k]["K"], runs[k]["L_um"])):
    r = runs[key]
    Pk = r.get("P_in_first_K") or []
    if Pk:
        imax = max(range(len(Pk)), key=lambda i: Pk[i])
        pmax = f"{Pk[imax]:.4f}"
    else:
        imax, pmax = "-", "-"
    top = r.get("n_top8") or []
    if top:
        j = min(range(len(top)), key=lambda i: abs(top[i] - SIG))
        near = f"{top[j]:.10f} (indice {j} entre los 8 primeros)"
        pn = f"{Pk[j]:.4f}" if j < len(Pk) else "-"
    else:
        near, pn = "-", "-"
    lines.append(f"| {key} | {pmax} | {imax} | {near} | {pn} |")
lines.append("")
lines.append("## Criterios (pass calculado por el codigo)")
lines.append("")
lines.append("| id | descripcion | pass | evaluable | valor |")
lines.append("|---|---|---|---|---|")
for c in crit:
    v = json.dumps(c.get("value"), ensure_ascii=False, default=float)
    if len(v) > 300:
        v = v[:297] + "..."
    lines.append(f"| {c['id']} | {c['description']} | {c['pass']} | {c['evaluable']} | `{v}` |")
lines.append("")
lines.append("## Notas de estado (fijadas antes de calcular o de origen declarado)")
lines.append("")
lines.append("- Lo calculado: n_eff, P(r<=12), las diferencias de la tabla y los criterios de la tabla. "
             "Lo supuesto: sigma de la ronda 1, geometria, umbrales (contrato r4, seccion 3).")
lines.append("- Reproduccion: L = 60, h = 0,25, K = 30 da n_eff = 1,442189101534691, igual que la ronda 1 "
             "(K = 60). El modo seleccionado tiene otro indice (15 frente a 5) con el mismo n_eff.")
n80 = (runs.get("i|L80|h0.25|K30") or {}).get("n_core")
n120 = (runs.get("i|L120|h0.25|K30") or {}).get("n_core")
if n80 is not None and n120 is not None:
    lines.append(f"- Informativo (no es F4-C1, porque L = 100 no tiene modo ligado): n(L=120) - n(L=80) = {n120 - n80:+.4e} "
                 f"(h = 0,25, K = 30). Este par no se usa como criterio de convergencia.")
lines.append("- L = 100, K = 30: ningun modo de los 30 mas cercanos a sigma alcanza P(r<=12) >= 0,5; el maximo es 0,4332 "
             "(indice 13). Con la regla del contrato, la corrida queda 'no ligada' y n_core = null. "
             "F4-C1 no se puede evaluar: falta el L = 100 en el protocolo fijado.")
lines.append("- Diagnostico K = 60 en L = 100: fila 'L100|h0.25|K60' de la tabla de corridas, si existe. Es una desviacion "
             "de protocolo declarada (mas modos), solo informativa; no sustituye a F4-C1.")
lines.append("- Trazos (F4(d)): no ejecutados. F4-C1 no pasa ni se puede evaluar, asi que el limite de caja queda declarado y no se siguen los trazos.")
lines.append("- No afirmo vectorial, perdidas, fabricacion ni convergencia mas alla de L = 120 um.")
lines.append("")
open(os.path.join(HERE, "RESULTADOS-tracks-r4.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("md ok")
