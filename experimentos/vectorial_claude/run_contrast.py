"""Hypotheses H1-H3 of Docs/VECTORIAL-CONTRATO.md (with amendment E1).

Step 1: run gates V1-V5 (test_vector_step.py). If any gate fails, nothing is
reported and the script exits with status 2.
Step 2: evaluate H1-H3 with the thresholds fixed in the contract.
Step 3: write resultados_contraste.json next to this file.

Pure numpy/scipy, single thread. Run from this directory:
    python -B run_contrast.py
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import unittest

from vector_step import radius_for_v
from test_vector_step import LAM, N1, N2_PROJECT, V_STAR, modes

HERE = pathlib.Path(__file__).resolve().parent
H1_THRESHOLD = 1e-5   # |n_HE11 - n_LP01| / n1
H2_THRESHOLD = 1e-4   # (max - min) / mean of {TE01, TM01, HE21}, divided by n1
CONTRASTS = (0.001, 0.003, 0.005)


def polarisation_spread(m: dict, n1: float) -> float:
    """Relative spread of the three LP11-family exact indices."""
    values = [m["TE01"][1], m["TM01"][1], m["HE21"][1]]
    mean = sum(values) / len(values)
    return (max(values) - min(values)) / mean / n1


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_gates() -> bool:
    suite = unittest.defaultTestLoader.loadTestsFromName("test_vector_step")
    result = unittest.TextTestRunner(verbosity=1, stream=sys.stdout).run(suite)
    return result.wasSuccessful()


def main() -> int:
    if not run_gates():
        print("GATES V1-V5 FAILED: no results are reported.", file=sys.stderr)
        return 2

    m5 = modes(N1, N2_PROJECT, V_STAR)
    h1_value = abs(m5["HE11"][1] - m5["LP01"][1]) / N1
    h2_value = polarisation_spread(m5, N1)

    h3_rows = []
    for dn in CONTRASTS:
        n2 = N1 - dn
        mm = modes(N1, n2, V_STAR)
        h3_rows.append({
            "dn": dn,
            "a_um": radius_for_v(LAM, N1, n2, V_STAR) * 1e6,
            "spread_rel": polarisation_spread(mm, N1),
            "he11_minus_lp01_rel": (mm["HE11"][1] - mm["LP01"][1]) / N1,
        })
    spreads = [row["spread_rel"] for row in h3_rows]
    h3_monotonic = all(lo < hi for lo, hi in zip(spreads, spreads[1:]))

    report = {
        "contract": "Docs/VECTORIAL-CONTRATO.md",
        "amendment": "E1 (constant V* = %.6f for H3)" % V_STAR,
        "lambda_m": LAM, "n1": N1, "n2_project": N2_PROJECT,
        "a_project_um": 6.0, "V_star": V_STAR,
        "modes_project": {k: None if v is None else {"b": v[0], "n_eff": v[1]} for k, v in m5.items()},
        "H1": {"value": h1_value, "threshold": H1_THRESHOLD, "passed": h1_value <= H1_THRESHOLD},
        "H2": {"value": h2_value, "threshold": H2_THRESHOLD, "passed": h2_value >= H2_THRESHOLD},
        "H3": {"rows": h3_rows, "monotonic_increase": h3_monotonic, "passed": h3_monotonic},
        "sha256": {
            "vector_step.py": sha256(HERE / "vector_step.py"),
            "test_vector_step.py": sha256(HERE / "test_vector_step.py"),
            "run_contrast.py": sha256(HERE / "run_contrast.py"),
        },
    }
    out = HERE / "resultados_contraste.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    print(f"V* = {V_STAR:.6f}")
    for name, v in m5.items():
        print(f"  {name:5s} b={v[0]:.12f}  n_eff={v[1]:.12f}")
    print(f"H1 |HE11-LP01|/n1 = {h1_value:.3e}  threshold {H1_THRESHOLD:g}  passed={report['H1']['passed']}")
    print(f"H2 spread(TE01,TM01,HE21)/n1 = {h2_value:.3e}  threshold {H2_THRESHOLD:g}  passed={report['H2']['passed']}")
    for row in h3_rows:
        print(f"    dn={row['dn']:.3f} a={row['a_um']:.3f} um  spread={row['spread_rel']:.3e}")
    print(f"H3 monotonic increase with dn = {h3_monotonic}")
    print(f"written: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
