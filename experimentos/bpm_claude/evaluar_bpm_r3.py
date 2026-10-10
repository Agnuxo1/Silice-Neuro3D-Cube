"""Evaluacion de la ronda 3 (CONTRATO-bpm-r3.md, secciones 4-5).

Lee r3_runs/*.json (salida de run_b3_r3.py), calcula todos los pass por codigo y escribe:
  resultados_bpm_r3.json   (pass calculado por el script)
  RESULTADOS-bpm-r3.md     (texto generado a partir de los JSON)
Modelo numerico. Solo CPU. Sin dependencias fuera de la biblioteca estandar.
"""
import datetime
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
RUNS = HERE / "r3_runs"

NAMES = ["an_cap_dz1", "fd_cap_dz1", "an_cap_dz05", "fd_cap_dz05", "an_sin_dz1", "fd_sin_dz1"]
R1_LOSS_REF = 2.4600e-4   # ronda 1 y 2, B3 con dato analitico (r2_runs/base.json: 2,459999724e-4)
R2_DZ05_REF = 7.3692e-5   # r2_runs/dz05.json: dato analitico, dz = 0,5 (solo informativo)
B3_THRESHOLD = 1e-5        # umbral de B3 de la ronda 1; NO se cambia
N_REF = 1.4421921654570127  # n_eff analitico de LP01 (se recalcula en cada corrida; esta es la del propio analitico)


def load():
    data, missing = {}, []
    for n in NAMES:
        p = RUNS / f"{n}.json"
        if p.exists():
            data[n] = json.loads(p.read_text(encoding="utf-8"))
        else:
            missing.append(n)
    return data, missing


def rel(a, b):
    return abs(a - b) / abs(b)


def main():
    data, missing = load()
    crit = []

    def add(cid, desc, value, threshold, passed, kind="verificacion"):
        crit.append({"id": cid, "description": desc, "value": value, "threshold": threshold,
                     "pass": passed, "kind": kind})

    def need(*names):
        return all(n in data for n in names)

    # --- Verificacion ---
    if need("fd_cap_dz1"):
        d = data["fd_cap_dz1"]
        dn = abs(d["neff_solver2d"] - d["neff_analitico"])
        add("N1", "|n_eff solver2d - n_eff analitico| <= 1e-5 (modo discreto es guiado)",
            dn, 1e-5, dn <= 1e-5)
        ov = d["overlap2_solver2d_vs_LP01"]
        add("O1", "solape |<psi_FD|LP01>|^2 normalizado >= 0,999", ov, 0.999, ov >= 0.999)
    else:
        add("N1", "|n_eff solver2d - n_eff analitico| <= 1e-5", None, 1e-5, None)
        add("O1", "solape |<psi_FD|LP01>|^2 normalizado >= 0,999", None, 0.999, None)

    if need("fd_sin_dz1"):
        u = data["fd_sin_dz1"]["unitariedad_max_abs_P_over_P0_minus_1"]
        add("V1", "unitariedad sin CAP, dato discreto, 1 mm: max|P/P0-1| <= 1e-9", u, 1e-9, u <= 1e-9)
    else:
        add("V1", "unitariedad sin CAP, dato discreto, 1 mm", None, 1e-9, None)

    if need("an_cap_dz1"):
        pa = data["an_cap_dz1"]["perdida_1mm"]
        dv = rel(pa, R1_LOSS_REF)
        add("V2", "control: |P_perd(an, dz=1) - 2,4600e-4| / 2,4600e-4 <= 1e-3", dv, 1e-3, dv <= 1e-3)
    else:
        add("V2", "control de reproduccion", None, 1e-3, None)

    # --- Prueba principal B3-r3 ---
    if need("fd_cap_dz1"):
        pfd = data["fd_cap_dz1"]["perdida_1mm"]
        add("B3-r3", "perdida a 1 mm con E0 discreto solver2d (CAP base, dz = 1 um) <= 1e-5",
            pfd, B3_THRESHOLD, pfd <= B3_THRESHOLD, kind="principal")
    else:
        add("B3-r3", "perdida a 1 mm con E0 discreto solver2d <= 1e-5", None, B3_THRESHOLD, None, kind="principal")

    # --- Clasificacion ---
    if need("fd_cap_dz1", "an_cap_dz1"):
        pfd = data["fd_cap_dz1"]["perdida_1mm"]
        pan = data["an_cap_dz1"]["perdida_1mm"]
        h1v = rel(pfd, pan)
        add("H1", "el dato discreto no cambia la perdida: |P_fd - P_an| / P_an <= 0,10", h1v, 0.10, h1v <= 0.10,
            kind="clasificacion")
    else:
        add("H1", "el dato discreto no cambia la perdida", None, 0.10, None, kind="clasificacion")

    # --- Diagnosticos ---
    if need("fd_cap_dz05", "fd_cap_dz1"):
        a = data["fd_cap_dz05"]["perdida_1mm"]
        b = data["fd_cap_dz1"]["perdida_1mm"]
        dv = rel(a, b)
        add("D1-dz", "dependencia en dz (dato discreto): |P(dz=0,5) - P(dz=1)| / P(dz=1) <= 0,10", dv, 0.10,
            dv <= 0.10, kind="diagnostico")
    else:
        add("D1-dz", "dependencia en dz (dato discreto)", None, 0.10, None, kind="diagnostico")

    if need("fd_sin_dz1", "an_sin_dz1"):
        fa = data["fd_sin_dz1"]["fraccion_P_s_mayor_28_sobre_P0"]
        fb = data["an_sin_dz1"]["fraccion_P_s_mayor_28_sobre_P0"]
        dv = rel(fa, fb)
        add("R1", "radiacion sin CAP: |P(s>28)/P0 (fd) - P(s>28)/P0 (an)| / P(s>28)/P0 (an) <= 0,10", dv, 0.10,
            dv <= 0.10, kind="diagnostico")
    else:
        add("R1", "radiacion sin CAP", None, 0.10, None, kind="diagnostico")

    # --- Informativo (no tiene criterio pre-registrado) ---
    info = {}
    if need("an_cap_dz05"):
        info["P_perd_an_dz05_1mm"] = data["an_cap_dz05"]["perdida_1mm"]
        info["P_perd_an_dz05_vs_r2_dz05_ref_7p3692e-5"] = rel(data["an_cap_dz05"]["perdida_1mm"], R2_DZ05_REF)

    # --- Condicional G3 ---
    b3 = next((c for c in crit if c["id"] == "B3-r3"), None)
    if b3 is not None and b3["pass"] is True:
        g3 = "condicion B3-r3 cumplida: G3 debe ejecutarse segun CONTRATO-bpm-r3.md (no incluido en esta corrida)"
        g3_pass = None
    elif b3 is not None and b3["pass"] is False:
        g3 = "no ejecutado: condicion B3-r3 no cumplida (CONTRATO-bpm-r3.md, seccion 5)"
        g3_pass = None
    else:
        g3 = "pendiente: B3-r3 no evaluado"
        g3_pass = None

    # --- Clasificacion de la hipotesis ---
    h1 = next((c for c in crit if c["id"] == "H1"), None)
    if b3 is None or b3["pass"] is None:
        clas = "pendiente"
    elif b3["pass"]:
        clas = "H-DATO sostenida en esta construccion del dato (solver2d FD): la perdida cae por debajo de 1e-5"
    elif h1 is not None and h1["pass"]:
        clas = ("H-DATO refutada en esta construccion: el dato discreto no cambia la perdida "
                "(diferencia <= 10 % respecto al analitico), y B3-r3 no pasa")
    else:
        clas = ("el dato discreto cambia la perdida pero no la lleva por debajo de 1e-5; "
                "H-DATO no basta como explicacion unica")

    evaluated = [c for c in crit if c["pass"] is not None]
    required = [c for c in crit]
    status = "done" if len(evaluated) == len(required) and not missing else "partial"

    out = {
        "task": "B3 ronda 3 (dato inicial discreto) - CONTRATO-bpm-r3.md",
        "fecha_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "status": status,
        "corridas_faltantes": missing,
        "perdida_1mm_por_corrida": {n: (data[n]["perdida_1mm"] if n in data else None) for n in NAMES},
        "P_s28_sobre_P0_sin_CAP": {n: (data[n]["fraccion_P_s_mayor_28_sobre_P0"] if n in data else None)
                                   for n in ["an_sin_dz1", "fd_sin_dz1"]},
        "neff_solver2d": data["fd_cap_dz1"]["neff_solver2d"] if "fd_cap_dz1" in data else None,
        "neff_analitico": data["an_cap_dz1"]["neff_analitico"] if "an_cap_dz1" in data else None,
        "neff_espectral_control": data["fd_cap_dz1"]["neff_espectral_control"] if "fd_cap_dz1" in data else None,
        "criterios": crit,
        "informativo": info,
        "clasificacion_H_DATO": clas,
        "G3": {"estado": g3, "pass": g3_pass},
        "sha256": data["fd_cap_dz1"]["sha256"] if "fd_cap_dz1" in data else None,
    }
    (HERE / "resultados_bpm_r3.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    write_md(out, data)
    print(json.dumps({"status": status, "B3-r3": b3["pass"] if b3 else None,
                      "clasificacion": clas}, ensure_ascii=False))


def fmt(v, digits=4):
    if v is None:
        return "no evaluado"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        if v == 0:
            return "0"
        if abs(v) < 1e-3 or abs(v) >= 1e4:
            return f"{v:.{digits}e}"
        return f"{v:.{digits + 2}f}"
    return str(v)


def write_md(out, data):
    lines = []
    lines.append("# RESULTADOS-bpm-r3 - B3 con dato inicial discreto (ronda 3)")
    lines.append("")
    lines.append(f"Fecha de generacion: {out['fecha_utc']}. Estado: **{out['status']}**.")
    lines.append("Contrato: `CONTRATO-bpm-r3.md` (escrito antes de calcular). Modelo numerico escalar paraxial, "
                 "sin datos de laboratorio, no es un dispositivo.")
    lines.append("")
    lines.append("## Pregunta")
    lines.append("")
    lines.append("La perdida del modo guiado a 1 mm (ronda 1, 2,46e-4; umbral B3 = 1e-5) viene de que el dato "
                 "inicial LP01 muestreado no es el modo discreto del esquema (H-DATO)? Se prueba con un modo "
                 "discreto obtenido por solver2d (diferencias finitas) en la misma malla h = 0,2 um, ventana "
                 "+-40 um, indice promediado 16 x 16.")
    lines.append("")
    lines.append("## Resultado principal")
    lines.append("")
    b3 = next(c for c in out["criterios"] if c["id"] == "B3-r3")
    lines.append(f"- B3-r3 (perdida a 1 mm, E0 discreto solver2d, CAP base, dz = 1 um): "
                 f"**{fmt(b3['value'])}**, umbral {fmt(b3['threshold'])}, pass = **{fmt(b3['pass'])}**.")
    lines.append(f"- Clasificacion: {out['clasificacion_H_DATO']}.")
    lines.append(f"- G3: {out['G3']['estado']}.")
    lines.append("")
    lines.append("## Criterios (calculados por evaluar_bpm_r3.py)")
    lines.append("")
    lines.append("| id | tipo | descripcion | valor | umbral | pass |")
    lines.append("|---|---|---|---|---|---|")
    for c in out["criterios"]:
        lines.append(f"| {c['id']} | {c['kind']} | {c['description']} | {fmt(c['value'])} | "
                     f"{fmt(c['threshold'])} | {fmt(c['pass'])} |")
    lines.append("")
    lines.append("## Perdida a 1 mm por corrida (CAP base salvo indicacion)")
    lines.append("")
    lines.append("| corrida | dato | dz (um) | CAP | perdida 1 mm | P(s>28)/P0 (sin CAP) |")
    lines.append("|---|---|---|---|---|---|")
    for n in ["an_cap_dz1", "fd_cap_dz1", "an_cap_dz05", "fd_cap_dz05", "an_sin_dz1", "fd_sin_dz1"]:
        if n not in data:
            lines.append(f"| {n} | - | - | - | no evaluado | no evaluado |")
            continue
        d = data[n]
        cfg = d["config"]
        cap = "no" if not cfg["cap"] else f"R0 = {cfg['R0']}"
        p28 = fmt(d["fraccion_P_s_mayor_28_sobre_P0"]) if not cfg["cap"] else "-"
        lines.append(f"| {n} | {'discreto solver2d' if cfg['E0'] == 'fd' else 'analitico LP01'} | {cfg['dz']} | "
                     f"{cap} | {fmt(d['perdida_1mm'])} | {p28} |")
    lines.append("")
    lines.append("## Verificacion del dato discreto")
    lines.append("")
    if "fd_cap_dz1" in data:
        d = data["fd_cap_dz1"]
        lines.append(f"- n_eff solver2d = {d['neff_solver2d']:.10f}; n_eff analitico = {d['neff_analitico']:.10f}; "
                     f"diferencia = {d['delta_neff_solver2d_vs_analitico']:.3e}.")
        lines.append(f"- n_eff del control espectral (Lanczos de la ronda 2, mismo codigo) = "
                     f"{d['neff_espectral_control']:.10f}.")
        lines.append(f"- Solape |<psi_FD|LP01>|^2 = {d['overlap2_solver2d_vs_LP01']:.10f}; "
                     f"solape |<psi_FD|psi_espectral>|^2 = {d['overlap2_solver2d_vs_espectral_control']:.10f}.")
    lines.append("")
    lines.append("## Lo calculado y lo supuesto")
    lines.append("")
    lines.append("- Calculado en esta ronda: las seis corridas de `r3_runs/`, con sha256 de solver2d.py, bpm_r2.py "
                 "y run_b3_r3.py en cada JSON.")
    lines.append("- Tomado de la ronda 2 y citado, no recalculado: `r2_runs/disc.json` (Lanczos espectral, "
                 "perdida 2,4596e-4) y `r2_runs/dz05.json` (7,369e-5).")
    lines.append("- Supuesto del modelo: escalar paraxial, ventana periodica con CAP, split-step de Strang, h = 0,2 um. "
                 "No se mide nada en laboratorio.")
    lines.append("")
    lines.append("## Lo que no se hizo")
    lines.append("")
    lines.append("- El autovector del propio esquema de un paso (Strang) no se calculo; queda pendiente. "
                 "Solo se usaron dos construcciones del modo discreto (solver2d FD y Lanczos espectral de la ronda 2).")
    lines.append("- G3 no se ejecuto salvo que B3-r3 pase. Ver seccion de resultados.")
    lines.append("- No hay caracterizacion de convergencia en h ni en dz mas alla de dz = 0,5 y 1 um.")
    lines.append("")
    lines.append("## Nota sobre la ronda 2")
    lines.append("")
    lines.append("`resultados_bpm_r2.json` quedo en estado parcial (escrito a las 06:57 UTC, con campos nulos), "
                 "aunque las corridas de `r2_runs/` terminaron despues (hasta 07:07 UTC). Esta ronda cita "
                 "las cifras de `r2_runs/*.json` y no modifica el JSON de la ronda 2.")
    lines.append("")
    (HERE / "RESULTADOS-bpm-r3.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
