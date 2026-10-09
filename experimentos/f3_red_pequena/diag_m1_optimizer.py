"""Diagnostic for CONTRATO-F3.md (not a pre-registered result): is M1's accuracy
an optimiser artefact? 32 restarts, maxiter 2000, same loss and task as run_f3.py."""
import json
import pathlib
import sys
import numpy as np
from scipy.optimize import minimize

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import run_f3 as R  # noqa: E402

rows = []
for seed in range(1, 33):
    p0 = 0.5 * np.random.default_rng(seed).standard_normal(16)
    res = minimize(R.xent, p0, args=("m1", R.X_TR, R.Y_TR), method="L-BFGS-B", options={"maxiter": 2000})
    rows.append({"seed": seed, "train_loss": float(res.fun), "nit": int(res.nit), "success": bool(res.success),
                 "test_acc": R.accuracy("m1", res.x, R.X_TE, R.Y_TE)})
best = min(rows, key=lambda r: r["train_loss"])
summary = {"restarts": len(rows), "all_success": all(r["success"] for r in rows),
           "nit_range": [min(r["nit"] for r in rows), max(r["nit"] for r in rows)],
           "train_loss_best": best["train_loss"], "test_acc_of_best": best["test_acc"],
           "test_acc_range": [min(r["test_acc"] for r in rows), max(r["test_acc"] for r in rows)]}
out = pathlib.Path(__file__).resolve().parent / "diag_m1_optimizer.json"
out.write_text(json.dumps({"summary": summary, "rows": rows}, indent=1, ensure_ascii=False) + "\n",
               encoding="utf-8", newline="\n")
print(json.dumps(summary, ensure_ascii=False))
