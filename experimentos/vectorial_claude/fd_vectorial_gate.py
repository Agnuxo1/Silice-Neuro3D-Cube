"""Controlador T6 r5 (CONTRATO-T6-r5.md): verificaciones V-a..V-f, puerta G1 y, solo si G1 pasa, paso 2 (C-T).

Cada corrida FD va en su proceso (fd_vectorial_run.py) para medir su pico de memoria.
Los criterios se evaluan aqui con codigo; ningun 'pass' se escribe a mano.
Salida: resultados_t6_r5.json (en esta carpeta). Ejecutar con: python -B fd_vectorial_gate.py
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import pathlib
import platform
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import numpy as np  # noqa: E402
import scipy  # noqa: E402

import fd_vectorial_core as C  # noqa: E402
from vector_step import Guide, residual_ok, top_root, v_number  # noqa: E402

RUN = HERE / "fd_vectorial_run.py"
DIR = HERE / "t6_corridas"
ENV = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
           PYTHONDONTWRITEBYTECODE="1")

LAM, N1, N2, A = 1.55, 1.444, 1.439, 6.0
K0 = 2.0 * math.pi / LAM
L = 30.0
H_GATE = [0.25, 0.125, 0.0625]
H_STAR = 0.0625
G1_THRESHOLD = 1e-6
MEM_LIMIT_BYTES = 2.0e9      # 2 GB (decimal)
V_B_RESID = 1e-8
V_A_RTOL = 1e-10
V_C_TOL = 1e-12
V_D_TOL = 1e-10
V_F_TOL = 1e-7
V_E_TOL = 1e-12
C_T_FRAC = 0.10
NEFF_CORE_TARGET = 1.43969   # sigma del paso 2 (E3)
K_STEP2 = 8
DN, T_TR = -0.005, 6.0


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(name: str, args: list[str]) -> dict:
    DIR.mkdir(parents=True, exist_ok=True)
    out = DIR / f"{name}.json"
    cmd = [sys.executable, "-B", str(RUN), *args, "--out", str(out)]
    t0 = time.perf_counter()
    res = subprocess.run(cmd, cwd=str(HERE), env=ENV, capture_output=True, text=True, timeout=1200)
    if res.returncode != 0:
        raise RuntimeError(f"corrida {name} fallo: {res.stderr[-1500:]}")
    d = json.loads(out.read_text(encoding="utf-8"))
    d["name"] = name
    d["wall_s"] = time.perf_counter() - t0
    return d


def main() -> int:
    t_start = time.perf_counter()
    crit = []

    def add(cid, desc, value, threshold, passed, note=""):
        crit.append({"id": cid, "description": desc, "value": value, "threshold": threshold,
                     "pass": bool(passed), "note": note})

    # ---------------- referencias analiticas (vector_step.py, sin cambios)
    V = v_number(LAM * 1e-6, N1, N2, A * 1e-6)
    g = Guide(N1, N2, V)
    tH = top_root(lambda b: g.hybrid(b, 1))
    HE11 = float(g.n_eff(tH[0]))
    HE11_ok = residual_ok(lambda b: g.hybrid(b, 1), tH)
    tL = top_root(g.lp01)
    LP01 = float(g.n_eff(tL[0]))
    HE11_STORED = 1.4421892973651511
    refs = {"V_star": V, "HE11_neff": HE11, "HE11_b": float(tH[0]), "HE11_residual_ok": bool(HE11_ok),
            "LP01_neff": LP01, "LP01_b": float(tL[0]), "HE11_minus_LP01": HE11 - LP01,
            "HE11_stored_ronda_previa": HE11_STORED}

    # V-e: referencia HE11
    add("V-e", "HE11 recalculado: residuo de raiz (V3) y coincidencia con el valor previo",
        abs(HE11 - HE11_STORED), V_E_TOL, HE11_ok and abs(HE11 - HE11_STORED) <= V_E_TOL,
        "valor = |HE11 - valor previo|")

    # V-c: suma de areas de disco en el cuadrante
    Mstar = int(round(L / H_STAR))
    Fst = C.cell_fraction(Mstar, H_STAR, A)
    area_err = abs(float(Fst.sum()) * H_STAR * H_STAR - math.pi * A * A / 4.0)
    add("V-c", "suma de fracciones de celda = pi a^2/4 en el cuadrante (h = 0,0625)",
        area_err, V_C_TOL, area_err <= V_C_TOL)

    # ---------------- corridas de la puerta
    gate_semi = {}
    gate_scal = {}
    for h in H_GATE:
        tag = f"{h:g}".replace(".", "p")
        gate_semi[h] = run(f"semi_jump_h{tag}",
                           ["--geom", "jump", "--semi", "1", "--h", str(h), "--L", str(L), "--k", "3"])
        gate_scal[h] = run(f"escalar_jump_h{tag}",
                           ["--geom", "jump", "--semi", "0", "--h", str(h), "--L", str(L), "--k", "3"])
        print(f"h={h}: semi n_eff={gate_semi[h]['neff']:.10f} scal n_eff={gate_scal[h]['neff']:.10f}", flush=True)

    # V-b: residuos de los modos fundamentales de la puerta
    resid_max = max(gate_semi[h]["resid_rel_selected"] for h in H_GATE)
    add("V-b", "residuo relativo ||A H - beta^2 H|| / ||H|| del modo fundamental (todas las mallas de la puerta)",
        resid_max, V_B_RESID, resid_max <= V_B_RESID)

    # V-a: medio uniforme con solucion exacta (E1)
    ua = run("uniforme_semi_h0p0625", ["--geom", "uniform", "--semi", "1", "--h", str(H_STAR), "--L", str(L)])
    ub = run("uniforme_escalar_h0p0625", ["--geom", "uniform", "--semi", "0", "--h", str(H_STAR), "--L", str(L)])
    Mx = int(round(L / H_STAR))
    beta2_exact = K0 * K0 * N1 * N1 - (4.0 / H_STAR ** 2) * (1.0 - math.cos(math.pi / (2.0 * Mx)))
    rel_a = []
    for d in (ua, ub):
        b2 = (d["neff"] * K0) ** 2
        rel_a.append(abs(b2 - beta2_exact) / abs(beta2_exact))
    add("V-a", "medio uniforme, beta^2 exacto del operador de 5 puntos (E1), error relativo semi y escalar",
        max(rel_a), V_A_RTOL, max(rel_a) <= V_A_RTOL,
        f"semi={rel_a[0]:.3e}, escalar={rel_a[1]:.3e}")

    # V-d: simetria (malla completa frente a cuadrante con Neumann), h = 0,25
    full = run("completa_semi_h0p25", ["--geom", "jump", "--semi", "1", "--h", "0.25", "--L", str(L),
                                       "--full", "1", "--k", "3"])
    dd = abs(full["neff"] - gate_semi[0.25]["neff"])
    add("V-d", "malla completa [-L,L]^2 frente a cuadrante con Neumann, h = 0,25 (semivectorial)",
        dd, V_D_TOL, dd <= V_D_TOL)

    # V-f: caja L = 36 frente a L = 30 en h = 0,125 (limite de caja, no bloquea)
    box36 = run("caja36_semi_h0p125", ["--geom", "jump", "--semi", "1", "--h", "0.125", "--L", "36", "--k", "3"])
    df = abs(box36["neff"] - gate_semi[0.125]["neff"])
    add("V-f", "caja L = 36 frente a L = 30 en h = 0,125 (semivectorial)", df, V_F_TOL, df <= V_F_TOL,
        "limite de caja; no bloquea la puerta si falla")

    # ---------------- puerta G1 (solo si V-a..V-e pasan)
    verif_ok = all(c["pass"] for c in crit if c["id"] in ("V-a", "V-b", "V-c", "V-d", "V-e"))
    gs = gate_semi[H_STAR]
    err_star = gs["neff"] - HE11
    mem_star = gs["peak_mem_bytes"]
    g1_pass = verif_ok and abs(err_star) <= G1_THRESHOLD and (0 <= mem_star <= MEM_LIMIT_BYTES)
    add("G1", "puerta: |n_eff(h=0,0625) - n_HE11| <= 1e-6 y pico de memoria <= 2 GB (verificaciones V-a..V-e previas)",
        abs(err_star), G1_THRESHOLD, g1_pass,
        f"n_eff={gs['neff']:.12f}; mem_pico={mem_star / 1e9:.3f} GB")

    # ---------------- diagnosticos (no son criterios de puerta)
    hs = H_GATE
    e_semi = [gate_semi[h]["neff"] - HE11 for h in hs]
    e_scal = [gate_scal[h]["neff"] - LP01 for h in hs]
    p_obs = None
    n_cont = None
    if abs(e_semi[1]) > 0 and abs(e_semi[2]) > 0 and abs(e_semi[1]) != abs(e_semi[2]):
        p_obs = math.log2(abs(gate_semi[0.125]["neff"] - gate_semi[0.25]["neff"]) /
                          abs(gate_semi[0.0625]["neff"] - gate_semi[0.125]["neff"]))
        n_cont = gate_semi[0.0625]["neff"] + (gate_semi[0.0625]["neff"] - gate_semi[0.125]["neff"]) / (2.0 ** p_obs - 1.0)
    diag = {
        "semi_err_HE11": dict(zip([str(h) for h in hs], e_semi)),
        "escalar_err_LP01": dict(zip([str(h) for h in hs], e_scal)),
        "semi_resid_rel": {str(h): gate_semi[h]["resid_rel_selected"] for h in hs},
        "semi_unknowns": {str(h): gate_semi[h]["unknowns"] for h in hs},
        "semi_peak_mem_GB": {str(h): gate_semi[h]["peak_mem_bytes"] / 1e9 for h in hs},
        "semi_wall_s": {str(h): gate_semi[h]["wall_s"] for h in hs},
        "orden_observado_semi_0p125_0p0625": p_obs,
        "neff_continuo_richardson_semi": n_cont,
        "error_de_modelo_continuo_minus_HE11": (n_cont - HE11) if n_cont is not None else None,
        "escalar_neff": {str(h): gate_scal[h]["neff"] for h in hs},
        "escalar_orden_observado": None,
    }
    ee = [abs(x) for x in e_scal]
    if ee[1] > 0 and ee[2] > 0:
        diag["escalar_orden_observado"] = math.log2(ee[1] / ee[2])
    if ee[0] > 0 and ee[1] > 0:
        diag["escalar_orden_0p25_0p125"] = math.log2(ee[0] / ee[1])

    # ---------------- paso 2 (solo si G1 pasa)
    step2 = {"ejecutado": False}
    if g1_pass:
        import trinchera_vectorial as TV  # referencia vectorial exacta (vector_layers.py)
        ref_te = TV.solve(DN, T_TR, "TE01")
        ref_tm = TV.solve(DN, T_TR, "TM01")
        delta_ref = ref_te["n_eff_re"] - ref_tm["n_eff_re"]
        tm = run("trench_TM_like_h0p0625", ["--geom", "trench", "--semi", "1", "--h", str(H_STAR), "--L", str(L),
                                             "--sx", "-1", "--sy", "1", "--k", str(K_STEP2), "--select", "core",
                                             "--sigma_neff", str(NEFF_CORE_TARGET)])
        te = run("trench_TE_like_h0p0625", ["--geom", "trench", "--semi", "1", "--h", str(H_STAR), "--L", str(L),
                                             "--sx", "1", "--sy", "-1", "--k", str(K_STEP2), "--select", "core",
                                             "--sigma_neff", str(NEFF_CORE_TARGET)])
        delta_fd = te["neff"] - tm["neff"]
        ok_t = abs(delta_fd - delta_ref) < C_T_FRAC * abs(delta_ref)
        add("C-T", "contraste TE-TM (trinchera dn=-0,005, t=6 um): |Delta_FD - Delta_ref| < 0,10 |Delta_ref|",
            abs(delta_fd - delta_ref), C_T_FRAC * abs(delta_ref), ok_t,
            f"Delta_FD={delta_fd:.4e}, Delta_ref={delta_ref:.4e}; fraccion nucleo TM={tm['frac_core_list'][0]:.3f}, TE={te['frac_core_list'][0]:.3f}")
        step2 = {
            "ejecutado": True,
            "delta_ref_vector_layers": delta_ref,
            "ref_TE01_neff_re": ref_te["n_eff_re"], "ref_TE01_loss_dB_cm": ref_te["loss_dB_per_cm"],
            "ref_TM01_neff_re": ref_tm["n_eff_re"], "ref_TM01_loss_dB_cm": ref_tm["loss_dB_per_cm"],
            "fd_TM_like_neff": tm["neff"], "fd_TE_like_neff": te["neff"], "delta_FD": delta_fd,
            "fd_TM_like_list_k8": tm["neff_list"], "fd_TM_like_frac_core_k8": tm["frac_core_list"],
            "fd_TE_like_list_k8": te["neff_list"], "fd_TE_like_frac_core_k8": te["frac_core_list"],
            "advertencia": "La referencia vector_layers.py es abierta (con fuga, Im n_eff ~1e-4); la caja cerrada no reproduce esa fuga.",
        }

    # ---------------- estado y resultado
    evaluados = {c["id"] for c in crit}
    requeridos = {"V-a", "V-b", "V-c", "V-d", "V-e", "G1"}
    if g1_pass:
        requeridos.add("C-T")
    if requeridos <= evaluados:
        status = "done"
    else:
        status = "partial"
    gate_verdict = "PASA" if g1_pass else "NO PASA"

    out = {
        "task": "T6 r5 solver semivectorial H_y de orden 2 con permitividad promediada en la interfaz",
        "status": status,
        "contract": "CONTRATO-T6-r5.md",
        "contract_sha256": sha256(HERE / "CONTRATO-T6-r5.md"),
        "solver": ("semivectorial H_y: beta^2 H = eps d_x((1/eps) d_x H) + d_y^2 H + k0^2 eps H; "
                   "celdas centradas en cuadrante [0,L]^2, Neumann en ejes, Dirichlet en L; "
                   "eps promediado en el area exacta de la celda; u = 1/eps en caras por media armonica; "
                   "shift-invert eigs. Escalar de control: mismo promediado, LP01."),
        "gate_verdict": gate_verdict,
        "gate_threshold": {"error_neff": G1_THRESHOLD, "h_um": H_STAR, "memoria_bytes": MEM_LIMIT_BYTES},
        "references": refs,
        "criteria": crit,
        "diagnostics": diag,
        "step2": step2,
        "runs": {c["name"]: {k: c[k] for k in ("neff", "unknowns", "resid_rel_selected", "elapsed_solve_s",
                                              "peak_mem_bytes", "wall_s", "h_um", "L_um", "semi", "sx", "sy", "full")}
                 for c in [gate_semi[h] for h in hs] + [gate_scal[h] for h in hs] + [ua, ub, full, box36]},
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                        "OMP_NUM_THREADS": "1", "os": platform.platform()},
        "limits": [
            "Formulacion semivectorial (H_y dominante); no es vectorial completo. Su error de modelo frente a HE11 se estima con la extrapolacion, no se elimina.",
            "Caja de L = 30 um con Dirichlet en el borde; modos con fuga (trinchera) no se representan de forma exacta.",
            "Medida de memoria: pico del working set del proceso de la corrida (Windows).",
            "Razon de orden observada con tres mallas; con dos puntos el orden es una estimacion.",
        ],
        "elapsed_total_s": time.perf_counter() - t_start,
    }
    outp = HERE / "resultados_t6_r5.json"
    outp.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": status, "gate": gate_verdict,
                      "criteria": [{k: c[k] for k in ("id", "pass")} for c in crit]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
