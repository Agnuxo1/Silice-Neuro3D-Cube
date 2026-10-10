"""Evaluacion de la ronda 4 (CONTRATO-bpm-r4.md, secciones 4 y 5). Calcula todos los pass por codigo.

Uso: python -B evaluar_bpm_r4.py
Lee r4_runs/*.json y escribe resultados_bpm_r4.json. Solo CPU, sin dependencias externas.
"""
import datetime
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
RUNS = HERE / "r4_runs"
OUT = HERE / "resultados_bpm_r4.json"

UMBRAL_B3 = 1e-5
CONTROL_R2 = 2.4600e-4


def load(name):
    p = RUNS / f"{name}.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def rel(a, b):
    return abs(a - b) / abs(b)


def main():
    r = {n: load(n) for n in ["r4_W40_dz1", "r4_W60_dz1", "r4_W80_dz1", "r4_W40_dz05", "r4_PEIG_W40_dz1"]}
    faltan = [n for n, d in r.items() if d is None]
    P = {n: (d["perdida_1mm"] if d else None) for n, d in r.items()}
    crit = []
    no_eval = []

    def add(cid, desc, value, passed, nota=""):
        crit.append({"id": cid, "description": desc, "value": value, "pass": bool(passed), "nota": nota})

    # Verificacion
    if P["r4_W40_dz1"] is not None:
        v0 = rel(P["r4_W40_dz1"], CONTROL_R2)
        add("V0", "control: |P_perd(r4_W40_dz1) - 2,4600e-4| / 2,4600e-4 <= 1e-3",
            f"{v0:.3e} (P={P['r4_W40_dz1']:.6e})", v0 <= 1e-3)
    else:
        no_eval.append("V0")
    d = r["r4_PEIG_W40_dz1"]
    if d is not None:
        ok1 = d["residuo_relativo_U"] <= 1e-6 and d["ov2_LP01_analitico"] >= 0.999
        add("V1", "P-EIG convergido: residuo ||U E - lambda E||/||E|| <= 1e-6 y ov2(LP01) >= 0,999",
            f"residuo={d['residuo_relativo_U']:.3e}, ov2_LP01={d['ov2_LP01_analitico']:.9f}", ok1)
        v2 = abs(P["r4_PEIG_W40_dz1"] - d["perdida_eigen_teorica_1mm"])
        add("V2", "consistencia P-EIG: |P_perd - (1 - |lambda|^2000)| <= 1e-6",
            f"{v2:.3e} (P={P['r4_PEIG_W40_dz1']:.6e}, teorica={d['perdida_eigen_teorica_1mm']:.6e})", v2 <= 1e-6)
    else:
        no_eval += ["V1", "V2"]

    # Prueba principal
    cands = {n: P[n] for n in ["r4_W40_dz1", "r4_W60_dz1", "r4_W80_dz1", "r4_W40_dz05", "r4_PEIG_W40_dz1"] if P[n] is not None}
    if len(cands) == 5:
        mejor = min(cands, key=cands.get)
        b3 = cands[mejor] <= UMBRAL_B3
        add("B3-r4", "alguna configuracion de C con P_perd(1 mm) <= 1e-5 (CAP activo)",
            ", ".join(f"{n}={v:.4e}" for n, v in cands.items()), b3,
            nota=f"mejor configuracion: {mejor}")
    else:
        no_eval.append("B3-r4")
        b3 = None

    # Diagnosticos
    if None not in (P["r4_W40_dz1"], P["r4_W60_dz1"], P["r4_W80_dz1"]):
        dw = max(rel(P["r4_W60_dz1"], P["r4_W40_dz1"]) if False else abs(P["r4_W60_dz1"] - P["r4_W40_dz1"]) / P["r4_W40_dz1"],
                 abs(P["r4_W80_dz1"] - P["r4_W60_dz1"]) / P["r4_W60_dz1"])
        add("D-W", "H-CONTORNO: max(|P60-P40|/P40, |P80-P60|/P60) <= 0,10 (pass = perdida independiente de W)",
            f"{dw:.4f} (P40={P['r4_W40_dz1']:.5e}, P60={P['r4_W60_dz1']:.5e}, P80={P['r4_W80_dz1']:.5e})", dw <= 0.10)
    else:
        no_eval.append("D-W")
    if None not in (P["r4_W40_dz05"], P["r4_W40_dz1"]):
        ddz = abs(P["r4_W40_dz05"] - P["r4_W40_dz1"]) / P["r4_W40_dz1"]
        add("D-dz", "|P(dz05) - P(dz1)| / P(dz1) <= 0,10 (pass = perdida independiente de dz)",
            f"{ddz:.4f} (P_dz05={P['r4_W40_dz05']:.5e}, P_dz1={P['r4_W40_dz1']:.5e})", ddz <= 0.10)
    else:
        no_eval.append("D-dz")
    if P["r4_PEIG_W40_dz1"] is not None:
        add("D-PROP", "H-PROP: P_perd(r4_PEIG_W40_dz1) <= 1e-5 (pass = el modo del propio esquema no pierde potencia)",
            f"{P['r4_PEIG_W40_dz1']:.6e}", P["r4_PEIG_W40_dz1"] <= UMBRAL_B3)
        dcons = abs(P["r4_PEIG_W40_dz1"] - r["r4_PEIG_W40_dz1"]["perdida_eigen_teorica_1mm"]) / P["r4_PEIG_W40_dz1"] \
            if P["r4_PEIG_W40_dz1"] > 0 else float("inf")
        add("D-CONS", "|P_perd(PEIG) - (1 - |lambda|^2000)| / P_perd(PEIG) <= 0,10",
            f"{dcons:.4f}", dcons <= 0.10)
    else:
        no_eval += ["D-PROP", "D-CONS"]

    # G3 condicionado
    if b3 is True:
        g3 = "pendiente: no ejecutado por plazo (B3-r4 pasa, G3 requiere >10 min por corrida)"
    elif b3 is False:
        g3 = "no ejecutado: condicion no cumplida"
    else:
        g3 = "no evaluado: falta B3-r4"

    evaluados = [c["id"] for c in crit]
    estado = "done" if (not faltan and not no_eval and b3 is not None) else "partial"
    if b3 is True:
        estado = "partial"  # G3 queda pendiente por plazo

    resumen = {
        "B3_r4_pass": b3,
        "P_perd_1mm": P,
        "G3": g3,
        "estado": estado,
        "criterios_no_evaluados": no_eval,
        "runs_faltantes": faltan,
        "citados_de_r2_no_reevaluados": {
            "G0_R0_0.05": 2.2791e-4, "s0_34_w6": 2.4293e-4, "W60c_s0_28": 2.4745e-4,
            "disc_Lanczos": 2.4596e-4, "dz05_analitico_r2": 7.3692e-5
        },
        "nota_protocolo": "prueba (a) no aplica (el esquema ya es split-step de Strang); sustituida por P-EIG (declarado en el contrato)",
    }
    out = {
        "task": "B4 bpm r4 - origen de la perdida del modo guiado",
        "fecha_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "contrato": "CONTRATO-bpm-r4.md",
        "umbral_B3": UMBRAL_B3,
        "criterios": crit,
        "resumen": resumen,
        "texto": (
            "B3-r4 " + ("PASA" if b3 else ("NO PASA" if b3 is False else "no evaluado")) + ". "
            + "P_perd(1 mm): " + ", ".join(f"{n}={v:.4e}" for n, v in P.items() if v is not None) + ". "
            + "G3: " + g3 + "."
        ),
    }
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(resumen, indent=2, ensure_ascii=False))
    print("criterios evaluados:", evaluados)


if __name__ == "__main__":
    main()
