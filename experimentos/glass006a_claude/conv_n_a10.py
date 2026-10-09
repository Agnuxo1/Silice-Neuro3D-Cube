"""N-convergence for a = 10 um (CONTRACT-N-CONV.md). One case per process.

Usage: python -B conv_n_a10.py <t_um> <dn>
Writes or updates conv_n_a10.json. Re-uses the mode selection of diag_g2_radius10.
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

MESHES = (500, 700, 900, 1100)
A = 10e-6
R0, RMAX, THETA = 70e-6, 150e-6, 0.6


def main(argv):
    t_um, dn = float(argv[1]), float(argv[2])
    t0 = time.monotonic()
    res = {}
    for n in MESHES:
        g, core = selected_mode(A, t_um * 1e-6, dn, dict(N=n, R0=R0, Rmax=RMAX, theta=THETA))
        res[str(n)] = {"re": g.real, "im": g.imag, "core": core}
    loss = {k: 2 * v["im"] * (10 / 2.302585092994046) * 0.01 for k, v in res.items()}
    pairs = []
    for lo, hi in zip(MESHES[:-1], MESHES[1:]):
        rel_re = abs(res[str(hi)]["re"] - res[str(lo)]["re"]) / abs(res[str(lo)]["re"])
        abs_loss = abs(loss[str(hi)] - loss[str(lo)])
        rel_loss = abs_loss / max(abs(loss[str(lo)]), 1e-30)
        pairs.append({"N": [lo, hi], "re_rel": rel_re, "loss_abs_dBcm": abs_loss, "loss_rel": rel_loss,
                      "G2_re": rel_re < 0.01,
                      "G2_loss": (rel_loss < 0.10) or (abs_loss < 0.005)})
    fine = pairs[-1]
    record = {"a_um": 10.0, "t_um": t_um, "dn": dn, "meshes": res, "loss_dB_cm": loss,
              "pairs": pairs, "G2_finest_pair": fine["G2_re"] and fine["G2_loss"],
              "elapsed_s": time.monotonic() - t0}
    out = HERE / "conv_n_a10.json"
    records = json.loads(out.read_text(encoding="utf-8")) if out.exists() else []
    records = [r for r in records if not (r["t_um"] == t_um and r["dn"] == dn)]
    records.append(record)
    out.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"t": t_um, "dn": dn, "re_rel_by_pair": [round(p["re_rel"], 5) for p in pairs],
                      "G2_finest": record["G2_finest_pair"], "elapsed_s": round(record["elapsed_s"], 1)}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
