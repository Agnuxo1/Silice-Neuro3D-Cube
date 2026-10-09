"""G2 diagnosis at a = 10 um (CONTRACT-G2-DIAG.md), one factor at a time.

Usage (one case per process, to stay under the 30 s per-script budget):
    python -B diag_g2_radius10.py <a_um> <t_um> <dn>
Appends one record to diag_g2_radius10.json. Stored results in resultados.json
are read for check P1 and are never modified.
"""
import json
import math
import os
import pathlib
import sys
import time

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "glass005_claude"))

import numpy as np  # noqa: E402
import scipy.linalg as la  # noqa: E402
from radial_ecs import build  # noqa: E402

RC = 60e-6
CFGS = {
    "nom": dict(N=500, R0=70e-6, Rmax=150e-6, theta=0.6),
    "Nx": dict(N=700, R0=70e-6, Rmax=150e-6, theta=0.6),
    "Th": dict(N=500, R0=70e-6, Rmax=150e-6, theta=0.8),
    "Dom": dict(N=500, R0=90e-6, Rmax=200e-6, theta=0.6),
    "B": dict(N=700, R0=90e-6, Rmax=200e-6, theta=0.5),
}
P1_TOL = 1e-6


def selected_mode(a, t, dn, c):
    """Same selection as run006a.modes/cands: top Re with |Im|<3000 and core>0.3."""
    x, r, s, h, H = build(dn, a, t, **c)
    ev, V = la.eig(H)
    w = r * s * h
    Vn = V / np.sqrt((V * V * w[:, None]).sum(0))
    ph = x < RC
    d = np.abs(Vn) ** 2 * np.abs(w)[:, None]
    core = d[x < a].sum(0) / d[ph].sum(0)
    ok = [i for i in np.argsort(-ev.real) if abs(ev[i].imag) < 3000 and core[i] > 0.3]
    i = ok[0]
    return complex(ev[i]), float(core[i])


def stored(a_um, t_um, dn):
    data = json.loads((HERE / "resultados.json").read_text(encoding="utf-8"))
    for case in data["cases"]:
        if case["a_um"] == a_um and case["t_um"] == t_um and case["dn"] == dn:
            return case["configs"]
    raise KeyError((a_um, t_um, dn))


def main(argv):
    a_um, t_um, dn = float(argv[1]), float(argv[2]), float(argv[3])
    t0 = time.monotonic()
    res = {}
    for name, cfg in CFGS.items():
        g, core = selected_mode(a_um * 1e-6, t_um * 1e-6, dn, dict(cfg))
        res[name] = {"re": g.real, "im": g.imag, "core": core}
    ref = stored(a_um, t_um, dn)
    p1 = {}
    for name in ("nom", "B"):
        s = ref[name]["gamma_re"]
        p1[name] = abs(res[name]["re"] - s) / abs(s)
    p1_ok = all(v <= P1_TOL for v in p1.values())

    re_nom = res["nom"]["re"]
    delta_b = abs(res["B"]["re"] - re_nom) / abs(re_nom)
    rel = {f: abs(res[f]["re"] - re_nom) / abs(re_nom) for f in ("Nx", "Th", "Dom")}
    # P2 as a set: every single factor that reaches 50 % of the nom-to-B change.
    # More than one factor may qualify; the set is reported, never one pick.
    names = {"Dom": "domain (R0, Rmax)", "Nx": "grid N", "Th": "grid theta"}
    qualifying = [names[f] for f in ("Dom", "Nx", "Th") if delta_b > 0 and rel[f] >= 0.5 * delta_b]
    attribution = qualifying if (p1_ok and qualifying) else ("not attributed" if p1_ok else "P1 failed")

    record = {
        "a_um": a_um, "t_um": t_um, "dn": dn,
        "configs": res, "P1_relative_error": p1, "P1_passed": p1_ok,
        "delta_B_relative": delta_b, "single_factor_relative": rel,
        "attribution_rule_50pct": attribution,
        "elapsed_s": time.monotonic() - t0,
    }
    out = HERE / "diag_g2_radius10.json"
    records = json.loads(out.read_text(encoding="utf-8")) if out.exists() else []
    records = [r for r in records if not (r["a_um"] == a_um and r["t_um"] == t_um and r["dn"] == dn)]
    records.append(record)
    out.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: record[k] for k in ("a_um", "t_um", "dn", "P1_passed", "delta_B_relative",
                                             "single_factor_relative", "attribution_rule_50pct",
                                             "elapsed_s")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
