"""Tarea E (CONTRATO-ABLACION.md): separar deteccion intermedia y activacion MZM.

Uso (desde esta carpeta):  python -B ablacion.py
Lee run_f3.py y run_f3b.py (sin modificarlos) y los resultados guardados de F3 y F3-b.
Escribe solo ablacion_resultados.json. Modelo numerico en CPU, no un dispositivo.
Verificaciones aleatorias: numpy.random.default_rng(20261014), fijada aqui.
"""
import json
import os
import pathlib
import sys
import time

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from scipy.linalg import logm  # noqa: E402
from scipy.optimize import minimize  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_f3 as F  # noqa: E402  (tarea congelada, malla unitaria, train de M1)
import run_f3b as F3B  # noqa: E402  (activacion MZM, logits A y B, paired_ci)

SEEDS = range(1, 9)  # protocolo F3-b
MAXITER = 300
N_PARAMS = 32
UPPER = np.triu_indices(4, 1)
OUT = HERE / "ablacion_resultados.json"


def logits_nonlin_off(p, X):
    """Deteccion |.|^2 conservada, sin MZM: a2 = sqrt(I1) = |X U1^T| (real, fase cero)."""
    U1 = F.unpack_unitary(p[:16])
    U2 = F.unpack_unitary(p[16:32])
    I1 = np.abs(X @ U1.T) ** 2
    a2 = np.sqrt(I1)
    return np.abs(a2 @ U2.T) ** 2


def logits_det_off(p, X):
    """Cascada de dos mallas en amplitud compleja; intensidad solo al final."""
    U1 = F.unpack_unitary(p[:16])
    U2 = F.unpack_unitary(p[16:32])
    return np.abs((X @ U1.T) @ U2.T) ** 2


MODELS = {
    "M_full": F3B.logits_A,
    "M_nonlin_off": logits_nonlin_off,
    "M_det_off": logits_det_off,
    "M_real": F3B.logits_B,
}


def xent_of(p, logit_fn, X, y):
    """Misma formula que run_f3b.xent: entropia cruzada media."""
    z = logit_fn(p, X)
    z = z - z.max(1, keepdims=True)
    lse = np.log(np.exp(z).sum(1))
    return float((lse - z[np.arange(len(y)), y]).mean())


def fit(logit_fn, n):
    """8 reinicios (semillas 1..8), L-BFGS-B, seleccion por perdida de entrenamiento."""
    rows = []
    for s in SEEDS:
        p0 = 0.5 * np.random.default_rng(s).standard_normal(n)
        res = minimize(xent_of, p0, args=(logit_fn, F.X_TR, F.Y_TR), method="L-BFGS-B",
                       options={"maxiter": MAXITER})
        pred_te = logit_fn(res.x, F.X_TE).argmax(1)
        rows.append({
            "seed": s, "p": res.x, "train_loss": float(res.fun),
            "success": bool(res.success), "nit": int(res.nit), "message": str(res.message),
            "train_acc": float((logit_fn(res.x, F.X_TR).argmax(1) == F.Y_TR).mean()),
            "test_acc": float((pred_te == F.Y_TE).mean()), "test_pred": pred_te,
        })
    best = min(rows, key=lambda r: r["train_loss"])
    return rows, best


def summarize(rows, best, n):
    tl = np.array([r["train_loss"] for r in rows])
    return {
        "n_params": n, "best_seed": best["seed"], "train_loss": best["train_loss"],
        "train_acc": best["train_acc"], "test_acc": best["test_acc"],
        "selected_success": best["success"], "selected_nit": best["nit"],
        "selected_message": best["message"],
        "restarts_train_loss_min_max": [float(tl.min()), float(tl.max())],
        "restarts_within_1e-6_of_best": int(np.sum(tl - tl.min() < 1e-6)),
        "restarts": [{k: r[k] for k in ("seed", "train_loss", "train_acc", "test_acc", "success", "nit")}
                     for r in rows],
        "p_selected": best["p"].tolist(),
    }


def ci_dict(d, ci, point):
    """punto_estimado: diferencia de exactitudes de prueba (muestra completa).
    media_bootstrap: media de los 1000 remuestreos (lo que devuelve run_f3b.paired_ci)."""
    return {"punto_estimado": float(point), "media_bootstrap": float(d),
            "ci95": [float(ci[0]), float(ci[1])]}


def main():
    t0 = time.monotonic()
    stored_a = [json.loads((HERE / "f3b_seeds" / f"a_s{s}.json").read_text(encoding="utf-8")) for s in SEEDS]
    f3b = json.loads((HERE / "f3b_resultados.json").read_text(encoding="utf-8"))
    f3 = json.loads((HERE / "f3_resultados.json").read_text(encoding="utf-8"))
    f3b_agg = json.loads((HERE / "f3b_aggregate.json").read_text(encoding="utf-8"))

    fits = {name: fit(fn, N_PARAMS) for name, fn in MODELS.items()}
    rows_a, best_a = fits["M_full"]
    rows_b, best_b = fits["M_real"]

    # ---- E0: reproduccion de A (control bloqueante) ----
    dl = max(abs(r["train_loss"] - s["train_loss"]) for r, s in zip(rows_a, stored_a))
    best_stored_a = min(stored_a, key=lambda r: r["train_loss"])
    e0_mismatch = int(np.sum(best_a["test_pred"] != np.array(best_stored_a["test_pred"])))
    e0_acc_diff = abs(best_a["test_acc"] - 0.6425)
    e0 = {
        "best_seed": best_a["seed"], "best_seed_esperada": 5,
        "best_seed_guardada_f3b": best_stored_a["seed"],
        "test_acc": best_a["test_acc"], "test_acc_esperada": 0.6425,
        "abs_diff_test_acc": e0_acc_diff,
        "max_abs_diff_train_loss_8_semillas": dl,
        "test_pred_mismatches_vs_f3b": e0_mismatch,
        "criterio": "abs_diff_test_acc < 1e-12 y semilla 5 y max_abs_diff_train_loss < 1e-9",
        "pass": bool(e0_acc_diff < 1e-12 and best_a["seed"] == 5 and dl < 1e-9),
    }

    # ---- E1: reproduccion de M1 con la funcion congelada de run_f3 ----
    best_m1 = F.train("m1")
    acc_m1 = F.accuracy("m1", best_m1["p"], F.X_TE, F.Y_TE)
    pred_m1_own = F.logits("m1", best_m1["p"], F.X_TE).argmax(1)
    pred_m1 = np.array(f3["m1"]["test_pred"])
    e1_mismatch = int(np.sum(pred_m1_own != pred_m1))
    e1 = {
        "best_seed": best_m1["seed"], "best_seed_guardada_f3": f3["m1"]["best_seed"],
        "test_acc": acc_m1, "test_acc_guardada_f3": f3["m1"]["test_acc"],
        "abs_diff_test_acc": abs(acc_m1 - 0.5905),
        "train_loss": best_m1["train_loss"], "train_loss_guardada_f3": f3["m1"]["train_loss"],
        "test_pred_mismatches_vs_f3": e1_mismatch,
        "criterio": "abs_diff_test_acc < 1e-12 y 0 discrepancias de prediccion",
        "pass": bool(abs(acc_m1 - 0.5905) < 1e-12 and e1_mismatch == 0),
    }

    # ---- E2: reproduccion de B (M_real) ----
    e2_mismatch = int(np.sum(best_b["test_pred"] != np.array(f3b["b"]["test_pred"])))
    e2_diff = abs(best_b["test_acc"] - f3b["b"]["test_acc"])
    e2 = {
        "best_seed": best_b["seed"], "best_seed_guardada_f3b": f3b["b"]["best_seed"],
        "test_acc": best_b["test_acc"], "test_acc_guardada_f3b": f3b["b"]["test_acc"],
        "abs_diff_test_acc": e2_diff, "test_pred_mismatches_vs_f3b": e2_mismatch,
        "criterio": "abs_diff_test_acc < 1e-12",
        "pass": bool(e2_diff < 1e-12),
    }

    # ---- Verificaciones analiticas ----
    rng = np.random.default_rng(20261014)

    # V1 unitariedad
    err_u = []
    for _ in range(100):
        U = F.unpack_unitary(rng.standard_normal(16) * 2.0)
        err_u.append(float(np.max(np.abs(U @ U.conj().T - np.eye(4)))))
    v1 = {"max_unitarity_error": max(err_u), "criterio": "< 1e-12", "pass": bool(max(err_u) < 1e-12)}

    # V2 identidad de clase: M_det_off = |X (U2 U1)^T|^2
    err_2 = []
    for _ in range(20):
        p = rng.standard_normal(N_PARAMS) * 2.0
        U = F.unpack_unitary(p[16:]) @ F.unpack_unitary(p[:16])
        ref = np.abs(F.X_TE @ U.T) ** 2
        err_2.append(float(np.max(np.abs(logits_det_off(p, F.X_TE) - ref))))
    v2 = {"max_abs_diff": max(err_2), "criterio": "< 1e-10", "pass": bool(max(err_2) < 1e-10)}

    # V2b equivalencia constructiva: M1 representa U2 U1
    err_u2b, err_l2b = [], []
    for _ in range(20):
        p = rng.standard_normal(N_PARAMS) * 2.0
        U = F.unpack_unitary(p[16:]) @ F.unpack_unitary(p[:16])
        H = -1j * logm(U)
        H = (H + H.conj().T) / 2
        p16 = np.concatenate([np.real(np.diag(H)), np.real(H[UPPER]), np.imag(H[UPPER])])
        err_u2b.append(float(np.max(np.abs(F.unpack_unitary(p16) - U))))
        err_l2b.append(float(np.max(np.abs(F.logits("m1", p16, F.X_TE) - logits_det_off(p, F.X_TE)))))
    v2b = {"max_unitary_reconstruction_error": max(err_u2b), "max_logit_diff": max(err_l2b),
           "criterio": "ambos < 1e-8", "pass": bool(max(err_u2b) < 1e-8 and max(err_l2b) < 1e-8)}

    # V3 bootstrap degenerado
    pa = best_a["test_pred"]
    d_self, ci_self = F3B.paired_ci(pa, pa, F.Y_TE)
    v3 = {"diff": d_self, "ci95": ci_self, "criterio": "[0,0] exacto",
          "pass": bool(d_self == 0.0 and ci_self[0] == 0.0 and ci_self[1] == 0.0)}

    # V4 activacion
    t0_val = float(F3B.activation(np.array([0.0]))[0])
    t1_val = float(F3B.activation(np.array([1.0]))[0])
    v4 = {"T_0": t0_val, "T_1": t1_val, "criterio": "|T(0)-1| < 1e-15 y |T(1)| < 1e-15",
          "pass": bool(abs(t0_val - 1.0) < 1e-15 and abs(t1_val) < 1e-15)}

    # V5 reproduccion del IC pareado de F3-b (A frente a M1)
    d_a1, ci_a1 = F3B.paired_ci(pa, pred_m1, F.Y_TE)
    ref5 = f3b_agg["H-F3"]
    v5_diff = abs(d_a1 - ref5["paired_diff_A_minus_M1"])
    v5_ci = max(abs(ci_a1[0] - ref5["ci95"][0]), abs(ci_a1[1] - ref5["ci95"][1]))
    v5 = {"diff": float(d_a1), "ci95": [float(ci_a1[0]), float(ci_a1[1])],
          "diff_guardada_f3b": ref5["paired_diff_A_minus_M1"], "ci95_guardada_f3b": ref5["ci95"],
          "max_abs_diff": float(max(v5_diff, v5_ci)), "criterio": "< 1e-12",
          "pass": bool(max(v5_diff, v5_ci) < 1e-12)}

    # C-CONV convergencia del reinicio seleccionado
    cconv = {name: {"selected_success": fits[name][1]["success"], "selected_nit": fits[name][1]["nit"],
                    "selected_message": fits[name][1]["message"]} for name in MODELS}
    cconv["pass"] = bool(all(fits[name][1]["success"] for name in MODELS))

    # ---- Hipotesis ----
    pred = {name: fits[name][1]["test_pred"] for name in MODELS}
    d1, ci1 = F3B.paired_ci(pred["M_full"], pred["M_nonlin_off"], F.Y_TE)
    d2, ci2 = F3B.paired_ci(pred["M_nonlin_off"], pred["M_det_off"], F.Y_TE)
    d3, ci3 = F3B.paired_ci(pred["M_det_off"], pred_m1, F.Y_TE)
    d4, ci4 = F3B.paired_ci(pred["M_full"], pred["M_real"], F.Y_TE)
    d5, ci5 = F3B.paired_ci(pred["M_nonlin_off"], pred_m1, F.Y_TE)
    acc = {name: fits[name][1]["test_acc"] for name in MODELS}
    acc_m1_val = float(acc_m1)
    hyp = {
        "H-A1": {"enunciado": "exact(M_full) - exact(M_nonlin_off) > 0, IC95 excluye 0",
                 **ci_dict(d1, ci1, acc["M_full"] - acc["M_nonlin_off"]),
                 "criterio": "ci95[0] > 0", "pass": bool(ci1[0] > 0)},
        "H-A2": {"enunciado": "exact(M_nonlin_off) - exact(M_det_off) > 0, IC95 excluye 0",
                 **ci_dict(d2, ci2, acc["M_nonlin_off"] - acc["M_det_off"]),
                 "criterio": "ci95[0] > 0", "pass": bool(ci2[0] > 0)},
        "H-A3": {"enunciado": "exact(M_det_off) - exact(M1) con IC95; cumple si IC95 contiene 0",
                 **ci_dict(d3, ci3, acc["M_det_off"] - acc_m1_val),
                 "criterio": "ci95[0] <= 0 <= ci95[1]",
                 "pass": bool(ci3[0] <= 0.0 <= ci3[1])},
    }
    info = {
        "M_full_menos_M_real": ci_dict(d4, ci4, acc["M_full"] - acc["M_real"]),
        "M_nonlin_off_menos_M1": ci_dict(d5, ci5, acc["M_nonlin_off"] - acc_m1_val),
        "nota": "informativo, no es criterio de decision",
    }

    models = {name: summarize(*fits[name], n=N_PARAMS) for name in MODELS}
    models["M1_ref_F3"] = {"n_params": 16, "best_seed": best_m1["seed"], "train_loss": best_m1["train_loss"],
                           "train_acc": float(F.accuracy("m1", best_m1["p"], F.X_TR, F.Y_TR)),
                           "test_acc": acc_m1, "nota": "reentrenada con run_f3.train; E1 la reproduce"}

    # ---- Diagnosticos (informativos, no son criterios de decision) ----
    p_det = np.array(fits["M_det_off"][1]["p"])
    p_full = np.array(best_a["p"])
    I1_tr = np.abs(F.X_TR @ F.unpack_unitary(p_full[:16]).T) ** 2
    diag = {
        "det_off_vs_M1_test_pred_mismatches": int(np.sum(pred["M_det_off"] != pred_m1)),
        "det_off_train_loss_seleccionado": float(xent_of(p_det, logits_det_off, F.X_TR, F.Y_TR)),
        "M1_train_loss_guardada_f3": f3["m1"]["train_loss"],
        "M_full_I1_train_quantiles_05_25_50_75_95_99": [float(q) for q in
                                                        np.quantile(I1_tr, [0.05, 0.25, 0.5, 0.75, 0.95, 0.99])],
        "M_full_I1_train_max": float(I1_tr.max()),
        "M_full_frac_I1_menor_1": float((I1_tr < 1).mean()),
        "M_full_frac_I1_mayor_igual_1": float((I1_tr >= 1).mean()),
        "M_full_frac_I1_mayor_igual_2": float((I1_tr >= 2).mean()),
        "M_real_restarts_que_agotan_maxiter": int(sum(1 for r in fits["M_real"][0] if r["nit"] >= MAXITER)),
        "nota": "M_det_off y M1 tienen el mismo optimo; T(I) de periodo 2 con V_pi=1, theta_b=0. "
                "La causa de H-A1 negativa no esta probada aqui; es una hipotesis a contrastar.",
    }

    out = {
        "contrato": "CONTRATO-ABLACION.md",
        "diagnosticos": diag,
        "protocolo": "L-BFGS-B, maxiter 300, 8 reinicios (semillas 1..8), seleccion por perdida de entrenamiento, "
                     "IC pareado 95 % con 1000 remuestreos (run_f3b.paired_ci, semilla 20261013)",
        "controles": {"E0_reproduccion_M_full_F3b": e0, "E1_reproduccion_M1_F3": e1,
                      "E2_reproduccion_M_real_F3b": e2},
        "verificaciones": {"V1_unitariedad": v1, "V2_identidad_clase_det_off": v2,
                           "V2b_equivalencia_constructiva_M1": v2b, "V3_bootstrap_degenerado": v3,
                           "V4_activacion": v4, "V5_reproduccion_IC_F3b": v5, "C_CONV": cconv},
        "modelos": models,
        "hipotesis": hyp,
        "comparaciones_informativas": info,
        "limites": ["modelo numerico, no dispositivo", "activacion con electronica de control y fotodetector",
                    "IC solo por muestreo de prueba (2000 muestras), una tarea sintetica congelada",
                    "M_det_off y M1 son la misma clase de funciones (V2, V2b)"],
        "tiempo_s": time.monotonic() - t0,
    }
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    # resumen en consola
    print("E0", e0["pass"], e0["test_acc"], "E1", e1["pass"], e1["test_acc"], "E2", e2["pass"], e2["test_acc"])
    print("V1", v1["pass"], "V2", v2["pass"], "V2b", v2b["pass"], "V3", v3["pass"], "V4", v4["pass"],
          "V5", v5["pass"], "CCONV", cconv["pass"])
    for name in MODELS:
        m = models[name]
        print(name, "seed", m["best_seed"], "train", m["train_acc"], "test", m["test_acc"],
              "success", m["selected_success"])
    for k, v in hyp.items():
        print(k, "punto", v["punto_estimado"], "bootstrap_media", v["media_bootstrap"], v["ci95"], v["pass"])
    print("tiempo_s", round(out["tiempo_s"], 2))


if __name__ == "__main__":
    main()
