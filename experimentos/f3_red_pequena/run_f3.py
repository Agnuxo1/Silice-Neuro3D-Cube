"""F3 (CONTRATO-F3.md): small unitary optical mesh vs electronic baselines.

Usage: python -B run_f3.py <m1|m2|m3|aggregate>
One model per process (each under 30 s on one thread). Results go to
f3_resultados.json, one key per model. The aggregate step computes H1-H3 and
the energy break-even from those results.
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
from scipy.linalg import expm  # noqa: E402
from scipy.optimize import minimize  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
N_TR, N_TE, K = 2000, 2000, 4
RESTARTS = range(1, 9)

# Frozen task (seeds fixed in CONTRATO-F3.md)
X_TR = np.random.default_rng(20261009).standard_normal((N_TR, 4))
X_TE = np.random.default_rng(20261010).standard_normal((N_TE, 4))
_q = np.random.default_rng(20261011)
Q = np.stack([(lambda A: (A + A.T) / 2)(_q.standard_normal((4, 4))) for _ in range(K)])


def labels(X):
    return np.einsum("ni,kij,nj->nk", X, Q, X).argmax(1)


Y_TR, Y_TE = labels(X_TR), labels(X_TE)


def unpack_unitary(p):
    """16 real parameters -> Hermitian H (4x4) -> U = exp(iH)."""
    H = np.zeros((4, 4), complex)
    H[np.diag_indices(4)] = p[:4]
    iu = np.triu_indices(4, 1)
    re, im = p[4:10], p[10:16]
    H[iu] = re + 1j * im
    H = H + np.conj(H.T) - np.diag(np.diag(H))
    return expm(1j * H)


def logits(model, p, X):
    if model == "m1":
        U = unpack_unitary(p)
        Z = X @ U.T
        return np.abs(Z) ** 2
    if model == "m2":
        A = p.reshape(4, 4)
        return (X @ A.T) ** 2
    # m3: full quadratic, 4 symmetric matrices of 10 parameters each
    P = np.zeros((K, 4, 4))
    idx = 0
    for k in range(K):
        for i in range(4):
            for j in range(i, 4):
                P[k, i, j] = P[k, j, i] = p[idx]
                idx += 1
    return np.einsum("ni,kij,nj->nk", X, P, X)


def n_params(model):
    return {"m1": 16, "m2": 16, "m3": 40}[model]


def xent(p, model, X, y):
    z = logits(model, p, X)
    z = z - z.max(1, keepdims=True)
    lse = np.log(np.exp(z).sum(1))
    return float((lse - z[np.arange(len(y)), y]).mean())


def accuracy(model, p, X, y):
    return float((logits(model, p, X).argmax(1) == y).mean())


def train(model):
    best = None
    for seed in RESTARTS:
        rng = np.random.default_rng(seed)
        p0 = 0.5 * rng.standard_normal(n_params(model))
        res = minimize(xent, p0, args=(model, X_TR, Y_TR), method="L-BFGS-B",
                       options={"maxiter": 300})
        if best is None or res.fun < best["train_loss"]:
            best = {"seed": seed, "train_loss": float(res.fun), "p": res.x}
    return best


def run_model(model):
    t0 = time.monotonic()
    best = train(model)
    p = best["p"]
    out = {
        "model": model, "n_params": n_params(model), "best_seed": best["seed"],
        "train_loss": best["train_loss"],
        "train_acc": accuracy(model, p, X_TR, Y_TR),
        "test_acc": accuracy(model, p, X_TE, Y_TE),
        "test_pred": logits(model, p, X_TE).argmax(1).tolist(),
        "elapsed_s": time.monotonic() - t0,
    }
    store = HERE / "f3_resultados.json"
    data = json.loads(store.read_text(encoding="utf-8")) if store.exists() else {}
    data[model] = out
    store.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: out[k] for k in ("model", "n_params", "best_seed", "train_acc", "test_acc",
                                          "elapsed_s")}))


def aggregate():
    data = json.loads((HERE / "f3_resultados.json").read_text(encoding="utf-8"))
    m1, m2, m3 = data["m1"], data["m2"], data["m3"]
    p1 = np.array(m1["test_pred"]) == Y_TE
    p2 = np.array(m2["test_pred"]) == Y_TE
    rng = np.random.default_rng(20261012)
    diffs = []
    for _ in range(1000):
        idx = rng.integers(0, N_TE, N_TE)
        diffs.append(p1[idx].mean() - p2[idx].mean())
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    h1 = m1["test_acc"] >= 0.60
    h2 = (lo > 0)
    h3 = m3["test_acc"] >= m1["test_acc"]
    # energy break-even: electronic baseline does 20 operations per inference
    ops_elec = 20
    table = []
    for e_src in (1e-12, 1e-11):          # J per inference from the source
        for e_det in (1e-15, 1e-14, 1e-13):  # J per photodetection
            e_opt = e_src + 4 * e_det
            table.append({"E_src_J": e_src, "E_det_J": e_det, "E_opt_J": e_opt,
                          "E_op_breakeven_J": e_opt / ops_elec})
    agg = {
        "H1": {"test_acc_M1": m1["test_acc"], "threshold": 0.60, "passed": bool(h1)},
        "H2": {"acc_M1": m1["test_acc"], "acc_M2": m2["test_acc"],
               "diff_mean": float(np.mean(diffs)), "ci95": [float(lo), float(hi)], "passed": bool(h2)},
        "H3": {"acc_M3": m3["test_acc"], "acc_M1": m1["test_acc"], "passed": bool(h3)},
        "energy_breakeven_table": table,
        "energy_note": "Parametric break-even only; source and detector energies are assumptions, no advantage is claimed.",
    }
    (HERE / "f3_aggregate.json").write_text(json.dumps(agg, indent=1, ensure_ascii=False) + "\n",
                                            encoding="utf-8", newline="\n")
    print(json.dumps({"H1": agg["H1"]["passed"], "H2": agg["H2"]["passed"],
                      "H3": agg["H3"]["passed"], "test_acc": {"M1": m1["test_acc"], "M2": m2["test_acc"],
                                                              "M3": m3["test_acc"]}}))


if __name__ == "__main__":
    arg = sys.argv[1]
    if arg == "aggregate":
        aggregate()
    else:
        run_model(arg)
