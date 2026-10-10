"""Evalua los criterios de CONTRATO-bpm-r5.md y escribe resultados_bpm_r5.json. Todos los pass los calcula este codigo.

Uso: python -B evaluar_bpm_r5.py   (lee r5_runs/*.json)
"""
import datetime
import json
import math
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
RUNS = HERE / "r5_runs"
UMBRAL_B3 = 1e-5
DZ_CASOS = [("dz1", 1.0), ("dz05", 0.5), ("dz025", 0.25), ("dz0125", 0.125)]
R4 = {1.0: 2.4600e-4, 0.5: 7.3692e-5}
LIMITE_MIN = 15.0 * 60.0


def load(name):
    p = RUNS / f"{name}.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def fmt(x):
    return "no definido" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.6e}"


def main():
    runs = {n: load(n) for n, _ in DZ_CASOS}
    unit = load("unit")
    pert = load("pert")
    P = {dz: runs[n]["perdida_1mm"] for n, dz in DZ_CASOS if runs[n] is not None}
    T = {dz: runs[n]["tiempo_propagacion_s"] for n, dz in DZ_CASOS if runs[n] is not None}
    crit = []

    def add(cid, desc, value, ok, nota=""):
        crit.append({"id": cid, "description": desc, "value": value, "pass": ok, "nota": nota})

    # V0, V1: controles frente a r4.
    for cid, dz in (("V0", 1.0), ("V1", 0.5)):
        if dz in P:
            rel = abs(P[dz] - R4[dz]) / R4[dz]
            add(cid, f"control dz={dz}: |P - r4| / r4 <= 1e-3",
                f"P={fmt(P[dz])}, rel={rel:.3e}", rel <= 1e-3)
        else:
            add(cid, f"control dz={dz}", "no evaluado", None)

    # V2: unitariedad sin CAP.
    if unit is not None:
        dev = unit["max_abs_P_over_P0_minus_1"]
        add("V2", "unitariedad sin CAP (dz=0,125, z<=100 um): max|P/P0-1| <= 1e-9",
            f"{dev:.3e}", dev <= 1e-9)
    else:
        add("V2", "unitariedad sin CAP", "no evaluado", None)

    # B3-r5 (criterio principal).
    cumplen = [dz for _, dz in DZ_CASOS if dz in P and P[dz] <= UMBRAL_B3]
    b3_ok = None if len(P) < len(DZ_CASOS) else len(cumplen) > 0
    dz_star = max(cumplen) if cumplen else None
    valores_b3 = ", ".join(f"dz={dz}: {fmt(P.get(dz))}" for _, dz in DZ_CASOS)
    add("B3-r5", "existe dz en {1,0,5,0,25,0,125} con P_perd(1 mm) <= 1e-5 (W=40, h=0,2, CAP base)",
        valores_b3, b3_ok, nota=(f"dz* (la mayor que cumple) = {dz_star}" if dz_star else "ninguna dz cumple"))

    # Orden de convergencia y Richardson.
    ord_pares = {}
    for (na, a), (nb, b) in zip(DZ_CASOS[:-1], DZ_CASOS[1:]):
        if a in P and b in P and P[a] > P[b] > 0:
            ord_pares[f"{a}->{b}"] = math.log2(P[a] / P[b])
    p_last = None
    P_ext = None
    P_ext2 = None
    if all(d in P for d in (0.5, 0.25, 0.125)):
        num = P[0.5] - P[0.25]
        den = P[0.25] - P[0.125]
        if den > 0 and num > 0:
            p_last = math.log2(num / den)
            P_ext = P[0.125] + (P[0.125] - P[0.25]) / (2.0 ** p_last - 1.0)
        P_ext2 = P[0.125] + (P[0.125] - P[0.25]) / 3.0
    if p_last is not None:
        add("D-ORD", "|p_last - 2| <= 0,25 (orden de Strang observado en 0,5/0,25/0,125)",
            f"p_last={p_last:.4f}; pares={ {k: round(v, 4) for k, v in ord_pares.items()} }",
            abs(p_last - 2.0) <= 0.25)
    else:
        add("D-ORD", "|p_last - 2| <= 0,25", "no definido (serie no monotona o no evaluada)", None)

    if 0.25 in P and 0.125 in P:
        conv = abs(P[0.125] - P[0.25]) / P[0.125]
        add("D-CONV", "|P(0,125) - P(0,25)| / P(0,125) <= 0,10", f"{conv:.4f}", conv <= 0.10)
    else:
        add("D-CONV", "convergencia en dz al 10 %", "no evaluado", None)

    if P_ext is not None:
        add("D-EXT", "P_ext (Richardson, p_last) <= 1e-5",
            f"P_ext={fmt(P_ext)}; P_ext(p=2)={fmt(P_ext2)}", P_ext <= UMBRAL_B3)
    else:
        add("D-EXT", "P_ext <= 1e-5", "no definido", None)

    if pert is not None and P_ext is not None:
        Pp = pert["P_pert_1mm_h0.2"]
        rel = abs(P_ext - Pp) / Pp
        add("D-PERT", "|P_ext - P_pert| / P_pert <= 0,10",
            f"P_ext={fmt(P_ext)}, P_pert={fmt(Pp)}, rel={rel:.4e}", rel <= 0.10)
    else:
        add("D-PERT", "|P_ext - P_pert| / P_pert <= 0,10", "no evaluado", None)

    # G3 (condicional).
    g3 = {}
    if b3_ok is None:
        g3_estado = "no evaluado"
        add("G3", "G3 (condicional a B3-r5)", "no evaluado", None)
    elif not b3_ok:
        g3_estado = "no ejecutado: condicion no cumplida"
        add("G3", "G3 (condicional a B3-r5)", g3_estado, None,
            nota="no ejecutado por condicion; no cuenta como criterio faltante")
        crit[-1]["no_ejecutado"] = True
    else:
        ok_all = True
        faltan_g3 = False
        for caso, d in (("d14", 14.0), ("d16", 16.0)):
            g = load(f"g3_{caso}")
            if g is None:
                g3[caso] = None
                faltan_g3 = True
                add(f"G3.{caso}", f"G3 d={d} um: |z_max(P2m) - L_c| / L_c <= 0,10",
                    "pendiente: no ejecutado", None)
                continue
            zmax = g["z_max_um"]
            Lc = g["L_c_um"]
            interior = bool(g["max_interior"])
            rel = abs(zmax - Lc) / Lc if interior else float("nan")
            ok = interior and rel <= 0.10
            ok_all = ok_all and ok
            g3[caso] = {"d_um": d, "h_um": g["h_um"], "dz_um": g["dz_um"], "L_c_um": Lc,
                        "z_max_um": zmax, "error_relativo": rel, "pass": ok,
                        "tiempo_propagacion_s": g["tiempo_propagacion_s"]}
            add(f"G3.{caso}", f"G3 d={d} um: |z_max(P2m) - L_c| / L_c <= 0,10 (z_max interior)",
                f"z_max={zmax:.3f} um, L_c={Lc:.3f} um, rel={rel:.4f}" if interior else "sin maximo interior",
                ok, nota=f"h={g['h_um']} um, dz={g['dz_um']} um, t_prop={g['tiempo_propagacion_s']:.1f} s")
        if faltan_g3:
            g3_estado = "pendiente: no ejecutado"
            add("G3", "G3 global: d=14 y d=16 cumplen el 10 %", g3_estado, None)
        else:
            g3_estado = "evaluado"
            add("G3", "G3 global: d=14 y d=16 cumplen el 10 %", "ver G3.d14 y G3.d16", ok_all)

    # Costes y contingencias.
    tiempos = {n: (runs[n]["tiempo_propagacion_s"] if runs[n] else None) for n, _ in DZ_CASOS}
    por_paso = {n: (runs[n]["tiempo_por_paso_ms"] if runs[n] else None) for n, _ in DZ_CASOS}
    sup = [n for n, t in tiempos.items() if t is not None and t > LIMITE_MIN]

    evaluados = [c["pass"] for c in crit if c["pass"] is not None]
    faltan = [c["id"] for c in crit if c["pass"] is None and not c.get("no_ejecutado")]
    if faltan:
        estado = "partial"
    else:
        estado = "done"

    texto = (
        f"B3-r5: {'PASA' if b3_ok else ('NO PASA' if b3_ok is False else 'no evaluado')}"
        f" (dz* = {dz_star}). P_perd(1 mm): " + ", ".join(f"dz={dz}: {fmt(P.get(dz))}" for _, dz in DZ_CASOS)
        + f". p_last={p_last if p_last is None else round(p_last, 4)}. P_ext={fmt(P_ext)}. "
        + f"P_pert={fmt(pert['P_pert_1mm_h0.2']) if pert else 'no evaluado'}. G3: {g3_estado}."
    )

    out = {
        "task": "B5 bpm r5 - convergencia en dz de la perdida del BPM",
        "fecha_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "contrato": "CONTRATO-bpm-r5.md",
        "umbral_B3": UMBRAL_B3,
        "criterios": crit,
        "resumen": {
            "B3_r5_pass": b3_ok,
            "dz_star_um": dz_star,
            "P_perd_1mm": {f"dz={dz}": P.get(dz) for _, dz in DZ_CASOS},
            "tiempo_propagacion_s": {n: tiempos[n] for n, _ in DZ_CASOS},
            "tiempo_por_paso_ms": {n: por_paso[n] for n, _ in DZ_CASOS},
            "corridas_mas_de_15_min": sup,
            "ordenes_pares": ord_pares,
            "p_last": p_last,
            "P_ext_richardson_p_last": P_ext,
            "P_ext_richardson_p2": P_ext2,
            "P_pert_1mm_h0.2": pert["P_pert_1mm_h0.2"] if pert else None,
            "referencias_pert": pert["referencias"] if pert else None,
            "r4_citados": {str(k): v for k, v in R4.items()},
            "G3": g3_estado,
            "G3_detalle": g3,
            "criterios_no_evaluados": faltan,
            "estado": estado,
        },
        "texto": texto,
    }
    (HERE / "resultados_bpm_r5.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(texto)
    print(f"estado={estado}; criterios evaluados={len(evaluados)}; no evaluados={faltan}")


if __name__ == "__main__":
    main()
