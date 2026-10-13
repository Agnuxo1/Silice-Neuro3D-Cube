"""Digital references for the neuro-cube benchmark (outside Blender; test never read).

* majority: most frequent training class.
* logistic: sklearn LogisticRegression (C = 1, lbfgs); unconstrained gain, counted as a resource.
* mlp: sklearn MLPClassifier, one tanh hidden layer of n units, lbfgs, seeds 1-8,
  selected by validation log-loss; unconstrained gain (spectral norms reported).
* real_matched: same topology as the optical network with real weights
  W = eta Q1 diag(cos t) Q2^T (spectral norm <= eta, the optical layer's
  transmission), the same signed MZM activation and the same readout-gain grid,
  trained and selected exactly like the optical model (gain-matched reference).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

if sys.version_info[:2] == (3, 11):  # Blender's bundled Python: same numpy/scipy stack as the optical training
    sys.path.insert(0, "D:/TOOLS/blender_pylibs_neurocubo")
import numpy as np
import scipy

for _p in (str(Path(__file__).resolve().parents[2]), str(Path(__file__).resolve().parent)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import neurocubo_core as nc  # noqa: E402


def load_split(path: Path):
    with np.load(path, allow_pickle=False) as data:
        return data["X"].copy(), data["y"].copy()


def mlp_logits(weights: dict, x) -> np.ndarray:
    hidden = np.tanh(np.asarray(x) @ np.asarray(weights["W1"]) + np.asarray(weights["b1"]))
    return hidden @ np.asarray(weights["W2"]) + np.asarray(weights["b2"])


def logistic_logits(weights: dict, x) -> np.ndarray:
    return np.asarray(x) @ np.asarray(weights["coef"]).T + np.asarray(weights["intercept"])


def fit_sklearn_references(x, y, xv, yv, n: int, ports, seeds) -> dict:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import log_loss
    from sklearn.neural_network import MLPClassifier
    classes = int(len(ports))
    out = {}
    counts = np.bincount(y, minlength=classes)
    out["majority"] = {"class": int(np.argmax(counts)), "train_counts": counts.tolist(),
                       "validation_accuracy": float(np.mean(yv == np.argmax(counts)))}
    t0 = time.perf_counter()
    lr = LogisticRegression(C=1.0, max_iter=10000).fit(x, y)
    weights = {"coef": lr.coef_.tolist(), "intercept": lr.intercept_.tolist()}
    assert np.array_equal(logistic_logits(weights, xv).argmax(1), lr.predict(xv))
    out["logistic"] = {"weights": weights, "n_iter": int(lr.n_iter_.max()), "converged": bool(lr.n_iter_.max() < 10000),
                       "validation_accuracy": float(lr.score(xv, yv)),
                       "validation_log_loss": float(log_loss(yv, lr.predict_proba(xv), labels=range(classes))),
                       "weight_spectral_norm": float(np.linalg.norm(lr.coef_, 2)),
                       "parameters": int(lr.coef_.size + lr.intercept_.size), "seconds": time.perf_counter() - t0}
    starts = []
    for seed in seeds:
        t0 = time.perf_counter()
        mlp = MLPClassifier(hidden_layer_sizes=(n,), activation="tanh", solver="lbfgs", alpha=1e-4,
                            max_iter=5000, random_state=seed).fit(x, y)
        w = {"W1": mlp.coefs_[0].tolist(), "b1": mlp.intercepts_[0].tolist(),
             "W2": mlp.coefs_[1].tolist(), "b2": mlp.intercepts_[1].tolist()}
        assert np.array_equal(mlp_logits(w, xv).argmax(1), mlp.predict(xv))
        starts.append({"seed": seed, "weights": w, "n_iter": int(mlp.n_iter_),
                       "converged": bool(mlp.n_iter_ < 5000),
                       "validation_accuracy": float(mlp.score(xv, yv)),
                       "validation_log_loss": float(log_loss(yv, mlp.predict_proba(xv), labels=range(classes))),
                       "spectral_norms": [float(np.linalg.norm(mlp.coefs_[0], 2)),
                                          float(np.linalg.norm(mlp.coefs_[1], 2))],
                       "seconds": time.perf_counter() - t0})
    chosen = min(starts, key=lambda s: s["validation_log_loss"])
    out["mlp"] = {"selected_seed": chosen["seed"], "selected": chosen, "starts": starts,
                  "selection_rule": "minimum validation log-loss across seeds",
                  "parameters": int(n * n + n + n * classes + classes)}
    return out


def fit_real_matched(x, y, xv, yv, n: int, ports, gains, seeds, maxiter: int, threshold: float) -> dict:
    out = {}
    per_gain = []
    for gain in gains:
        cfg = nc.real_matched_config(n, gain, ports)
        records = []
        for seed in seeds:
            t0 = time.perf_counter()
            run = nc.fit_start(x, y, cfg, nc.init_params(cfg, seed), maxiter, threshold)
            for key in ("trajectory", "loss_history", "gradient_history"):
                run.pop(key)
            run.update({"seed": seed, "gain": gain, "seconds": time.perf_counter() - t0,
                        "validation_cross_entropy": nc.cross_entropy(run["parameters"], xv, yv, cfg),
                        "train_accuracy": nc.accuracy(run["parameters"], x, y, cfg),
                        "validation_accuracy": nc.accuracy(run["parameters"], xv, yv, cfg)})
            records.append(run)
        converged = [r for r in records if r["converged"]]
        best = min(converged or records, key=lambda r: r["training_loss"])
        per_gain.append({"gain": gain, "selected_seed": best["seed"], "selected_converged": best["converged"],
                         "converged_starts": len(converged),
                         "validation_cross_entropy": best["validation_cross_entropy"],
                         "validation_accuracy": best["validation_accuracy"], "starts": records})
    eligible = [g for g in per_gain if g["selected_converged"]]
    chosen_gain = min(eligible or per_gain, key=lambda g: (g["validation_cross_entropy"], -g["validation_accuracy"]))
    final = next(r for r in chosen_gain["starts"] if r["seed"] == chosen_gain["selected_seed"])
    out["real_matched"] = {"chosen_gain": chosen_gain["gain"], "chosen_seed": final["seed"],
                           "chosen_converged": final["converged"], "no_converged_selection": not eligible,
                           "parameters_vector": final["parameters"], "per_gain": per_gain,
                           "eta": nc.real_matched_config(n, 1.0, ports).etas[0],
                           "parameters": 2 * n * n, "selection_rule": "same as the optical model"}
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--ports", type=int, nargs="+", default=[0, 1, 2, 3])
    parser.add_argument("--gains", type=float, nargs="+", default=[1.0, 4.0, 16.0])
    parser.add_argument("--seeds", type=int, nargs="+", default=list(range(1, 9)))
    parser.add_argument("--maxiter", type=int, default=5000)
    parser.add_argument("--gradient-threshold", type=float, default=1e-5)
    parser.add_argument("--part", choices=["sklearn", "real_matched"], required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError("Output must be new")
    folder = args.data_dir / args.task
    x, y = load_split(folder / ("train_N%d.npz" % args.n))
    xv, yv = load_split(folder / ("validation_N%d.npz" % args.n))
    t0 = time.perf_counter()
    if args.part == "sklearn":
        import sklearn
        result = fit_sklearn_references(x, y, xv, yv, args.n, args.ports, args.seeds)
        stack = {"sklearn": sklearn.__version__}
    else:
        result = fit_real_matched(x, y, xv, yv, args.n, args.ports, args.gains, args.seeds, args.maxiter,
                                  args.gradient_threshold)
        stack = {}
    stack.update({"python": sys.version.split()[0], "numpy": np.__version__, "scipy": scipy.__version__})
    result.update({"part": args.part, "environment": stack,"task": args.task, "n": args.n, "ports": args.ports, "scope": nc.SCOPE,
                   "data_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in (folder / ("train_N%d.npz" % args.n),
                                             folder / ("validation_N%d.npz" % args.n))},
                   "test_evaluated": False, "seconds_total": time.perf_counter() - t0})
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=1)
    summary = ({"logistic_val": result["logistic"]["validation_accuracy"],
                "mlp_val": result["mlp"]["selected"]["validation_accuracy"]} if args.part == "sklearn" else
               {"real_matched_gain": result["real_matched"]["chosen_gain"],
                "real_matched_converged": result["real_matched"]["chosen_converged"]})
    print(json.dumps({"task": args.task, "n": args.n, "part": args.part, **summary}))


if __name__ == "__main__":
    main()
