"""F3-b (CONTRATO-F3-RED-FUNCIONAL.md): two-layer network with optoelectronic activation.

Usage:
  python -B run_f3b.py seed <a|b> <s>   one restart per process (CPU budget <30 s)
  python -B run_f3b.py select <a|b>     pick the restart with the lowest training loss
  python -B run_f3b.py aggregate        H-F1..H-F3 with paired bootstrap

A: two unitary meshes (32 real params), intensity readout, MZM activation.
B: same topology with real 4x4 weights (32 params), same activation.
"""
import json
import pathlib
import sys

import numpy as np
from scipy.optimize import minimize

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_f3 as F  # noqa: E402  (frozen task and unitary parameterisation)

V_PI, THETA_B = 1.0, 0.0
SEEDS = range(1, 9)


def activation(I):
    """Mach-Zehnder transmission driven by detected power: T = (1 + cos(pi I / V_pi + theta_b)) / 2."""
    return (1.0 + np.cos(np.pi * I / V_PI + THETA_B)) / 2.0


def logits_A(p, X):
    U1 = F.unpack_unitary(p[:16])
    U2 = F.unpack_unitary(p[16:32])
    I1 = np.abs(X @ U1.T) ** 2
    a2 = np.sqrt(np.clip(activation(I1), 0.0, 1.0))
    return np.abs(a2 @ U2.T) ** 2


def logits_B(p, X):
    W1 = p[:16].reshape(4, 4)
    W2 = p[16:32].reshape(4, 4)
    I1 = (X @ W1.T) ** 2
    a2 = np.sqrt(np.clip(activation(I1), 0.0, 1.0))
    return (a2 @ W2.T) ** 2


LOG = {"a": logits_A, "b": logits_B}


def xent(p, model, X, y):
    z = LOG[model](p, X)
    z = z - z.max(1, keepdims=True)
    lse = np.log(np.exp(z).sum(1))
    return float((lse - z[np.arange(len(y)), y]).mean())


def acc(model, p, X, y):
    return float((LOG[model](p, X).argmax(1) == y).mean())


def run_seed(model, seed):
    d = HERE / "f3b_seeds"
    d.mkdir(exist_ok=True)
    p0 = 0.5 * np.random.default_rng(seed).standard_normal(32)
    res = minimize(xent, p0, args=(model, F.X_TR, F.Y_TR), method="L-BFGS-B", options={"maxiter": 300})
    rec = {"model": model, "seed": seed, "train_loss": float(res.fun), "p": res.x.tolist(),
           "train_acc": acc(model, res.x, F.X_TR, F.Y_TR), "test_acc": acc(model, res.x, F.X_TE, F.Y_TE),
           "test_pred": LOG[model](res.x, F.X_TE).argmax(1).tolist()}
    (d / f"{model}_s{seed}.json").write_text(json.dumps(rec, ensure_ascii=False) + "\n",
                                             encoding="utf-8", newline="\n")
    print(json.dumps({"model": model, "seed": seed, "train_loss": round(rec["train_loss"], 5)}))


def select(model):
    """Restart with the lowest training loss (never chosen by test accuracy)."""
    recs = [json.loads(f.read_text(encoding="utf-8")) for f in (HERE / "f3b_seeds").glob(f"{model}_s*.json")]
    best = min(recs, key=lambda r: r["train_loss"])
    out = {"model": model, "n_params": 32, "best_seed": best["seed"], "n_restarts": len(recs),
           "train_loss": best["train_loss"], "train_acc": best["train_acc"], "test_acc": best["test_acc"],
           "test_pred": best["test_pred"]}
    store = HERE / "f3b_resultados.json"
    data = json.loads(store.read_text(encoding="utf-8")) if store.exists() else {}
    data[model] = out
    store.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: out[k] for k in ("model", "best_seed", "n_restarts", "train_acc", "test_acc")}))


def paired_ci(pa, pb, y, B=1000, seed=20261013):
    rng = np.random.default_rng(seed)
    ca, cb = (pa == y).astype(float), (pb == y).astype(float)
    n = len(y)
    d = np.array([ca[idx].mean() - cb[idx].mean() for idx in (rng.integers(0, n, n) for _ in range(B))])
    return float(d.mean()), [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]


def aggregate():
    data = json.loads((HERE / "f3b_resultados.json").read_text(encoding="utf-8"))
    f3 = json.loads((HERE / "f3_resultados.json").read_text(encoding="utf-8"))
    A, B = data["a"], data["b"]
    pa, pb = np.array(A["test_pred"]), np.array(B["test_pred"])
    pm1 = np.array(f3["m1"]["test_pred"])
    h1 = A["test_acc"] >= 0.70
    h2 = A["test_acc"] >= B["test_acc"] - 0.02
    d_ab, ci_ab = paired_ci(pa, pb, F.Y_TE)
    d_a1, ci_a1 = paired_ci(pa, pm1, F.Y_TE)
    h3 = ci_a1[0] > 0
    agg = {"H-F1": {"test_acc_A": A["test_acc"], "threshold": 0.70, "passed": bool(h1)},
           "H-F2": {"test_acc_A": A["test_acc"], "test_acc_B": B["test_acc"], "margin": 0.02,
                    "paired_diff_AB": d_ab, "ci95_AB": ci_ab, "passed": bool(h2)},
           "H-F3": {"test_acc_A": A["test_acc"], "test_acc_F3_M1": f3["m1"]["test_acc"],
                    "paired_diff_A_minus_M1": d_a1, "ci95": ci_a1, "passed": bool(h3)}}
    (HERE / "f3b_aggregate.json").write_text(json.dumps(agg, indent=1, ensure_ascii=False) + "\n",
                                             encoding="utf-8", newline="\n")
    print(json.dumps({k: v["passed"] for k, v in agg.items()}), "A", A["test_acc"], "B", B["test_acc"])


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "seed":
        run_seed(sys.argv[2], int(sys.argv[3]))
    elif cmd == "select":
        select(sys.argv[2])
    elif cmd == "aggregate":
        aggregate()
    else:
        raise SystemExit("unknown command")
