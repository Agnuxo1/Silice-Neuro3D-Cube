"""Barrido modal completo (CONTRATO-BARRIDO-MODAL.md): one case and one mesh per process.

Usage: python -B barrido_modal.py <a_um> <t_um> <dn> <N>
Writes barrido/a{a}_t{t}_dn{dn}_N{N}.json with the eight largest-Re eigenvalues,
the historical selection rule (run006a.cands), the eigen residual of the
selected mode, and the reason when no mode is selected.
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
sys.path.insert(0, str(HERE.parent / "glass005_claude"))

import numpy as np  # noqa: E402
import scipy.linalg as la  # noqa: E402
from radial_ecs import build  # noqa: E402

RC = 60e-6
R0, RMAX, THETA = 70e-6, 150e-6, 0.6


def main(argv):
    a_um, t_um, dn, n = float(argv[1]), float(argv[2]), float(argv[3]), int(argv[4])
    t0 = time.monotonic()
    x, r, s, h, H = build(dn, a_um * 1e-6, t_um * 1e-6, R0=R0, Rmax=RMAX, N=n, theta=THETA)
    ev, V = la.eig(H)
    w = r * s * h
    Vn = V / np.sqrt((V * V * w[:, None]).sum(0))
    ph = x < RC
    d = np.abs(Vn) ** 2 * np.abs(w)[:, None]
    core = d[x < a_um * 1e-6].sum(0) / d[ph].sum(0)
    order = np.argsort(-ev.real)[:8]
    top = []
    for i in order:
        res = float(np.linalg.norm(H @ Vn[:, i] - ev[i] * Vn[:, i]) / np.linalg.norm(Vn[:, i]))
        top.append({"re": float(ev[i].real), "im": float(ev[i].imag), "core": float(core[i]), "residual": res,
                    "passes_rule": bool(abs(ev[i].imag) < 3000 and core[i] > 0.3)})
    ok = [i for i in np.argsort(-ev.real) if abs(ev[i].imag) < 3000 and core[i] > 0.3]
    if ok:
        i = ok[0]
        sel = {"re": float(ev[i].real), "im": float(ev[i].imag), "core": float(core[i]),
               "residual": float(np.linalg.norm(H @ Vn[:, i] - ev[i] * Vn[:, i]) / np.linalg.norm(Vn[:, i]))}
        reason = None
    else:
        sel = None
        best = max(range(len(core)), key=lambda j: core[j])
        reason = {"best_core_candidate": {"re": float(ev[best].real), "im": float(ev[best].imag),
                                          "core": float(core[best])},
                  "excluded_by": "|Im| >= 3000" if abs(ev[best].imag) >= 3000 else "core <= 0.3"}
    rec = {"a_um": a_um, "t_um": t_um, "dn": dn, "N": n, "top8": top, "selected": sel, "no_mode_reason": reason,
           "elapsed_s": time.monotonic() - t0}
    out_dir = HERE / "barrido"
    out_dir.mkdir(exist_ok=True)
    (out_dir / f"a{a_um:g}_t{t_um:g}_dn{dn:g}_N{n}.json").write_text(
        json.dumps(rec, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"a": a_um, "t": t_um, "dn": dn, "N": n,
                      "selected": None if sel is None else round(sel["re"], 3),
                      "elapsed_s": round(rec["elapsed_s"], 2)}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
