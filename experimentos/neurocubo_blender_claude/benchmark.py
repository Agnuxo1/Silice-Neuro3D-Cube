"""One-shot benchmark of the frozen neuro-cube against digital references.

Phase A (no labels): CPU reference outputs through an independent path
(agentkit.mzi.clements_reconstruct), equivalence with the Blender outputs,
reference predictions, fabrication-error robustness with and without
recalibration on the training set, DAC quantization and CPU cost. All test
predictions are saved and hashed. Phase B: the custodian reveals the sealed test
labels once per task. Phase C: metrics, intervals, paired differences,
preregistered three-zone decisions, responses panel data and criteria.

python -B benchmark.py run --results-dir R --data-dir D --sealed-dir S --protocol P
python -B benchmark.py finalize --results-dir R --protocol P --out resultados/agent/prereg/NEUROCUBO_result.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for _p in (str(ROOT), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import custodian  # noqa: E402
import neurocubo_core as nc  # noqa: E402
import references as refs  # noqa: E402
from agentkit import mzi as akm  # noqa: E402
from agentkit import stats as aks  # noqa: E402
from agentkit.evidence import canonical  # noqa: E402
from agentkit.learning import paired_accuracy  # noqa: E402

SEED = 20261013
NONINFERIORITY_MARGIN = 0.05
TASK_INDEX = {"dev03": 0, "res47": 1, "syn": 2}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=1)


def load(path: Path, *keys):
    with np.load(path, allow_pickle=False) as data:
        return [data[k].copy() for k in keys]


# ----------------------------------------------------------------------------- independent CPU reference
def independent_forward(model: dict, x) -> tuple[np.ndarray, np.ndarray]:
    """Logits and intensities using agentkit.mzi.clements_reconstruct for every mesh."""
    transfers = []
    for layer in model["layers"]:
        spec, p = nc.spec_from_geometry_layer(layer)
        dec = nc.decomposition_from_params(p, spec)
        transfers.append(spec.eta * np.exp(1j * spec.common_phase) * akm.clements_reconstruct(dec, spec.eps))
    oe, ro = model["optoelectronic_stage"], model["readout"]
    z1 = np.asarray(x, float) @ transfers[0].T
    a = np.cos(0.5 * (math.pi * np.abs(z1) ** 2 / oe["v_pi"] + oe["bias"]))
    intensity = np.abs(a @ transfers[1].T) ** 2
    return ro["gain"] * intensity[:, ro["ports"]], intensity


# ----------------------------------------------------------------------------- metrics
def confusion(pred, labels, classes: int) -> np.ndarray:
    m = np.zeros((classes, classes), dtype=int)
    for t, p in zip(labels, pred):
        m[int(t), int(p)] += 1
    return m


def balanced_accuracy(pred, labels, classes: int) -> float:
    m = confusion(pred, labels, classes)
    return float(np.mean([m[c, c] / m[c].sum() for c in range(classes) if m[c].sum() > 0]))


def macro_f1(pred, labels, classes: int) -> float:
    m = confusion(pred, labels, classes)
    scores = []
    for c in range(classes):
        tp, fp, fn = m[c, c], m[:, c].sum() - m[c, c], m[c].sum() - m[c, c]
        scores.append(0.0 if 2 * tp + fp + fn == 0 else 2 * tp / (2 * tp + fp + fn))
    return float(np.mean(scores))


def metric_block(pred, labels, classes: int, repeats: int) -> dict:
    pred, labels = np.asarray(pred), np.asarray(labels)
    k, n = int(np.sum(pred == labels)), len(labels)
    rng = np.random.default_rng(SEED)
    ba, f1 = [], []
    for _ in range(repeats):
        idx = rng.integers(0, n, n)
        ba.append(balanced_accuracy(pred[idx], labels[idx], classes))
        f1.append(macro_f1(pred[idx], labels[idx], classes))
    return {"accuracy": k / n, "accuracy_ci95_clopper_pearson": aks.clopper_pearson(k, n),
            "balanced_accuracy": balanced_accuracy(pred, labels, classes),
            "balanced_accuracy_ci95_bootstrap": np.percentile(ba, [2.5, 97.5]).tolist(),
            "macro_f1": macro_f1(pred, labels, classes),
            "macro_f1_ci95_bootstrap": np.percentile(f1, [2.5, 97.5]).tolist(),
            "confusion_matrix_rows_true": confusion(pred, labels, classes).tolist(), "n": n, "correct": k}


def noninferiority(optical, reference, labels, repeats: int) -> dict:
    """Paired difference (optical - reference) and the three-zone verdict on reference - optical."""
    paired = paired_accuracy(optical, reference, labels, repeats, SEED)
    lo, hi = paired["percentile_ci95"]
    decision = aks.three_zone_decision(-hi, -lo, NONINFERIORITY_MARGIN)
    meaning = {"CONFIRMED": "non-inferior within the margin", "FALSIFIED": "inferior by more than the margin",
               "INCONCLUSIVE": "interval contains the margin", "MODEL_CONTROL_FAIL": "n/a"}[decision["verdict"]]
    return {"paired_first_minus_reference": paired, "three_zone_on_reference_minus_first": decision,
            "margin": NONINFERIORITY_MARGIN, "reading": meaning,
            "first_superior": bool(lo > 0), "superiority_rule": "paired 95 % CI lower bound > 0"}


# ----------------------------------------------------------------------------- phase A
def phase_a(args, task: str, n: int, bundle: dict, info: dict) -> None:
    res = args.results_dir
    folder = args.data_dir / task
    key = "%s_N%d" % (task, n)
    model = json.loads((res / "models" / ("model_%s.json" % key)).read_text(encoding="utf-8"))
    if model["sha256"] != nc.geometry_hash(model):
        raise RuntimeError("Frozen model hash mismatch: " + key)
    cfg, params = nc.config_from_geometry(model)
    (x_test,) = load(folder / ("test_X_N%d.npz" % n), "X")
    x_train, y_train = load(folder / ("train_N%d.npz" % n), "X", "y")
    logits_cpu, intensity_cpu = independent_forward(model, x_test)
    logits_nc, intensity_nc, _ = nc.forward(params, x_test, cfg)
    logits_bl, intensity_bl, pred_bl = load(res / "blender_eval" / ("outputs_%s.npz" % key),
                                            "logits", "intensity", "predictions")
    pred_cpu = logits_cpu.argmax(1)
    equivalence = {"predictions_identical": bool(np.array_equal(pred_cpu, pred_bl)
                                                 and np.array_equal(pred_cpu, logits_nc.argmax(1))),
                   "max_abs_logit_difference": float(np.max(abs(logits_cpu - logits_bl))),
                   "max_abs_intensity_difference": float(np.max(abs(intensity_cpu - intensity_bl))),
                   "max_abs_logit_difference_core_vs_independent": float(np.max(abs(logits_cpu - logits_nc))),
                   "min_top2_logit_gap": float(np.min(np.diff(np.sort(logits_cpu, 1)[:, -2:], axis=1)))}
    bundle["optical_" + key] = pred_cpu
    bundle["optical_logits_" + key] = logits_cpu
    bundle["optical_intensity_" + key] = intensity_cpu
    ref = json.loads((res / "references" / ("references_%s.json" % key)).read_text(encoding="utf-8"))
    ref_rm = json.loads((res / "references" / ("real_matched_%s.json" % key)).read_text(encoding="utf-8"))
    bundle["majority_" + key] = np.full(len(x_test), ref["majority"]["class"])
    bundle["logistic_" + key] = refs.logistic_logits(ref["logistic"]["weights"], x_test).argmax(1)
    bundle["mlp_" + key] = refs.mlp_logits(ref["mlp"]["selected"]["weights"], x_test).argmax(1)
    rm = ref_rm["real_matched"]
    rcfg = nc.real_matched_config(n, rm["chosen_gain"], cfg.ports)
    bundle["real_matched_" + key] = nc.predict(rm["parameters_vector"], x_test, rcfg)
    robustness = {"sigmas": args.sigmas, "correlation": args.correlation, "realizations": args.realizations,
                  "recalibration": "ORACLE UPPER BOUND: all phases re-optimized on the training set on the "
                                   "erroneous device with exact knowledge of its transfer (T27 strategy B), "
                                   "start = frozen phases, L-BFGS-B maxiter %d" % args.recal_maxiter,
                  "conditions": []}
    for si, sigma in enumerate(args.sigmas):
        recal_diag = []
        for r in range(args.realizations):
            rng = np.random.default_rng([SEED, TASK_INDEX[task], n, si, r])
            cfg_e = nc.with_errors(cfg, nc.draw_splitter_errors(cfg, sigma, args.correlation, rng))
            bundle["robust_norecal_%s_s%d_r%d" % (key, si, r)] = nc.predict(params, x_test, cfg_e)
            run = nc.fit_start(x_train, y_train, cfg_e, params, args.recal_maxiter, 1e-5)
            bundle["robust_recal_%s_s%d_r%d" % (key, si, r)] = nc.predict(run["parameters"], x_test, cfg_e)
            recal_diag.append({"r": r, "iterations": run["iterations"], "converged": run["converged"],
                               "gradient_infinity_norm": run["gradient_infinity_norm"],
                               "train_accuracy": nc.accuracy(run["parameters"], x_train, y_train, cfg_e),
                               "train_accuracy_before": nc.accuracy(params, x_train, y_train, cfg_e)})
        robustness["conditions"].append({"sigma": sigma, "recalibration_diagnostics": recal_diag})
    for bits in args.bits:
        bundle["dac_%s_b%d" % (key, bits)] = nc.predict(nc.quantize_phases(params, bits), x_test, cfg)
    single = []
    for r in range(200):
        t0 = time.perf_counter()
        nc.forward(params, x_test[r % len(x_test)][None, :], cfg)
        single.append(time.perf_counter() - t0)
    candidates = json.loads((res / "training" / ("candidates_%s.json" % key)).read_text(encoding="utf-8"))
    blender_eval = json.loads((res / "blender_eval" / ("outputs_%s.json" % key)).read_text(encoding="utf-8"))
    info[key] = {"equivalence": equivalence, "robustness": robustness, "model_sha256": model["sha256"],
                 "gain": cfg.gain, "ports": list(cfg.ports), "classes": len(cfg.ports),
                 "chosen_converged": candidates["chosen_converged"], "chosen_seed": candidates["chosen_seed"],
                 "training_seconds_total": candidates["seconds_total"],
                 "keyframes_total": candidates["keyframes_total"],
                 "converged_starts_per_gain": {str(g["gain"]): g["converged_starts"] for g in candidates["per_gain"]},
                 "reference_summary": {"logistic_parameters": ref["logistic"]["parameters"],
                                       "logistic_weight_spectral_norm": ref["logistic"]["weight_spectral_norm"],
                                       "mlp_parameters": ref["mlp"]["parameters"],
                                       "mlp_spectral_norms": ref["mlp"]["selected"]["spectral_norms"],
                                       "real_matched_gain": rm["chosen_gain"],
                                       "real_matched_converged": rm["chosen_converged"],
                                       "optical_heater_parameters": cfg.n_params},
                 "cost": {"cpu_single_sample_seconds_median": float(np.median(single)),
                          "blender_single_sample_seconds_median": blender_eval["single_sample_seconds_median"],
                          "blender_batch_seconds_per_sample": blender_eval["batch_seconds_per_sample"],
                          "note": "CPU simulation time on one thread; NOT optical latency"}}


# ----------------------------------------------------------------------------- phase C
def phase_c(args, task: str, n: int, bundle: dict, labels: np.ndarray, info: dict) -> dict:
    key = "%s_N%d" % (task, n)
    classes = info[key]["classes"]
    out = {"models": {}, "comparisons": {}}
    for name in ("optical", "majority", "logistic", "mlp", "real_matched"):
        out["models"][name] = metric_block(bundle["%s_%s" % (name, key)], labels, classes, args.bootstrap)
    optical = bundle["optical_" + key]
    for name in ("logistic", "mlp", "real_matched", "majority"):
        out["comparisons"]["optical_vs_" + name] = noninferiority(optical, bundle["%s_%s" % (name, key)],
                                                                  labels, args.bootstrap)
    out["comparisons"]["mlp_vs_logistic"] = noninferiority(bundle["mlp_" + key], bundle["logistic_" + key],
                                                           labels, args.bootstrap)
    base = out["models"]["optical"]["accuracy"]
    rob = []
    for si, sigma in enumerate(args.sigmas):
        accs = {}
        for mode in ("norecal", "recal"):
            values = np.array([np.mean(bundle["robust_%s_%s_s%d_r%d" % (mode, key, si, r)] == labels)
                               for r in range(args.realizations)])
            accs[mode] = {"mean": float(values.mean()), "p05": float(np.percentile(values, 5)),
                          "min": float(values.min()), "drop_mean": float(base - values.mean()),
                          "values": values.tolist()}
        diag = info[key]["robustness"]["conditions"][si]["recalibration_diagnostics"]
        rob.append({"sigma": sigma, "without_recalibration": accs["norecal"], "with_recalibration": accs["recal"],
                    "recalibration_converged_fraction": float(np.mean([d["converged"] for d in diag]))})
    out["robustness"] = [{"sigma": 0.0, "accuracy": base}] + rob
    out["dac"] = [{"bits": b, "accuracy": float(np.mean(bundle["dac_%s_b%d" % (key, b)] == labels)),
                   "drop": float(base - np.mean(bundle["dac_%s_b%d" % (key, b)] == labels))} for b in args.bits]
    out["majority_test_share"] = out["models"]["majority"]["accuracy"]
    out["cp_low_minus_majority"] = out["models"]["optical"]["accuracy_ci95_clopper_pearson"][0] - out["majority_test_share"]
    wrong = np.flatnonzero(optical != labels)
    out["failures"] = {"count": int(len(wrong)), "test_positions": wrong.tolist(),
                       "true": labels[wrong].tolist(), "predicted": optical[wrong].tolist()}
    return out


def responses(args, task: str, n: int, bundle: dict, labels: np.ndarray) -> dict:
    key = "%s_N%d" % (task, n)
    (raw,) = load(args.data_dir / task / ("test_X_N%d.npz" % n), "raw_indices")
    images = custodian.load_images(task, raw, args.data_dir)
    logits, intensity, pred = bundle["optical_logits_" + key], bundle["optical_intensity_" + key], bundle["optical_" + key]
    probs = np.exp(logits - logits.max(1, keepdims=True))
    probs /= probs.sum(1, keepdims=True)
    chosen = []
    for c in range(logits.shape[1]):
        chosen += list(np.flatnonzero(labels == c)[:3])
    entry = lambda i: {"test_position": int(i), "raw_index": int(raw[i]), "true": int(labels[i]),
                       "predicted": int(pred[i]), "correct": bool(pred[i] == labels[i]),
                       "output_intensities": intensity[i].tolist(), "softmax": probs[i].tolist(),
                       "image_8x8": images[i].tolist()}
    return {"task": task, "n": n, "selection": "first three test examples of each class in test order",
            "examples": [entry(i) for i in chosen],
            "failures": [entry(i) for i in np.flatnonzero(pred != labels)]}


def run(args) -> None:
    """Phase A for every task, then one reveal per task, then the metrics."""
    res = args.results_dir
    bench = res / "benchmark"
    if (bench / "phase_a_info.json").exists():
        raise FileExistsError("Phase A was already run; the test is evaluated once (use `metrics` to resume)")
    bench.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    info = {}
    for task in args.tasks:
        bundle = {}
        for n in args.sizes:
            phase_a(args, task, n, bundle, info)
        with (bench / ("predictions_frozen_%s.npz" % task)).open("xb") as handle:
            np.savez_compressed(handle, **bundle)
    settings = {k: (str(v) if isinstance(v, Path) else v) for k, v in vars(args).items()}
    write_new_json(bench / "phase_a_info.json", {"per_config": info, "seconds": time.perf_counter() - started,
                                                 "settings": settings})
    for task in args.tasks:
        custodian.reveal(task, args.data_dir, args.sealed_dir, bench / ("predictions_frozen_%s.npz" % task), bench)
    metrics(args)


def metrics(args) -> None:
    """Metrics from the frozen predictions and the revealed labels (no model is evaluated here)."""
    res = args.results_dir
    bench = res / "benchmark"
    if (bench / "benchmark.json").exists():
        raise FileExistsError("benchmark.json already exists")
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    phase = json.loads((bench / "phase_a_info.json").read_text(encoding="utf-8"))
    info = phase["per_config"]
    report = {"scope": nc.SCOPE, "protocol_sha256": hashlib.sha256(canonical(protocol)).hexdigest(),
              "phase_a_seconds": phase["seconds"], "tasks": {}, "equivalence": {}, "per_config": info}
    for task in args.tasks:
        path = bench / ("predictions_frozen_%s.npz" % task)
        receipt = json.loads((bench / ("reveal_receipt_%s.json" % task)).read_text(encoding="utf-8"))
        if receipt["predictions_sha256"] != sha(path):
            raise RuntimeError("Frozen predictions changed after the reveal: " + task)
        with np.load(path, allow_pickle=False) as data:
            bundle = {k: data[k].copy() for k in data.files}
        (labels,) = load(bench / receipt["labels_file"], "y")
        report["tasks"][task] = {"predictions_sha256": receipt["predictions_sha256"],
                                 "reveal": receipt["revealed_at_utc"], "results": {}}
        for n in args.sizes:
            report["tasks"][task]["results"]["N%d" % n] = phase_c(args, task, n, bundle, labels, info)
        if task == args.show_task:
            report["responses"] = responses(args, task, args.show_n, bundle, labels)
            other = [v for v in args.sizes if v != args.show_n][0]
            report["responses_other_size"] = responses(args, task, other, bundle, labels)
    eq = [info[k]["equivalence"] for k in info]
    report["equivalence"] = {"predictions_identical": all(e["predictions_identical"] for e in eq),
                             "max_abs_output_difference": max(max(e["max_abs_logit_difference"],
                                                                  e["max_abs_intensity_difference"]) for e in eq)}
    write_new_json(bench / "benchmark.json", report)
    print(json.dumps({"equivalence": report["equivalence"],
                      "optical_accuracy": {t: {k: v["models"]["optical"]["accuracy"]
                                               for k, v in report["tasks"][t]["results"].items()}
                                           for t in report["tasks"]}}))


def finalize(args) -> None:
    """Criteria metrics and the artifact list for the preregistration audit."""
    res = args.results_dir
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    report = json.loads((res / "benchmark" / "benchmark.json").read_text(encoding="utf-8"))
    check = json.loads((res / "checks" / "geometry_roundtrip.json").read_text(encoding="utf-8"))
    tests = json.loads((res / "checks" / "core_tests.json").read_text(encoding="utf-8"))
    reserved = report["tasks"][args.reserved_task]["results"]
    metrics = {
        "geometry_reconstruction_error_max": check["geometry_reconstruction_error_max"],
        "gradient_check_relative_error_max": max(tests["gradient_relative_errors"].values()),
        "blender_cpu_predictions_identical": report["equivalence"]["predictions_identical"],
        "blender_cpu_max_abs_output_difference": report["equivalence"]["max_abs_output_difference"],
        "optical_configs_converged_fraction": float(np.mean([v["chosen_converged"]
                                                             for v in report["per_config"].values()])),
        "reserved_optical_cp_low_minus_majority_min": min(v["cp_low_minus_majority"] for v in reserved.values()),
        "reserved_recal_drop_sigma002_max": max(next(r for r in v["robustness"] if r["sigma"] == 0.02)
                                                ["with_recalibration"]["drop_mean"] for v in reserved.values()),
        "reserved_dac10_drop_max": max(next(d for d in v["dac"] if d["bits"] == 10)["drop"]
                                       for v in reserved.values()),
    }
    planned = protocol["planned_artifacts"]
    produced = [p for p in planned if (ROOT / p).exists()]
    result = {"experiment_id": protocol["experiment_id"],
              "protocol_sha256": hashlib.sha256(canonical(protocol)).hexdigest(),
              "scope": protocol["scope"], "status": "completed", "artifacts": produced, "metrics": metrics,
              "planned_but_missing": [p for p in planned if p not in produced]}
    write_new_json(args.out, result)
    print(json.dumps(result["metrics"], indent=1))


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    r = sub.add_parser("run")
    m = sub.add_parser("metrics")
    r.add_argument("--data-dir", type=Path, required=True)
    r.add_argument("--sealed-dir", type=Path, required=True)
    r.add_argument("--tasks", nargs="+", default=["dev03", "res47"])
    r.add_argument("--sizes", type=int, nargs="+", default=[4, 8])
    r.add_argument("--sigmas", type=float, nargs="+", default=[0.01, 0.02, 0.05])
    r.add_argument("--correlation", type=float, default=0.8)
    r.add_argument("--realizations", type=int, default=20)
    r.add_argument("--recal-maxiter", type=int, default=500)
    r.add_argument("--bits", type=int, nargs="+", default=[8, 10, 12])
    r.add_argument("--bootstrap", type=int, default=2000)
    r.add_argument("--show-task", default="res47")
    r.add_argument("--show-n", type=int, default=8)
    m.add_argument("--data-dir", type=Path, required=True)
    m.add_argument("--tasks", nargs="+", default=["dev03", "res47"])
    m.add_argument("--sizes", type=int, nargs="+", default=[4, 8])
    m.add_argument("--sigmas", type=float, nargs="+", default=[0.01, 0.02, 0.05])
    m.add_argument("--realizations", type=int, default=20)
    m.add_argument("--bits", type=int, nargs="+", default=[8, 10, 12])
    m.add_argument("--bootstrap", type=int, default=2000)
    m.add_argument("--show-task", default="res47")
    m.add_argument("--show-n", type=int, default=8)
    f = sub.add_parser("finalize")
    f.add_argument("--out", type=Path, required=True)
    f.add_argument("--reserved-task", default="res47")
    for p in (r, m, f):
        p.add_argument("--results-dir", type=Path, required=True)
        p.add_argument("--protocol", type=Path, required=True)
    args = parser.parse_args()
    {"run": run, "metrics": metrics, "finalize": finalize}[args.command](args)


if __name__ == "__main__":
    main()
