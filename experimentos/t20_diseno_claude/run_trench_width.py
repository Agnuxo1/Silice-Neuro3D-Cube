"""Design prediction: HE11 leakage of the trench guide versus trench width (H1 amendment A1).

Uses the existing exact vector leaky-mode solver of the project
(experimentos/vectorial_claude/trinchera_vectorial.py, validated against the
step-index fibre for n_eff) without changing it. Geometry: core n0 = 1.444
(radius a = 6 um), trench n0 - 0.005 of width t, unbounded cladding n0,
lambda = 1550 nm. Output: leakage (dB/cm) for each t and the smallest width
whose leakage is at most 10 % of the state-of-the-art loss S1550 = 0.06 dB/cm.

Usage (from the repository root):
  python -B experimentos/t20_diseno_claude/run_trench_width.py --out resultados/agent/t20_trench_width_20261013/results.json
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experimentos" / "vectorial_claude"))

import trinchera_vectorial as solver  # noqa: E402

WIDTHS_UM = (12.0, 13.0, 14.0, 15.0, 16.0, 18.0, 20.0)
DN = -0.005
S1550 = 0.06          # dB/cm, Ackermann et al. 2025 (T26 rule R1)
TARGET = 0.1 * S1550  # leakage budget: 10 % of the state of the art


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out if args.out.is_absolute() else ROOT / args.out
    if out.exists():
        raise FileExistsError("Output must be new")
    out.parent.mkdir(parents=True, exist_ok=True)
    rows, started = [], time.monotonic()
    for t in WIDTHS_UM:
        tick = time.monotonic()
        r = solver.solve(DN, t, "HE11")
        rows.append({"t_um": t, "valid": r is not None,
                     "n_eff_re": None if r is None else r["n_eff_re"],
                     "n_eff_im": None if r is None else r["n_eff_im"],
                     "leakage_db_per_cm": None if r is None else r["loss_dB_per_cm"],
                     "n_valid_roots": None if r is None else r["n_valid_roots"],
                     "seconds": time.monotonic() - tick})
        print(json.dumps(rows[-1]), flush=True)
    valid = all(r["valid"] for r in rows)
    losses = [r["leakage_db_per_cm"] for r in rows]
    monotonic = valid and all(b < a for a, b in zip(losses, losses[1:]))
    reproduces = valid and abs(losses[0] - 0.044044) / 0.044044 < 1e-3
    t_star = None
    if monotonic:
        for (t0, l0), (t1, l1) in zip(zip(WIDTHS_UM, losses), zip(WIDTHS_UM[1:], losses[1:])):
            if l0 > TARGET >= l1:  # log-linear interpolation between grid points
                t_star = t0 + (t1 - t0) * (math.log(l0) - math.log(TARGET)) / (math.log(l0) - math.log(l1))
                break
    metrics = {"all_solves_valid": valid, "leakage_decreases_with_width": monotonic,
               "reproduces_registered_t12_value": reproduces,
               "t_min_um_for_10pct_of_sota": t_star}
    out.write_text(json.dumps({"scope": "numerical_model", "dn": DN, "a_um": 6.0, "wavelength_m": 1.55e-6,
                               "n0": 1.444, "s1550_db_per_cm": S1550, "target_db_per_cm": TARGET,
                               "rows": rows, "metrics": metrics,
                               "elapsed_s": time.monotonic() - started}, indent=1) + "\n",
                   encoding="utf-8", newline="\n")
    print(json.dumps(metrics))


if __name__ == "__main__":
    main()
