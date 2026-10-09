"""E2 extension of CONTRACT-N-CONV.md: one case and one mesh per process.

Usage: python -B conv_extend.py <t_um> <dn> <N>
Writes conv_n_a10_ext.json, keyed by case and mesh.
"""
import json
import os
import pathlib
import sys
import time

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from diag_g2_radius10 import selected_mode  # noqa: E402

A = 10e-6
R0, RMAX, THETA = 70e-6, 150e-6, 0.6


def main(argv):
    t_um, dn, n = float(argv[1]), float(argv[2]), int(argv[3])
    t0 = time.monotonic()
    g, core = selected_mode(A, t_um * 1e-6, dn, dict(N=n, R0=R0, Rmax=RMAX, theta=THETA))
    rec = {"t_um": t_um, "dn": dn, "N": n, "re": g.real, "im": g.imag, "core": core,
           "elapsed_s": time.monotonic() - t0}
    out = HERE / "conv_n_a10_ext.json"
    rows = json.loads(out.read_text(encoding="utf-8")) if out.exists() else []
    rows = [r for r in rows if not (r["t_um"] == t_um and r["dn"] == dn and r["N"] == n)]
    rows.append(rec)
    out.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in rec.items()}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
