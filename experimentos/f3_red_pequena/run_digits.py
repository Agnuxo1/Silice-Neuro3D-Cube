"""F3-c (CONTRATO-DIGITS.md): same model family on real data (sklearn load_digits, digits 0-3).

Usage:
  python -B run_digits.py train <m1|m2|m3|a|b>   one model per process (8 restarts)
  python -B run_digits.py aggregate              H-D1..H-D3 with paired bootstrap
"""
import json
import pathlib
import sys

import numpy as np
from scipy.optimize import minimize
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_f3 as F  # noqa: E402
import run_f3b as G  # noqa: E402

SEEDS = range(1, 9)
NPAR = {"m1": 16, "m2": 16, "m3": 40, "a": 32, "b": 32}


def load():
    d = load_digits()
    mask = np.isin(d.target, [0, 1, 2, 3])
    X, y = d.data[mask], d.target[mask]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, stratify=y, random_state=20261020)
    sc = StandardScaler().fit(Xtr)
    pca = PCA(4, random_state=0).fit(sc.transform(Xtr))
    T = lambda Z: pca.transform(sc.transform(Z))  # noqa: E731
    return T(Xtr), ytr, T(Xte), yte


def loss_fn(model):
    return G.xent if model in ("a", "b") else F.xent


def logits_fn(model):
    return G.LOG[model] if model in ("a", "b") else (lambda p, X: F.logits(model, p, X))


def acc_fn(model, p, X, y):
    return float((logits_fn(model)(p, X).argmax(1) == y).mean())


def train(model):
    Xtr, ytr, Xte, yte = load()
    best = None
    for s in SEEDS:
        p0 = 0.5 * np.random.default_rng(s).standard_normal(NPAR[model])
        res = minimize(loss_fn(model), p0, args=(model, Xtr, ytr), method="L-BFGS-B", options={"maxiter": 300})
        if best is None or res.fun < best["train_loss"]:
            best = {"seed": s, "train_loss": float(res.fun), "p": res.x}
    p = best["p"]
    out = {"model": model, "n_params": NPAR[model], "best_seed": best["seed"], "train_loss": best["train_loss"],
           "train_acc": acc_fn(model, p, Xtr, ytr), "test_acc": acc_fn(model, p, Xte, yte),
           "test_pred": logits_fn(model)(p, Xte).argmax(1).tolist(), "n_test": int(len(yte))}
    (HERE / "digits_resultados").mkdir(exist_ok=True)
    (HERE / "digits_resultados" / f"{model}.json").write_text(json.dumps(out, ensure_ascii=False) + "\n",
                                                              encoding="utf-8", newline="\n")
    print(json.dumps({k: out[k] for k in ("model", "best_seed", "train_acc", "test_acc")}))


def aggregate():
    R = {m: json.loads((HERE / "digits_resultados" / f"{m}.json").read_text(encoding="utf-8")) for m in NPAR}
    _, _, _, yte = load()
    pm1, pm2, pb = (np.array(R[m]["test_pred"]) for m in ("m1", "m2", "b"))
    h1 = R["m1"]["test_acc"] >= 0.70
    h2 = R["b"]["test_acc"] >= 0.90
    d_12, ci_12 = G.paired_ci(pm1, pm2, yte)
    h3 = ci_12[1] < 0 and d_12 < -0.05
    agg = {"H-D1": {"test_acc_M1": R["m1"]["test_acc"], "threshold": 0.70, "passed": bool(h1)},
           "H-D2": {"test_acc_B": R["b"]["test_acc"], "threshold": 0.90, "passed": bool(h2)},
           "H-D3": {"paired_diff_M1_minus_M2": d_12, "ci95": ci_12, "threshold": -0.05, "passed": bool(h3)},
           "all_models": {m: {"n_params": R[m]["n_params"], "train_acc": R[m]["train_acc"],
                              "test_acc": R[m]["test_acc"]} for m in NPAR}}
    (HERE / "digits_aggregate.json").write_text(json.dumps(agg, indent=1, ensure_ascii=False) + "\n",
                                                encoding="utf-8", newline="\n")
    print(json.dumps({k: agg[k]["passed"] for k in ("H-D1", "H-D2", "H-D3")}),
          {m: round(R[m]["test_acc"], 4) for m in NPAR})


if __name__ == "__main__":
    if sys.argv[1] == "train":
        train(sys.argv[2])
    elif sys.argv[1] == "aggregate":
        aggregate()
    else:
        raise SystemExit("unknown command")
