"""T12 control (CONTRATO-F3-SENSIBILIDAD.md): sensitivity of trained model A to V_pi and theta_b.

No retraining and no selection on the test set. The trained parameters are those of the restart with the
lowest training loss (f3b_seeds/a_s{seed}.json), evaluated with the control parameters changed.
Run: python -B sensibilidad_control.py   -> sensibilidad_resultados.json (same folder).
"""
import json, math, pathlib, sys
import numpy as np

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_f3 as F  # noqa: E402
import run_f3b as G  # noqa: E402

VPI_GRID = [0.5, 1.0, 2.0]
THB_GRID = [-math.pi / 4, 0.0, math.pi / 4]
TRAINED = {"V_PI": 1.0, "THETA_B": 0.0}
SENS_THRESHOLD = 0.05


def evaluate(p, vpi, thb):
    G.V_PI, G.THETA_B = vpi, thb  # the activation reads these module globals at call time
    return {"train_acc": G.acc("a", p, F.X_TR, F.Y_TR), "test_acc": G.acc("a", p, F.X_TE, F.Y_TE)}


if __name__ == "__main__":
    stored = json.loads((HERE / "f3b_resultados.json").read_text(encoding="utf-8"))["a"]
    rec = json.loads((HERE / "f3b_seeds" / f"a_s{stored['best_seed']}.json").read_text(encoding="utf-8"))
    p = np.array(rec["p"])
    base = evaluate(p, TRAINED["V_PI"], TRAINED["THETA_B"])
    s1_train = abs(base["train_acc"] - stored["train_acc"])
    s1_test = abs(base["test_acc"] - stored["test_acc"])
    s1_pass = bool(s1_train < 1e-12 and s1_test < 1e-12)
    grid = []
    for vpi in VPI_GRID:
        for thb in THB_GRID:
            r = evaluate(p, vpi, thb)
            grid.append({"V_pi": vpi, "theta_b": thb, **r})
    test_vals = [g["test_acc"] for g in grid]
    rng = max(test_vals) - min(test_vals)
    out = {
        "best_seed": stored["best_seed"],
        "trained_setting": TRAINED,
        "stored": {"train_acc": stored["train_acc"], "test_acc": stored["test_acc"]},
        "S1_reproduction": {"abs_diff_train": s1_train, "abs_diff_test": s1_test, "pass": s1_pass},
        "grid": grid,
        "S2_test_range": rng,
        "S2_sensitive": bool(rng > SENS_THRESHOLD),
        "S2_threshold": SENS_THRESHOLD,
    }
    (HERE / "sensibilidad_resultados.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                                                       encoding="utf-8", newline="\n")
    print(f"S1 reproduction: train diff {s1_train:.1e}, test diff {s1_test:.1e}, pass={s1_pass}")
    for g in grid:
        print(f"V_pi={g['V_pi']:<4} theta_b={g['theta_b']:+.4f}  train={g['train_acc']:.4f}  test={g['test_acc']:.4f}")
    print(f"S2 test range={rng:.4f} sensitive={rng > SENS_THRESHOLD}")
